import { useCallback, useState, type ReactNode } from 'react';
import { ApiError } from '../../api';
import { Icon } from '../../components/Icon';
import { useI18n } from '../../i18n';
import { errorKey } from '../../lib';

/** Context every case action needs: the version to send, and how to report a confirmed save. */
export interface CaseActions {
  ifMatch: Record<string, string>;
  /** Called only after the server confirmed: shows the message and reloads the case from the server. */
  saved: (message: string) => Promise<void>;
  reload: () => Promise<void>;
}

/** One action's request state. Input stays in the form on failure; success only after the server says so. */
export function useMutation() {
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<unknown>(null);
  const run = useCallback(async (fn: () => Promise<unknown>): Promise<boolean> => {
    setBusy(true);
    setError(null);
    try {
      await fn();
      return true;
    } catch (e) {
      setError(e);
      return false;
    } finally {
      setBusy(false);
    }
  }, []);
  return { busy, error, run, clear: () => setError(null) };
}

export const isConflict = (e: unknown) => e instanceof ApiError && (e.status === 409 || e.status === 412);

/** An action's error, with field detail from the server and a reload button when the case changed. */
export function MutationError({ error, onReload }: { error: unknown; onReload: () => void }) {
  const { t } = useI18n();
  if (!error) return null;
  const k = errorKey(error);
  const detail = error instanceof ApiError && error.status === 422 ? error.details.map((d) => d.message).filter(Boolean).join(' ') || error.message : null;
  return (
    <div className="field-error action-error" role="alert">
      <Icon.alert size={16} />
      <span>
        {t(k.key, k.vars)}{detail ? ` ${detail}` : ''}
        {isConflict(error) && <> <button type="button" className="link-btn" onClick={onReload}>{t('case.reloadLatest')}</button></>}
      </span>
    </div>
  );
}

export function Section({ title, aside, children, className = '' }: { title: string; aside?: ReactNode; children: ReactNode; className?: string }) {
  return (
    <section className={`panel case-section ${className}`}>
      <div className="panel-head"><h2>{title}</h2>{aside}</div>
      {children}
    </section>
  );
}
