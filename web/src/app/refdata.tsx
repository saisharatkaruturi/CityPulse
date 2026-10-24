import { createContext, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import { api, type Category, type Department, type Officer, type Ward } from '../api';
import { useAuth } from '../auth';
import { useI18n } from '../i18n';
import { capabilities } from '../roles';

interface RefData {
  categories: Category[];
  /** Selectable leaf categories (active, not parents), in a stable order. */
  leaves: Category[];
  wards: Ward[];
  departments: Department[];
  officers: Officer[];
  /** False when the category list failed to load, so screens can say so instead of showing blanks. */
  categoriesFailed: boolean;
  category: (id: string | null | undefined) => Category | undefined;
  catName: (id: string | null | undefined) => string;
  catCode: (id: string | null | undefined) => string | null;
  wardName: (id: string | null | undefined) => string;
  deptName: (id: string | null | undefined) => string;
  officerName: (id: string | null | undefined) => string;
}

const Ctx = createContext<RefData | null>(null);

/**
 * Names for ids. Categories come back in the UI language (Accept-Language) and reload when it changes.
 * Departments and officers load only for roles that may list them; the provider remounts per user, so
 * nothing from a previous account survives a sign-out or a switch of demo account.
 */
export function RefDataProvider({ children }: { children: ReactNode }) {
  const { user, experience } = useAuth();
  const { locale, t } = useI18n();
  const [categories, setCategories] = useState<Category[]>([]);
  const [categoriesFailed, setFailed] = useState(false);
  const [wards, setWards] = useState<Ward[]>([]);
  const [departments, setDepartments] = useState<Department[]>([]);
  const [officers, setOfficers] = useState<Officer[]>([]);
  const caps = capabilities(experience);
  const canListDepartments = caps.manage || experience === 'auditor';

  useEffect(() => {
    const ctrl = new AbortController();
    api<Category[]>('/categories', { signal: ctrl.signal })
      .then((c) => { setCategories(c); setFailed(false); })
      .catch((e) => { if (!ctrl.signal.aborted) setFailed(Boolean(e)); });
    return () => ctrl.abort();
  }, [locale]);

  useEffect(() => {
    api<Ward[]>('/wards').then(setWards).catch(() => setWards([]));
  }, []);

  useEffect(() => {
    if (!user || !canListDepartments) return;
    api<Department[]>('/admin/departments').then(setDepartments).catch(() => setDepartments([]));
    if (caps.manage) api<Officer[]>('/admin/officers').then(setOfficers).catch(() => setOfficers([]));
  }, [user, canListDepartments, caps.manage]);

  const value = useMemo<RefData>(() => {
    const by = <T extends { id: string }>(xs: T[]) => new Map(xs.map((x) => [x.id, x]));
    const c = by(categories), w = by(wards), d = by(departments), o = by(officers);
    const parents = new Set(categories.map((x) => x.parent_id).filter(Boolean));
    const leaves = categories
      .filter((x) => x.is_active && !parents.has(x.id))
      .sort((a, b) => Number(a.is_triage) - Number(b.is_triage) || a.code.localeCompare(b.code));
    return {
      categories, leaves, wards, departments, officers, categoriesFailed,
      category: (id) => (id ? c.get(id) : undefined),
      catName: (id) => (id ? c.get(id)?.label ?? t('category.unknown') : t('category.none')),
      catCode: (id) => (id ? c.get(id)?.code ?? null : null),
      wardName: (id) => (id ? w.get(id)?.name ?? '—' : '—'),
      deptName: (id) => (id ? d.get(id)?.name ?? '—' : '—'),
      officerName: (id) => (id ? o.get(id)?.display_name ?? '—' : '—'),
    };
  }, [categories, wards, departments, officers, categoriesFailed, t]);

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useRef$(): RefData {
  const v = useContext(Ctx);
  if (!v) throw new Error('useRef$ outside RefDataProvider');
  return v;
}
