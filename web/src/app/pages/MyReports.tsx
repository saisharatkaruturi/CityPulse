import '../../styles/resident.css';

import { useEffect, useState, type FormEvent } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { api, qs, type ComplaintItem, type Page } from '../../api';
import { Icon } from '../../components/Icon';
import {
  CategoryMark, EmptyState, ErrorState, PageHeader, RefreshControl, Skeleton, StaleNotice, StatusPill,
} from '../../components/ui';
import { useI18n } from '../../i18n';
import { OPEN } from '../../lib';
import { useResource } from '../../lib/useResource';
import { useRef$ } from '../refdata';

const PAGE_SIZE = 25;

/** Screen question: which of my reports needs something from me? */
export default function MyReports() {
  const { t, plural, fmt } = useI18n();
  const ref = useRef$();
  const [params, setParams] = useSearchParams();
  const q = params.get('q') ?? '';
  const page = Math.max(1, Number(params.get('page')) || 1);
  const [draft, setDraft] = useState(q);
  useEffect(() => setDraft(q), [q]);

  const key = `mine?q=${q}&page=${page}`;
  const res = useResource<Page<ComplaintItem>>(key, (signal) =>
    api<Page<ComplaintItem>>(`/complaints${qs({ mine: true, q: q || undefined, page, page_size: PAGE_SIZE, sort: '-created_at' })}`, { signal }));
  const data = res.data;

  const set = (next: Record<string, string | null>) => setParams((p) => {
    for (const [k, v] of Object.entries(next)) { if (v) p.set(k, v); else p.delete(k); }
    return p;
  });
  const onSearch = (e: FormEvent) => { e.preventDefault(); set({ q: draft.trim() || null, page: null }); };

  // The finding is computed from the rows on this page and says so when the list is paginated.
  const items = data?.items ?? [];
  const waiting = items.filter((c) => c.status === 'awaiting_resident').length;
  const toConfirm = items.filter((c) => c.status === 'resolved').length;
  const open = items.filter((c) => OPEN.includes(c.status)).length;
  const finding = !data ? t('common.loading')
    : data.total === 0 ? (q ? t('resident.my.noMatch', { q }) : t('resident.my.none'))
    : [
      waiting ? plural('resident.my.needReply', waiting) : null,
      toConfirm ? plural('resident.my.toConfirm', toConfirm) : null,
      plural('resident.my.open', open),
    ].filter(Boolean).join(' · ');

  return (
    <>
      <PageHeader
        title={t('nav.myReports')}
        sub={finding}
        actions={(
          <>
            <RefreshControl onRefresh={res.reload} refreshing={res.refreshing} updatedAt={res.updatedAt} />
            <Link className="btn btn-primary" to="/app/report"><Icon.plus size={18} />{t('nav.report')}</Link>
          </>
        )}
      />

      <form className="search-row" role="search" onSubmit={onSearch}>
        <label htmlFor="my-q" className="visually-hidden">{t('resident.my.searchLabel')}</label>
        <input id="my-q" className="input" type="search" value={draft} onChange={(e) => setDraft(e.target.value)}
          placeholder={t('resident.my.searchPh')} maxLength={100} />
        <button className="btn" type="submit"><Icon.search size={18} />{t('common.search')}</button>
        {q && <button className="btn btn-quiet" type="button" onClick={() => set({ q: null, page: null })}>{t('common.clear')}</button>}
      </form>

      {res.error != null && data && <StaleNotice error={res.error} onRetry={res.reload} />}
      {res.error != null && !data && <ErrorState error={res.error} onRetry={res.reload} title={t('resident.my.loadError')} />}
      {res.loading && !data && <Skeleton rows={5} height={44} />}

      {data && data.total === 0 && (
        q ? <EmptyState title={t('resident.my.noMatch', { q })} action={<button className="btn" onClick={() => set({ q: null })}>{t('common.clear')}</button>} />
          : (
            <EmptyState title={t('resident.my.emptyTitle')} action={<Link className="btn btn-primary" to="/app/report">{t('nav.report')}</Link>}>
              <p>{t('resident.my.emptyBody')}</p>
            </EmptyState>
          )
      )}

      {data && data.total > 0 && (
        <>
          <div className="table-wrap">
            <table className="data stack-table">
              <caption className="visually-hidden">{t('nav.myReports')}</caption>
              <thead>
                <tr>
                  <th scope="col">{t('resident.my.colReport')}</th>
                  <th scope="col">{t('resident.my.colKind')}</th>
                  <th scope="col">{t('resident.my.colStatus')}</th>
                  <th scope="col" className="num">{t('resident.my.colSent')}</th>
                </tr>
              </thead>
              <tbody>
                {items.map((c) => (
                  <tr key={c.id}>
                    <td>
                      <Link className="row-title" to={`/app/reports/${c.id}`}>{c.title}</Link>
                      <span className="meta ref num">{c.reference}</span>
                    </td>
                    <td data-label={t('resident.my.colKind')}><CategoryMark code={ref.catCode(c.category_id)} label={ref.catName(c.category_id)} /></td>
                    <td data-label={t('resident.my.colStatus')}><StatusPill status={c.status} /></td>
                    <td data-label={t('resident.my.colSent')} className="num">{fmt.date(c.created_at)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <div className="pager">
            <span className="meta num">{t('common.pageOf', {
              from: (data.page - 1) * data.page_size + 1, to: Math.min(data.page * data.page_size, data.total), total: data.total,
            })}</span>
            {data.total > data.page_size && (
              <span className="actions">
                <button className="btn btn-sm" disabled={page <= 1} onClick={() => set({ page: String(page - 1) })}>{t('common.previous')}</button>
                <button className="btn btn-sm" disabled={page * data.page_size >= data.total} onClick={() => set({ page: String(page + 1) })}>{t('common.next')}</button>
              </span>
            )}
          </div>
          <p className="meta honest-note">{t('resident.my.honest')}</p>
        </>
      )}
    </>
  );
}
