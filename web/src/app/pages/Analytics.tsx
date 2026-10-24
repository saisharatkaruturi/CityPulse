import '../../styles/staff.css';

import { useId, useMemo, useState, type FormEvent } from 'react';
import { api, apiRaw, qs, type Analytics as A, type AnalyticsGroup } from '../../api';
import { useAuth } from '../../auth';
import { Icon } from '../../components/Icon';
import { EmptyState, ErrorState, PageHeader, RefreshControl, Skeleton, StaleNotice } from '../../components/ui';
import { useI18n } from '../../i18n';
import { errorKey, filenameFrom, type Family } from '../../lib';
import { useResource } from '../../lib/useResource';
import { capabilities } from '../../roles';
import { useRef$ } from '../refdata';
import {
  PRESETS, PRIORITY_ORDER, barPct, byFamily, customWindow, presetWindow, targetState, worstDepartment,
  type Preset, type Window,
} from '../staff/analyticsLogic';

type Range = { kind: 'preset'; preset: Preset } | { kind: 'custom'; from: string; to: string; window: Window };

/** Screen question: which department is falling behind, and are reports being handled within target? */
export default function Analytics() {
  const { experience } = useAuth();
  const caps = capabilities(experience);
  const { t, tk, fmt, plural } = useI18n();
  const ref = useRef$();
  const [range, setRange] = useState<Range>({ kind: 'preset', preset: '90' });
  const [category, setCategory] = useState('');
  const window_ = useMemo(() => (range.kind === 'preset' ? presetWindow(range.preset) : range.window), [range]);
  const filters = { ...window_, category_id: category || undefined };
  const query = qs(filters);
  const res = useResource<A>(`analytics${query}`, (signal) => api<A>(`/admin/analytics${query}`, { signal }));
  const scope = experience === 'admin' || experience === 'auditor' ? t('analytics.scope.all') : t('analytics.scope.yours');
  const period = t('analytics.period', { from: fmt.date(window_.date_from), to: fmt.date(new Date(Date.parse(window_.date_to) - 1).toISOString()) });
  const families = ref.categories.filter((c) => !c.parent_id && ref.categories.some((k) => k.parent_id === c.id));

  const d = res.data;
  const worst = d ? worstDepartment(d.by_department) : null;
  const deptLabel = (key: string) => (key === 'none' ? t('analytics.unrouted') : ref.deptName(key) === '—' ? t('analytics.department') : ref.deptName(key));
  const finding = !d ? null
    : d.issues_total === 0 ? t('analytics.finding.none')
      : worst ? t('analytics.finding.worst', { dept: deptLabel(worst.key), overdue: worst.overdue_open, open: worst.open })
        : d.open ? t('analytics.finding.clear', { open: d.open }) : t('analytics.finding.allClosed');

  return (
    <>
      <PageHeader title={t('analytics.title')} sub={<>{scope} · {period}</>}
        actions={<RefreshControl onRefresh={() => void res.reload()} refreshing={res.refreshing} updatedAt={res.updatedAt} />} />

      <section className="analytics-controls" aria-label={t('analytics.controls')}>
        <RangePicker range={range} onChange={setRange} />
        <div className="field analytics-cat">
          <label htmlFor="an-cat">{t('analytics.family')}</label>
          <select id="an-cat" className="input" value={category} onChange={(e) => setCategory(e.target.value)}>
            <option value="">{t('queue.filter.anyCategory')}</option>
            {families.map((f) => <option key={f.id} value={f.id}>{f.label}</option>)}
          </select>
        </div>
        {caps.export && <ExportButton filters={filters} />}
      </section>

      {res.error != null && d && <StaleNotice error={res.error} onRetry={() => void res.reload()} />}
      {res.loading && <Skeleton rows={4} height={88} />}
      {res.error != null && !d && <ErrorState error={res.error} onRetry={() => void res.reload()} title={t('analytics.loadFailed')} />}

      {d && (
        <div className="analytics-grid">
          <p className="analytics-finding">{finding}</p>

          <section className="panel kpi-strip" aria-label={t('analytics.kpis')}>
            <Kpi label={t('analytics.kpi.reported')} value={d.issues_total}
              note={d.merged_duplicates ? plural('analytics.kpi.merged', d.merged_duplicates) : undefined} />
            <Kpi label={t('analytics.kpi.open')} value={d.open} />
            <Kpi label={t('analytics.kpi.overdue')} value={d.overdue_open} alert={d.overdue_open > 0} />
            <Kpi label={t('analytics.kpi.resolved')} value={(d.by_status.resolved ?? 0) + (d.by_status.closed ?? 0)} />
          </section>

          {d.issues_total === 0 ? (
            <EmptyState title={t('analytics.emptyTitle')}>{t('analytics.emptyBody')}</EmptyState>
          ) : (
            <>
              <DepartmentChart groups={d.by_department} label={deptLabel} />
              <TargetPanel a={d} period={period} />
              <TimesPanel a={d} />
              <BarChart id="fam" title={t('analytics.byFamily')} unit={t('analytics.unit.reports')}
                rows={byFamily(d.by_category, ref.catCode).map((g) => ({ key: g.key, label: tk(`family.${g.key}`), value: g.total, family: g.key }))} />
              <BarChart id="prio" title={t('analytics.byPriority')} unit={t('analytics.unit.reports')}
                rows={d.by_priority.slice().sort((a, b) => PRIORITY_ORDER.indexOf(a.key) - PRIORITY_ORDER.indexOf(b.key))
                  .map((g) => ({ key: g.key, label: tk(`priority.${g.key}`), value: g.total }))} />
            </>
          )}
          <p className="meta analytics-source">{t('analytics.source')}</p>
        </div>
      )}
    </>
  );
}

function Kpi({ label, value, note, alert }: { label: string; value: number; note?: string; alert?: boolean }) {
  const { fmt } = useI18n();
  return (
    <div className="kpi">
      <span className="kpi-label">{label}</span>
      <span className={`kpi-value num ${alert ? 'is-overdue' : ''}`}>{alert && <Icon.alert size={18} />}{fmt.number(value)}</span>
      {note && <span className="meta">{note}</span>}
    </div>
  );
}

function RangePicker({ range, onChange }: { range: Range; onChange: (r: Range) => void }) {
  const { t } = useI18n();
  const id = useId();
  const [custom, setCustom] = useState(range.kind === 'custom');
  const [from, setFrom] = useState(range.kind === 'custom' ? range.from : '');
  const [to, setTo] = useState(range.kind === 'custom' ? range.to : '');
  const [error, setError] = useState<string | null>(null);
  const apply = (e: FormEvent) => {
    e.preventDefault();
    const r = customWindow(from, to);
    if (!r.window) { setError(t(`analytics.rangeError.${r.error}` as 'analytics.rangeError.order')); return; }
    setError(null);
    onChange({ kind: 'custom', from, to, window: r.window });
  };
  return (
    <div className="range-picker">
      <div className="segmented" role="group" aria-label={t('analytics.range')}>
        {PRESETS.map((p) => (
          <button key={p} type="button" aria-pressed={!custom && range.kind === 'preset' && range.preset === p}
            onClick={() => { setCustom(false); onChange({ kind: 'preset', preset: p }); }}>
            {t(`analytics.preset.${p}` as 'analytics.preset.30')}
          </button>
        ))}
        <button type="button" aria-pressed={custom} aria-expanded={custom} aria-controls={`${id}-custom`} onClick={() => setCustom(true)}>
          {t('analytics.preset.custom')}
        </button>
      </div>
      {custom && (
        <form id={`${id}-custom`} className="custom-range" onSubmit={apply} noValidate>
          <div className="field">
            <label htmlFor={`${id}-from`}>{t('queue.filter.from')}</label>
            <input id={`${id}-from`} type="date" className="input" value={from} onChange={(e) => setFrom(e.target.value)} aria-invalid={Boolean(error)} />
          </div>
          <div className="field">
            <label htmlFor={`${id}-to`}>{t('queue.filter.to')}</label>
            <input id={`${id}-to`} type="date" className="input" value={to} onChange={(e) => setTo(e.target.value)} aria-invalid={Boolean(error)} />
          </div>
          <button className="btn" type="submit">{t('analytics.apply')}</button>
          {error && <p className="field-error" role="alert"><Icon.alert size={16} />{error}</p>}
        </form>
      )}
    </div>
  );
}

function ExportButton({ filters }: { filters: Record<string, string | undefined> }) {
  const { t, plural } = useI18n();
  const [busy, setBusy] = useState(false);
  const [msg, setMsg] = useState<{ tone: 'ok' | 'warn' | 'bad'; text: string } | null>(null);
  const run = async () => {
    if (busy) return;
    setBusy(true);
    setMsg(null);
    try {
      const res = await apiRaw(`/admin/analytics/export.csv${qs(filters)}`);
      const blob = await res.blob();
      const rows = Number(res.headers.get('X-Row-Count') ?? 'NaN');
      const name = filenameFrom(res.headers.get('Content-Disposition'), 'ycys-reports');
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = name;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.setTimeout(() => URL.revokeObjectURL(url), 1000);
      setMsg(rows === 0 ? { tone: 'warn', text: t('analytics.export.empty', { name }) }
        : { tone: 'ok', text: Number.isFinite(rows) ? plural('analytics.export.done', rows, { name }) : t('analytics.export.doneNoCount', { name }) });
    } catch (e) {
      const k = errorKey(e);
      setMsg({ tone: 'bad', text: `${t('analytics.export.failed')} ${t(k.key, k.vars)}` });
    } finally {
      setBusy(false);
    }
  };
  return (
    <div className="export">
      <button type="button" className="btn" onClick={run} disabled={busy} aria-busy={busy}>
        <Icon.download size={18} />{busy ? t('analytics.export.preparing') : t('analytics.export.button')}
      </button>
      <p className="meta">{t('analytics.export.hint')}</p>
      <div role="status" aria-live="polite">{msg && <p className={`notice notice-${msg.tone}`}>{msg.text}</p>}</div>
    </div>
  );
}

/** "Met the target": definition, observed value, sample and period, or an honest reason there is none. */
function TargetPanel({ a, period }: { a: A; period: string }) {
  const { t, fmt } = useI18n();
  const s = targetState(a);
  return (
    <section className="panel target-panel" aria-labelledby="target-h">
      <div className="panel-head"><h2 id="target-h">{t('analytics.target.title')}</h2></div>
      {s.kind === 'not_configured' && <p className="target-status"><strong>{t('analytics.target.notConfigured')}</strong> {t('analytics.target.notConfiguredBody')}</p>}
      {s.kind === 'insufficient' && <p className="target-status"><strong>{t('analytics.target.insufficient')}</strong> {t('analytics.target.insufficientBody')}</p>}
      {s.kind === 'value' && (
        <>
          <p className="target-figure"><span className="num">{fmt.percent(s.fraction)}</span></p>
          <p>{t('analytics.target.observed', { met: fmt.number(s.met), measured: fmt.number(s.measured) })}</p>
          <div className="target-bar" aria-hidden="true"><span style={{ width: `${s.fraction * 100}%` }} /></div>
          {s.small && <p className="notice notice-warn"><Icon.alert size={16} />{t('analytics.target.small', { n: s.measured })}</p>}
        </>
      )}
      <dl className="kv target-def">
        <dt>{t('analytics.target.definition')}</dt><dd>{t('analytics.target.definitionBody')}</dd>
        <dt>{t('analytics.target.calculation')}</dt><dd>{t('analytics.target.calculationBody')}</dd>
        <dt>{t('analytics.target.periodLabel')}</dt><dd>{period}</dd>
        {a.sla_policies_active > 0 && <><dt>{t('analytics.target.policies')}</dt>
          <dd>{a.sla_policies_illustrative ? t('analytics.target.illustrative', { n: a.sla_policies_active }) : t('analytics.target.configured', { n: a.sla_policies_active })}</dd></>}
      </dl>
    </section>
  );
}

function TimesPanel({ a }: { a: A }) {
  const { t, fmt } = useI18n();
  const resolved = (a.by_status.resolved ?? 0) + (a.by_status.closed ?? 0);
  return (
    <section className="panel times-panel" aria-labelledby="times-h">
      <div className="panel-head"><h2 id="times-h">{t('analytics.times.title')}</h2></div>
      <dl className="kv">
        <dt>{t('analytics.times.assign')}</dt>
        <dd><span className="num">{fmt.hours(a.assignment_hours_median)}</span> <span className="meta">{t('analytics.times.sample', { n: a.assignment_measured })}</span></dd>
        <dt>{t('analytics.times.resolveMedian')}</dt><dd className="num">{fmt.hours(a.resolution_hours_median)}</dd>
        <dt>{t('analytics.times.resolveAvg')}</dt><dd className="num">{fmt.hours(a.resolution_hours_avg)}</dd>
        <dt>{t('analytics.times.reopened')}</dt><dd className="num">{fmt.number(a.reopened)}</dd>
      </dl>
      <p className="meta">{t('analytics.times.note', { n: resolved })}</p>
    </section>
  );
}

/** Open reports per department; the past-target part is a hatched, darker segment with its own label. */
function DepartmentChart({ groups, label }: { groups: AnalyticsGroup[]; label: (k: string) => string }) {
  const { t, fmt } = useI18n();
  const [table, setTable] = useState(false);
  const rows = groups.slice().sort((a, b) => b.overdue_open - a.overdue_open || b.open - a.open || a.key.localeCompare(b.key));
  const max = Math.max(0, ...rows.map((r) => r.open));
  const summary = rows.map((r) => t('analytics.dept.summaryRow', { dept: label(r.key), open: r.open, overdue: r.overdue_open })).join('; ');
  return (
    <section className="panel chart-panel dept-chart" aria-labelledby="dept-h">
      <div className="panel-head">
        <h2 id="dept-h">{t('analytics.dept.title')}</h2>
        <div className="legend" aria-hidden="true">
          <span><i className="sw sw-open" />{t('analytics.dept.withinTarget')}</span>
          <span><i className="sw sw-over" />{t('analytics.dept.pastTarget')}</span>
        </div>
      </div>
      <p className="visually-hidden">{summary}</p>
      {max === 0 ? <p className="meta">{t('analytics.dept.noneOpen')}</p> : (
        <ul className="bars" aria-hidden="true">
          {rows.map((r) => (
            <li key={r.key}>
              <span className="bar-label">{label(r.key)}</span>
              <span className="bar-track">
                <span className="bar bar-open" style={{ width: `${barPct(r.open - r.overdue_open, max)}%` }} />
                {r.overdue_open > 0 && <span className="bar bar-over" style={{ width: `${barPct(r.overdue_open, max)}%` }} />}
              </span>
              <span className="bar-value num">{fmt.number(r.open)}{r.overdue_open > 0 && <span className="is-overdue"> · {t('analytics.dept.overShort', { n: fmt.number(r.overdue_open) })}</span>}</span>
            </li>
          ))}
        </ul>
      )}
      <button type="button" className="link-btn table-toggle" aria-expanded={table} onClick={() => setTable((v) => !v)}>
        {table ? t('analytics.hideTable') : t('analytics.showTable')}
      </button>
      {table && (
        <div className="table-wrap">
          <table className="data">
            <caption className="visually-hidden">{t('analytics.dept.title')}</caption>
            <thead><tr><th scope="col">{t('analytics.department')}</th><th scope="col" className="num">{t('analytics.col.reported')}</th>
              <th scope="col" className="num">{t('analytics.col.open')}</th><th scope="col" className="num">{t('analytics.col.overdue')}</th>
              <th scope="col" className="num">{t('analytics.col.resolved')}</th></tr></thead>
            <tbody>
              {rows.map((r) => (
                <tr key={r.key}><th scope="row">{label(r.key)}</th><td className="num">{fmt.number(r.total)}</td><td className="num">{fmt.number(r.open)}</td>
                  <td className="num">{fmt.number(r.overdue_open)}</td><td className="num">{fmt.number(r.resolved_or_closed)}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}

function BarChart({ id, title, unit, rows }: {
  id: string; title: string; unit: string; rows: { key: string; label: string; value: number; family?: Family }[];
}) {
  const { t, fmt } = useI18n();
  const [table, setTable] = useState(false);
  const max = Math.max(0, ...rows.map((r) => r.value));
  return (
    <section className="panel chart-panel" aria-labelledby={`${id}-h`}>
      <div className="panel-head"><h2 id={`${id}-h`}>{title}</h2><span className="meta">{unit}</span></div>
      <p className="visually-hidden">{rows.map((r) => `${r.label}: ${r.value}`).join('; ')}</p>
      {rows.length === 0 ? <p className="meta">{t('analytics.noRows')}</p> : (
        <ul className="bars" aria-hidden="true">
          {rows.map((r) => (
            <li key={r.key}>
              <span className="bar-label">{r.label}</span>
              <span className="bar-track"><span className={`bar bar-data ${r.family ? `fam-${r.family}` : ''}`} style={{ width: `${barPct(r.value, max)}%` }} /></span>
              <span className="bar-value num">{fmt.number(r.value)}</span>
            </li>
          ))}
        </ul>
      )}
      <button type="button" className="link-btn table-toggle" aria-expanded={table} onClick={() => setTable((v) => !v)}>
        {table ? t('analytics.hideTable') : t('analytics.showTable')}
      </button>
      {table && (
        <div className="table-wrap">
          <table className="data">
            <caption className="visually-hidden">{title}</caption>
            <thead><tr><th scope="col">{title}</th><th scope="col" className="num">{unit}</th></tr></thead>
            <tbody>{rows.map((r) => <tr key={r.key}><th scope="row">{r.label}</th><td className="num">{fmt.number(r.value)}</td></tr>)}</tbody>
          </table>
        </div>
      )}
    </section>
  );
}
