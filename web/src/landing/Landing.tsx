import '../styles/app.css';
import '../styles/landing.css';

import { useEffect, useId, useRef, useState, type KeyboardEvent, type PointerEvent, type RefObject } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { api, qs, type Category, type ServiceSearch, type Suggestion } from '../api';
import { useAuth } from '../auth';
import { FamilyIcon, Icon } from '../components/Icon';
import { LogoMark, Wordmark } from '../components/Logo';
import { Copyright, DemoBadge, LanguageSwitch, Pill } from '../components/ui';
import { useI18n } from '../i18n';
import type { Family } from '../lib';
import { homeFor } from '../roles';
import { groupCategories, matchReasons, reportTarget } from './helpers';
import { Hero3D } from './Hero3D';
import { Backdrop } from '../components/Backdrop';

const prefersReducedMotion = () =>
  typeof window !== 'undefined' && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

/**
 * Section entrances: content is visible by default; only when script runs and motion is allowed do the
 * parts start lowered and rise as their section enters. Observers are disconnected on unmount.
 */
function useReveal(root: RefObject<HTMLElement>) {
  useEffect(() => {
    const el = root.current;
    if (!el || prefersReducedMotion() || !('IntersectionObserver' in window)) return;
    el.classList.add('motion-ok');
    const targets = Array.from(el.querySelectorAll<HTMLElement>('[data-reveal]'));
    const io = new IntersectionObserver((entries) => {
      entries.forEach((e) => {
        if (!e.isIntersecting) return;
        e.target.classList.add('is-in');
        io.unobserve(e.target);
      });
    }, { rootMargin: '0px 0px -10% 0px' });
    targets.forEach((t) => {
      const section = t.closest('section, footer');
      const i = section ? Array.from(section.querySelectorAll('[data-reveal]')).indexOf(t) : 0;
      t.style.setProperty('--reveal-delay', `${Math.min(i, 4) * 80}ms`);
      io.observe(t);
    });
    return () => io.disconnect();
  }, [root]);
}

// ---- header -------------------------------------------------------------------------------------

function Header() {
  const { t } = useI18n();
  const { user, isStaff, experience } = useAuth();
  return (
    <header className="l-header-wrap"><div className="l-header glass l-frame-inner">
      <Link to="/" className="l-brand" aria-label={t('app.home')}><Wordmark /></Link>
      <nav aria-label={t('nav.main')} className="l-nav">
        <a href="#report">{t('landing.nav.report')}</a>
        <a href="#services">{t('landing.nav.services')}</a>
        <a href="#faq">{t('landing.nav.faq')}</a>
        {user ? <Link to={homeFor(experience)}>{t('landing.nav.openWork')}</Link> : <Link to="/signin">{t('nav.signIn')}</Link>}
      </nav>
      <div className="l-header-end">
        <LanguageSwitch />
        <Link className="btn btn-primary l-header-cta" to={reportTarget(isStaff)}>
          {isStaff ? t('landing.nav.openQueue') : t('nav.report')}
        </Link>
      </div>
    </div></header>
  );
}

// ---- hero and the live router -------------------------------------------------------------------

function Router() {
  const { t } = useI18n();
  const id = useId();
  const [text, setText] = useState('');
  const [result, setResult] = useState<Suggestion | null>(null);
  const [state, setState] = useState<'idle' | 'loading' | 'error'>('idle');

  useEffect(() => {
    const q = text.trim();
    if (q.length < 6) {
      setResult(null);
      setState('idle');
      return;
    }
    setState('loading');
    const ctrl = new AbortController();
    const timer = window.setTimeout(() => {
      api<Suggestion>('/routing/suggest', { body: { description: q }, signal: ctrl.signal })
        .then((r) => { setResult(r); setState('idle'); })
        .catch((e) => { if (!ctrl.signal.aborted && !(e instanceof DOMException)) setState('error'); });
    }, 400);
    return () => { window.clearTimeout(timer); ctrl.abort(); };
  }, [text]);

  const routed = result && result.outcome === 'routed' && result.category && result.department_name;
  return (
    <form className="router glass" role="search" onSubmit={(e) => e.preventDefault()}>
      <label htmlFor={`${id}-q`} className="router-label">{t('landing.router.label')}</label>
      <div className="router-field">
        <Icon.search />
        <input id={`${id}-q`} value={text} onChange={(e) => setText(e.target.value)} placeholder={t('landing.router.placeholder')}
          autoComplete="off" maxLength={300} aria-describedby={`${id}-out ${id}-note`} />
      </div>
      <div id={`${id}-out`} className={`router-out ${result && state === 'idle' ? 'has-result' : ''}`} aria-live="polite">
        {state === 'error' && <p>{t('landing.router.error')}</p>}
        {state === 'loading' && <p className="meta">{t('landing.router.checking')}</p>}
        {state === 'idle' && !result && <p className="meta">{t('landing.router.idle')}</p>}
        {state === 'idle' && result && (
          <p className="router-answer">
            <span className={`router-dot ${routed ? 'is-routed' : ''}`} aria-hidden="true" />
            <span>
              {t('landing.router.routedLead')}{' '}
              <strong>
                {routed
                  ? t('landing.router.routed', { dept: result.department_name ?? '', category: result.category!.label })
                  : t('landing.router.fallback')}
              </strong>
            </span>
          </p>
        )}
      </div>
      <p id={`${id}-note`} className="router-note">{t('landing.router.note')}</p>
    </form>
  );
}

function Hero() {
  const { t } = useI18n();
  const { isStaff } = useAuth();
  return (
    <section className="hero l-frame" aria-labelledby="hero-h">
      <h1 id="hero-h" className="hero-title">
        <span className="mask"><span className="line">{t('landing.hero.line1')}</span></span>{' '}
        <span className="mask"><span className="line line-2"><span className="hl">{t('landing.hero.line2')}</span></span></span>
      </h1>
      <div className="hero-top">
        <div className="hero-copy-col">
          <div className="hero-copy">
            <p className="hero-lead">{t('landing.hero.lead')}</p>
            <div className="actions hero-actions">
              <Link className="btn btn-signal btn-lg" to={reportTarget(isStaff)}>
                {isStaff ? t('landing.cta.staff') : t('landing.hero.primary')} <Icon.arrowRight />
              </Link>
              <a className="btn btn-lg btn-glass" href="#services">{t('landing.hero.secondary')}</a>
              <a className="text-link" href="#how">{t('landing.hero.how')}</a>
            </div>
          </div>
        </div>
        <Hero3D />
      </div>
      <Router />
    </section>
  );
}

// ---- how it works: the slip ---------------------------------------------------------------------

function Slip() {
  const { t } = useI18n();
  const groups: { head: Parameters<typeof t>[0]; rows: [Parameters<typeof t>[0], Parameters<typeof t>[0]][] }[] = [
    { head: 'landing.how.groupYou', rows: [['landing.how.submitted', 'landing.how.submittedWho'], ['landing.how.routed', 'landing.how.routedWho']] },
    { head: 'landing.how.groupStaff', rows: [['landing.how.picked', 'landing.how.pickedWho'], ['landing.how.question', 'landing.how.questionWho']] },
    { head: 'landing.how.groupEnd', rows: [['landing.how.resolved', 'landing.how.resolvedWho'], ['landing.how.confirm', 'landing.how.confirmWho']] },
  ];
  return (
    <section id="how" className="how l-frame" aria-labelledby="how-h">
      <div className="how-text" data-reveal>
        <h2 id="how-h" className="l-h2">{t('landing.how.title')}</h2>
        <p className="l-lead">{t('landing.how.lead')}</p>
        <p className="how-not"><Icon.info size={18} /><span>{t('landing.how.notOnSlip')}</span></p>
      </div>
      <div className="slip-wrap" data-reveal>
        <div className="slip" role="group" aria-label={t('landing.how.slip')}>
          <span className="slip-track" aria-hidden="true"><span className="slip-token" /></span>
          <p className="slip-title"><LogoMark size={22} /> {t('landing.how.slip')}</p>
          {groups.map((g) => (
            <div key={g.head} className="slip-group">
              <h3>{t(g.head)}</h3>
              <ul>
                {g.rows.map(([what, who]) => (
                  <li key={what}><span>{t(what)}</span><span className="leader" aria-hidden="true" /><span className="slip-who">{t(who)}</span></li>
                ))}
              </ul>
            </div>
          ))}
          <p className="slip-total"><span>{t('landing.how.total')}</span><span>{t('landing.how.totalWho')}</span></p>
        </div>
      </div>
    </section>
  );
}

// ---- your city: the drawn desk and its services -------------------------------------------------

const NODES: { family: Family; x: number; y: number; path: string }[] = [
  { family: 'roads', x: 150, y: 110, path: 'M150 110 H340 V250 H462' },
  { family: 'water', x: 860, y: 110, path: 'M860 110 H660 V250 H538' },
  { family: 'electrical', x: 620, y: 40, path: 'M620 40 V180 H520 V222' },
  { family: 'drainage', x: 150, y: 420, path: 'M150 420 H340 V290 H462' },
  { family: 'lighting', x: 860, y: 420, path: 'M860 420 H660 V290 H538' },
  { family: 'sanitation', x: 380, y: 490, path: 'M380 490 V420 H500 V298' },
];

function CityMap() {
  const { t } = useI18n();
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    if (prefersReducedMotion() || !('IntersectionObserver' in window)) return;
    el.classList.add('will-draw');
    const io = new IntersectionObserver(([e]) => {
      if (e.isIntersecting) { el.classList.add('is-drawn'); io.disconnect(); }
    }, { threshold: 0.35 });
    io.observe(el);
    return () => io.disconnect();
  }, []);
  return (
    <section id="city" className="city l-frame" aria-labelledby="city-h">
      <div className="city-text" data-reveal>
        <h2 id="city-h" className="l-h2">{t('landing.city.title')}</h2>
        <p className="l-lead">{t('landing.city.lead')}</p>
        <ul className="city-list" aria-label={t('landing.city.listLabel')}>
          {NODES.map((n) => {
            const I = FamilyIcon[n.family];
            return <li key={n.family} className={`cat cat-${n.family}`}><span className="cat-mark"><I size={16} /></span>{t(`family.${n.family}` as Parameters<typeof t>[0])}</li>;
          })}
        </ul>
      </div>
      <figure className="city-figure glass" ref={ref}>
        <svg viewBox="0 0 1000 530" className="city-svg" aria-hidden="true" focusable="false">
          <g className="grid-far">
            {Array.from({ length: 26 }, (_, i) => <path key={`v${i}`} d={`M${i * 40} 0V530`} />)}
            {Array.from({ length: 14 }, (_, i) => <path key={`h${i}`} d={`M0 ${i * 40}H1000`} />)}
          </g>
          <g className="grid-near">
            <path d="M0 110H1000M0 250H1000M0 290H1000M0 420H1000M150 0V530M340 0V530M500 0V530M660 0V530M860 0V530" />
          </g>
          <g className="blocks">
            <rect x="180" y="140" width="130" height="80" rx="6" /><rect x="690" y="140" width="140" height="80" rx="6" />
            <rect x="180" y="320" width="130" height="70" rx="6" /><rect x="690" y="320" width="140" height="70" rx="6" />
            <rect x="370" y="20" width="100" height="60" rx="6" /><rect x="530" y="450" width="100" height="60" rx="6" />
          </g>
          {NODES.map((n, i) => (
            <path key={n.family} d={n.path} pathLength={1} className={`route route-${n.family}`} style={{ transitionDelay: `${i * 140}ms` }} />
          ))}
          {NODES.map((n, i) => (
            <g key={`f-${n.family}`} className={`flow flow-${n.family}`}>
              <circle r="9" className="flow-glow" />
              <circle r="5" className="flow-dot" />
              <animateMotion dur={`${3.2 + (i % 3) * 0.5}s`} begin={`${i * 0.45}s`} repeatCount="indefinite" path={n.path} />
            </g>
          ))}
          <g className="desk">
            <rect x="460" y="220" width="80" height="80" rx="14" />
            <path d="M478 270c8 0 7-16 16-17 6-1 9-5 12-10" fill="none" stroke="#f6f3ed" strokeWidth="4" strokeLinecap="round" />
            <circle cx="518" cy="240" r="7" fill="#e8902f" />
          </g>
          {NODES.map((n, i) => {
            const I = FamilyIcon[n.family];
            return (
              <g key={n.family} className={`node node-${n.family}`} style={{ transitionDelay: `${300 + i * 140}ms` }}>
                <circle cx={n.x} cy={n.y} r="24" />
                <g transform={`translate(${n.x - 11} ${n.y - 11})`} style={{ color: '#ffffff' }}><I size={22} /></g>
              </g>
            );
          })}
        </svg>
        <div className="city-labels" aria-hidden="true">
          {NODES.map((n) => (
            <span key={n.family} style={{ left: `${(n.x / 1000) * 100}%`, top: `${(n.y / 530) * 100}%` }}
              className={n.y > 300 ? 'below' : 'above'}>{t(`family.${n.family}` as Parameters<typeof t>[0])}</span>
          ))}
          <span className="desk-label" style={{ left: '50%', top: `${(310 / 530) * 100}%` }}>{t('landing.city.desk')}</span>
        </div>
        <figcaption>{t('landing.city.caption')}</figcaption>
      </figure>
    </section>
  );
}

// ---- what can you report ------------------------------------------------------------------------

/** 3D tilt with a glare that follows the pointer, for the category cards. Fine pointers only; off under
 *  reduced motion. One delegated listener on the grid. */
const canTilt = () => typeof window !== 'undefined' && window.matchMedia('(hover: hover) and (pointer: fine)').matches && !prefersReducedMotion();
function tilt(e: PointerEvent<HTMLElement>) {
  if (!canTilt()) return;
  const row = (e.target as HTMLElement).closest<HTMLElement>('.poster-row');
  if (!row) return;
  const r = row.getBoundingClientRect();
  const px = (e.clientX - r.left) / r.width, py = (e.clientY - r.top) / r.height;
  row.style.setProperty('--ry', `${(px - 0.5) * 10}deg`);
  row.style.setProperty('--rx', `${(0.5 - py) * 10}deg`);
  row.style.setProperty('--gx', `${px * 100}%`);
  row.style.setProperty('--gy', `${py * 100}%`);
  row.classList.add('is-tilting');
}
function reset(row: HTMLElement) {
  row.classList.remove('is-tilting');
  row.style.removeProperty('--rx');
  row.style.removeProperty('--ry');
}
function untilt(e: PointerEvent<HTMLElement>) {
  e.currentTarget.querySelectorAll<HTMLElement>('.poster-row.is-tilting').forEach(reset);
}
function untiltRow(e: PointerEvent<HTMLElement>) {
  const row = (e.target as HTMLElement).closest<HTMLElement>('.poster-row');
  const to = e.relatedTarget as HTMLElement | null;
  if (row && !(to && row.contains(to))) reset(row);
}

function ReportList() {
  const { t, tk, locale } = useI18n();
  const { isStaff } = useAuth();
  const [cats, setCats] = useState<Category[] | null>(null);
  const [failed, setFailed] = useState(false);
  useEffect(() => {
    const ctrl = new AbortController();
    api<Category[]>('/categories', { signal: ctrl.signal })
      .then((c) => { setCats(c); setFailed(false); })
      .catch(() => { if (!ctrl.signal.aborted) setFailed(true); });
    return () => ctrl.abort();
  }, [locale]);
  const groups = groupCategories(cats);
  return (
    <section id="report" className="report l-frame" aria-labelledby="report-h">
      <div className="report-head" data-reveal>
        <h2 id="report-h" className="l-h2">{t('landing.report.title')}</h2>
        <p className="l-lead">{t('landing.report.lead')}</p>
        {failed && <p className="notice notice-warn"><Icon.info size={16} />{t('landing.report.offline')}</p>}
        {isStaff && <p className="notice notice-info"><Icon.info size={16} />{t('landing.report.staffNote')}</p>}
      </div>
      <div className="report-groups" onPointerMove={tilt} onPointerLeave={untilt} onPointerOut={untiltRow}>
        {groups.map((g) => {
          const I = FamilyIcon[g.family];
          return (
            <div key={g.family} className={`report-group fam-${g.family}`} data-reveal>
              <h3 className="report-family"><span className="fam-mark"><I size={18} /></span>{tk(`family.${g.family}`)}</h3>
              <ul className="poster">
                {g.rows.map((r) => (
                  <li key={r.code}>
                    <Link to={reportTarget(isStaff, r.code)} className="poster-row">
                      <span className="poster-name">{r.label ?? tk(`landing.cat.${r.code}`)}</span>
                      <span className="poster-desc">{tk(`landing.desc.${r.code}`) === humanLast(r.code) ? t('landing.desc.default') : tk(`landing.desc.${r.code}`)}</span>
                      <span className="poster-go"><span className="visually-hidden">{t('landing.report.start')}: </span><Icon.arrowRight /></span>
                    </Link>
                  </li>
                ))}
              </ul>
              {g.family === 'electrical' && (
                <p className="notice notice-safety safety-inline" role="note"><Icon.alert size={18} /><span>{t('safety.electrical')}</span></p>
              )}
            </div>
          );
        })}
      </div>
    </section>
  );
}

/** What the i18n fallback returns for a code with no description, so we can show the default instead. */
function humanLast(code: string) {
  const last = code.split('.').pop() ?? code;
  const w = last.replace(/([A-Z])/g, ' $1').replace(/[_-]+/g, ' ').toLowerCase();
  return w.charAt(0).toUpperCase() + w.slice(1);
}

// ---- service finder: the command list -----------------------------------------------------------

function ServiceFinder() {
  const { t, tk, plural, locale } = useI18n();
  const { user, isStaff } = useAuth();
  const nav = useNavigate();
  const id = useId();
  const [q, setQ] = useState('');
  const [data, setData] = useState<ServiceSearch | null>(null);
  const [state, setState] = useState<'loading' | 'ready' | 'error'>('loading');
  const [sel, setSel] = useState(0);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    const ctrl = new AbortController();
    setState('loading');
    const timer = window.setTimeout(() => {
      api<ServiceSearch>(`/services${qs({ q: q.trim(), limit: 8 })}`, { signal: ctrl.signal })
        .then((d) => { setData(d); setSel(0); setState('ready'); })
        .catch(() => { if (!ctrl.signal.aborted) setState('error'); });
    }, q ? 250 : 0);
    return () => { window.clearTimeout(timer); ctrl.abort(); };
  }, [q, locale, attempt]);

  const items = data?.items ?? [];
  const detailHref = (code: string) => (user ? `/app/services/${code}` : `/signin?next=${encodeURIComponent(`/app/services/${code}`)}`);
  const onKey = (e: KeyboardEvent<HTMLInputElement>) => {
    if (!items.length) return;
    if (e.key === 'ArrowDown') { e.preventDefault(); setSel((s) => Math.min(items.length - 1, s + 1)); }
    if (e.key === 'ArrowUp') { e.preventDefault(); setSel((s) => Math.max(0, s - 1)); }
    if (e.key === 'Enter' && !isStaff && items[sel]) { e.preventDefault(); nav(detailHref(items[sel].service.code)); }
  };

  return (
    <section id="services" className="services l-frame" aria-labelledby="services-h">
      <div className="services-head" data-reveal>
        <h2 id="services-h" className="l-h2">{t('landing.services.title')}</h2>
        <p className="l-lead">{t('landing.services.lead')}</p>
      </div>
      <div className="command glass" data-reveal>
        <label htmlFor={`${id}-q`} className="visually-hidden">{t('landing.services.inputLabel')}</label>
        <div className="command-input">
          <Icon.search size={24} />
          <input id={`${id}-q`} type="search" value={q} onChange={(e) => setQ(e.target.value)} onKeyDown={onKey}
            placeholder={t('landing.services.placeholder')} autoComplete="off" maxLength={200}
            aria-controls={`${id}-list`} aria-describedby={`${id}-status`} />
        </div>
        <p id={`${id}-status`} className="command-status meta" aria-live="polite">
          {state === 'loading' && t('landing.services.loading')}
          {state === 'ready' && items.length > 0 && `${plural('landing.services.results', items.length)}. ${t('landing.services.keys')}`}
          {locale !== 'en' && state === 'ready' && items.length > 0 && ` ${t('landing.services.englishOnly')}`}
        </p>
        {state === 'error' && (
          <div className="state state-error" role="alert">
            <Icon.alert size={22} />
            <div><p>{t('landing.services.error')}</p>
              <button type="button" className="btn btn-quiet" onClick={() => setAttempt((a) => a + 1)}>{t('common.retry')}</button></div>
          </div>
        )}
        {state === 'ready' && data?.no_match && (
          <div className="state state-empty">
            <p>{t('landing.services.none', { q: q.trim() })}</p>
            <Link className="btn btn-primary" to={reportTarget(isStaff)}>{t('landing.services.reportAnyway')}</Link>
          </div>
        )}
        <ul id={`${id}-list`} className="command-list">
          {items.map((m, i) => {
            const on = i === sel;
            const reasons = matchReasons(m.matched_on);
            return (
              <li key={m.service.id} className={on ? 'is-on' : ''}>
                <button type="button" className="command-row" aria-expanded={on} aria-controls={`${id}-d-${i}`}
                  onClick={() => setSel(i)} onMouseEnter={() => setSel(i)}>
                  <span className="command-name" lang="en">{m.service.name}</span>
                  {m.service.state === 'unavailable' && <Pill tone="warn">{t('landing.services.unavailable')}</Pill>}
                </button>
                <div id={`${id}-d-${i}`} className="command-detail" hidden={!on}>
                  <p lang="en">{m.service.summary}</p>
                  {reasons.length > 0 && (
                    <p className="command-why">
                      <strong>{t('landing.match.prefix')}</strong>{' '}
                      {reasons.map((r) => tk(`landing.match.${r}`, { category: m.matched_category?.label ?? '' })).join(' ')}
                    </p>
                  )}
                  {!isStaff && (
                    <Link className="btn btn-primary btn-sm" to={detailHref(m.service.code)}>
                      {t('landing.services.open')} <Icon.arrowRight size={16} />
                    </Link>
                  )}
                </div>
              </li>
            );
          })}
        </ul>
      </div>
    </section>
  );
}

// ---- FAQ ----------------------------------------------------------------------------------------

const FAQ = ['emergency', 'department', 'status', 'services', 'privacy', 'photos', 'electrical', 'duplicate',
  'time', 'reopen', 'language', 'account', 'demo'] as const;

function Faq() {
  const { t, tk } = useI18n();
  const id = useId();
  const [open, setOpen] = useState<Set<string>>(() => new Set());
  const toggle = (k: string) => setOpen((s) => {
    const n = new Set(s);
    if (n.has(k)) n.delete(k); else n.add(k);
    return n;
  });
  return (
    <section id="faq" className="faq l-frame" aria-labelledby="faq-h">
      <div className="faq-head" data-reveal>
        <h2 id="faq-h" className="l-h2">{t('landing.faq.title')}</h2>
        <p className="l-lead">{t('landing.faq.lead')}</p>
      </div>
      <div className="faq-list" data-reveal>
        {FAQ.map((k) => {
          const isOpen = open.has(k);
          return (
            <div key={k} className={`faq-item ${isOpen ? 'is-open' : ''}`}>
              <h3>
                <button type="button" id={`${id}-b-${k}`} aria-expanded={isOpen} aria-controls={`${id}-p-${k}`} onClick={() => toggle(k)}>
                  <span>{tk(`landing.faq.q.${k}`)}</span>
                  <span className="faq-sign" aria-hidden="true"><Icon.chevronDown /></span>
                </button>
              </h3>
              <div id={`${id}-p-${k}`} role="region" aria-labelledby={`${id}-b-${k}`} className="faq-panel" hidden={!isOpen}>
                <div><p>{tk(`landing.faq.a.${k}`)}</p></div>
              </div>
            </div>
          );
        })}
      </div>
    </section>
  );
}

// ---- seen something broken: CTA with a dimensional pin ------------------------------------------

function Cta() {
  const { t } = useI18n();
  const { isStaff } = useAuth();
  const scene = useRef<HTMLDivElement>(null);
  const frame = useRef(0);
  const fine = useRef(false);
  useEffect(() => {
    fine.current = window.matchMedia('(hover: hover) and (pointer: fine)').matches && !prefersReducedMotion();
    return () => cancelAnimationFrame(frame.current);
  }, []);
  const onMove = (e: PointerEvent<HTMLElement>) => {
    if (!fine.current || !scene.current) return;
    const r = e.currentTarget.getBoundingClientRect();
    const clamp = (v: number) => Math.max(-6, Math.min(6, v));
    const ry = clamp(((e.clientX - r.left) / r.width - 0.5) * 12);
    const rx = clamp(-((e.clientY - r.top) / r.height - 0.5) * 12);
    cancelAnimationFrame(frame.current);
    frame.current = requestAnimationFrame(() => {
      scene.current?.style.setProperty('--rx', `${rx}deg`);
      scene.current?.style.setProperty('--ry', `${ry}deg`);
    });
  };
  const onLeave = () => {
    cancelAnimationFrame(frame.current);
    scene.current?.style.setProperty('--rx', '0deg');
    scene.current?.style.setProperty('--ry', '0deg');
  };
  return (
    <section className="cta" aria-labelledby="cta-h" onPointerMove={onMove} onPointerLeave={onLeave}>
      <div className="cta-inner l-frame">
        <div className="cta-text" data-reveal>
          <h2 id="cta-h" className="cta-title">{t('landing.cta.title')}</h2>
          <p className="cta-lead">{t('landing.cta.lead')}</p>
          <Link className="btn btn-signal btn-lg" to={reportTarget(isStaff)}>
            {isStaff ? t('landing.cta.staff') : t('landing.cta.button')} <Icon.arrowRight />
          </Link>
        </div>
        <div className="pin-scene" aria-hidden="true" data-reveal>
          <div className="pin-tilt" ref={scene}>
            <div className="plane">
              <svg viewBox="0 0 400 400" focusable="false">
                {Array.from({ length: 11 }, (_, i) => <path key={`a${i}`} d={`M${i * 40} 0V400M0 ${i * 40}H400`} className="plane-grid" />)}
                <path d="M0 160H400M200 0V400" className="plane-street" />
                <rect x="210" y="60" width="110" height="80" rx="6" className="plane-block" />
                <rect x="60" y="210" width="110" height="120" rx="6" className="plane-block" />
                <rect x="250" y="250" width="80" height="80" rx="6" className="plane-block" />
                <ellipse cx="200" cy="160" rx="34" ry="34" className="plane-ring" />
              </svg>
            </div>
            <div className="ripples"><span /><span /><span /></div>
            <div className="pin">
              <svg viewBox="0 0 80 110" focusable="false">
                <path d="M40 106S8 66 8 40a32 32 0 0 1 64 0c0 26-32 66-32 66z" className="pin-body" />
                <path d="M40 106S8 66 8 40a32 32 0 0 1 32-32" className="pin-shade" />
                <circle cx="40" cy="40" r="12" className="pin-dot" />
              </svg>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

// ---- footer -------------------------------------------------------------------------------------

function Footer() {
  const { t } = useI18n();
  return (
    <footer className="l-footer">
      <div className="l-frame">
        <nav className="foot-cols" aria-label={t('landing.footer.title')}>
          <div>
            <h3>{t('footer.residents')}</h3>
            <Link to="/app/report">{t('nav.report')}</Link>
            <Link to="/app">{t('landing.footer.myReports')}</Link>
            <Link to="/app/services">{t('nav.services')}</Link>
          </div>
          <div>
            <h3>{t('footer.staff')}</h3>
            <Link to="/signin">{t('nav.signIn')}</Link>
            <Link to="/app/queue">{t('nav.queue')}</Link>
            <Link to="/app/analytics">{t('nav.analytics')}</Link>
          </div>
          <div>
            <h3>{t('footer.about')}</h3>
            <a href="#how">{t('footer.howItWorks')}</a>
            <a href="#faq">{t('footer.faq')}</a>
            <a href="/docs">{t('footer.apiDocs')}</a>
          </div>
          <div className="foot-note">
            <p>{t('footer.notEmergency')}</p>
            <LanguageSwitch className="lang-dark" />
          </div>
        </nav>
        <p className="foot-name" aria-hidden="true">Your City, Your Services</p>
        <div className="foot-last">
          <Copyright />
          <DemoBadge withNote />
        </div>
      </div>
    </footer>
  );
}

export default function Landing() {
  const { t } = useI18n();
  const root = useRef<HTMLDivElement>(null);
  useReveal(root);
  useEffect(() => { document.title = t('app.name'); }, [t]);
  return (
    <div className="landing aurora" ref={root}>
      <Backdrop />
      <a className="skip-link" href="#main">{t('app.skip')}</a>
      <Header />
      <main id="main">
        <Hero />
        <Slip />
        <CityMap />
        <ReportList />
        <ServiceFinder />
        <Faq />
        <Cta />
      </main>
      <Footer />
    </div>
  );
}
