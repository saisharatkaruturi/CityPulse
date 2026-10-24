import '../../styles/staff.css';

import { useEffect, useId, useMemo, useState, type FormEvent } from 'react';
import { Link, useLocation, useSearchParams } from 'react-router-dom';
import { api, ApiError, PRIORITIES, qs, type ComplaintItem, type Page, type Status } from '../../api';
import { useAuth } from '../../auth';
import { Icon } from '../../components/Icon';
import {
  CategoryMark, EmptyState, ErrorState, PageHeader, PriorityPill, RefreshControl, Skeleton, StaleNotice, StatusPill,
} from '../../components/ui';
import { useI18n } from '../../i18n';
import { FINISHED, dueState } from '../../lib';
import { useResource } from '../../lib/useResource';
import { capabilities } from '../../roles';
import { useRef$ } from '../refdata';
import { CategoryOptions } from '../staff/CategoryOptions';
import {
  PAGE_SIZE, VIEWS, activeFilterCount, apiParams, applyPatch, ariaSort, impossibleStatus, lastPage, nextSort,
  parseQueue, toSearch, viewsFor, type QueueState, type SortColumn, type ViewKey,
} from '../staff/queueParams';

export const QUEUE_URL_KEY = 'ycys.queueUrl';

/** Screen question: which reports in my scope need me next? */
export default function Queue() {
  const { experience, user } = useAuth();
  const caps = capabilities(experience);
  const { t, fmt } = useI18n();
  const loc = useLocation();
  const [params, setParams] = useSearchParams();
  const state = useMemo(() => parseQueue(params, experience), [params, experience]);
  const views = viewsFor(experience);
  const blocked = impossibleStatus(state);
  const query = qs(apiParams(state));

  const rows = useResource<Page<ComplaintItem>>(blocked ? null : `list${query}`,
    (signal) => api<Page<ComplaintItem>>(`/complaints${query}`, { signal }));
  const counts = useResource<Partial<Record<ViewKey, number>>>(`counts:${experience}`, async (signal) => {
    const entries = await Promise.all(views.map(async (v) => {
      const p = await api<Page<ComplaintItem>>(`/complaints${qs({ ...VIEWS[v].params, page_size: 1 })}`, { signal });
      return [v, p.total] as const;
    }));
    return Object.fromEntries(entries);
  });

  // Remember where the queue was, so a case can send the user back to exactly this list.
  useEffect(() => {
    try { sessionStorage.setItem(QUEUE_URL_KEY, loc.pathname + loc.search); } catch { /* not essential */ }
  }, [loc.pathname, loc.search]);

  const update = (patch: Partial<QueueState>) => setParams(toSearch(applyPatch(state, patch), experience));

  // A refresh can shrink the list under the current page; move to the last real page rather than show nothing.
  const total = rows.data?.total;
  useEffect(() => {
    if (total !== undefined && state.page > lastPage(total)) update({ page: lastPage(total) });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [total, state.page]);

  const refresh = () => { void rows.reload(); void counts.reload(); };
  const deptGrant = user?.roles.find((r) => r.department_name);
  const scope = experience === 'admin' || experience === 'auditor' ? t('queue.scope.city')
    : experience === 'officer' ? t('queue.scope.officer')
      : t('queue.scope.dept', { dept: deptGrant?.department_name ?? t('common.dash') });

  const c = counts.data ?? {};
  const overdue = c.overdue ?? 0;
  const waitingRouting = c.triage ?? c.review ?? 0;
  const finding = !counts.data ? null
    : experience === 'officer' ? t('queue.finding.officer', { mine: c.mine ?? 0, overdue })
      : overdue > 0 ? t('queue.finding.overdue', { overdue, waiting: waitingRouting })
        : waitingRouting > 0 ? t('queue.finding.waiting', { waiting: waitingRouting })
          : t('queue.finding.clear');

  return (
    <>
      <PageHeader
        title={t('queue.title')}
        sub={<>{scope}{finding ? ` ${finding}` : ''}</>}
        actions={<RefreshControl onRefresh={refresh} refreshing={rows.refreshing || counts.refreshing} updatedAt={rows.updatedAt}
          label={t('queue.refreshLabel')} />}
      />
      {caps.readOnly && <p className="notice notice-info" style={{ marginBottom: 16 }}><Icon.info size={16} />{t('queue.readOnly')}</p>}

      <div className="queue-views" role="group" aria-label={t('queue.viewsLabel')}>
        {views.map((v) => (
          <button key={v} type="button" className="queue-view" aria-pressed={state.view === v} onClick={() => update({ view: v, status: [] })}>
            <span className="queue-view-label">{t(VIEWS[v].label)}</span>
            <span className="queue-view-count num">{counts.data ? fmt.number(c[v] ?? 0) : t('common.dash')}</span>
          </button>
        ))}
      </div>
      {counts.error != null && !counts.data && <p className="meta" style={{ marginTop: 8 }}>{t('queue.countsFailed')}</p>}

      <Filters state={state} onChange={update} />

      {rows.error != null && rows.data && <StaleNotice error={rows.error} onRetry={() => void rows.reload()} />}
      {blocked && <EmptyState title={t('queue.empty.impossible')} action={<button className="btn" onClick={() => update({ status: [] })}>{t('queue.clearStatus')}</button>} />}
      {!blocked && rows.loading && <Skeleton rows={6} height={44} />}
      {!blocked && rows.error != null && !rows.data && (
        <ErrorState error={rows.error} onRetry={() => void rows.reload()}
          title={rows.error instanceof ApiError && rows.error.status === 401 ? t('guard.sessionTitle') : t('queue.loadFailed')} />
      )}
      {rows.data && rows.data.total === 0 && (
        <EmptyState title={activeFilterCount(state) ? t('queue.empty.filtered') : t(VIEWS[state.view].empty)}
          action={activeFilterCount(state) ? <button className="btn" onClick={() => update(CLEARED)}>{t('queue.clearFilters')}</button> : undefined} />
      )}
      {rows.data && rows.data.total > 0 && (
        <QueueRows page={rows.data} state={state} onSort={(col) => update({ sort: nextSort(state.sort, col) })}
          showAssignee={caps.manage || experience === 'auditor'} from={loc.pathname + loc.search} />
      )}
      {rows.data && rows.data.total > PAGE_SIZE && (
        <nav className="pager" aria-label={t('queue.pagination')}>
          <span className="meta num">{t('common.pageOf', {
            from: (state.page - 1) * PAGE_SIZE + 1, to: Math.min(state.page * PAGE_SIZE, rows.data.total), total: rows.data.total,
          })}</span>
          <span className="actions">
            <button className="btn btn-sm" disabled={state.page <= 1} onClick={() => update({ page: state.page - 1 })}>
              <Icon.chevronLeft size={16} />{t('common.previous')}
            </button>
            <button className="btn btn-sm" disabled={state.page >= lastPage(rows.data.total)} onClick={() => update({ page: state.page + 1 })}>
              {t('common.next')}<Icon.chevronRight size={16} />
            </button>
          </span>
        </nav>
      )}
    </>
  );
}

const CLEARED: Partial<QueueState> = { status: [], priority: '', category: '', assign: '', from: '', to: '', q: '' };

function Filters({ state, onChange }: { state: QueueState; onChange: (p: Partial<QueueState>) => void }) {
  const { t, tk } = useI18n();
  const { experience } = useAuth();
  const ref = useRef$();
  const id = useId();
  const [q, setQ] = useState(state.q);
  const [open, setOpen] = useState(false);
  useEffect(() => setQ(state.q), [state.q]);
  const n = activeFilterCount(state);
  const viewStatuses = (VIEWS[state.view].params.status as Status[] | undefined) ?? STATUS_CHOICES;
  const submit = (e: FormEvent) => { e.preventDefault(); onChange({ q: q.trim() }); };
  const toggleStatus = (s: Status) => onChange({ status: state.status.includes(s) ? state.status.filter((x) => x !== s) : [...state.status, s] });

  return (
    <section className="queue-filters" aria-label={t('queue.filters')}>
      <form className="queue-search" role="search" onSubmit={submit}>
        <label htmlFor={`${id}-q`} className="visually-hidden">{t('queue.searchLabel')}</label>
        <Icon.search />
        <input id={`${id}-q`} className="input" value={q} maxLength={100} onChange={(e) => setQ(e.target.value)}
          placeholder={t('queue.searchPlaceholder')} />
        <button className="btn" type="submit">{t('common.search')}</button>
      </form>
      <button type="button" className="btn btn-quiet filter-toggle" aria-expanded={open} aria-controls={`${id}-panel`} onClick={() => setOpen((o) => !o)}>
        <Icon.filter /> {n ? t('queue.filtersOn', { n }) : t('queue.filters')}
      </button>
      {n > 0 && <button type="button" className="link-btn" onClick={() => onChange(CLEARED)}>{t('queue.clearFilters')}</button>}
      <div id={`${id}-panel`} className={`filter-panel ${open ? 'open' : ''}`}>
        <fieldset className="field filter-status">
          <legend className="label">{t('queue.filter.status')}</legend>
          <div className="check-row">
            {viewStatuses.map((s) => (
              <label key={s} className="check chip-check">
                <input type="checkbox" checked={state.status.includes(s)} onChange={() => toggleStatus(s)} />
                <span>{tk(`status.${s}`)}</span>
              </label>
            ))}
          </div>
        </fieldset>
        <div className="field">
          <label htmlFor={`${id}-pr`}>{t('queue.filter.priority')}</label>
          <select id={`${id}-pr`} className="input" value={state.priority} onChange={(e) => onChange({ priority: e.target.value as QueueState['priority'] })}>
            <option value="">{t('queue.filter.any')}</option>
            {PRIORITIES.slice().reverse().map((p) => <option key={p} value={p}>{tk(`priority.${p}`)}</option>)}
          </select>
        </div>
        <div className="field">
          <label htmlFor={`${id}-cat`}>{t('queue.filter.category')}</label>
          <select id={`${id}-cat`} className="input" value={state.category} onChange={(e) => onChange({ category: e.target.value })}>
            <option value="">{t('queue.filter.anyCategory')}</option>
            <CategoryOptions categories={ref.categories} families />
          </select>
        </div>
        <div className="field">
          <label htmlFor={`${id}-as`}>{t('queue.filter.assignment')}</label>
          <select id={`${id}-as`} className="input" value={state.assign} onChange={(e) => onChange({ assign: e.target.value as QueueState['assign'] })}>
            <option value="">{t('queue.filter.any')}</option>
            <option value="unassigned">{t('queue.filter.unassigned')}</option>
            {experience === 'officer' && <option value="mine">{t('queue.filter.mine')}</option>}
          </select>
        </div>
        <div className="field">
          <label htmlFor={`${id}-from`}>{t('queue.filter.from')}</label>
          <input id={`${id}-from`} type="date" className="input" value={state.from} max={state.to || undefined} onChange={(e) => onChange({ from: e.target.value })} />
        </div>
        <div className="field">
          <label htmlFor={`${id}-to`}>{t('queue.filter.to')}</label>
          <input id={`${id}-to`} type="date" className="input" value={state.to} min={state.from || undefined} onChange={(e) => onChange({ to: e.target.value })} />
        </div>
      </div>
    </section>
  );
}

const STATUS_CHOICES: Status[] = ['submitted', 'under_review', 'assigned', 'in_progress', 'awaiting_resident', 'on_hold', 'reopened', 'resolved', 'closed', 'rejected', 'withdrawn'];

function SortHeader({ col, state, onSort, children, className }: {
  col: SortColumn; state: QueueState; onSort: (c: SortColumn) => void; children: string; className?: string;
}) {
  const s = ariaSort(state.sort, col);
  const I = s === 'ascending' ? Icon.sortAsc : s === 'descending' ? Icon.sortDesc : Icon.sort;
  return (
    <th aria-sort={s} className={className} scope="col">
      <button type="button" className="sort-btn" onClick={() => onSort(col)}>{children}<I size={14} /></button>
    </th>
  );
}

function QueueRows({ page, state, onSort, showAssignee, from }: {
  page: Page<ComplaintItem>; state: QueueState; onSort: (c: SortColumn) => void; showAssignee: boolean; from: string;
}) {
  const { t, tk, fmt } = useI18n();
  const ref = useRef$();
  const target = (c: ComplaintItem) => {
    if (FINISHED.includes(c.status)) return { text: t('common.dash'), overdue: false };
    const d = dueState(c.due_at);
    return { text: tk(d.key, d.vars), overdue: c.is_overdue || d.overdue };
  };
  return (
    <>
      <div className="table-wrap queue-table">
        <table className="data">
          <caption className="visually-hidden">{t('queue.tableCaption', { view: t(VIEWS[state.view].label) })}</caption>
          <thead>
            <tr>
              <th scope="col">{t('queue.col.report')}</th>
              <th scope="col">{t('queue.col.category')}</th>
              <SortHeader col="priority" state={state} onSort={onSort}>{t('queue.col.priority')}</SortHeader>
              <th scope="col">{t('queue.col.status')}</th>
              <th scope="col">{t('queue.col.ward')}</th>
              {showAssignee && <th scope="col">{t('queue.col.assignee')}</th>}
              <SortHeader col="created_at" state={state} onSort={onSort}>{t('queue.col.age')}</SortHeader>
              <SortHeader col="due_at" state={state} onSort={onSort}>{t('queue.col.target')}</SortHeader>
            </tr>
          </thead>
          <tbody>
            {page.items.map((c) => {
              const tg = target(c);
              return (
                <tr key={c.id} className="queue-row">
                  <td className="queue-title-cell">
                    <Link className="row-link" to={`/app/reports/${c.id}`} state={{ from }}>{c.title}</Link>
                    <span className="ref num">{c.reference}</span>
                  </td>
                  <td><CategoryMark code={ref.catCode(c.category_id)} label={ref.catName(c.category_id)} /></td>
                  <td><PriorityPill priority={c.priority} /></td>
                  <td><StatusPill status={c.status} /></td>
                  <td>{ref.wardName(c.ward_id)}</td>
                  {showAssignee && <td>{c.assigned_officer_id ? ref.officerName(c.assigned_officer_id) : <span className="meta">{t('queue.unassigned')}</span>}</td>}
                  <td className="num" title={fmt.dateTime(c.created_at)}>{fmt.relative(c.created_at)}</td>
                  <td className={`num ${tg.overdue ? 'is-overdue' : ''}`}>{tg.overdue && <Icon.alert size={14} />}{tg.text}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
      <ul className="queue-cards" aria-label={t('queue.tableCaption', { view: t(VIEWS[state.view].label) })}>
        {page.items.map((c) => {
          const tg = target(c);
          return (
            <li key={c.id}>
              <Link className="queue-card" to={`/app/reports/${c.id}`} state={{ from }}>
                <span className="queue-card-top"><span className="ref num">{c.reference}</span><StatusPill status={c.status} /></span>
                <span className="queue-card-title">{c.title}</span>
                <span className="queue-card-meta">
                  <CategoryMark code={ref.catCode(c.category_id)} label={ref.catName(c.category_id)} />
                  <PriorityPill priority={c.priority} />
                </span>
                <span className="queue-card-foot meta">
                  <span>{ref.wardName(c.ward_id)} · {fmt.relative(c.created_at)}</span>
                  <span className={tg.overdue ? 'is-overdue' : ''}>{tg.text}</span>
                </span>
              </Link>
            </li>
          );
        })}
      </ul>
    </>
  );
}
