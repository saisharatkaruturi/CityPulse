import '../styles/app.css';
import '../styles/auth.css';

import { useEffect, useId, useRef, useState, type FormEvent, type ReactNode } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { ApiError, type DemoAccount, type User } from '../api';
import { useAuth } from '../auth';
import { Icon } from '../components/Icon';
import { LogoMark, Wordmark } from '../components/Logo';
import { Backdrop } from '../components/Backdrop';
import { Copyright, DemoBadge, Dialog, LanguageSwitch } from '../components/ui';
import { useI18n, type MessageKey } from '../i18n';
import { afterSignIn, looksLikeEmail } from '../landing/helpers';
import { errorKey } from '../lib';
import { useMeta } from '../meta';
import { experienceOf } from '../roles';

const GROUP_ORDER = ['resident', 'road_officer', 'road_supervisor', 'triage_desk', 'municipal_admin', 'auditor'];

/** Shared frame for sign-in and sign-up: the form on paper, a quiet ink panel with the mark beside it. */
export function AuthFrame({ children }: { children: ReactNode }) {
  const { t } = useI18n();
  return (
    <div className="auth aurora">
      <Backdrop />
      <a className="skip-link" href="#main">{t('app.skip')}</a>
      <div className="auth-side">
        <header className="auth-top">
          <Link to="/" className="auth-brand" aria-label={t('app.home')}><Wordmark /></Link>
          <LanguageSwitch />
        </header>
        <main id="main" className="auth-main">{children}</main>
        <footer className="auth-foot">
          <Copyright />
          <DemoBadge withNote />
        </footer>
      </div>
      <div className="auth-art" aria-hidden="true">
        <div className="auth-mark"><LogoMark size={180} tone="dark" /></div>
        <p className="auth-art-title">{t('auth.signIn.artTitle')}</p>
        <p className="auth-art-body">{t('auth.signIn.artBody')}</p>
      </div>
    </div>
  );
}

/** Password input with a visibility toggle that keeps focus and announces its state. */
export function PasswordField({ id, value, onChange, error, autoComplete, describedBy }: {
  id: string; value: string; onChange: (v: string) => void; error?: string; autoComplete: string; describedBy?: string;
}) {
  const { t } = useI18n();
  const [shown, setShown] = useState(false);
  const desc = [error ? `${id}-err` : null, describedBy].filter(Boolean).join(' ') || undefined;
  return (
    <div className="pw">
      <input id={id} className="input" type={shown ? 'text' : 'password'} value={value} autoComplete={autoComplete}
        onChange={(e) => onChange(e.target.value)} aria-invalid={Boolean(error)} aria-describedby={desc} spellCheck={false} />
      <button type="button" className="pw-toggle" onClick={() => setShown((s) => !s)} aria-pressed={shown}
        aria-label={shown ? t('auth.field.hidePassword') : t('auth.field.showPassword')} aria-controls={id}>
        {shown ? <Icon.eyeOff size={18} /> : <Icon.eye size={18} />}
      </button>
    </div>
  );
}

export function FieldError({ id, text }: { id: string; text?: string }) {
  if (!text) return null;
  return <p id={id} className="field-error"><Icon.alert size={16} />{text}</p>;
}

function signInErrorKey(e: unknown): { key: MessageKey; vars?: Record<string, string | number> } {
  // 401 and 422 both mean "these credentials don't work"; one message, so nothing reveals which emails exist.
  if (e instanceof ApiError && (e.status === 401 || e.status === 422 || e.status === 400)) return { key: 'auth.signIn.invalid' };
  return errorKey(e);
}

export default function SignIn() {
  const { signIn, expired, user, experience } = useAuth();
  const { meta } = useMeta();
  const { t, tk } = useI18n();
  const nav = useNavigate();
  const [params] = useSearchParams();
  const id = useId();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errors, setErrors] = useState<{ email?: string; password?: string }>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [demoOpen, setDemoOpen] = useState(false);
  const [demoBusy, setDemoBusy] = useState<string | null>(null);
  const [demoError, setDemoError] = useState<string | null>(null);
  const pending = useRef(false);
  const next = params.get('next');

  useEffect(() => { document.title = `${t('auth.signIn.title')} · ${t('app.name')}`; }, [t]);

  const go = (me: User) => nav(afterSignIn(next, experienceOf(me.roles)), { replace: true });

  async function submit(e: FormEvent) {
    e.preventDefault();
    if (pending.current) return;
    const errs: typeof errors = {};
    if (!email.trim()) errs.email = t('auth.err.emailRequired');
    else if (!looksLikeEmail(email)) errs.email = t('auth.err.emailFormat');
    if (!password) errs.password = t('auth.err.passwordRequired');
    setErrors(errs);
    setFormError(null);
    if (errs.email || errs.password) {
      document.getElementById(errs.email ? `${id}-email` : `${id}-pw`)?.focus();
      return;
    }
    pending.current = true;
    setBusy(true);
    try {
      go(await signIn(email.trim(), password));
    } catch (err) {
      const k = signInErrorKey(err);
      setFormError(t(k.key, k.vars));
    } finally {
      pending.current = false;
      setBusy(false);
    }
  }

  async function chooseDemo(a: DemoAccount) {
    if (pending.current) return;
    pending.current = true;
    setDemoBusy(a.email);
    setDemoError(null);
    try {
      const me = await signIn(a.email, a.password);
      setDemoOpen(false);
      go(me);
    } catch (err) {
      const k = signInErrorKey(err);
      setDemoError(t(k.key, k.vars));
    } finally {
      pending.current = false;
      setDemoBusy(null);
    }
  }

  const accounts = meta?.demo_accounts ?? [];
  const groups = [...GROUP_ORDER, ...accounts.map((a) => a.group).filter((g) => !GROUP_ORDER.includes(g))]
    .filter((g, i, arr) => arr.indexOf(g) === i)
    .map((g) => ({ group: g, items: accounts.filter((a) => a.group === g) }))
    .filter((g) => g.items.length);

  return (
    <AuthFrame>
      <div className="auth-card glass">
        <h1 className="auth-title">{t('auth.signIn.title')}</h1>
        <p className="auth-lead">{t('auth.signIn.lead')}</p>
        {expired && !user && <p className="notice notice-warn" role="status"><Icon.clock size={16} />{t('auth.signIn.expired')}</p>}
        {user && (
          <p className="notice notice-info" role="status">
            <Icon.info size={16} />
            <span>{t('nav.signedInAs', { name: user.display_name })} · <Link to={afterSignIn(next, experience)}>{t('landing.nav.openWork')}</Link></span>
          </p>
        )}
        <form className="stack auth-form" onSubmit={submit} noValidate aria-describedby={formError ? `${id}-form-err` : undefined}>
          <div className="field">
            <label htmlFor={`${id}-email`}>{t('auth.field.email')}</label>
            <input id={`${id}-email`} className="input" type="email" inputMode="email" autoComplete="username" value={email}
              onChange={(e) => setEmail(e.target.value)} aria-invalid={Boolean(errors.email)}
              aria-describedby={errors.email ? `${id}-email-err` : undefined} spellCheck={false} autoCapitalize="none" />
            <FieldError id={`${id}-email-err`} text={errors.email} />
          </div>
          <div className="field">
            <label htmlFor={`${id}-pw`}>{t('auth.field.password')}</label>
            <PasswordField id={`${id}-pw`} value={password} onChange={setPassword} error={errors.password} autoComplete="current-password" />
            <FieldError id={`${id}-pw-err`} text={errors.password} />
          </div>
          {formError && <p id={`${id}-form-err`} className="notice notice-bad auth-error" role="alert"><Icon.alert size={16} />{formError}</p>}
          <button className="btn btn-primary btn-block" type="submit" disabled={busy} aria-busy={busy}>
            {busy ? t('auth.signIn.busy') : t('auth.signIn.submit')}
          </button>
        </form>

        {meta?.demo_mode && (
          <div className="demo-entry">
            <DemoBadge />
            <button type="button" className="btn btn-block" onClick={() => { setDemoError(null); setDemoOpen(true); }} aria-haspopup="dialog">
              <Icon.user size={18} /> {t('auth.demo.open')}
            </button>
          </div>
        )}

        <p className="auth-alt">
          {t('auth.signIn.noAccount')} <Link to={`/signup${next ? `?next=${encodeURIComponent(next)}` : ''}`}>{t('auth.signIn.create')}</Link>
        </p>
        <p className="auth-alt"><Link to="/"><Icon.chevronLeft size={16} /> {t('auth.backHome')}</Link></p>
      </div>

      <Dialog open={demoOpen} onClose={() => { if (!demoBusy) setDemoOpen(false); }} title={t('auth.demo.title')} size="lg">
        <div className="demo-dialog">
          <p className="demo-dialog-lead"><DemoBadge /> <span>{t('auth.demo.lead')}</span></p>
          {demoError && <p className="notice notice-bad" role="alert"><Icon.alert size={16} />{demoError}</p>}
          {groups.length === 0 && <p className="meta">{t('auth.demo.none')}</p>}
          {groups.map((g) => (
            <section key={g.group} className="demo-group" aria-labelledby={`${id}-g-${g.group}`}>
              <h3 id={`${id}-g-${g.group}`}>{GROUP_ORDER.includes(g.group) ? tk(`auth.demo.group.${g.group}`) : g.group}</h3>
              <p className="meta">{GROUP_ORDER.includes(g.group) ? tk(`auth.demo.desc.${g.group}`) : g.items[0].description}</p>
              <ul>
                {g.items.map((a) => (
                  <li key={a.email}>
                    <button type="button" className="demo-account" onClick={() => chooseDemo(a)} disabled={demoBusy !== null}
                      aria-busy={demoBusy === a.email}>
                      <span className="demo-name">{demoBusy === a.email ? t('auth.demo.busy', { name: a.display_name }) : a.display_name}</span>
                      <span className="demo-email">{a.email}</span>
                      <span className="demo-go" aria-hidden="true"><Icon.arrowRight size={18} /></span>
                      <span className="visually-hidden">{t('auth.demo.use', { name: a.display_name })}</span>
                    </button>
                  </li>
                ))}
              </ul>
            </section>
          ))}
        </div>
      </Dialog>
    </AuthFrame>
  );
}
