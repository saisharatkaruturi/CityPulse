// Thin typed client for the FastAPI backend. Every call goes to /api on the same origin
// (Vite proxies it in development; FastAPI serves this app in production).

const TOKEN_KEY = 'ycys.token';
let apiLocale = 'en';

/** Called by the locale provider so category labels and match explanations come back in the UI language. */
export function setApiLocale(locale: string): void {
  apiLocale = locale;
}

export function getToken(): string | null {
  try {
    return sessionStorage.getItem(TOKEN_KEY);
  } catch {
    return null;
  }
}

export function setToken(token: string | null): void {
  try {
    if (token) sessionStorage.setItem(TOKEN_KEY, token);
    else sessionStorage.removeItem(TOKEN_KEY);
  } catch {
    /* storage unavailable: the session lasts for this page only */
  }
}

export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
    public details: { field?: string; issue?: string; message?: string }[] = [],
  ) {
    super(message);
  }
}

export const isAbort = (e: unknown) => e instanceof DOMException && e.name === 'AbortError';

type Opts = {
  method?: string; body?: unknown; headers?: Record<string, string>; form?: FormData; signal?: AbortSignal;
};

async function send(path: string, opts: Opts): Promise<Response> {
  const headers: Record<string, string> = { Accept: 'application/json', 'Accept-Language': apiLocale, ...opts.headers };
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  let body: BodyInit | undefined;
  if (opts.form) body = opts.form;
  else if (opts.body !== undefined) {
    headers['Content-Type'] = 'application/json';
    body = JSON.stringify(opts.body);
  }
  try {
    return await fetch(`/api${path}`, { method: opts.method ?? (body ? 'POST' : 'GET'), headers, body, signal: opts.signal });
  } catch (e) {
    if (isAbort(e)) throw e;
    throw new ApiError(0, 'network', 'Could not reach the service. Check your connection and try again.');
  }
}

async function fail(res: Response, hadToken: boolean): Promise<never> {
  const data = await res.json().catch(() => null);
  const e = data?.error;
  if (res.status === 401 && hadToken) {
    setToken(null);
    window.dispatchEvent(new Event('ycys:signed-out'));
  }
  throw new ApiError(res.status, e?.code ?? 'error', e?.message ?? `Request failed (${res.status})`, e?.details ?? []);
}

export async function api<T>(path: string, opts: Opts = {}): Promise<T> {
  const hadToken = Boolean(getToken());
  const res = await send(path, opts);
  if (!res.ok) return fail(res, hadToken);
  if (res.status === 204) return undefined as T;
  return (await res.json()) as T;
}

/** For downloads: returns the raw response (blob and headers) after the same auth and error handling. */
export async function apiRaw(path: string, opts: Opts = {}): Promise<Response> {
  const hadToken = Boolean(getToken());
  const res = await send(path, { ...opts, headers: { Accept: '*/*', ...opts.headers } });
  if (!res.ok) return fail(res, hadToken);
  return res;
}

export const qs = (params: Record<string, string | number | boolean | string[] | undefined | null>) => {
  const p = new URLSearchParams();
  for (const [k, v] of Object.entries(params)) {
    if (v === undefined || v === null || v === '' || v === false) continue;
    if (Array.isArray(v)) v.forEach((x) => p.append(k, x));
    else p.set(k, String(v));
  }
  const s = p.toString();
  return s ? `?${s}` : '';
};

// ---- types (mirror app/schemas) ---------------------------------------------------------------

export type Role = 'resident' | 'field_officer' | 'supervisor' | 'municipal_admin' | 'system_admin' | 'auditor';
export const STATUSES = [
  'submitted', 'under_review', 'assigned', 'in_progress', 'awaiting_resident', 'on_hold',
  'resolved', 'closed', 'rejected', 'withdrawn', 'reopened',
] as const;
export type Status = (typeof STATUSES)[number];
export const PRIORITIES = ['low', 'medium', 'high', 'critical'] as const;
export type Priority = (typeof PRIORITIES)[number];

export interface RoleGrant {
  role: Role; department_id: string | null; ward_id: string | null;
  department_code?: string | null; department_name?: string | null;
}
export interface User {
  id: string; email: string; display_name: string; phone: string | null; preferred_language: string;
  is_active: boolean; roles: RoleGrant[]; created_at: string;
}
export interface DemoAccount { group: string; email: string; display_name: string; description: string; password: string }
export interface Meta { app_name: string; demo_mode: boolean; demo_accounts: DemoAccount[] }
export interface Page<T> { items: T[]; total: number; page: number; page_size: number }
export interface Category {
  id: string; code: string; parent_id: string | null; label: string; description: string | null;
  synonyms: string[]; is_active: boolean; is_triage: boolean; default_priority: Priority;
}
export interface Ward { id: string; code: string; name: string; has_boundary: boolean; provenance: string; is_demo: boolean }
export interface Department {
  id: string; code: string; name: string; is_active: boolean; is_fallback: boolean; is_demo: boolean;
}
export interface Officer { id: string; user_id: string; department_id: string; team_id: string | null; is_active: boolean; accepts_assignments: boolean; display_name: string | null }
export interface Service {
  id: string; code: string; name: string; summary: string; instructions: string | null; service_type: 'information' | 'complaint';
  state: string; public_contact: string | null; operating_hours: string | null; eligibility: string | null;
  owner_department_id: string | null; department_ids: string[]; category_ids: string[]; last_reviewed_at: string | null; is_demo: boolean;
}
export interface ServiceMatch { service: Service; score: number; matched_on: string[]; matched_category: Category | null }
export interface ServiceSearch { items: ServiceMatch[]; total: number; no_match: boolean; guidance: string | null; used_provider: string }
export interface Suggestion {
  category: { category_id: string; category_code: string; label: string; confidence: number } | null;
  alternatives: { category_id: string; category_code: string; label: string; confidence: number }[];
  needs_manual_review: boolean; classifier: string; classifier_simulated: boolean; ward_id: string | null;
  outcome: 'routed' | 'fallback'; department_id: string | null; department_name: string | null;
  reason_code: string; explanation: string; emergency_notice: string;
}
export interface Progress {
  received_locally: boolean; routed_to_department: boolean; department_acknowledged: boolean;
  externally_acknowledged: boolean; external_is_simulated: boolean; marked_resolved: boolean;
  resident_confirmed: boolean; summary: string;
}
export interface TimelineEvent { from_status: Status | null; to_status: Status; actor_kind: string; actor_is_staff: boolean | null; reason: string | null; created_at: string }
export interface Assignment {
  kind: string; from_department_id: string | null; to_department_id: string | null; from_officer_id: string | null;
  to_officer_id: string | null; actor_kind: string; reason: string | null; created_at: string;
}
export interface Complaint {
  id: string; reference: string; title: string; description: string; original_language: string;
  category_id: string | null; reported_category_id: string | null; ward_id: string | null;
  latitude: number | null; longitude: number | null; address_text: string | null; visibility: 'private' | 'public';
  priority: Priority; status: Status; department_id: string | null; routing_outcome: 'routed' | 'fallback';
  due_at: string | null; created_at: string; updated_at: string; resolved_at: string | null; closed_at: string | null;
  resolution_notes: string | null; merged_into_reference: string | null; external_sync_state: string;
  external_case_id: string | null; external_is_simulated: boolean; version: number; progress: Progress; timeline: TimelineEvent[];
  // staff-only fields
  reporter_id?: string; category_source?: string; priority_reason?: string | null; team_id?: string | null;
  assigned_officer_id?: string | null; routing_explanation?: string; initial_routing?: Record<string, string | null>;
  acknowledge_due_at?: string | null; sla_paused_at?: string | null; is_overdue?: boolean; escalation_level?: number;
  reopen_count?: number; reassignment_count?: number; merged_into_id?: string | null; assignments?: Assignment[];
}
export interface ComplaintItem {
  id: string; reference: string; title: string; status: Status; priority: Priority; category_id: string | null;
  department_id: string | null; ward_id: string | null; assigned_officer_id: string | null; is_overdue: boolean;
  due_at: string | null; created_at: string; updated_at: string;
}
export interface Comment { id: string; author_id: string; author_is_staff: boolean; body: string; is_information_request: boolean; created_at: string }
export interface Note { id: string; author_id: string; body: string; created_at: string }
export interface Media { id: string; original_filename: string; content_type: string; size_bytes: number; kind: string; created_at: string; exif_stripped?: boolean }
export interface Duplicate { id: string | null; reference: string; title: string | null; category_id: string | null; status: Status; distance_m: number | null; text_similarity: number; created_at: string }
export interface Notification { id: string; complaint_id: string | null; complaint_reference: string | null; event_type: string; title: string; body: string; created_at: string; read_at: string | null }
export interface AnalyticsGroup { key: string; total: number; open: number; resolved_or_closed: number; overdue_open: number }
export interface Analytics {
  date_from: string; date_to: string;
  reports_total: number; issues_total: number; merged_duplicates: number; by_status: Record<Status, number>;
  open: number; overdue_open: number; reopened: number; resolution_hours_avg: number | null; resolution_hours_median: number | null;
  sla_met: number; sla_measured: number; sla_compliance: number | null;
  sla_policies_active: number; sla_policies_illustrative: boolean;
  assignment_hours_median: number | null; assignment_measured: number;
  by_department: AnalyticsGroup[]; by_category: AnalyticsGroup[]; by_ward: AnalyticsGroup[]; by_priority: AnalyticsGroup[];
}
