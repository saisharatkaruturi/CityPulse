import '../../styles/resident.css';

import { useEffect, useMemo, useState } from 'react';
import { Link, useLocation, useNavigate, useParams, useSearchParams } from 'react-router-dom';
import { api, qs, type ServiceMatch, type ServiceSearch } from '../../api';
import { FamilyIcon, Icon } from '../../components/Icon';
import { CategoryMark, Dialog, EmptyState, ErrorState, PageHeader, Pill, Skeleton, StaleNotice } from '../../components/ui';
import { useI18n } from '../../i18n';
import { FAMILIES, asFamily } from '../../lib';
import { useResource } from '../../lib/useResource';
import { useRef$ } from '../refdata';
import { isClearBest, matchReasons } from '../resident/helpers';

/** Screen question: which service handles the problem I have? */
export default function Services() {
  const { t, tk, locale } = useI18n();
  const ref = useRef$();
  const { code } = useParams();
  const loc = useLocation();
  const nav = useNavigate();
  const [params, setParams] = useSearchParams();
  const q = params.get('q') ?? '';
  const fam = params.get('family') ?? '';
  const [draft, setDraft] = useState(q);
  useEffect(() => setDraft(q), [q]);

  // Typing updates the URL after a short pause, so back navigation returns to the same results.
  useEffect(() => {
    const h = window.setTimeout(() => {
      if (draft.trim() === q) return;
      setParams((p) => { if (draft.trim()) p.set('q', draft.trim()); else p.delete('q'); return p; }, { replace: true });
    }, 350);
    return () => window.clearTimeout(h);
  }, [draft, q, setParams]);

  // Family filters are offered only for families that exist as parent categories.
  const families = useMemo(() => FAMILIES
    .map((f) => ({ f, cat: ref.categories.find((c) => c.code === f && !c.parent_id) }))
    .filter((x) => x.cat), [ref.categories]);
  const famCat = families.find((x) => x.f === fam)?.cat;

  const key = `svc?q=${q}&cat=${famCat?.id ?? ''}&l=${locale}`;
  const res = useResource<ServiceSearch>(key, (signal) =>
    api<ServiceSearch>(`/services${qs({ q: q || undefined, category_id: famCat?.id, limit: 20 })}`, { signal }));
  const items = res.data?.items ?? [];
  const searching = Boolean(q);
  const best = searching && isClearBest(items) ? items[0] : null;
  const rest = best ? items.slice(1) : items;

  const openHref = (c: string) => `/app/services/${encodeURIComponent(c)}${loc.search}`;
  const close = () => {
    if (!code) return;
    if ((loc.state as { fromList?: boolean } | null)?.fromList) nav(-1);
    else nav(`/app/services${loc.search}`, { replace: true });
  };
  const setFamily = (f: string) => setParams((p) => { if (f) p.set('family', f); else p.delete('family'); return p; });

  return (
    <>
      <PageHeader title={t('nav.services')} sub={t('resident.svc.sub')} />

      <form className="svc-search" role="search" onSubmit={(e) => { e.preventDefault(); setParams((p) => { if (draft.trim()) p.set('q', draft.trim()); else p.delete('q'); return p; }); }}>
        <label htmlFor="svc-q" className="svc-search-label">{t('resident.svc.searchLabel')}</label>
        <div className="svc-search-row">
          <Icon.search size={22} />
          <input id="svc-q" className="input" type="search" value={draft} onChange={(e) => setDraft(e.target.value)}
            placeholder={t('resident.svc.searchPh')} maxLength={200} autoComplete="off" />
        </div>
        <p className="meta">{t('resident.svc.howRanked')}</p>
      </form>

      {families.length > 0 && (
        <div className="family-filter" role="group" aria-label={t('resident.svc.filterLabel')}>
          <button type="button" aria-pressed={!fam} onClick={() => setFamily('')}>{t('resident.svc.allKinds')}</button>
          {families.map(({ f }) => {
            const I = FamilyIcon[f];
            return (
              <button key={f} type="button" aria-pressed={fam === f} onClick={() => setFamily(fam === f ? '' : f)}>
                <I size={16} />{tk(`family.${f}`)}
              </button>
            );
          })}
        </div>
      )}

      {locale !== 'en' && <p className="notice notice-info"><Icon.info size={16} />{t('resident.svc.englishOnly')}</p>}

      <div aria-live="polite" aria-busy={res.loading || res.refreshing}>
        {res.error != null && res.data && <StaleNotice error={res.error} onRetry={res.reload} />}
        {res.error != null && !res.data && <ErrorState error={res.error} onRetry={res.reload} title={t('resident.svc.loadError')} />}
        {res.loading && !res.data && <Skeleton rows={4} height={64} />}

        {res.data?.no_match && (
          <EmptyState title={t('resident.svc.noMatchTitle', { q })}
            action={<Link className="btn btn-primary" to="/app/report">{t('resident.svc.reportAnyway')}</Link>}>
            <p>{res.data.guidance ?? t('resident.svc.noMatchBody')}</p>
            <p>{t('resident.svc.noMatchTry')}</p>
          </EmptyState>
        )}

        {best && <BestMatch m={best} href={openHref(best.service.code)} />}

        {rest.length > 0 && (
          <section aria-labelledby="svc-list-h" className="svc-list-wrap">
            <h2 id="svc-list-h" className="svc-list-h">
              {best ? t('resident.svc.alsoRelevant') : searching ? t('resident.svc.matches') : t('resident.svc.allServices')}
            </h2>
            <ul className="svc-list">
              {rest.map((m) => <ServiceRow key={m.service.id} m={m} href={openHref(m.service.code)} explain={searching} />)}
            </ul>
          </section>
        )}
      </div>

      <ServiceDetail code={code ?? null} fromResults={items} onClose={close} />
    </>
  );
}

function Reasons({ m }: { m: ServiceMatch }) {
  const { t } = useI18n();
  const reasons = matchReasons(m);
  if (!reasons.length) return null;
  return <ul className="reasons">{reasons.map((r, i) => <li key={i}><Icon.check size={14} />{t(r.key, r.vars)}</li>)}</ul>;
}

function BestMatch({ m, href }: { m: ServiceMatch; href: string }) {
  const { t } = useI18n();
  const s = m.service;
  return (
    <section className="best-match" aria-labelledby="best-h">
      <p className="best-label"><Icon.check size={16} />{t('resident.svc.bestMatch')}</p>
      <h2 id="best-h" className="best-name">{s.name}</h2>
      <p className="best-summary">{s.summary}</p>
      <Reasons m={m} />
      <div className="actions">
        <Link className="btn btn-primary" to={href} state={{ fromList: true }}>{t('resident.svc.details')}<Icon.arrowRight size={18} /></Link>
        {s.service_type === 'complaint' && <ReportLink categoryIds={s.category_ids} />}
      </div>
    </section>
  );
}

function ServiceRow({ m, href, explain }: { m: ServiceMatch; href: string; explain: boolean }) {
  const { t } = useI18n();
  const ref = useRef$();
  const s = m.service;
  const fam = asFamily(ref.catCode(s.category_ids[0]));
  const I = FamilyIcon[fam];
  return (
    <li>
      <Link className="svc-row" to={href} state={{ fromList: true }}>
        <span className={`cat-mark cat-${fam}`}><I size={18} /></span>
        <span className="svc-row-text">
          <span className="svc-row-name">{s.name}</span>
          <span className="svc-row-summary">{s.summary}</span>
          {explain && <Reasons m={m} />}
        </span>
        <span className="svc-row-tags">
          {s.service_type === 'information' && <Pill tone="neutral">{t('resident.svc.information')}</Pill>}
          {s.state === 'unavailable' && <Pill tone="warn">{t('resident.svc.unavailable')}</Pill>}
        </span>
        <Icon.chevronRight size={18} />
      </Link>
    </li>
  );
}

function ReportLink({ categoryIds }: { categoryIds: string[] }) {
  const { t } = useI18n();
  const ref = useRef$();
  const first = categoryIds.map((id) => ref.catCode(id)).find(Boolean);
  return <Link className="btn" to={`/app/report${first ? `?category=${encodeURIComponent(first)}` : ''}`}>{t('resident.svc.reportThis')}</Link>;
}

/** Detail for one service. Opens from a result or from a direct link; shows only data the server holds. */
function ServiceDetail({ code, fromResults, onClose }: { code: string | null; fromResults: ServiceMatch[]; onClose: () => void }) {
  const { t, fmt } = useI18n();
  const ref = useRef$();
  const known = code ? fromResults.find((m) => m.service.code === code)?.service : undefined;
  // A direct link may name a service that is not in the current results: look it up in the full directory.
  const lookup = useResource<ServiceSearch>(code && !known ? `svc-detail:${code}` : null,
    (signal) => api<ServiceSearch>('/services?limit=50', { signal }));
  const s = known ?? lookup.data?.items.find((m) => m.service.code === code)?.service;
  const missing = Boolean(code && !known && lookup.data && !s);

  return (
    <Dialog open={Boolean(code)} onClose={onClose} title={s?.name ?? (missing ? t('error.notFound') : t('common.loading'))} size="lg">
      {lookup.error != null && !s && <ErrorState error={lookup.error} onRetry={lookup.reload} />}
      {!s && !lookup.error && !missing && <Skeleton rows={3} />}
      {missing && <p>{t('resident.svc.notFound')}</p>}
      {s && (
        <div className="svc-detail">
          {s.is_demo && <p className="notice notice-warn"><Icon.info size={16} />{t('resident.svc.demoService')}</p>}
          <p className="svc-detail-summary">{s.summary}</p>
          {s.state === 'unavailable' && <p className="notice notice-warn"><Icon.alert size={16} />{t('resident.svc.unavailableLong')}</p>}
          {s.instructions && (
            <section>
              <h3>{t('resident.svc.howTo')}</h3>
              <p className="pre">{s.instructions}</p>
            </section>
          )}
          {s.category_ids.length > 0 && (
            <section>
              <h3>{t('resident.svc.issueTypes')}</h3>
              <ul className="plain issue-types">
                {s.category_ids.map((id) => <li key={id}><CategoryMark code={ref.catCode(id)} label={ref.catName(id)} /></li>)}
              </ul>
            </section>
          )}
          <section>
            <h3>{t('resident.svc.contact')}</h3>
            {s.public_contact || s.operating_hours || s.eligibility ? (
              <dl className="kv">
                {s.public_contact && <><dt>{t('resident.svc.contactLabel')}</dt><dd>{s.public_contact}</dd></>}
                {s.operating_hours && <><dt>{t('resident.svc.hours')}</dt><dd>{s.operating_hours}</dd></>}
                {s.eligibility && <><dt>{t('resident.svc.eligibility')}</dt><dd>{s.eligibility}</dd></>}
              </dl>
            ) : <p className="meta">{t('resident.svc.noContact')}</p>}
          </section>
          {s.department_ids.length > 0 && ref.departments.length > 0 && (
            <section>
              <h3>{t('resident.svc.departments')}</h3>
              <p>{s.department_ids.map((id) => ref.deptName(id)).join(', ')}</p>
            </section>
          )}
          {s.last_reviewed_at && <p className="meta">{t('resident.svc.reviewed', { date: fmt.date(s.last_reviewed_at) })}</p>}
          <div className="actions">
            {s.service_type === 'complaint' && <ReportLink categoryIds={s.category_ids} />}
            <button type="button" className="btn btn-quiet" onClick={onClose}>{t('common.close')}</button>
          </div>
        </div>
      )}
    </Dialog>
  );
}
