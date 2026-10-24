import '../../styles/resident.css';

import { useEffect, useMemo, useRef, useState, type DragEvent, type FormEvent } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { api, ApiError, qs, type Category, type Complaint, type Media, type Suggestion } from '../../api';
import { FamilyIcon, Icon } from '../../components/Icon';
import { CategoryMark, PageHeader, StatusPill, useUnsavedWarning } from '../../components/ui';
import { LOCALES, useI18n, type MessageKey } from '../../i18n';
import { FAMILIES, asFamily, errorKey, fieldErrors, newIdempotencyKey, type Family } from '../../lib';
import { useResource } from '../../lib/useResource';
import { useRef$ } from '../refdata';
import {
  ACCEPTED_TYPES, LIMITS, checkFile, locationPayload, locationSummary, validateReport, type FormErrors,
} from '../resident/helpers';

interface Nearby { id: string; reference: string; title: string; status: string; distance_m: number | null; support_count: number }
type Gps = { latitude: number; longitude: number; accuracy_m?: number };
type GeoState = 'idle' | 'busy' | 'denied' | 'unavailable' | 'timeout' | 'unsupported';
interface Photo { id: string; file: File; preview: string; status: 'uploading' | 'done' | 'error'; media?: Media; error?: string }

/** Short, plain descriptions for the seeded categories. Unknown categories simply show their name. */
const CAT_DESC: Record<string, MessageKey> = {
  'roads.pothole': 'resident.cat.pothole',
  'roads.footpath': 'resident.cat.footpath',
  'sanitation.garbage': 'resident.cat.garbage',
  'water.leak': 'resident.cat.leak',
  'water.no_supply': 'resident.cat.noSupply',
  'drainage.blocked': 'resident.cat.drain',
  'lighting.streetlight': 'resident.cat.streetlight',
  'electrical.exposed_wire': 'resident.cat.wire',
  'electrical.public_fixture': 'resident.cat.fixture',
  'other.stray_animals': 'resident.cat.animals',
};

const GEO_MSG: Record<Exclude<GeoState, 'idle' | 'busy'>, MessageKey> = {
  denied: 'resident.loc.denied',
  unavailable: 'resident.loc.unavailable',
  timeout: 'resident.loc.timeout',
  unsupported: 'resident.loc.unsupported',
};

export default function NewReport() {
  const nav = useNavigate();
  const [params] = useSearchParams();
  const { t, tk, locale, plural } = useI18n();
  const ref = useRef$();
  const idemKey = useMemo(newIdempotencyKey, []); // one key per form, so a retried send never files twice

  const [phase, setPhase] = useState<'edit' | 'review'>('edit');
  const [categoryId, setCategoryId] = useState('');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [language, setLanguage] = useState<string>(locale);
  const [wardId, setWardId] = useState('');
  const [address, setAddress] = useState('');
  const [gps, setGps] = useState<Gps | null>(null);
  const [geo, setGeo] = useState<GeoState>('idle');
  const [photos, setPhotos] = useState<Photo[]>([]);
  const [isPublic, setPublic] = useState(false);
  const [safety, setSafety] = useState(false);
  const [errors, setErrors] = useState<FormErrors>({});
  const [serverErrors, setServerErrors] = useState<Record<string, string>>({});
  const [formError, setFormError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [sent, setSent] = useState(false);
  const [supported, setSupported] = useState<Record<string, boolean>>({});
  const [dragging, setDragging] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);
  const titleRef = useRef<HTMLInputElement>(null);
  const descRef = useRef<HTMLTextAreaElement>(null);
  const reviewRef = useRef<HTMLHeadingElement>(null);
  const preselected = useRef(false);

  const dirty = !sent && Boolean(title.trim() || description.trim() || photos.length || categoryId);
  useUnsavedWarning(dirty);

  // Choices, grouped by family. The triage category is offered as "Not sure" (no category sent).
  const choices = useMemo(() => ref.leaves.filter((c) => !c.is_triage), [ref.leaves]);
  const groups = useMemo(() => FAMILIES
    .map((f) => ({ family: f, items: choices.filter((c) => asFamily(c.code) === f) }))
    .filter((g) => g.items.length), [choices]);
  const selected = ref.category(categoryId);
  const electrical = asFamily(selected?.code) === 'electrical';

  // ?category=<code> from the landing page preselects once; a family code opens nothing but is harmless.
  useEffect(() => {
    if (preselected.current || !ref.leaves.length) return;
    const code = params.get('category');
    preselected.current = true;
    const match = code ? ref.leaves.find((c) => c.code === code && !c.is_triage) : undefined;
    if (match) choose(match);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [ref.leaves, params]);

  function choose(c: Category | null) {
    setCategoryId(c?.id ?? '');
    if (c && asFamily(c.code) === 'electrical') setSafety(true); // pre-ticked; the resident can untick it
  }

  // Live preview of where the report would go, from the city's routing rules. Nothing is saved.
  const suggestText = `${title}. ${description}`.trim();
  const suggestKey = categoryId || suggestText.length >= 12
    ? JSON.stringify({ categoryId, text: categoryId ? '' : suggestText, wardId, gps: gps ? [gps.latitude, gps.longitude] : null })
    : null;
  const [debouncedKey, setDebouncedKey] = useState<string | null>(null);
  useEffect(() => {
    const h = window.setTimeout(() => setDebouncedKey(suggestKey), 500);
    return () => window.clearTimeout(h);
  }, [suggestKey]);
  const suggestion = useResource<Suggestion>(debouncedKey, (signal) => api<Suggestion>('/routing/suggest', {
    signal,
    body: {
      description: categoryId ? undefined : suggestText, category_id: categoryId || undefined,
      ward_id: wardId || undefined, ...(gps ?? {}),
    },
  }));

  // Open public reports near the GPS point, so the resident can support one instead of filing twice.
  const nearbyKey = gps ? `${gps.latitude},${gps.longitude},${categoryId}` : null;
  const nearby = useResource<Nearby[]>(nearbyKey, (signal) => api<Nearby[]>(`/complaints/nearby${qs({
    lat: gps?.latitude, lng: gps?.longitude, radius_m: 300, category_id: categoryId || undefined,
  })}`, { signal }));

  // Release preview URLs when the form goes away.
  const photosRef = useRef(photos);
  photosRef.current = photos;
  useEffect(() => () => photosRef.current.forEach((p) => URL.revokeObjectURL(p.preview)), []);

  // ---- location ----
  function locate() {
    if (!('geolocation' in navigator)) { setGeo('unsupported'); return; }
    setGeo('busy');
    navigator.geolocation.getCurrentPosition(
      (p) => {
        setGps({ latitude: +p.coords.latitude.toFixed(6), longitude: +p.coords.longitude.toFixed(6), accuracy_m: Math.round(p.coords.accuracy) });
        setGeo('idle');
      },
      (e) => setGeo(e.code === 1 ? 'denied' : e.code === 3 ? 'timeout' : 'unavailable'),
      { enableHighAccuracy: true, timeout: 12000, maximumAge: 60000 },
    );
  }

  // ---- photos ----
  async function uploadOne(p: Photo) {
    setPhotos((xs) => xs.map((x) => (x.id === p.id ? { ...x, status: 'uploading', error: undefined } : x)));
    try {
      const fd = new FormData();
      fd.append('file', p.file);
      fd.append('kind', 'report_photo');
      const m = await api<Media>('/media', { form: fd });
      setPhotos((xs) => xs.map((x) => (x.id === p.id ? { ...x, status: 'done', media: m } : x)));
    } catch (e) {
      const k = errorKey(e);
      const msg = e instanceof ApiError && e.status === 413 ? t('resident.photos.tooBig')
        : e instanceof ApiError && e.status === 422 ? e.message : t(k.key, k.vars);
      setPhotos((xs) => xs.map((x) => (x.id === p.id ? { ...x, status: 'error', error: msg } : x)));
    }
  }

  const [photoNote, setPhotoNote] = useState<string | null>(null);
  async function addFiles(list: FileList | File[] | null) {
    if (!list) return;
    const files = Array.from(list);
    const room = LIMITS.maxPhotos - photos.length;
    const notes: string[] = [];
    if (files.length > room) notes.push(t('resident.photos.tooMany', { n: LIMITS.maxPhotos }));
    const fresh: Photo[] = [];
    for (const f of files.slice(0, Math.max(0, room))) {
      const problem = checkFile(f);
      if (problem) { notes.push(`${f.name}: ${t(problem)}`); continue; }
      fresh.push({ id: `${Date.now()}-${Math.random().toString(36).slice(2)}`, file: f, preview: URL.createObjectURL(f), status: 'uploading' });
    }
    setPhotoNote(notes.length ? notes.join(' ') : null);
    if (fileRef.current) fileRef.current.value = '';
    if (!fresh.length) return;
    setPhotos((xs) => [...xs, ...fresh]);
    for (const p of fresh) await uploadOne(p); // one at a time keeps a slow connection usable
  }

  function removePhoto(id: string) {
    setPhotos((xs) => {
      const p = xs.find((x) => x.id === id);
      if (p) URL.revokeObjectURL(p.preview);
      return xs.filter((x) => x.id !== id);
    });
  }

  function onDrop(e: DragEvent) {
    e.preventDefault();
    setDragging(false);
    void addFiles(e.dataTransfer.files);
  }

  async function support(id: string) {
    try {
      await api(`/complaints/${id}/support`, { method: 'POST' });
      setSupported((s) => ({ ...s, [id]: true }));
    } catch (e) {
      if (e instanceof ApiError && e.code === 'already_supported') setSupported((s) => ({ ...s, [id]: true }));
    }
  }

  // ---- review and send ----
  const uploading = photos.some((p) => p.status === 'uploading');
  const failedPhotos = photos.filter((p) => p.status === 'error').length;
  const loc = { wardId, address, gps };
  const locLines = locationSummary(loc, (id) => ref.wardName(id));

  function toReview(e: FormEvent) {
    e.preventDefault();
    const v = validateReport({ title, description });
    setErrors(v);
    setServerErrors({});
    setFormError(null);
    if (v.title) { titleRef.current?.focus(); return; }
    if (v.description) { descRef.current?.focus(); return; }
    setPhase('review');
    requestAnimationFrame(() => reviewRef.current?.focus());
  }

  async function send() {
    if (busy || uploading) return;
    setBusy(true);
    setFormError(null);
    try {
      const c = await api<Complaint>('/complaints', {
        body: {
          title: title.trim(), description: description.trim(), category_id: categoryId || undefined,
          location: locationPayload(loc), visibility: isPublic ? 'public' : 'private', safety_risk: safety, language,
          media_ids: photos.filter((p) => p.media).map((p) => p.media!.id), source_channel: 'web',
        },
        headers: { 'Idempotency-Key': idemKey },
      });
      setSent(true);
      nav(`/app/reports/${c.id}?new=1`, { replace: true });
    } catch (err) {
      const fe = fieldErrors(err);
      if (Object.keys(fe).length) {
        setServerErrors(fe);
        setPhase('edit');
        setFormError(t('error.validation'));
      } else {
        const k = errorKey(err);
        setFormError(`${t(k.key, k.vars)} ${t('resident.form.notSent')}`);
      }
    } finally {
      setBusy(false);
    }
  }

  const err = (field: 'title' | 'description') => (errors[field] ? t(errors[field]!) : serverErrors[field]);

  return (
    <>
      <PageHeader title={t('nav.report')} sub={t('resident.form.sub')} />
      <p className="notice notice-info form-intro"><Icon.info size={16} /><span>{t('safety.emergency')}</span></p>

      {phase === 'edit' && (
        <form className="report-form" onSubmit={toReview} noValidate aria-describedby={formError ? 'form-error' : undefined}>
          {formError && <p id="form-error" className="notice notice-bad" role="alert"><Icon.alert size={16} />{formError}</p>}

          {/* 1 — kind of problem */}
          <fieldset className="panel form-section">
            <legend className="section-legend">{t('resident.form.kindTitle')}</legend>
            <p className="meta section-hint">{t('resident.form.kindHint')}</p>
            {ref.categoriesFailed && <p className="notice notice-warn"><Icon.alert size={16} />{t('resident.form.catsFailed')}</p>}
            <div className="choice-groups">
              {groups.map((g) => (
                <div className="choice-group" key={g.family} role="group" aria-labelledby={`fam-${g.family}`}>
                  <p className="choice-group-name" id={`fam-${g.family}`}>{tk(`family.${g.family}`)}</p>
                  <div className="choices">
                    {g.items.map((c) => <Choice key={c.id} c={c} family={g.family} checked={categoryId === c.id} onChoose={() => choose(c)}
                      desc={CAT_DESC[c.code] ? t(CAT_DESC[c.code]) : undefined} />)}
                  </div>
                </div>
              ))}
              <div className="choice-group">
                <div className="choices">
                  <label className={`choice choice-unsure${categoryId === '' ? ' is-checked' : ''}`}>
                    <input type="radio" name="category" value="" checked={categoryId === ''} onChange={() => choose(null)} />
                    <span className="choice-icon cat-other"><FamilyIcon.other size={20} /></span>
                    <span className="choice-text">
                      <span className="choice-name">{t('resident.form.unsure')}</span>
                      <span className="choice-desc">{t('resident.form.unsureDesc')}</span>
                    </span>
                  </label>
                </div>
              </div>
            </div>
            {electrical && <p className="notice notice-safety" role="note"><Icon.alert size={20} /><span>{t('safety.electrical')}</span></p>}
          </fieldset>

          {/* 2 — describe it */}
          <fieldset className="panel form-section">
            <legend className="section-legend">{t('resident.form.describeTitle')}</legend>
            <div className="field">
              <label htmlFor="r-title">{t('resident.form.titleLabel')} <span className="req">({t('common.required')})</span></label>
              <input id="r-title" ref={titleRef} className="input" value={title} maxLength={LIMITS.titleMax}
                onChange={(e) => setTitle(e.target.value)} placeholder={t('resident.form.titlePh')}
                aria-invalid={Boolean(err('title'))} aria-describedby={err('title') ? 'r-title-err' : undefined} autoComplete="off" />
              {err('title') && <p id="r-title-err" className="field-error"><Icon.alert size={16} />{err('title')}</p>}
            </div>
            <div className="field">
              <label htmlFor="r-desc">{t('resident.form.descLabel')} <span className="req">({t('common.required')})</span></label>
              <textarea id="r-desc" ref={descRef} className="input" rows={5} value={description} maxLength={LIMITS.descMax}
                onChange={(e) => setDescription(e.target.value)} aria-invalid={Boolean(err('description'))}
                aria-describedby={`r-desc-hint${err('description') ? ' r-desc-err' : ''}`} lang={language} />
              <p id="r-desc-hint" className="hint">{t('resident.form.descHint', { n: LIMITS.descMin })} <span className="num">{description.trim().length}/{LIMITS.descMax}</span></p>
              {err('description') && <p id="r-desc-err" className="field-error"><Icon.alert size={16} />{err('description')}</p>}
            </div>
            <div className="field narrow">
              <label htmlFor="r-lang">{t('resident.form.langLabel')}</label>
              <select id="r-lang" className="input" value={language} onChange={(e) => setLanguage(e.target.value)}>
                {LOCALES.map((l) => <option key={l.code} value={l.code}>{l.native}{l.native !== l.english ? ` · ${l.english}` : ''}</option>)}
              </select>
            </div>
            <RoutePreview suggestion={suggestion.data} loading={suggestion.loading || suggestion.refreshing} failed={Boolean(suggestion.error)}
              chosen={Boolean(categoryId)} onUse={(id) => { const c = ref.category(id); if (c) choose(c); }} />
          </fieldset>

          {/* 3 — location */}
          <fieldset className="panel form-section">
            <legend className="section-legend">{t('resident.loc.title')} <span className="req">({t('common.optional')})</span></legend>
            <p className="meta section-hint">{t('resident.loc.why')}</p>
            <div className="row-2">
              <div className="field">
                <label htmlFor="r-ward">{t('resident.loc.ward')}</label>
                <select id="r-ward" className="input" value={wardId} onChange={(e) => setWardId(e.target.value)}>
                  <option value="">{t('resident.loc.noWard')}</option>
                  {ref.wards.map((w) => <option key={w.id} value={w.id}>{w.name}{w.is_demo ? ` (${t('resident.loc.demoWard')})` : ''}</option>)}
                </select>
              </div>
              <div className="field">
                <label htmlFor="r-addr">{t('resident.loc.address')}</label>
                <input id="r-addr" className="input" value={address} maxLength={300} onChange={(e) => setAddress(e.target.value)}
                  placeholder={t('resident.loc.addressPh')} autoComplete="off" />
              </div>
            </div>
            <div className="gps-row">
              <button type="button" className="btn" onClick={locate} disabled={geo === 'busy'} aria-busy={geo === 'busy'}>
                <Icon.pin size={18} />
                {geo === 'busy' ? t('resident.loc.finding') : gps ? t('resident.loc.update') : t('resident.loc.useMine')}
              </button>
              {gps && <button type="button" className="btn btn-quiet" onClick={() => setGps(null)}><Icon.close size={18} />{t('resident.loc.removeGps')}</button>}
              <p className="meta">{t('resident.loc.gpsWhy')}</p>
            </div>
            {geo !== 'idle' && geo !== 'busy' && (
              <p className="notice notice-warn" role="status"><Icon.alert size={16} />{t(GEO_MSG[geo])}</p>
            )}
            <div className="loc-summary" aria-live="polite">
              <p className="loc-summary-title">{t('resident.loc.summaryTitle')}</p>
              <ul>{locLines.map((l, i) => <li key={i}>{t(l.key, l.vars)}</li>)}</ul>
            </div>
          </fieldset>

          {/* 4 — photos */}
          <fieldset className="panel form-section">
            <legend className="section-legend">{t('resident.photos.title')} <span className="req">({t('common.optional')})</span></legend>
            <div className={`dropzone${dragging ? ' is-over' : ''}`}
              onDragOver={(e) => { e.preventDefault(); setDragging(true); }} onDragLeave={() => setDragging(false)} onDrop={onDrop}>
              <Icon.image size={24} />
              <label htmlFor="r-photos" className="btn">
                <Icon.upload size={18} />{t('resident.photos.choose')}
              </label>
              <input ref={fileRef} id="r-photos" className="visually-hidden-input" type="file" accept={ACCEPTED_TYPES.join(',')} multiple
                disabled={photos.length >= LIMITS.maxPhotos} onChange={(e) => addFiles(e.target.files)} aria-describedby="r-photos-hint" />
              <p id="r-photos-hint" className="meta">{t('resident.photos.hint', { n: LIMITS.maxPhotos })}</p>
            </div>
            <p className="meta">{t('resident.photos.privacy')}</p>
            {photoNote && <p className="field-error" role="alert"><Icon.alert size={16} />{photoNote}</p>}
            {photos.length > 0 && (
              <ul className="photo-grid">
                {photos.map((p) => (
                  <li key={p.id} className={`photo photo-${p.status}`}>
                    <img src={p.preview} alt={t('resident.photos.alt', { name: p.file.name })} width={120} height={120} />
                    <span className="photo-status" role="status">
                      {p.status === 'uploading' && t('resident.photos.uploading')}
                      {p.status === 'done' && <><Icon.check size={14} />{t('resident.photos.done')}</>}
                      {p.status === 'error' && <><Icon.alert size={14} />{p.error}</>}
                    </span>
                    <span className="photo-actions">
                      {p.status === 'error' && <button type="button" className="btn btn-sm" onClick={() => uploadOne(p)}>{t('common.retry')}</button>}
                      <button type="button" className="btn btn-sm btn-quiet" onClick={() => removePhoto(p.id)} disabled={p.status === 'uploading'}
                        aria-label={t('resident.photos.removeNamed', { name: p.file.name })}>{t('resident.photos.remove')}</button>
                    </span>
                  </li>
                ))}
              </ul>
            )}
          </fieldset>

          {/* 5 — who can see it */}
          <fieldset className="panel form-section">
            <legend className="section-legend">{t('resident.vis.title')}</legend>
            <div className="choices choices-2">
              <label className={`choice${!isPublic ? ' is-checked' : ''}`}>
                <input type="radio" name="vis" checked={!isPublic} onChange={() => setPublic(false)} />
                <span className="choice-text"><span className="choice-name">{t('resident.vis.private')}</span><span className="choice-desc">{t('resident.vis.privateDesc')}</span></span>
              </label>
              <label className={`choice${isPublic ? ' is-checked' : ''}`}>
                <input type="radio" name="vis" checked={isPublic} onChange={() => setPublic(true)} />
                <span className="choice-text"><span className="choice-name">{t('resident.vis.public')}</span><span className="choice-desc">{t('resident.vis.publicDesc')}</span></span>
              </label>
            </div>
            <label className="check">
              <input type="checkbox" checked={safety} onChange={(e) => setSafety(e.target.checked)} />
              <span>{t('resident.form.safety')}</span>
            </label>
          </fieldset>

          {gps && <NearbyPanel items={nearby.data} loading={nearby.loading} failed={Boolean(nearby.error)} supported={supported} onSupport={support} />}

          <div className="form-foot">
            {uploading && <p className="meta" role="status">{t('resident.photos.waitUpload')}</p>}
            <button className="btn btn-primary" type="submit" disabled={uploading}>{t('resident.form.toReview')}<Icon.arrowRight size={18} /></button>
          </div>
        </form>
      )}

      {phase === 'review' && (
        <section className="panel review" aria-labelledby="review-h">
          <h2 id="review-h" ref={reviewRef} tabIndex={-1}>{t('resident.review.title')}</h2>
          <p className="meta">{t('resident.review.sub')}</p>
          <dl className="review-list">
            <dt>{t('resident.review.kind')}</dt>
            <dd>{selected ? <CategoryMark code={selected.code} label={selected.label} /> : t('resident.form.unsure')}</dd>
            <dt>{t('resident.form.titleLabel')}</dt><dd>{title.trim()}</dd>
            <dt>{t('resident.form.descLabel')}</dt><dd className="pre" lang={language}>{description.trim()}</dd>
            <dt>{t('resident.loc.summaryTitle')}</dt>
            <dd><ul className="plain">{locLines.map((l, i) => <li key={i}>{t(l.key, l.vars)}</li>)}</ul></dd>
            <dt>{t('resident.photos.title')}</dt>
            <dd>
              {plural('resident.review.photos', photos.filter((p) => p.media).length)}
              {failedPhotos > 0 && <span className="field-error"><Icon.alert size={14} />{plural('resident.review.photosFailed', failedPhotos)}</span>}
            </dd>
            <dt>{t('resident.vis.title')}</dt><dd>{isPublic ? t('resident.vis.public') : t('resident.vis.private')}</dd>
            <dt>{t('resident.review.safety')}</dt><dd>{safety ? t('resident.review.yes') : t('resident.review.no')}</dd>
          </dl>
          {electrical && <p className="notice notice-safety"><Icon.alert size={20} /><span>{t('safety.electrical')}</span></p>}
          <p className="notice notice-info"><Icon.info size={16} /><span>{t('resident.review.honest')}</span></p>
          {formError && <p className="notice notice-bad" role="alert"><Icon.alert size={16} />{formError}</p>}
          <div className="actions">
            <button type="button" className="btn btn-quiet" onClick={() => setPhase('edit')} disabled={busy}><Icon.chevronLeft size={18} />{t('resident.review.edit')}</button>
            <button type="button" className="btn btn-primary" onClick={send} disabled={busy || uploading} aria-busy={busy}>
              {busy ? t('resident.review.sending') : t('resident.review.send')}
            </button>
          </div>
        </section>
      )}
    </>
  );
}

function Choice({ c, family, checked, onChoose, desc }: { c: Category; family: Family; checked: boolean; onChoose: () => void; desc?: string }) {
  const I = FamilyIcon[family];
  return (
    <label className={`choice${checked ? ' is-checked' : ''}`}>
      <input type="radio" name="category" value={c.id} checked={checked} onChange={onChoose} />
      <span className={`choice-icon cat-${family}`}><I size={20} /></span>
      <span className="choice-text">
        <span className="choice-name">{c.label}</span>
        {desc && <span className="choice-desc">{desc}</span>}
      </span>
    </label>
  );
}

function RoutePreview({ suggestion, loading, failed, chosen, onUse }: {
  suggestion: Suggestion | null; loading: boolean; failed: boolean; chosen: boolean; onUse: (id: string) => void;
}) {
  const { t } = useI18n();
  return (
    <div className="route-preview" aria-live="polite">
      <p className="route-title">{t('resident.route.title')}</p>
      {failed ? <p className="meta">{t('resident.route.failed')}</p>
        : !suggestion ? <p className="meta">{loading ? t('common.loading') : t('resident.route.idle')}</p>
        : (
          <>
            <p>
              {suggestion.outcome === 'routed' && suggestion.department_name
                ? t('resident.route.routed', { dept: suggestion.department_name })
                : t('resident.route.triage')}
            </p>
            {!chosen && suggestion.category && (
              <p className="route-suggest">
                <span>{t('resident.route.soundsLike', { category: suggestion.category.label })}</span>
                <button type="button" className="btn btn-sm" onClick={() => onUse(suggestion.category!.category_id)}>{t('resident.route.use')}</button>
              </p>
            )}
            <p className="meta">{t('resident.route.rules')}</p>
          </>
        )}
    </div>
  );
}

function NearbyPanel({ items, loading, failed, supported, onSupport }: {
  items: Nearby[] | null; loading: boolean; failed: boolean; supported: Record<string, boolean>; onSupport: (id: string) => void;
}) {
  const { t, fmt, plural } = useI18n();
  return (
    <section className="panel form-section" aria-labelledby="nearby-h">
      <h2 id="nearby-h" className="section-legend">{t('resident.nearby.title')}</h2>
      {loading && <p className="meta">{t('common.loading')}</p>}
      {failed && <p className="meta">{t('resident.nearby.failed')}</p>}
      {items && items.length === 0 && <p className="meta">{t('resident.nearby.none')}</p>}
      {items && items.length > 0 && (
        <ul className="nearby">
          {items.map((n) => (
            <li key={n.id}>
              <span className="nearby-text">
                <strong>{n.title}</strong>
                <span className="meta">
                  {n.reference}
                  {n.distance_m != null && ` · ${t('resident.nearby.distance', { m: fmt.number(n.distance_m) })}`}
                  {` · ${plural('resident.nearby.supporters', n.support_count)}`}
                </span>
                <StatusPill status={n.status} />
              </span>
              <button type="button" className="btn btn-sm" onClick={() => onSupport(n.id)} disabled={supported[n.id]}>
                {supported[n.id] ? t('resident.nearby.supported') : t('resident.nearby.support')}
              </button>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}
