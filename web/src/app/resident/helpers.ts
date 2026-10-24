// Pure logic behind the resident screens, kept apart from the components so it can be unit tested.
import type { Notification, ServiceMatch } from '../../api';
import type { MessageKey } from '../../i18n';

// ---- report form ----------------------------------------------------------------------------------

/** Limits mirror app/schemas/complaints.py (Title 3–200, Description 10–5000, 5 media) and settings. */
export const LIMITS = { titleMin: 3, titleMax: 200, descMin: 10, descMax: 5000, maxPhotos: 5, maxBytes: 5_000_000 };
export const ACCEPTED_TYPES = ['image/jpeg', 'image/png', 'image/webp'];

export type FormErrors = Partial<Record<'title' | 'description', MessageKey>>;

export function validateReport(v: { title: string; description: string }): FormErrors {
  const e: FormErrors = {};
  const title = v.title.trim();
  const desc = v.description.trim();
  if (!title) e.title = 'resident.form.titleRequired';
  else if (title.length < LIMITS.titleMin) e.title = 'resident.form.titleShort';
  if (!desc) e.description = 'resident.form.descRequired';
  else if (desc.length < LIMITS.descMin) e.description = 'resident.form.descShort';
  return e;
}

/** Client-side check before upload; the server checks again from the file's content. */
export function checkFile(f: { type: string; size: number }): MessageKey | null {
  if (!ACCEPTED_TYPES.includes(f.type)) return 'resident.photos.badType';
  if (f.size > LIMITS.maxBytes) return 'resident.photos.tooBig';
  if (f.size === 0) return 'resident.photos.empty';
  return null;
}

// ---- location ---------------------------------------------------------------------------------------

export interface LocationChoice {
  wardId: string;
  address: string;
  gps: { latitude: number; longitude: number; accuracy_m?: number } | null;
}

/** Exactly what is sent. Nothing is attached unless the resident chose it. */
export function locationPayload(c: LocationChoice): Record<string, unknown> | undefined {
  const address = c.address.trim();
  if (c.gps) return { ...c.gps, source: 'gps', ward_id: c.wardId || undefined, address_text: address || undefined };
  if (c.wardId) return { ward_id: c.wardId, source: 'ward_selection', address_text: address || undefined };
  if (address) return { source: 'address', address_text: address };
  return undefined;
}

/** Plain-language lines describing the attached location. Never prints coordinates. */
export function locationSummary(c: LocationChoice, wardName: (id: string) => string):
  { key: MessageKey; vars?: Record<string, string | number> }[] {
  const out: { key: MessageKey; vars?: Record<string, string | number> }[] = [];
  if (c.wardId) out.push({ key: 'resident.loc.sumWard', vars: { ward: wardName(c.wardId) } });
  if (c.address.trim()) out.push({ key: 'resident.loc.sumAddress', vars: { text: c.address.trim() } });
  if (c.gps) {
    out.push(c.gps.accuracy_m != null
      ? { key: 'resident.loc.sumGps', vars: { m: Math.round(c.gps.accuracy_m) } }
      : { key: 'resident.loc.sumGpsNoAcc' });
  }
  if (!out.length) out.push({ key: 'resident.loc.sumNone' });
  return out;
}

// ---- services ---------------------------------------------------------------------------------------

/** Why a service matched, in words, from the server's own signals. Rule-based; never described as AI. */
export function matchReasons(m: Pick<ServiceMatch, 'matched_on' | 'matched_category'>):
  { key: MessageKey; vars?: Record<string, string> }[] {
  const out: { key: MessageKey; vars?: Record<string, string> }[] = [];
  const on = new Set(m.matched_on);
  if (on.has('category') && m.matched_category) out.push({ key: 'resident.svc.whyCategory', vars: { category: m.matched_category.label } });
  else if (on.has('related_category') && m.matched_category) out.push({ key: 'resident.svc.whyRelated', vars: { category: m.matched_category.label } });
  if (on.has('name') || on.has('name_terms')) out.push({ key: 'resident.svc.whyName' });
  if (on.has('synonyms')) out.push({ key: 'resident.svc.whySynonyms' });
  if (on.has('description')) out.push({ key: 'resident.svc.whyDescription' });
  return out;
}

/** The top result is a confident "best match" only when it clearly leads the next one. */
export function isClearBest(items: Pick<ServiceMatch, 'score'>[]): boolean {
  if (!items.length) return false;
  if (items.length === 1) return true;
  return items[0].score >= items[1].score * 1.25;
}

// ---- notifications ----------------------------------------------------------------------------------

export function groupByDay<T extends Pick<Notification, 'created_at'>>(items: T[], now = new Date()):
  { today: T[]; earlier: T[] } {
  const start = new Date(now);
  start.setHours(0, 0, 0, 0);
  const today: T[] = [];
  const earlier: T[] = [];
  for (const n of items) (new Date(n.created_at) >= start ? today : earlier).push(n);
  return { today, earlier };
}
