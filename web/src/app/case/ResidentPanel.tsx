import { useId, useState, type FormEvent } from 'react';
import { api, type Complaint } from '../../api';
import { ConfirmDialog, useUnsavedWarning } from '../../components/ui';
import { useI18n } from '../../i18n';
import { OPEN } from '../../lib';
import { MutationError, Section, useMutation, type CaseActions } from './mutation';

/** What the person who reported it can do: confirm a fix, say it is not fixed, or withdraw it. */
export function ResidentPanel({ c, actions }: { c: Complaint; actions: CaseActions }) {
  const { t } = useI18n();
  const id = useId();
  const [rating, setRating] = useState(5);
  const [comment, setComment] = useState('');
  const [reopen, setReopen] = useState('');
  const [withdraw, setWithdraw] = useState(false);
  const confirmM = useMutation();
  const reopenM = useMutation();
  useUnsavedWarning(reopen.trim().length > 0 || comment.trim().length > 0);

  const confirmFixed = async (e: FormEvent) => {
    e.preventDefault();
    if (confirmM.busy) return;
    const ok = await confirmM.run(() => api(`/complaints/${c.id}/feedback`, { body: { rating, comment: comment.trim() || undefined, confirm_resolved: true } }));
    if (ok) { setComment(''); await actions.saved(t('case.saved.confirmed')); }
  };
  const sendReopen = async (e: FormEvent) => {
    e.preventDefault();
    if (reopen.trim().length < 3 || reopenM.busy) return;
    const ok = await reopenM.run(() => api(`/complaints/${c.id}/reopen`, { body: { reason: reopen.trim() }, headers: actions.ifMatch }));
    if (ok) { setReopen(''); await actions.saved(t('case.saved.reopened')); }
  };

  return (
    <>
      {c.status === 'resolved' && !c.progress.resident_confirmed && (
        <Section title={t('case.res.isFixed')}>
          <p className="meta" style={{ marginBottom: 12 }}>{t('case.res.isFixedHint')}</p>
          <form className="stack-sm case-form" onSubmit={confirmFixed}>
            <div className="field">
              <label htmlFor={`${id}-rating`}>{t('case.res.rating')}</label>
              <select id={`${id}-rating`} className="input" value={rating} onChange={(e) => setRating(Number(e.target.value))}>
                {[5, 4, 3, 2, 1].map((n) => <option key={n} value={n}>{t(`case.res.rating${n}` as 'case.res.rating5')}</option>)}
              </select>
            </div>
            <div className="field">
              <label htmlFor={`${id}-comment`}>{t('case.res.comment')} <span className="req">({t('common.optional')})</span></label>
              <textarea id={`${id}-comment`} className="input" rows={2} maxLength={2000} value={comment} onChange={(e) => setComment(e.target.value)} />
            </div>
            <MutationError error={confirmM.error} onReload={() => void actions.reload()} />
            <button className="btn btn-primary" disabled={confirmM.busy}>{confirmM.busy ? t('common.saving') : t('case.res.yesFixed')}</button>
          </form>
        </Section>
      )}
      {(c.status === 'resolved' || c.status === 'closed') && !c.merged_into_reference && (
        <Section title={t('case.res.notFixed')}>
          <form className="stack-sm case-form" onSubmit={sendReopen}>
            <div className="field">
              <label htmlFor={`${id}-reopen`}>{t('case.res.reopenReason')}</label>
              <textarea id={`${id}-reopen`} className="input" rows={3} maxLength={1000} value={reopen} onChange={(e) => setReopen(e.target.value)} />
              <span className="hint">{t('case.res.reopenHint')}</span>
            </div>
            <MutationError error={reopenM.error} onReload={() => void actions.reload()} />
            <button className="btn" disabled={reopenM.busy || reopen.trim().length < 3}>{reopenM.busy ? t('common.saving') : t('case.res.reopen')}</button>
          </form>
        </Section>
      )}
      {OPEN.includes(c.status) && (
        <Section title={t('case.res.noLonger')}>
          <p className="meta" style={{ marginBottom: 12 }}>{t('case.res.withdrawHint')}</p>
          <button className="btn" type="button" onClick={() => setWithdraw(true)}>{t('case.res.withdraw')}</button>
          <ConfirmDialog open={withdraw} onClose={() => setWithdraw(false)} title={t('case.res.withdrawTitle', { ref: c.reference })}
            body={t('case.res.withdrawBody')} confirmLabel={t('case.res.withdraw')} danger
            onConfirm={async () => {
              await api(`/complaints/${c.id}/withdraw`, { body: {}, headers: actions.ifMatch });
              await actions.saved(t('case.saved.withdrawn'));
            }} />
        </Section>
      )}
    </>
  );
}
