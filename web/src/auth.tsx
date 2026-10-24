import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import { api, getToken, setToken, type Role, type User } from './api';
import { experienceOf, roleTitleKey, type Experience } from './roles';

interface AuthState {
  user: User | null;
  loading: boolean;
  /** Set when the session ended on its own (expired token), so sign-in can say so. */
  expired: boolean;
  experience: Experience;
  roleTitle: ReturnType<typeof roleTitleKey>;
  signIn: (email: string, password: string) => Promise<User>;
  signOut: () => Promise<void>;
  has: (...roles: Role[]) => boolean;
  isStaff: boolean;
}

const AuthContext = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(Boolean(getToken()));
  const [expired, setExpired] = useState(false);

  useEffect(() => {
    if (!getToken()) return;
    api<User>('/users/me')
      .then(setUser)
      .catch(() => setToken(null))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    const out = () => {
      setUser(null);
      setExpired(true);
    };
    window.addEventListener('ycys:signed-out', out);
    return () => window.removeEventListener('ycys:signed-out', out);
  }, []);

  const signIn = useCallback(async (email: string, password: string) => {
    // A new sign-in always starts clean: drop any previous token and any role-specific state first.
    setToken(null);
    setUser(null);
    const t = await api<{ access_token: string }>('/auth/login', { body: { email, password } });
    setToken(t.access_token);
    const me = await api<User>('/users/me');
    setExpired(false);
    setUser(me);
    return me;
  }, []);

  const signOut = useCallback(async () => {
    try {
      await api('/auth/logout', { method: 'POST' });
    } catch {
      /* the token is discarded locally either way */
    } finally {
      setToken(null);
      setUser(null);
      setExpired(false);
    }
  }, []);

  const value = useMemo<AuthState>(() => {
    const grants = user?.roles ?? [];
    const roles = new Set(grants.map((r) => r.role));
    const experience = experienceOf(grants);
    return {
      user, loading, expired, signIn, signOut, experience,
      roleTitle: roleTitleKey(grants),
      has: (...rs) => rs.some((r) => roles.has(r)),
      isStaff: experience !== 'resident',
    };
  }, [user, loading, expired, signIn, signOut]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth outside AuthProvider');
  return ctx;
}
