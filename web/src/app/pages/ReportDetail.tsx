import '../../styles/staff.css';

import { useCallback, useState } from 'react';
import { Link, useLocation, useParams, useSearchParams } from 'react-router-dom';
import { api, ApiError, type Comment, type Complaint, type Duplicate, type Media, type Note } from '../../api';
import { useAuth } from '../../auth';
import { Icon } from '../../components/Icon';
import { CategoryMark, ErrorState, PriorityPill, Skeleton, StaleNotice, StatusPill } from '../../components/ui';
import { useI18n } from '../../i18n';
import { FINISHED } from '../../lib';
import { useResource } from '../../lib/useResource';
import { capabilities } from '../../roles';
import { ResidentPanel } from '../case/ResidentPanel';
import { AssignPanel, CaseFacts, CorrectionPanel, Duplicates, MovePanel, ResolvePanel } from '../case/StaffPanel';
import { Section, type CaseActions } from '../case/mutation';
import { Conversation, LocationBlock, Notes, Photos, StatusTrail, Timeline } from '../case/parts';
import { useRef$ } from '../refdata';
import { QUEUE_URL_KEY } from './Queue';

interface CaseData {
  c: Complaint;
  comments: Comment[];
  media: Media[];
  notes: Note[] | null;
  dups: Duplicate[] | null;
  dupsFailed: boolean;
}

async function loadCase(id: string, signal: AbortSignal): Promise<CaseData> {
  const c = await api<Complaint>(`/complaints/${id}`, { signal });
  const staff = c.reporter_id !== undefined;
  const [comments, media, notes, dups] = await Promise.all([
    api<Comment[]>(`/complaints/${id}/comments`, { signal }),
    api<Media[]>(`/complaints/${id}/media`, { signal }),
    staff ? api<Note[]>(`/complaints/${id}/notes`, { signal }).catch(() => null) : Promise.resolve(null),
    staff ? api<Duplicate[]>(`/complaints/${id}/possible-duplicates`, { signal }).catch(() => 'failed' as const) : Promise.resolve(null),
  ]);
  return { c, comments, media, notes, dups: dups === 'failed' ? [] : dups, dupsFailed: dups === 'failed' };
}

function backTarget(state: unknown): string {
  const from = (state as { from?: string } | null)?.from;
  if (from?.startsWith('/app/queue')) return from;
  try {
    const saved = sessionStorage.getItem(QUEUE_URL_KEY);
    if (saved?.startsWith('/app/queue')) return saved;
  } catch { /* not essential */ }
  return '/app/queue';
}

/** Screen question: what is this case, where is it, and what is the next thing I can do about it? */
export default function ReportDetail() {
  const { id = '' } = useParams();
  const [params] = useSearchParams();
  const loc = useLocation();
  const { user, experience } = useAuth();
  const caps = capabilities(experience);
  const { t, tk, fmt } = useI18n();
  const ref = useRef$();
  const res = useResource<CaseData>(id ? `case:${id}` : null, (signal) => loadCase(id, signal));
  const [savedMsg, setSavedMsg] = useState<{ id: string; text: string } | null>(null);

  const saved = useCallback(async (text: string) => {
    setSavedMsg({ id, text });
    await res.reload();
  }, [id, res]);

  if (res.loading) {
    return <div aria-busy="true"><Skeleton rows={1} height={36} /><div style={{ height: 16 }} /><Skeleton rows={5} height={56} /></div>;
  }
  if (!res.data) {
    const e = res.error;
    const nf = e instanceof ApiError && (e.status === 404 || e.status === 403);
    return (
      <>
        <ErrorState error={e} onRetry={nf ? undefined : () => void res.reload()} title={nf ? t('case.notFound') : t('case.loadFailed')} />
        <p style={{ marginTop: 16 }}>
          <Link className="btn" to={experience === 'resident' ? '/app' : backTarget(loc.state)}>
            <Icon.chevronLeft size={16} />{experience === 'resident' ? t('case.backToReports') : t('case.backToQueue')}
          </Link>
        </p>
      </>
    );
  }

  const { c, comments, media, notes, dups, dupsFailed } = res.data;
  const staffView = c.reporter_id !== undefined;
  const mine = staffView ? c.reporter_id === user?.id : true;
  const open = !FINISHED.includes(c.status);
  const actions: CaseActions = { ifMatch: { 'If-Match': String(c.version) }, saved, reload: res.reload };
  const back = staffView && !mine ? backTarget(loc.state) : '/app';
  const corrected = staffView && c.reported_category_id && c.reported_category_id !== c.category_id;

  return (
    <article className="case" key={c.id}>
      <nav className="crumb" aria-label={t('case.breadcrumb')}>
        <Link to={back}><Icon.chevronLeft size={16} />{staffView && !mine ? t('case.backToQueue') : t('case.backToReports')}</Link>
        <span aria-hidden="true">/</span>
        <span className="num">{c.reference}</span>
      </nav>

      <header className="case-head">
        <div className="case-head-main">
          <p className="case-ref num">{c.reference}</p>
          <h1>{c.title}</h1>
          <div className="case-tags">
            <StatusPill status={c.status} />
            <CategoryMark code={ref.catCode(c.category_id)} label={ref.catName(c.category_id)} />
            <PriorityPill priority={c.priority} />
          </div>
          <p className="meta">
            {t('case.submittedAt', { when: fmt.dateTime(c.created_at) })}
            {staffView && ` · ${c.assigned_officer_id ? t('case.assignedTo', { officer: ref.officerName(c.assigned_officer_id) }) : t('queue.unassigned')}`}
          </p>
        </div>
        <div className="case-head-side">
          {res.updatedAt && <span className="meta">{t('common.updatedAt', { time: fmt.time(res.updatedAt) })}</span>}
          <button type="button" className="btn btn-quiet" onClick={() => void res.reload()} disabled={res.refreshing} aria-busy={res.refreshing}>
            <Icon.refresh size={18} />{res.refreshing ? t('common.refreshing') : t('common.refresh')}
          </button>
        </div>
      </header>

      {params.get('new') && mine && (
        <div className="notice notice-ok case-new" role="status">
          <Icon.check size={18} />
          <span>{t('case.newSaved', { ref: c.reference })} {t('case.newNotMunicipal')}</span>
        </div>
      )}
      {res.error != null && <StaleNotice error={res.error} onRetry={() => void res.reload()} />}
      {c.merged_into_reference && <p className="notice notice-info"><Icon.merge size={16} />{t('case.mergedInto', { ref: c.merged_into_reference })}</p>}

      <StatusTrail c={c} />

      <div className="case-grid">
        <div className="case-main">
          <Section title={staffView && !mine ? t('case.fromResident') : t('case.whatYouReported')} className="resident-content">
            <p className="case-description" lang={c.original_language}>{c.description}</p>
            {corrected && (
              <p className="meta original-cat">
                {t('case.originalCategory', { original: ref.catName(c.reported_category_id), current: ref.catName(c.category_id) })}
              </p>
            )}
            <h3 className="sub-h">{t('case.location')}</h3>
            <LocationBlock c={c} staff={staffView && !mine} />
            {media.length > 0 && <h3 className="sub-h">{t('case.photos')}</h3>}
            <Photos media={media} />
            {c.resolution_notes && (
              <div className="resolution">
                <h3 className="sub-h">{t('case.resolutionNote')}</h3>
                <p>{c.resolution_notes}</p>
                <p className="meta">{t('case.resolutionCaveat')}</p>
              </div>
            )}
          </Section>

          <Conversation comments={comments} staffView={staffView && !mine} canWrite={open && (mine || caps.work)}
            onReload={() => void res.reload()}
            onSend={async (body, ask) => {
              await api(`/complaints/${c.id}/comments`, { body: { body, request_information: ask } });
              await saved(t('case.saved.message'));
            }} />

          <Section title={t('case.history')} aside={<span className="meta">{t('case.historyNote')}</span>}>
            <Timeline c={c} mine={mine} />
          </Section>

          {staffView && notes && (
            <Notes notes={notes} canWrite={caps.work} onReload={() => void res.reload()}
              onSend={async (body) => {
                await api(`/complaints/${c.id}/notes`, { body: { body } });
                await saved(t('case.saved.note'));
              }} />
          )}
        </div>

        <aside className="case-side" aria-label={t('case.actions')}>
          <div className="saved-region" role="status" aria-live="polite">
            {savedMsg && savedMsg.id === c.id && <p className="notice notice-ok"><Icon.check size={16} />{savedMsg.text}</p>}
          </div>
          {mine && <ResidentPanel c={c} actions={actions} />}
          {staffView && <CaseFacts c={c} />}
          {staffView && caps.readOnly && <p className="notice notice-info"><Icon.info size={16} />{t('case.readOnly')}</p>}
          {staffView && caps.work && open && <MovePanel c={c} actions={actions} />}
          {staffView && caps.work && open && <ResolvePanel c={c} actions={actions} />}
          {staffView && caps.manage && open && <AssignPanel key={`a-${c.id}`} c={c} actions={actions} />}
          {staffView && caps.manage && open && <CorrectionPanel key={`c-${c.id}`} c={c} actions={actions} />}
          {staffView && dups && (
            <Duplicates c={c} dups={dups} failed={dupsFailed} canMerge={caps.manage} actions={actions} onRetry={() => void res.reload()} />
          )}
          {staffView && !open && <p className="meta">{t('case.closedNoActions', { status: tk(`status.${c.status}`) })}</p>}
        </aside>
      </div>
    </article>
  );
}
