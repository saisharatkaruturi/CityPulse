// Shared building blocks. Styling lives in styles/app.css (app screens) and styles/landing.css (public).
import { useEffect, useId, useRef, useState, type FormEvent, type ReactNode } from 'react';
import type { Priority, Status } from '../api';
import { LOCALES, useI18n } from '../i18n';
import { PRIORITY_TONE, STATUS_TONE, asFamily, errorKey, isPriority, isStatus, type Tone } from '../lib';
import { useMeta } from '../meta';
import { FamilyIcon, Icon } from './Icon';

// ---- status, priority, category -----------------------------------------------------------------

const TONE_GLYPH: Record<Tone, ReactNode> = {
  // a shape per tone, so the pill reads without colour too
  neutral: <circle cx="5" cy="5" r="3.25" fill="none" stroke="currentColor" strokeWidth="1.5" />,
  info: <circle cx="5" cy="5" r="3.5" fill="currentColor" />,
  warn: <path d="M5 1.5 8.75 8.5H1.25z" fill="currentColor" />,
  ok: <path d="m1.75 5.25 2.25 2.25 4.25-4.75" fill="none" stroke="currentColor" strokeWidth="1.75" strokeLinecap="round" strokeLinejoin="round" />,
  bad: <rect x="1.75" y="1.75" width="6.5" height="6.5" rx="1" fill="currentColor" />,
};

export function Pill({ tone, children, title }: { tone: Tone; children: ReactNode; title?: string }) {
  return (
    <span className={`pill pill-${tone}`} title={title}>
      <svg viewBox="0 0 10 10" width="10" height="10" aria-hidden="true">{TONE_GLYPH[tone]}</svg>
      <span>{children}</span>
    </span>
  );
}

export function StatusPill({ status }: { status: Status | string }) {
  const { t, tk } = useI18n();
  if (!isStatus(status)) return <Pill tone="neutral">{t('status.unknown', { code: status })}</Pill>;
  return <Pill tone={STATUS_TONE[status]}>{tk(`status.${status}`)}</Pill>;
}

export function PriorityPill({ priority }: { priority: Priority | string }) {
  const { t, tk } = useI18n();
  if (!isPriority(priority)) return <Pill tone="neutral">{t('priority.unknown', { code: priority })}</Pill>;
  return <Pill tone={PRIORITY_TONE[priority]}>{tk(`priority.${priority}`)}</Pill>;
}

/** A category name with its family mark. Name always shown; colour and shape only reinforce it. */
export function CategoryMark({ code, label }: { code: string | null | undefined; label: string }) {
  const fam = asFamily(code);
  const I = FamilyIcon[fam];
  return (
    <span className={`cat cat-${fam}`}>
      <span className="cat-mark"><I size={16} /></span>
      <span>{label}</span>
    </span>
  );
}

// ---- demo, copyright, language ------------------------------------------------------------------

export function DemoBadge({ withNote = false }: { withNote?: boolean }) {
  const { meta } = useMeta();
  const { t } = useI18n();
  if (!meta?.demo_mode) return null;
  return (
    <span className="demo-badge-wrap">
      <span className="demo-badge" aria-label={`${t('app.demo')}: ${t('app.demoNote')}`}>{t('app.demo')}</span>
      {withNote && <span className="demo-note">{t('app.demoNote')}</span>}
    </span>
  );
}

export function Copyright() {
  return <span className="copyright">© 2026 Your City, Your Services</span>;
}

export function LanguageSwitch({ className = '' }: { className?: string }) {
  const { locale, setLocale, t } = useI18n();
  return (
    <div className={`lang-switch ${className}`} role="group" aria-label={t('app.language')}>
      <Icon.globe size={16} />
      {LOCALES.map((l) => (
        <button key={l.code} type="button" lang={l.code} aria-pressed={locale === l.code} onClick={() => setLocale(l.code)}>
          {l.native}
        </button>
      ))}
    </div>
  );
}

// ---- dialogs ------------------------------------------------------------------------------------

/**
 * Modal built on <dialog>: the browser traps focus, closes on Escape and draws it in the top layer, so no
 * parent can clip it. Focus returns to whatever opened it.
 */
export function Dialog({ open, onClose, title, children, footer, size = 'md', describedBy }: {
  open: boolean; onClose: () => void; title: string; children: ReactNode; footer?: ReactNode;
  size?: 'md' | 'lg'; describedBy?: string;
}) {
  const { t } = useI18n();
  const ref = useRef<HTMLDialogElement>(null);
  const opener = useRef<Element | null>(null);
  const titleId = useId();
  useEffect(() => {
    const d = ref.current;
    if (!d) return;
    if (open && !d.open) {
      opener.current = document.activeElement;
      d.showModal();
    } else if (!open && d.open) {
      d.close();
    }
  }, [open]);
  useEffect(() => () => {
    if (opener.current instanceof HTMLElement) opener.current.focus();
  }, []);
  return (
    <dialog
      ref={ref}
      className={`dialog dialog-${size}`}
      aria-labelledby={titleId}
      aria-describedby={describedBy}
      onClose={() => {
        onClose();
        if (opener.current instanceof HTMLElement) opener.current.focus();
      }}
      onCancel={(e) => { e.preventDefault(); onClose(); }}
      onClick={(e) => { if (e.target === ref.current) onClose(); }}
    >
      {open && (
        <div className="dialog-inner">
          <header className="dialog-head">
            <h2 id={titleId}>{title}</h2>
            <button type="button" className="icon-btn" onClick={onClose} aria-label={t('common.close')}>
              <Icon.close />
            </button>
          </header>
          <div className="dialog-body">{children}</div>
          {footer && <footer className="dialog-foot">{footer}</footer>}
        </div>
      )}
    </dialog>
  );
}

/**
 * Confirmation for a consequential action. With `reason`, a written reason (min 3 chars) is required and
 * passed to `onConfirm`. Errors from `onConfirm` stay inside the dialog with the text kept.
 */
export function ConfirmDialog({ open, onClose, title, body, confirmLabel, onConfirm, reason, reasonLabel, danger }: {
  open: boolean; onClose: () => void; title: string; body: ReactNode; confirmLabel: string;
  onConfirm: (reason: string) => Promise<void>; reason?: boolean; reasonLabel?: string; danger?: boolean;
}) {
  const { t } = useI18n();
  const [text, setText] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const id = useId();
  useEffect(() => { if (open) { setText(''); setError(null); } }, [open]);
  const submit = async (e: FormEvent) => {
    e.preventDefault();
    if (busy || (reason && text.trim().length < 3)) return;
    setBusy(true);
    setError(null);
    try {
      await onConfirm(text.trim());
      onClose();
    } catch (err) {
      const k = errorKey(err);
      setError(t(k.key, k.vars));
    } finally {
      setBusy(false);
    }
  };
  return (
    <Dialog open={open} onClose={() => !busy && onClose()} title={title} describedBy={`${id}-body`}>
      <form onSubmit={submit} className="stack-sm">
        <div id={`${id}-body`} className="dialog-text">{body}</div>
        {reason && (
          <div className="field">
            <label htmlFor={`${id}-reason`}>{reasonLabel}</label>
            <textarea id={`${id}-reason`} className="input" rows={3} value={text} maxLength={1000}
              onChange={(e) => setText(e.target.value)} required minLength={3} autoFocus />
          </div>
        )}
        {error && <p className="field-error" role="alert"><Icon.alert size={16} />{error}</p>}
        <div className="actions end">
          <button type="button" className="btn btn-quiet" onClick={onClose} disabled={busy}>{t('common.cancel')}</button>
          <button type="submit" className={`btn ${danger ? 'btn-danger' : 'btn-primary'}`}
            disabled={busy || (reason && text.trim().length < 3)} aria-busy={busy}>
            {busy ? t('common.saving') : confirmLabel}
          </button>
        </div>
      </form>
    </Dialog>
  );
}

// ---- page furniture -----------------------------------------------------------------------------

export function PageHeader({ title, sub, actions, children }: { title: string; sub?: ReactNode; actions?: ReactNode; children?: ReactNode }) {
  return (
    <div className="page-head">
      <div className="page-head-text">
        <h1>{title}</h1>
        {sub && <p className="page-sub">{sub}</p>}
        {children}
      </div>
      {actions && <div className="page-head-actions">{actions}</div>}
    </div>
  );
}

/** Refresh that really reloads: disabled while a request runs, shows when data last arrived. */
export function RefreshControl({ onRefresh, refreshing, updatedAt, label }: {
  onRefresh: () => void; refreshing: boolean; updatedAt: Date | null; label?: string;
}) {
  const { t, fmt } = useI18n();
  return (
    <div className="refresh">
      {updatedAt && <span className="meta" aria-live="polite">{t('common.updatedAt', { time: fmt.time(updatedAt) })}</span>}
      <button type="button" className="btn btn-quiet" onClick={onRefresh} disabled={refreshing} aria-busy={refreshing}
        aria-label={label ?? t('common.refresh')}>
        <Icon.refresh size={18} className={refreshing ? 'spin-once' : undefined} />
        <span>{refreshing ? t('common.refreshing') : t('common.refresh')}</span>
      </button>
    </div>
  );
}

export function ErrorState({ error, onRetry, title }: { error: unknown; onRetry?: () => void; title?: string }) {
  const { t } = useI18n();
  const k = errorKey(error);
  return (
    <div className="state state-error" role="alert">
      <Icon.alert size={22} />
      <div>
        {title && <p className="state-title">{title}</p>}
        <p>{t(k.key, k.vars)}</p>
        {onRetry && <button type="button" className="btn btn-quiet" onClick={onRetry}>{t('common.retry')}</button>}
      </div>
    </div>
  );
}

/** A failed background refresh while older data is still shown. */
export function StaleNotice({ error, onRetry }: { error: unknown; onRetry: () => void }) {
  const { t } = useI18n();
  const k = errorKey(error);
  return (
    <p className="notice notice-warn" role="status">
      <Icon.alert size={16} />
      <span>{t('common.staleData', { error: t(k.key, k.vars) })}</span>
      <button type="button" className="link-btn" onClick={onRetry}>{t('common.retry')}</button>
    </p>
  );
}

export function EmptyState({ title, children, action }: { title: string; children?: ReactNode; action?: ReactNode }) {
  return (
    <div className="state state-empty">
      <p className="state-title">{title}</p>
      {children && <div className="state-body">{children}</div>}
      {action}
    </div>
  );
}

export function Skeleton({ rows = 4, height = 20 }: { rows?: number; height?: number }) {
  const { t } = useI18n();
  return (
    <div className="skeleton-wrap" aria-busy="true" aria-label={t('common.loading')}>
      {Array.from({ length: rows }, (_, i) => <span key={i} className="skeleton" style={{ height }} />)}
    </div>
  );
}

/** Warn before the tab closes when a form holds edits that have not been saved. */
export function useUnsavedWarning(dirty: boolean) {
  useEffect(() => {
    if (!dirty) return;
    const h = (e: BeforeUnloadEvent) => { e.preventDefault(); e.returnValue = ''; };
    window.addEventListener('beforeunload', h);
    return () => window.removeEventListener('beforeunload', h);
  }, [dirty]);
}
