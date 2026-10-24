// Pure helpers for the public pages, kept out of components so they can be unit-tested.
import type { Category } from '../api';
import type { Family } from '../lib';
import { asFamily } from '../lib';
import { homeFor, type Experience } from '../roles';

/** Leaf categories shown when /api/categories cannot be reached (mirrors the demo seed). */
export const FALLBACK_CODES = [
  'roads.pothole', 'roads.footpath', 'sanitation.garbage', 'water.leak', 'water.no_supply', 'drainage.blocked',
  'lighting.streetlight', 'electrical.exposed_wire', 'electrical.public_fixture', 'other.stray_animals', 'other.triage',
] as const;

export const FAMILY_ORDER: Family[] = ['roads', 'sanitation', 'water', 'drainage', 'lighting', 'electrical', 'other'];

export interface ReportRow { code: string; label: string | null }

/** Groups reportable leaf categories by family, in a fixed family order; parents are not reportable. */
export function groupCategories(cats: Pick<Category, 'id' | 'code' | 'label' | 'parent_id' | 'is_active'>[] | null):
  { family: Family; rows: ReportRow[] }[] {
  const rows: ReportRow[] = cats
    ? (() => {
        const parents = new Set(cats.map((c) => c.parent_id).filter(Boolean));
        return cats.filter((c) => c.is_active && !parents.has(c.id) && c.code.includes('.'))
          .map((c) => ({ code: c.code, label: c.label }));
      })()
    : FALLBACK_CODES.map((code) => ({ code, label: null }));
  return FAMILY_ORDER
    .map((family) => ({
      family,
      rows: rows.filter((r) => asFamily(r.code) === family)
        // "Other / not sure" always last in its group
        .sort((a, b) => Number(a.code === 'other.triage') - Number(b.code === 'other.triage') || a.code.localeCompare(b.code)),
    }))
    .filter((g) => g.rows.length);
}

/** Reasons a service matched, strongest first, as message-key suffixes. Unknown reasons are dropped. */
const REASONS = ['category', 'related_category', 'name', 'synonyms', 'description', 'browse'] as const;
export type MatchReason = (typeof REASONS)[number];
export function matchReasons(matchedOn: string[]): MatchReason[] {
  const set = new Set(matchedOn.map((m) => (m === 'name_terms' ? 'name' : m)));
  return REASONS.filter((r) => set.has(r));
}

/**
 * Where to go after sign-in. `next` is honoured only for same-site paths the role can use; anything else
 * (another site, a resident page for a staff account) falls back to the role's start page.
 */
export function afterSignIn(next: string | null, e: Experience): string {
  if (!next || !next.startsWith('/') || next.startsWith('//') || next.startsWith('/\\')) return homeFor(e);
  const path = next.split(/[?#]/)[0];
  const residentOnly = path === '/app' || path === '/app/' || path.startsWith('/app/report') && !path.startsWith('/app/reports/')
    || path.startsWith('/app/services');
  const staffOnly = path.startsWith('/app/queue') || path.startsWith('/app/analytics');
  if (e === 'resident' ? staffOnly : residentOnly) return homeFor(e);
  return next;
}

/** Where a report CTA leads for the current visitor: staff to their queue, everyone else to the form. */
export function reportTarget(isStaff: boolean, code?: string): string {
  if (isStaff) return '/app/queue';
  return code ? `/app/report?category=${encodeURIComponent(code)}` : '/app/report';
}

/** Basic email shape check for inline validation; the server validates for real. */
export const looksLikeEmail = (s: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s.trim());
