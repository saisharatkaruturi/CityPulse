// Pure analytics helpers: the date window, the "met the target" state, bar scaling and family roll-ups.
// Every figure is computed from the API response; nothing is filled in when data is missing.

import type { Analytics, AnalyticsGroup } from '../../api';
import { asFamily, FAMILIES, type Family } from '../../lib';
import { dayToIso } from './queueParams';

export type Preset = '30' | '90' | '365';
export const PRESETS: Preset[] = ['30', '90', '365'];
export const MAX_RANGE_DAYS = 366;
export const SMALL_SAMPLE = 5;

export interface Window { date_from: string; date_to: string }

/** A preset ends at the start of tomorrow (local), so today's reports are included and the key is stable. */
export function presetWindow(p: Preset, now = new Date()): Window {
  const end = new Date(now.getFullYear(), now.getMonth(), now.getDate() + 1);
  const start = new Date(end.getFullYear(), end.getMonth(), end.getDate() - Number(p));
  return { date_from: start.toISOString(), date_to: end.toISOString() };
}

export type RangeError = 'missing' | 'order' | 'tooLong' | null;

/** Validates a custom range of local days (inclusive). */
export function customWindow(from: string, to: string): { window: Window | null; error: RangeError } {
  if (!from || !to) return { window: null, error: 'missing' };
  const w = { date_from: dayToIso(from), date_to: dayToIso(to, true) };
  const days = (Date.parse(w.date_to) - Date.parse(w.date_from)) / 86_400_000;
  if (days <= 0) return { window: null, error: 'order' };
  if (days > MAX_RANGE_DAYS) return { window: null, error: 'tooLong' };
  return { window: w, error: null };
}

export type TargetState =
  | { kind: 'not_configured' }
  | { kind: 'insufficient' }
  | { kind: 'value'; met: number; measured: number; fraction: number; small: boolean; illustrative: boolean };

/** "Met the target" is only stated when a target exists and at least one resolved report had one. */
export function targetState(a: Pick<Analytics, 'sla_policies_active' | 'sla_policies_illustrative' | 'sla_met' | 'sla_measured'>): TargetState {
  if (a.sla_policies_active === 0) return { kind: 'not_configured' };
  if (a.sla_measured === 0) return { kind: 'insufficient' };
  return {
    kind: 'value', met: a.sla_met, measured: a.sla_measured, fraction: a.sla_met / a.sla_measured,
    small: a.sla_measured < SMALL_SAMPLE, illustrative: a.sla_policies_illustrative,
  };
}

/** Bar length as a percentage of the largest value; a non-zero value never disappears entirely. */
export function barPct(value: number, max: number): number {
  if (max <= 0 || value <= 0) return 0;
  return Math.max(1.5, Math.min(100, (value / max) * 100));
}

/** Sums category groups into issue families. Unknown or missing categories count under "other". */
export function byFamily(groups: AnalyticsGroup[], codeOf: (id: string | null) => string | null): (AnalyticsGroup & { key: Family })[] {
  const acc = new Map<Family, AnalyticsGroup & { key: Family }>();
  for (const g of groups) {
    const fam = asFamily(codeOf(g.key === 'none' ? null : g.key));
    const cur = acc.get(fam) ?? { key: fam, total: 0, open: 0, resolved_or_closed: 0, overdue_open: 0 };
    cur.total += g.total;
    cur.open += g.open;
    cur.resolved_or_closed += g.resolved_or_closed;
    cur.overdue_open += g.overdue_open;
    acc.set(fam, cur);
  }
  return FAMILIES.map((f) => acc.get(f)).filter((g): g is AnalyticsGroup & { key: Family } => Boolean(g && g.total));
}

/** The department with the most open reports past target, if any — the dashboard's headline finding. */
export function worstDepartment(groups: AnalyticsGroup[]): AnalyticsGroup | null {
  const sorted = groups.slice().sort((a, b) => b.overdue_open - a.overdue_open || b.open - a.open || a.key.localeCompare(b.key));
  return sorted[0] && sorted[0].overdue_open > 0 ? sorted[0] : null;
}

export const PRIORITY_ORDER = ['critical', 'high', 'medium', 'low'];
