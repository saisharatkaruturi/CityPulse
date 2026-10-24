import { Link, Navigate } from 'react-router-dom';
import { useAuth } from '../auth';
import { useI18n } from '../i18n';
import { canAccess, homeFor, type RouteKey } from '../roles';

/**
 * Client-side route guard. A direct URL to a page outside the role shows a plain explanation instead of
 * the page. The server still refuses the data on its own, so this is convenience, not the protection.
 */
export function RequireRoute({ route, children }: { route: RouteKey; children: JSX.Element }) {
  const { experience, roleTitle, loading } = useAuth();
  const { t, tk } = useI18n();
  if (loading) return null;
  if (canAccess(route, experience)) return children;
  return (
    <section className="state state-empty" aria-labelledby="forbidden-h">
      <h1 id="forbidden-h" className="state-title">{t('guard.forbiddenTitle')}</h1>
      <p className="state-body">{t('guard.forbiddenBody', { role: tk(roleTitle.key) })}</p>
      <Link className="btn btn-primary" to={homeFor(experience)}>{t('guard.goHome')}</Link>
    </section>
  );
}

export function NotFound() {
  const { t } = useI18n();
  return (
    <section className="state state-empty" aria-labelledby="nf-h">
      <h1 id="nf-h" className="state-title">{t('guard.notFoundTitle')}</h1>
      <p className="state-body">{t('guard.notFoundBody')}</p>
      <Link className="btn btn-primary" to="/">{t('app.home')}</Link>
    </section>
  );
}

/** /app index: residents see their reports; staff go to their queue. */
export function AppHome({ resident }: { resident: JSX.Element }) {
  const { experience, loading } = useAuth();
  if (loading) return null;
  if (experience !== 'resident') return <Navigate to="/app/queue" replace />;
  return resident;
}
