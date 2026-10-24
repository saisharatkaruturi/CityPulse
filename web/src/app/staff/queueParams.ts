// Queue state lives in the URL, so refresh, back/forward and "Back to queue" from a case all restore it.
// Pure functions only; the Queue screen and its tests share them.

import { PRIORITIES, STATUSES, type Priority, type Status } from '../../api';
import type { MessageKey } from '../../i18n';
import type { Experience } from '../../roles';

export type ViewKey = 'mine' | 'triage' | 'review' | 'overdue' | 'waiting' | 'all';
export type SortKey = '-created_at' | 'created_at' | '-priority' | 'priority' | 'due_at' | '-due_at';
export type AssignFilter = '' | 'unassigned' | 'mine';
export const SORTS: SortKey[] = ['-created_at', 'created_at', '-priority', 'priority', 'due_at', '-due_at'];
export const PAGE_SIZE = 25;

type ApiParams = Record<string, string | string[] | boolean | number>;

const NEEDS_ROUTING: Status[] = ['submitted', 'under_review', 'reopened'];
const WORKING: Status[] = ['submitted', 'under_review', 'assigned', 'in_progress', 'reopened'];

export const VIEWS: Record<ViewKey, { label: MessageKey; empty: MessageKey; params: ApiParams }> = {
  mine: { label: 'queue.view.mine', empty: 'queue.empty.mine', params: { assigned_to_me: true, status: ['assigned', 'in_progress', 'reopened', 'awaiting_resident', 'on_hold'] } },
  triage: { label: 'queue.view.triage', empty: 'queue.empty.triage', params: { unassigned: true, status: NEEDS_ROUTING } },
  review: { label: 'queue.view.review', empty: 'queue.empty.review', params: { unassigned: true, status: NEEDS_ROUTING } },
  overdue: { label: 'queue.view.overdue', empty: 'queue.empty.overdue', params: { overdue: true, status: WORKING } },
  waiting: { label: 'queue.view.waiting', empty: 'queue.empty.waiting', params: { status: ['awaiting_resident', 'on_hold'] } },
  all: { label: 'queue.view.all', empty: 'queue.empty.all', params: {} },
};

const VIEWS_BY_ROLE: Record<Exclude<Experience, 'resident'>, ViewKey[]> = {
  officer: ['mine', 'overdue', 'waiting', 'all'],
  supervisor: ['triage', 'overdue', 'waiting', 'all'],
  triage: ['review', 'overdue', 'waiting', 'all'],
  admin: ['triage', 'overdue', 'waiting', 'all'],
  auditor: ['all', 'overdue', 'waiting'],
};

export const viewsFor = (e: Experience): ViewKey[] => (e === 'resident' ? [] : VIEWS_BY_ROLE[e]);
export const defaultView = (e: Experience): ViewKey => viewsFor(e)[0] ?? 'all';

export interface QueueState {
  view: ViewKey;
  status: Status[];
  priority: Priority | '';
  category: string;
  assign: AssignFilter;
  from: string; // yyyy-mm-dd, local
  to: string;
  q: string;
  sort: SortKey;
  page: number;
}

const DATE = /^\d{4}-\d{2}-\d{2}$/;

export function parseQueue(p: URLSearchParams, e: Experience): QueueState {
  const views = viewsFor(e);
  const view = p.get('view') as ViewKey | null;
  const priority = p.get('priority') ?? '';
  const assign = p.get('assign') ?? '';
  const sort = p.get('sort') as SortKey | null;
  const page = Number.parseInt(p.get('page') ?? '1', 10);
  return {
    view: view && views.includes(view) ? view : defaultView(e),
    status: p.getAll('status').filter((s): s is Status => (STATUSES as readonly string[]).includes(s)),
    priority: (PRIORITIES as readonly string[]).includes(priority) ? (priority as Priority) : '',
    category: /^[0-9a-f-]{36}$/i.test(p.get('category') ?? '') ? p.get('category')! : '',
    // "assigned to me" only means something for a field officer
    assign: assign === 'unassigned' || (assign === 'mine' && e === 'officer') ? assign : '',
    from: DATE.test(p.get('from') ?? '') ? p.get('from')! : '',
    to: DATE.test(p.get('to') ?? '') ? p.get('to')! : '',
    q: (p.get('q') ?? '').slice(0, 100),
    sort: sort && SORTS.includes(sort) ? sort : defaultSort(view && views.includes(view) ? view : defaultView(e)),
    page: Number.isFinite(page) && page > 0 ? page : 1,
  };
}

export const defaultSort = (v: ViewKey): SortKey => (v === 'all' ? '-created_at' : v === 'overdue' ? 'due_at' : '-priority');

/** Only non-default values go in the URL, so shared links stay short. */
export function toSearch(s: QueueState, e: Experience): URLSearchParams {
  const p = new URLSearchParams();
  if (s.view !== defaultView(e)) p.set('view', s.view);
  s.status.forEach((x) => p.append('status', x));
  if (s.priority) p.set('priority', s.priority);
  if (s.category) p.set('category', s.category);
  if (s.assign) p.set('assign', s.assign);
  if (s.from) p.set('from', s.from);
  if (s.to) p.set('to', s.to);
  if (s.q) p.set('q', s.q);
  if (s.sort !== defaultSort(s.view)) p.set('sort', s.sort);
  if (s.page > 1) p.set('page', String(s.page));
  return p;
}

const FILTER_FIELDS: (keyof QueueState)[] = ['view', 'status', 'priority', 'category', 'assign', 'from', 'to', 'q'];

/**
 * Apply a change. A change to what is being listed can make the current page meaningless, so it returns to
 * page 1; a change of sort keeps the page, and an ordinary refresh changes nothing at all.
 */
export function applyPatch(s: QueueState, patch: Partial<QueueState>): QueueState {
  const next = { ...s, ...patch };
  const filterChanged = FILTER_FIELDS.some((k) => k in patch && JSON.stringify(patch[k]) !== JSON.stringify(s[k]));
  if (filterChanged && !('page' in patch)) next.page = 1;
  if ('view' in patch && patch.view !== s.view && !('sort' in patch)) next.sort = defaultSort(next.view);
  return next;
}

/** The last valid page for a total; used when a refresh shrinks the list under the current page. */
export const lastPage = (total: number, size = PAGE_SIZE) => Math.max(1, Math.ceil(total / size));

/** Local calendar day to an ISO instant with timezone; `end` gives the start of the next day (exclusive). */
export function dayToIso(day: string, end = false): string {
  const [y, m, d] = day.split('-').map(Number);
  return new Date(y, m - 1, d + (end ? 1 : 0)).toISOString();
}

/** The API query for the list. An explicit status filter narrows the view's own statuses. */
export function apiParams(s: QueueState, extra: ApiParams = {}): ApiParams {
  const base = { ...VIEWS[s.view].params };
  const out: ApiParams = { ...base };
  if (s.status.length) {
    const viewStatus = base.status as Status[] | undefined;
    out.status = viewStatus ? s.status.filter((x) => viewStatus.includes(x)) : s.status;
    if (viewStatus && (out.status as Status[]).length === 0) out.status = ['__none__'];
  }
  if (s.priority) out.priority = s.priority;
  if (s.category) out.category_id = s.category;
  if (s.assign === 'unassigned') out.unassigned = true;
  if (s.assign === 'mine') out.assigned_to_me = true;
  if (s.from) out.created_from = dayToIso(s.from);
  if (s.to) out.created_to = dayToIso(s.to, true);
  if (s.q) out.q = s.q;
  out.sort = s.sort;
  out.page = s.page;
  out.page_size = PAGE_SIZE;
  return { ...out, ...extra };
}

/** True when the view's statuses and the chosen statuses have nothing in common (nothing can match). */
export const impossibleStatus = (s: QueueState) => (apiParams(s).status as string[] | undefined)?.[0] === '__none__';

export const activeFilterCount = (s: QueueState) =>
  [s.status.length > 0, s.priority, s.category, s.assign, s.from, s.to, s.q].filter(Boolean).length;

// ---- sortable headers ---------------------------------------------------------------------------

export type SortColumn = 'created_at' | 'priority' | 'due_at';

export function ariaSort(sort: SortKey, col: SortColumn): 'ascending' | 'descending' | 'none' {
  if (sort.replace('-', '') !== col) return 'none';
  // "-priority" lists critical first: the highest rank descending
  return sort.startsWith('-') ? 'descending' : 'ascending';
}

/** First click picks the useful direction (newest, most urgent, soonest due); the next click flips it. */
export function nextSort(sort: SortKey, col: SortColumn): SortKey {
  const first: Record<SortColumn, SortKey> = { created_at: '-created_at', priority: '-priority', due_at: 'due_at' };
  if (sort.replace('-', '') !== col) return first[col];
  return (sort.startsWith('-') ? sort.slice(1) : `-${sort}`) as SortKey;
}
