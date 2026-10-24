import '../styles/app.css';

import { useEffect, useState } from 'react';
import { Link, Navigate, NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom';
import { api, type ComplaintItem, type Notification, type Page } from '../api';
import { useAuth } from '../auth';
import { Icon } from '../components/Icon';
import { Wordmark } from '../components/Logo';
import { Copyright, DemoBadge, LanguageSwitch } from '../components/ui';
import { useI18n } from '../i18n';
import { navFor, type NavItem } from '../roles';
import { RefDataProvider } from './refdata';

function NavRow({ item, count }: { item: NavItem; count: number }) {
  const { t, plural } = useI18n();
  const I = Icon[item.icon];
  const countLabel = item.count === 'unread' ? plural('nav.unread', count) : plural('nav.waiting', count);
  return (
    <li>
      <NavLink to={item.to} end={item.end} className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}>
        <I />
        <span>{t(item.label)}</span>
        {count > 0 && <span className="count num" aria-label={countLabel}>{count}</span>}
      </NavLink>
    </li>
  );
}

export default function Shell() {
  const { user, loading, signOut, experience, roleTitle } = useAuth();
  const { t, tk } = useI18n();
  const [open, setOpen] = useState(false);
  const [unread, setUnread] = useState(0);
  const [waiting, setWaiting] = useState(0);
  const loc = useLocation();
  const nav = useNavigate();

  useEffect(() => setOpen(false), [loc.pathname]);
  useEffect(() => {
    if (!open) return;
    const h = (e: KeyboardEvent) => { if (e.key === 'Escape') setOpen(false); };
    window.addEventListener('keydown', h);
    return () => window.removeEventListener('keydown', h);
  }, [open]);

  // Counts are refetched on navigation so they follow the work; each is scoped by the server to this user.
  useEffect(() => {
    if (!user) return;
    const ctrl = new AbortController();
    api<Page<Notification>>('/notifications?unread_only=true&page_size=1', { signal: ctrl.signal })
      .then((p) => setUnread(p.total)).catch(() => undefined);
    if (['supervisor', 'triage', 'admin'].includes(experience))
      api<Page<ComplaintItem>>('/complaints?unassigned=true&status=submitted&status=under_review&status=reopened&page_size=1', { signal: ctrl.signal })
        .then((p) => setWaiting(p.total)).catch(() => undefined);
    return () => ctrl.abort();
  }, [user, experience, loc.pathname]);

  if (loading) return <div className="canvas" aria-busy="true" />;
  if (!user) return <Navigate to={`/signin?next=${encodeURIComponent(loc.pathname + loc.search)}`} replace />;

  const role = roleTitle.dept ? t('role.ofDept', { role: tk(roleTitle.key), dept: tk(`dept.${roleTitle.dept}`) }) : tk(roleTitle.key);
  const items = navFor(experience);

  return (
    // keyed by user: switching accounts remounts everything below, dropping the previous role's data
    <RefDataProvider key={user.id}>
      <a className="skip-link" href="#main">{t('app.skip')}</a>
      <div className="app aurora">
        {open && <button className="scrim" aria-label={t('nav.closeMenu')} onClick={() => setOpen(false)} />}
        <aside id="app-nav" className={`sidebar ${open ? 'open' : ''}`} aria-label={t('nav.main')}>
          <div className="actions" style={{ justifyContent: 'space-between', flexWrap: 'nowrap' }}>
            <Link to="/" aria-label={t('app.home')} style={{ textDecoration: 'none' }}><Wordmark compact /></Link>
            <button className="icon-btn sidebar-close" onClick={() => setOpen(false)} aria-label={t('nav.closeMenu')}><Icon.close /></button>
          </div>
          <div className="role-chip">
            <span className="role-name">{role}</span>
            <span className="role-user">{t('nav.signedInAs', { name: user.display_name })}</span>
          </div>
          <nav aria-label={t('nav.main')}>
            <ul className="nav-list">
              {items.map((i) => (
                <NavRow key={i.key} item={i} count={i.count === 'unread' ? unread : i.count === 'waiting' ? waiting : 0} />
              ))}
            </ul>
          </nav>
          <div className="sidebar-foot">
            <LanguageSwitch />
            <DemoBadge />
            <button className="btn btn-quiet" onClick={() => signOut().then(() => nav('/', { replace: true }))}>
              <Icon.logout /> {t('nav.signOut')}
            </button>
          </div>
        </aside>
        <div className="main">
          <header className="topbar">
            <button className="icon-btn" onClick={() => setOpen(true)} aria-label={t('nav.openMenu')} aria-expanded={open} aria-controls="app-nav">
              <Icon.menu />
            </button>
            <Link to="/" aria-label={t('app.home')} style={{ textDecoration: 'none' }}><Wordmark compact size={28} /></Link>
            <span className="topbar-role">{role}</span>
          </header>
          <main className="canvas" id="main" tabIndex={-1}>
            <Outlet />
          </main>
          <footer className="app-foot">
            <Copyright />
            <DemoBadge withNote />
          </footer>
        </div>
      </div>
    </RefDataProvider>
  );
}
