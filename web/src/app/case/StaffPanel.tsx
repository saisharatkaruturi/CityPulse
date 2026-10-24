import { useId, useState, type FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { api, PRIORITIES, type Complaint, type Duplicate, type Priority } from '../../api';
import { Icon } from '../../components/Icon';
import { ConfirmDialog, Pill, PriorityPill, StatusPill, useUnsavedWarning } from '../../components/ui';
import { useI18n } from '../../i18n';
import { dueState, FINISHED } from '../../lib';
import { useRef$ } from '../refdata';
import { CategoryOptions } from '../staff/CategoryOptions';
import { canResolve, movesFor, type Move } from './moves';
import { MutationError, Section, useMutation, type CaseActions } from './mutation';

/** Facts staff need at a glance: who has it, how urgent, against what target, and why it was routed there. */
export function CaseFacts({ c }: { c: Complaint }) {
  const { t, tk } = useI18n();
  const ref = useRef$();
  const open = !FINISHED.includes(c.status);
  const due = dueState(c.due_at, c.sla_paused_at);
  return (
    <Section title={t('case.facts')}>
      <dl className="kv">
        <dt>{t('case.department')}</dt><dd>{ref.deptName(c.department_id)}</dd>
        <dt>{t('case.officer')}</dt><dd>{c.assigned_officer_id ? ref.officerName(c.assigned_officer_id) : t('queue.unassigned')}</dd>
        <dt>{t('queue.col.priority')}</dt><dd><PriorityPill priority={c.priority} />{c.priority_reason && <span className="meta block">{c.priority_reason}</span>}</dd>
        <dt>{t('queue.col.target')}</dt>
        <dd className={open && (c.is_overdue || due.overdue) ? 'is-overdue' : ''}>{open ? tk(due.key, due.vars) : t('common.dash')}</dd>
        <dt>{t('case.escalation')}</dt><dd>{c.escalation_level ? t('case.escalationLevel', { n: c.escalation_level }) : t('common.none')}</dd>
        <dt>{t('case.routing')}</dt><dd>{c.routing_outcome === 'routed' ? t('case.routedByRule') : t('case.routedToTriage')}</dd>
      </dl>
      {c.routing_explanation && <p className="meta" style={{ marginTop: 10 }}>{c.routing_explanation}</p>}
    </Section>
  );
}

export function MovePanel({ c, actions }: { c: Complaint; actions: CaseActions }) {
  const { t, tk } = useI18n();
  const m = useMutation();
  const [dialog, setDialog] = useState<Move | null>(null);
  const moves = movesFor(c.status);
  if (!moves.length) return null;
  const go = (mv: Move, reason?: string) =>
    api(`/complaints/${c.id}/transitions`, { body: { to_status: mv.to, reason: reason || undefined }, headers: actions.ifMatch });
  return (
    <Section title={t('case.moveOn')} aside={<span className="meta">{t('case.now', { status: tk(`status.${c.status}`) })}</span>}>
      <div className="actions">
        {moves.map((mv) => (
          <button key={mv.to} type="button" className={`btn ${mv.danger ? '' : 'btn-primary'}`} disabled={m.busy}
            onClick={async () => {
              if (mv.reason) { setDialog(mv); return; }
              if (await m.run(() => go(mv))) await actions.saved(t('case.saved.status', { status: tk(`status.${mv.to}`) }));
            }}>
            {tk(mv.label)}
          </button>
        ))}
      </div>
      <MutationError error={m.error} onReload={() => void actions.reload()} />
      <ConfirmDialog
        open={dialog !== null}
        onClose={() => setDialog(null)}
        title={dialog ? tk(dialog.label) : ''}
        body={dialog ? t('case.moveConfirm', { from: tk(`status.${c.status}`), to: tk(`status.${dialog.to}`) }) : ''}
        confirmLabel={dialog ? tk(dialog.label) : ''}
        danger={dialog?.danger}
        reason
        reasonLabel={t('case.reasonResidentSees')}
        onConfirm={async (reason) => {
          const mv = dialog!;
          await go(mv, reason);
          await actions.saved(t('case.saved.status', { status: tk(`status.${mv.to}`) }));
        }}
      />
    </Section>
  );
}

export function AssignPanel({ c, actions }: { c: Complaint; actions: CaseActions }) {
  const { t } = useI18n();
  const ref = useRef$();
  const id = useId();
  const reassign = Boolean(c.assigned_officer_id);
  const [officer, setOfficer] = useState('');
  const [dept, setDept] = useState('');
  const [reason, setReason] = useState('');
  const [discard, setDiscard] = useState(false);
  const m = useMutation();
  const dirty = Boolean(officer || dept || reason.trim());
  useUnsavedWarning(dirty);
  const deptFallback = ref.departments.find((d) => d.id === c.department_id)?.is_fallback;
  const targetDept = dept || c.department_id;
  const officers = ref.officers.filter((o) => o.is_active && o.accepts_assignments && o.id !== c.assigned_officer_id
    && (!targetDept || o.department_id === targetDept || (!dept && deptFallback)));
  const reasonMissing = reassign && reason.trim().length < 3;
  const reset = () => { setOfficer(''); setDept(''); setReason(''); m.clear(); };
  const submit = async (e: FormEvent) => {
    e.preventDefault();
    if (!dirty || reasonMissing || m.busy) return;
    const body = { officer_id: officer || undefined, department_id: dept || undefined, ...(reassign ? { reason: reason.trim() } : {}) };
    if (await m.run(() => api(`/complaints/${c.id}/${reassign ? 'reassign' : 'assign'}`, { body, headers: actions.ifMatch }))) {
      reset();
      await actions.saved(t('case.saved.assignment'));
    }
  };
  return (
    <Section title={reassign ? t('case.reassign') : t('case.assign')}>
      <dl className="kv current">
        <dt>{t('case.current')}</dt>
        <dd>{ref.deptName(c.department_id)} · {c.assigned_officer_id ? ref.officerName(c.assigned_officer_id) : t('queue.unassigned')}</dd>
      </dl>
      <form className="stack-sm case-form" onSubmit={submit}>
        <div className="field">
          <label htmlFor={`${id}-dept`}>{t('case.moveToDept')}</label>
          <select id={`${id}-dept`} className="input" value={dept} onChange={(e) => { setDept(e.target.value); setOfficer(''); }}>
            <option value="">{t('case.sameDept')}</option>
            {ref.departments.filter((d) => d.is_active && d.id !== c.department_id).map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
          </select>
        </div>
        <div className="field">
          <label htmlFor={`${id}-off`}>{t('case.officer')}</label>
          <select id={`${id}-off`} className="input" value={officer} onChange={(e) => setOfficer(e.target.value)}>
            <option value="">{t('case.keepInQueue')}</option>
            {officers.map((o) => <option key={o.id} value={o.id}>{o.display_name ?? t('case.officer')} · {ref.deptName(o.department_id)}</option>)}
          </select>
          {officers.length === 0 && <span className="hint">{t('case.noOfficers')}</span>}
        </div>
        {reassign && (
          <div className="field">
            <label htmlFor={`${id}-why`}>{t('case.reassignReason')} <span className="req">({t('common.required')})</span></label>
            <textarea id={`${id}-why`} className="input" rows={2} maxLength={1000} value={reason} onChange={(e) => setReason(e.target.value)}
              aria-invalid={dirty && reasonMissing} aria-describedby={`${id}-why-hint`} />
            <span id={`${id}-why-hint`} className="hint">{t('case.reasonAudited')}</span>
          </div>
        )}
        <MutationError error={m.error} onReload={() => void actions.reload()} />
        <div className="actions">
          <button className="btn btn-primary" disabled={!dirty || reasonMissing || m.busy} aria-busy={m.busy}>
            {m.busy ? t('common.saving') : reassign ? t('case.reassign') : t('case.assign')}
          </button>
          {dirty && <button type="button" className="btn btn-quiet" onClick={() => setDiscard(true)}>{t('common.cancel')}</button>}
        </div>
      </form>
      <DiscardDialog open={discard} onClose={() => setDiscard(false)} onDiscard={reset} />
    </Section>
  );
}

function DiscardDialog({ open, onClose, onDiscard }: { open: boolean; onClose: () => void; onDiscard: () => void }) {
  const { t } = useI18n();
  return (
    <ConfirmDialog open={open} onClose={onClose} title={t('case.discardTitle')} body={t('case.discardBody')}
      confirmLabel={t('case.discard')} danger onConfirm={async () => onDiscard()} />
  );
}

/** Category and priority correction: current value beside the new one, with a reason that is audited. */
export function CorrectionPanel({ c, actions }: { c: Complaint; actions: CaseActions }) {
  const { t, tk } = useI18n();
  const ref = useRef$();
  const id = useId();
  const [cat, setCat] = useState('');
  const [prio, setPrio] = useState<Priority | ''>('');
  const [reason, setReason] = useState('');
  const [touched, setTouched] = useState(false);
  const [discard, setDiscard] = useState(false);
  const m = useMutation();
  const dirty = Boolean(cat || prio || reason.trim());
  useUnsavedWarning(dirty);
  const noChange = !cat && !prio;
  const reasonMissing = reason.trim().length < 3;
  const reset = () => { setCat(''); setPrio(''); setReason(''); setTouched(false); m.clear(); };
  const submit = async (e: FormEvent) => {
    e.preventDefault();
    setTouched(true);
    if (noChange || reasonMissing || m.busy) return;
    const ok = await m.run(() => api(`/complaints/${c.id}`, {
      method: 'PATCH', body: { category_id: cat || undefined, priority: prio || undefined, reason: reason.trim() }, headers: actions.ifMatch,
    }));
    if (ok) { reset(); await actions.saved(t('case.saved.correction')); }
  };
  return (
    <Section title={t('case.correct')}>
      <form className="stack-sm case-form" onSubmit={submit} noValidate>
        <div className="field">
          <label htmlFor={`${id}-cat`}>{t('queue.col.category')}</label>
          <p className="current-value"><span className="meta">{t('case.current')}</span> {ref.catName(c.category_id)}</p>
          <select id={`${id}-cat`} className="input" value={cat} onChange={(e) => setCat(e.target.value)}>
            <option value="">{t('case.keepCategory')}</option>
            <CategoryOptions categories={ref.categories} exclude={c.category_id} />
          </select>
          {cat && ref.catCode(cat)?.startsWith('electrical') && <span className="hint">{t('case.electricalRouting')}</span>}
        </div>
        <div className="field">
          <label htmlFor={`${id}-pr`}>{t('queue.col.priority')}</label>
          <p className="current-value"><span className="meta">{t('case.current')}</span> {tk(`priority.${c.priority}`)}</p>
          <select id={`${id}-pr`} className="input" value={prio} onChange={(e) => setPrio(e.target.value as Priority | '')}>
            <option value="">{t('case.keepPriority')}</option>
            {PRIORITIES.filter((p) => p !== c.priority).slice().reverse().map((p) => <option key={p} value={p}>{tk(`priority.${p}`)}</option>)}
          </select>
        </div>
        <div className="field">
          <label htmlFor={`${id}-why`}>{t('case.correctionReason')} <span className="req">({t('common.required')})</span></label>
          <textarea id={`${id}-why`} className="input" rows={2} maxLength={1000} value={reason} onChange={(e) => setReason(e.target.value)}
            aria-invalid={touched && reasonMissing} aria-describedby={`${id}-why-err`} />
          {touched && noChange && <span id={`${id}-why-err`} className="field-error"><Icon.alert size={16} />{t('case.correctionNothing')}</span>}
          {touched && !noChange && reasonMissing && <span id={`${id}-why-err`} className="field-error"><Icon.alert size={16} />{t('case.reasonTooShort')}</span>}
        </div>
        <MutationError error={m.error} onReload={() => void actions.reload()} />
        <div className="actions">
          <button className="btn btn-primary" disabled={m.busy} aria-busy={m.busy}>{m.busy ? t('common.saving') : t('case.saveCorrection')}</button>
          {dirty && <button type="button" className="btn btn-quiet" onClick={() => setDiscard(true)}>{t('common.cancel')}</button>}
        </div>
      </form>
      <DiscardDialog open={discard} onClose={() => setDiscard(false)} onDiscard={reset} />
    </Section>
  );
}

export function ResolvePanel({ c, actions }: { c: Complaint; actions: CaseActions }) {
  const { t } = useI18n();
  const id = useId();
  const [notes, setNotes] = useState('');
  const [confirm, setConfirm] = useState(false);
  useUnsavedWarning(notes.trim().length > 0);
  if (!canResolve(c.status)) return null;
  return (
    <Section title={t('case.resolve')}>
      <form className="stack-sm case-form" onSubmit={(e) => { e.preventDefault(); if (notes.trim()) setConfirm(true); }}>
        <div className="field">
          <label htmlFor={`${id}-notes`}>{t('case.resolveNotes')}</label>
          <textarea id={`${id}-notes`} className="input" rows={3} maxLength={5000} value={notes} onChange={(e) => setNotes(e.target.value)} />
          <span className="hint">{t('case.resolveHint')}</span>
        </div>
        <div className="actions"><button className="btn btn-primary" disabled={!notes.trim()}>{t('case.resolve')}</button></div>
      </form>
      <ConfirmDialog open={confirm} onClose={() => setConfirm(false)} title={t('case.resolve')} body={t('case.resolveConfirm')}
        confirmLabel={t('case.resolve')}
        onConfirm={async () => {
          await api(`/complaints/${c.id}/resolve`, { body: { resolution_notes: notes.trim() }, headers: actions.ifMatch });
          setNotes('');
          await actions.saved(t('case.saved.resolved'));
        }} />
    </Section>
  );
}

/** Possible duplicates are suggestions with their evidence. Merging is a human decision with a reason. */
export function Duplicates({ c, dups, failed, canMerge, actions, onRetry }: {
  c: Complaint; dups: Duplicate[]; failed: boolean; canMerge: boolean; actions: CaseActions; onRetry: () => void;
}) {
  const { t, fmt } = useI18n();
  const ref = useRef$();
  const [target, setTarget] = useState<Duplicate | null>(null);
  const open = !FINISHED.includes(c.status);
  return (
    <Section title={t('case.duplicates')} aside={<span className="meta">{t('case.duplicatesNote')}</span>}>
      {failed && (
        <p className="field-error" role="alert"><Icon.alert size={16} />{t('case.duplicatesFailed')} <button className="link-btn" onClick={onRetry}>{t('common.retry')}</button></p>
      )}
      {!failed && dups.length === 0 && <p className="meta">{t('case.noDuplicates')}</p>}
      <ul className="dup-list">
        {dups.map((d) => (
          <li key={d.reference} className="dup">
            <div className="dup-head">
              <Pill tone="neutral">{t('case.possibleDuplicate')}</Pill>
              {d.id ? <Link to={`/app/reports/${d.id}`} className="row-link">{d.title ?? d.reference}</Link> : <strong>{d.title ?? d.reference}</strong>}
            </div>
            <p className="meta"><span className="num">{d.reference}</span> · {ref.catName(d.category_id)} · {fmt.date(d.created_at)}</p>
            <ul className="dup-reasons">
              {d.distance_m != null && <li>{t('case.dupDistance', { n: fmt.number(d.distance_m) })}</li>}
              <li>{t('case.dupSimilarity', { pct: fmt.percent(d.text_similarity) })}</li>
            </ul>
            <div className="dup-foot">
              <StatusPill status={d.status} />
              {canMerge && open && d.id && (
                <button type="button" className="btn btn-sm" onClick={() => setTarget(d)}><Icon.merge size={16} />{t('case.merge')}</button>
              )}
            </div>
          </li>
        ))}
      </ul>
      <ConfirmDialog
        open={target !== null}
        onClose={() => setTarget(null)}
        title={t('case.mergeTitle')}
        body={target ? t('case.mergeBody', { from: c.reference, into: target.reference }) : ''}
        confirmLabel={t('case.mergeConfirm')}
        danger
        reason
        reasonLabel={t('case.mergeReason')}
        onConfirm={async (reason) => {
          await api(`/complaints/${c.id}/merge`, { body: { target_id: target!.id, reason }, headers: actions.ifMatch });
          await actions.saved(t('case.saved.merged', { into: target!.reference }));
        }}
      />
    </Section>
  );
}
