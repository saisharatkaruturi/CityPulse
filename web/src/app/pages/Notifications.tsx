import '../../styles/resident.css';

import { useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import { api, qs, type Notification, type Page } from '../../api';
import { Icon } from '../../components/Icon';
import { EmptyState, ErrorState, PageHeader, RefreshControl, Skeleton, StaleNotice } from '../../components/ui';
import { useI18n } from '../../i18n';
import { errorKey } from '../../lib';
import { useResource } from '../../lib/useResource';
import { groupByDay } from '../resident/helpers';

const PAGE_SIZE = 30;

/** Screen question: what changed on my reports, and what have I not seen yet? */
export default function Notifications() {
  const { t, plural } = useI18n();
  const [params, setParams] = useSearchParams();
  const page = Math.max(1, Number(params.get('page')) || 1);
  const res = useResource<Page<Notification>>(`notif?page=${page}`, (signal) =>
    api<Page<Notification>>(`/notifications${qs({ page, page_size: PAGE_SIZE })}`, { signal }));
  // Total unread across all pages comes from the server, not from the rows on screen.
  const unreadRes = useResource<Page<Notification>>(`notif-unread?u=${res.updatedAt?.getTime() ?? 0}`, (signal) =>
    api<Page<Notification>>('/notifications?unread_only=true&page_size=1', { signal }));
  const [busyId, setBusyId] = useState<string | null>(null);
  const [allBusy, setAllBusy] = useState(false);
  const [actionError, setActionError] = useState<string | null>(null);

  const data = res.data;
  const unread = unreadRes.data?.total ?? data?.items.filter((n) => !n.read_at).length ?? 0;
  const groups = data ? groupByDay(data.items) : null;
  const showGroups = Boolean(groups && groups.today.length && groups.earlier.length);

  async function markRead(n: Notification) {
    if (n.read_at || busyId) return;
    setBusyId(n.id);
    setActionError(null);
    try {
      const updated = await api<Notification>(`/notifications/${n.id}/read`, { method: 'PATCH' });
      if (data) res.setData({ ...data, items: data.items.map((x) => (x.id === n.id ? updated : x)) });
      void unreadRes.reload();
    } catch (e) {
      const k = errorKey(e);
      setActionError(t(k.key, k.vars));
    } finally {
      setBusyId(null);
    }
  }

  async function markAll() {
    setAllBusy(true);
    setActionError(null);
    try {
      await api<{ updated: number }>('/notifications/read-all', { method: 'POST' });
      await res.reload();
    } catch (e) {
      const k = errorKey(e);
      setActionError(t(k.key, k.vars));
    } finally {
      setAllBusy(false);
    }
  }

  const list = (items: Notification[]) => (
    <ul className="notif-list">
      {items.map((n) => <Item key={n.id} n={n} busy={busyId === n.id} onRead={() => markRead(n)} />)}
    </ul>
  );

  return (
    <>
      <PageHeader
        title={t('nav.notifications')}
        sub={!data ? t('common.loading') : unread ? plural('nav.unread', unread) : t('resident.notif.allRead')}
        actions={(
          <>
            <RefreshControl onRefresh={res.reload} refreshing={res.refreshing} updatedAt={res.updatedAt} />
            {unread > 0 && (
              <button type="button" className="btn" onClick={markAll} disabled={allBusy} aria-busy={allBusy}>
                <Icon.check size={18} />{allBusy ? t('common.saving') : t('resident.notif.markAll')}
              </button>
            )}
          </>
        )}
      />
      {actionError && <p className="notice notice-bad" role="alert"><Icon.alert size={16} />{actionError}</p>}
      {res.error != null && data && <StaleNotice error={res.error} onRetry={res.reload} />}
      {res.error != null && !data && <ErrorState error={res.error} onRetry={res.reload} title={t('resident.notif.loadError')} />}
      {res.loading && !data && <Skeleton rows={4} height={72} />}

      {data && data.total === 0 && (
        <EmptyState title={t('resident.notif.emptyTitle')}><p>{t('resident.notif.emptyBody')}</p></EmptyState>
      )}

      {groups && data && data.total > 0 && (
        showGroups ? (
          <>
            <section aria-labelledby="n-today"><h2 id="n-today" className="notif-group">{t('resident.notif.today')}</h2>{list(groups.today)}</section>
            <section aria-labelledby="n-earlier"><h2 id="n-earlier" className="notif-group">{t('resident.notif.earlier')}</h2>{list(groups.earlier)}</section>
          </>
        ) : list(data.items)
      )}

      {data && data.total > data.page_size && (
        <div className="pager">
          <span className="meta num">{t('common.pageOf', {
            from: (data.page - 1) * data.page_size + 1, to: Math.min(data.page * data.page_size, data.total), total: data.total,
          })}</span>
          <span className="actions">
            <button className="btn btn-sm" disabled={page <= 1} onClick={() => setParams({ page: String(page - 1) })}>{t('common.previous')}</button>
            <button className="btn btn-sm" disabled={page * data.page_size >= data.total} onClick={() => setParams({ page: String(page + 1) })}>{t('common.next')}</button>
          </span>
        </div>
      )}
    </>
  );
}

function Item({ n, busy, onRead }: { n: Notification; busy: boolean; onRead: () => void }) {
  const { t, fmt } = useI18n();
  const unread = !n.read_at;
  return (
    <li className={`notif${unread ? ' is-unread' : ''}`}>
      <span className="notif-marker" aria-hidden="true">
        <svg viewBox="0 0 12 12" width="12" height="12">
          {unread ? <circle cx="6" cy="6" r="5" fill="currentColor" /> : <circle cx="6" cy="6" r="4.25" fill="none" stroke="currentColor" strokeWidth="1.5" />}
        </svg>
      </span>
      <div className="notif-body">
        <p className="notif-head">
          <span className="notif-state">{unread ? t('resident.notif.unread') : t('resident.notif.read')}</span>
          <time dateTime={n.created_at} className="meta">{fmt.dateTime(n.created_at)}</time>
        </p>
        <p className="notif-title">{n.title}</p>
        <p className="notif-text">{n.body}</p>
        {n.complaint_reference && <p className="meta num">{t('resident.notif.reference', { ref: n.complaint_reference })}</p>}
      </div>
      <div className="notif-actions">
        {n.complaint_id && (
          <Link className="btn btn-sm" to={`/app/reports/${n.complaint_id}`} onClick={() => { if (unread) onRead(); }}>
            {t('resident.notif.open')}
          </Link>
        )}
        {unread && (
          <button type="button" className="btn btn-sm btn-quiet" onClick={onRead} disabled={busy} aria-busy={busy}>
            {busy ? t('common.saving') : t('resident.notif.markRead')}
          </button>
        )}
      </div>
    </li>
  );
}
