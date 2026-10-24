import { ApiError, PRIORITIES, STATUSES, type Priority, type Progress, type Status } from './api';
import type { MessageKey } from './i18n';

/** Statuses in which a report still needs work. */
export const OPEN: Status[] = ['submitted', 'under_review', 'assigned', 'in_progress', 'awaiting_resident', 'on_hold', 'reopened'];
export const FINISHED: Status[] = ['resolved', 'closed', 'rejected', 'withdrawn'];

export type Tone = 'neutral' | 'info' | 'warn' | 'ok' | 'bad';

/** Pill tone per status: neutral while waiting, info while work happens, positive only once staff say fixed. */
export const STATUS_TONE: Record<Status, Tone> = {
  submitted: 'neutral', under_review: 'info', assigned: 'info', in_progress: 'info', awaiting_resident: 'warn',
  on_hold: 'warn', resolved: 'ok', closed: 'ok', rejected: 'bad', withdrawn: 'neutral', reopened: 'warn',
};
export const PRIORITY_TONE: Record<Priority, Tone> = { low: 'neutral', medium: 'neutral', high: 'warn', critical: 'bad' };

export const isStatus = (s: string): s is Status => (STATUSES as readonly string[]).includes(s);
export const isPriority = (p: string): p is Priority => (PRIORITIES as readonly string[]).includes(p);

/** Defined sort order for priority (critical first), so sorting never falls back to the alphabet. */
export const PRIORITY_RANK: Record<Priority, number> = { critical: 0, high: 1, medium: 2, low: 3 };
export function comparePriority(a: string, b: string): number {
  const ra = isPriority(a) ? PRIORITY_RANK[a] : 99;
  const rb = isPriority(b) ? PRIORITY_RANK[b] : 99;
  return ra - rb;
}

/** Family (top-level code) of a category code: "electrical.exposed_wire" -> "electrical". */
export const familyOf = (code: string | null | undefined) => (code ? code.split('.')[0] : 'other');
export const FAMILIES = ['roads', 'sanitation', 'water', 'drainage', 'lighting', 'electrical', 'other'] as const;
export type Family = (typeof FAMILIES)[number];
export const asFamily = (code: string | null | undefined): Family => {
  const f = familyOf(code);
  return (FAMILIES as readonly string[]).includes(f) ? (f as Family) : 'other';
};

/** The honest stages a report can reach, in order. Each one is marked only when it really happened. */
export function stages(p: Progress): { key: string; label: MessageKey; done: boolean }[] {
  return [
    { key: 'submitted', label: 'stage.submitted', done: p.received_locally },
    { key: 'routed', label: 'stage.routed', done: p.routed_to_department },
    { key: 'picked', label: 'stage.pickedUp', done: p.department_acknowledged },
    { key: 'resolved', label: 'stage.resolved', done: p.marked_resolved },
    { key: 'confirmed', label: 'stage.confirmed', done: p.resident_confirmed },
  ];
}

/** "Due in 2 days" / "3 days overdue" / paused, measured against now. Returns a message key and vars. */
export function dueState(due: string | null | undefined, paused?: string | null, now = Date.now()):
  { key: MessageKey; vars?: Record<string, number>; overdue: boolean } {
  if (paused) return { key: 'due.paused' as MessageKey, overdue: false };
  if (!due) return { key: 'due.none' as MessageKey, overdue: false };
  const ms = new Date(due).getTime() - now;
  const days = Math.abs(ms) / 86_400_000;
  const unit = days >= 2 ? 'days' : 'hours';
  const n = unit === 'days' ? Math.round(days) : Math.max(1, Math.round(Math.abs(ms) / 3_600_000));
  return { key: `due.${ms >= 0 ? 'in' : 'over'}.${unit}` as MessageKey, vars: { n }, overdue: ms < 0 };
}

export function newIdempotencyKey(): string {
  const a = new Uint8Array(12);
  crypto.getRandomValues(a);
  return 'web-' + Array.from(a, (b) => b.toString(16).padStart(2, '0')).join('');
}

/** Maps an error to a plain-language message key; the server's own message is used for validation. */
export function errorKey(e: unknown): { key: MessageKey; vars?: Record<string, string | number> } {
  if (e instanceof ApiError) {
    if (e.status === 0) return { key: 'error.network' };
    if (e.status === 401) return { key: 'error.session' };
    if (e.status === 403) return { key: 'error.forbidden' };
    if (e.status === 404) return { key: 'error.notFound' };
    if (e.status === 409 || e.status === 412) return { key: 'error.conflict' };
    if (e.status === 429) return { key: 'error.rateLimited' };
    if (e.status === 422 || e.status === 400) return { key: 'error.validation' };
    if (e.status >= 500) return { key: 'error.server', vars: { status: e.status } };
  }
  return { key: 'error.generic' };
}

/** Field-level messages from a 422 response, keyed by the last part of the field path. */
export function fieldErrors(e: unknown): Record<string, string> {
  const out: Record<string, string> = {};
  if (e instanceof ApiError) e.details.forEach((d) => { if (d.field) out[d.field.split('.').pop()!] = d.message ?? d.issue ?? ''; });
  return out;
}

/** A safe CSV filename from the server's Content-Disposition, or a dated fallback. */
export function filenameFrom(disposition: string | null, fallback: string): string {
  const m = disposition?.match(/filename="?([^";]+)"?/i);
  const name = (m?.[1] ?? fallback).replace(/[^\w.-]+/g, '_');
  return name.toLowerCase().endsWith('.csv') ? name : `${name}.csv`;
}
