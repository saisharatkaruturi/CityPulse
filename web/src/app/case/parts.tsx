import { useEffect, useId, useState, type FormEvent } from 'react';
import { getToken, type Assignment, type Comment, type Complaint, type Media, type Note, type TimelineEvent } from '../../api';
import { useAuth } from '../../auth';
import { Icon } from '../../components/Icon';
import { Pill, useUnsavedWarning } from '../../components/ui';
import { useI18n } from '../../i18n';
import { stages } from '../../lib';
import { useRef$ } from '../refdata';
import { MutationError, Section, useMutation } from './mutation';

/** The honest trail: each stage is marked only when the platform recorded it. */
export function StatusTrail({ c }: { c: Complaint }) {
  const { t, tk } = useI18n();
  const st = stages(c.progress);
  const reached = st.filter((s) => s.done).length;
  return (
    <section className="trail-wrap" aria-labelledby="trail-h">
      <h2 id="trail-h" className="visually-hidden">{t('case.trailTitle')}</h2>
      <ol className="trail">
        {st.map((s, i) => (
          <li key={s.key} className={s.done ? 'done' : i === reached ? 'next' : ''}>
            <span className="trail-dot" aria-hidden="true">{s.done ? <Icon.check size={14} /> : null}</span>
            <span className="trail-label">{tk(s.label)}</span>
            <span className="trail-state">{s.done ? t('stage.done') : t('stage.notYet')}</span>
          </li>
        ))}
      </ol>
      <p className="trail-external">
        <Icon.info size={16} />
        <span>{c.progress.externally_acknowledged
          ? (c.progress.external_is_simulated || c.external_is_simulated ? t('stage.externalSimulated') : t('stage.external'))
          : t('stage.externalNone')}</span>
      </p>
      {c.progress.summary && <p className="meta trail-summary">{c.progress.summary}</p>}
    </section>
  );
}

/**
 * Where the resident said it is. Only what they supplied is shown, never anything read from a photo.
 * Exact coordinates are for staff working the case; residents see that a point is attached.
 */
export function LocationBlock({ c, staff }: { c: Complaint; staff: boolean }) {
  const { t } = useI18n();
  const ref = useRef$();
  const hasPoint = c.latitude != null && c.longitude != null;
  if (!c.ward_id && !c.address_text && !hasPoint) return <p className="meta">{t('case.location.none')}</p>;
  return (
    <dl className="kv">
      {c.ward_id && <><dt>{t('case.location.ward')}</dt><dd>{ref.wardName(c.ward_id)}</dd></>}
      {c.address_text && <><dt>{t('case.location.address')}</dt><dd>{c.address_text}</dd></>}
      {hasPoint && (
        <>
          <dt>{t('case.location.point')}</dt>
          <dd>
            {staff ? (
              <><span className="num">{c.latitude!.toFixed(5)}, {c.longitude!.toFixed(5)}</span> <span className="meta">{t('case.location.staffOnly')}</span></>
            ) : t('case.location.pointResident')}
          </dd>
        </>
      )}
    </dl>
  );
}

function MediaThumb({ m }: { m: Media }) {
  const { t } = useI18n();
  const [url, setUrl] = useState<string | null>(null);
  const [failed, setFailed] = useState(false);
  useEffect(() => {
    let u: string | null = null;
    const ctrl = new AbortController();
    const token = getToken();
    fetch(`/api/media/${m.id}/content`, { headers: token ? { Authorization: `Bearer ${token}` } : {}, signal: ctrl.signal })
      .then((r) => (r.ok ? r.blob() : Promise.reject(new Error(String(r.status)))))
      .then((b) => { u = URL.createObjectURL(b); setUrl(u); })
      .catch(() => { if (!ctrl.signal.aborted) setFailed(true); });
    return () => { ctrl.abort(); if (u) URL.revokeObjectURL(u); };
  }, [m.id]);
  const alt = m.kind === 'resolution_evidence' ? t('case.photo.evidence') : t('case.photo.report');
  if (failed) return <span className="case-photo photo-missing"><Icon.image /><span className="meta">{t('case.photo.failed')}</span></span>;
  return url
    ? <a className="case-photo" href={url} target="_blank" rel="noreferrer"><img src={url} alt={alt} width={160} height={120} /></a>
    : <span className="case-photo skeleton" aria-label={t('common.loading')} />;
}

export function Photos({ media }: { media: Media[] }) {
  const { t } = useI18n();
  if (!media.length) return null;
  return (
    <div className="photos-block">
      <div className="photos">{media.map((m) => <MediaThumb key={m.id} m={m} />)}</div>
      <p className="meta">{t('case.photo.privacy')}</p>
    </div>
  );
}

type Event = { at: string; kind: 'status'; e: TimelineEvent } | { at: string; kind: 'assign'; a: Assignment };

/** History straight from the server: status changes, plus assignments for staff. Nothing is inferred. */
export function Timeline({ c, mine }: { c: Complaint; mine: boolean }) {
  const { t, tk, fmt } = useI18n();
  const ref = useRef$();
  const events: Event[] = [
    ...c.timeline.map((e) => ({ at: e.created_at, kind: 'status' as const, e })),
    ...(c.assignments ?? []).map((a) => ({ at: a.created_at, kind: 'assign' as const, a })),
  ].sort((x, y) => Date.parse(x.at) - Date.parse(y.at));
  const who = (actorKind: string, isStaff: boolean | null) =>
    actorKind === 'system' ? t('case.by.system') : isStaff ? t('case.by.staff') : mine ? t('case.by.you') : t('case.by.resident');
  return (
    <ol className="timeline">
      {events.map((ev, i) => (
        <li key={`${ev.kind}-${ev.at}-${i}`}>
          <time dateTime={ev.at} className="meta num">{fmt.dateTime(ev.at)}</time>
          {ev.kind === 'status' ? (
            <span>
              <strong>{tk(`status.${ev.e.to_status}`)}</strong> <span className="meta">· {who(ev.e.actor_kind, ev.e.actor_is_staff)}</span>
              {ev.e.reason && <span className="timeline-reason">{ev.e.reason}</span>}
            </span>
          ) : (
            <span>
              <strong>{tk(`case.assignKind.${ev.a.kind}`)}</strong>
              <span className="meta"> · {ev.a.actor_kind === 'system' ? t('case.by.system') : t('case.by.staff')}</span>
              <span className="timeline-reason">
                {ev.a.to_department_id && ev.a.to_department_id !== ev.a.from_department_id && t('case.assign.toDept', { dept: ref.deptName(ev.a.to_department_id) })}
                {ev.a.to_officer_id && ` ${t('case.assign.toOfficer', { officer: ref.officerName(ev.a.to_officer_id) })}`}
                {ev.a.reason && ` — ${ev.a.reason}`}
              </span>
            </span>
          )}
        </li>
      ))}
    </ol>
  );
}

export function Conversation({ comments, canWrite, staffView, onSend, onReload }: {
  comments: Comment[]; canWrite: boolean; staffView: boolean;
  onSend: (body: string, ask: boolean) => Promise<void>; onReload: () => void;
}) {
  const { t, fmt, plural } = useI18n();
  const { user } = useAuth();
  const id = useId();
  const [body, setBody] = useState('');
  const [ask, setAsk] = useState(false);
  const m = useMutation();
  useUnsavedWarning(body.trim().length > 0);
  const submit = async (e: FormEvent) => {
    e.preventDefault();
    if (!body.trim() || m.busy) return;
    if (await m.run(() => onSend(body.trim(), ask))) { setBody(''); setAsk(false); }
  };
  return (
    <Section title={t('case.conversation')} aside={<span className="meta">{plural('case.messages', comments.length)}</span>}>
      {comments.length === 0 && <p className="meta">{t('case.noMessages')}</p>}
      <ul className="messages">
        {comments.map((c) => (
          <li key={c.id} className={`message ${c.author_is_staff ? 'from-staff' : ''}`}>
            <span className="meta">
              <strong>{c.author_is_staff ? t('case.by.staffName') : c.author_id === user?.id ? t('case.by.youName') : t('case.by.residentName')}</strong>
              {' · '}{fmt.dateTime(c.created_at)}
            </span>
            {c.is_information_request && <Pill tone="warn">{t('case.infoRequest')}</Pill>}
            <p>{c.body}</p>
          </li>
        ))}
      </ul>
      {canWrite && (
        <form className="stack-sm case-form" onSubmit={submit}>
          <div className="field">
            <label htmlFor={`${id}-msg`}>{staffView ? t('case.messageToResident') : t('case.messageToStaff')}</label>
            <textarea id={`${id}-msg`} className="input" rows={3} maxLength={2000} value={body} onChange={(e) => setBody(e.target.value)} />
          </div>
          {staffView && (
            <label className="check"><input type="checkbox" checked={ask} onChange={(e) => setAsk(e.target.checked)} />
              <span>{t('case.askInfo')}</span></label>
          )}
          <MutationError error={m.error} onReload={onReload} />
          <div className="actions"><button className="btn" disabled={m.busy || !body.trim()} aria-busy={m.busy}>{m.busy ? t('common.saving') : t('case.send')}</button></div>
        </form>
      )}
    </Section>
  );
}

export function Notes({ notes, canWrite, onSend, onReload }: {
  notes: Note[]; canWrite: boolean; onSend: (body: string) => Promise<void>; onReload: () => void;
}) {
  const { t, fmt } = useI18n();
  const id = useId();
  const [body, setBody] = useState('');
  const m = useMutation();
  useUnsavedWarning(body.trim().length > 0);
  return (
    <Section title={t('case.notes')} aside={<span className="meta">{t('case.notesPrivate')}</span>} className="notes-section">
      {notes.length === 0 && <p className="meta">{t('case.noNotes')}</p>}
      <ul className="messages">
        {notes.map((n) => (
          <li key={n.id} className="message"><span className="meta num">{fmt.dateTime(n.created_at)}</span><p>{n.body}</p></li>
        ))}
      </ul>
      {canWrite && (
        <form className="stack-sm case-form" onSubmit={async (e) => {
          e.preventDefault();
          if (body.trim() && !m.busy && await m.run(() => onSend(body.trim()))) setBody('');
        }}>
          <div className="field">
            <label htmlFor={`${id}-note`}>{t('case.addNote')}</label>
            <textarea id={`${id}-note`} className="input" rows={2} maxLength={2000} value={body} onChange={(e) => setBody(e.target.value)} />
          </div>
          <MutationError error={m.error} onReload={onReload} />
          <div className="actions"><button className="btn" disabled={m.busy || !body.trim()}>{m.busy ? t('common.saving') : t('case.saveNote')}</button></div>
        </form>
      )}
    </Section>
  );
}
