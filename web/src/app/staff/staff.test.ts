import { describe, expect, it } from 'vitest';
import { canResolve, movesFor } from '../case/moves';
import { barPct, byFamily, customWindow, presetWindow, targetState, worstDepartment } from './analyticsLogic';
import {
  activeFilterCount, apiParams, applyPatch, ariaSort, defaultView, impossibleStatus, lastPage, nextSort,
  parseQueue, toSearch, viewsFor,
} from './queueParams';

const CAT = '3f1b2c4d-0000-4000-8000-000000000001';

describe('queue URL state', () => {
  it('opens each role on its own default view', () => {
    expect(defaultView('officer')).toBe('mine');
    expect(defaultView('supervisor')).toBe('triage');
    expect(defaultView('triage')).toBe('review');
    expect(defaultView('admin')).toBe('triage');
    expect(defaultView('auditor')).toBe('all');
    expect(viewsFor('resident')).toEqual([]);
  });

  it('round-trips every filter through the URL', () => {
    const p = new URLSearchParams(`view=all&status=submitted&status=reopened&priority=high&category=${CAT}&assign=unassigned&from=2026-10-01&to=2026-10-20&q=PTH&sort=due_at&page=3`);
    const s = parseQueue(p, 'supervisor');
    expect(s).toMatchObject({ view: 'all', status: ['submitted', 'reopened'], priority: 'high', category: CAT, assign: 'unassigned', from: '2026-10-01', to: '2026-10-20', q: 'PTH', sort: 'due_at', page: 3 });
    expect(parseQueue(toSearch(s, 'supervisor'), 'supervisor')).toEqual(s);
  });

  it('drops invalid values instead of sending them', () => {
    const s = parseQueue(new URLSearchParams('view=mine&status=bogus&priority=urgent&category=x&assign=mine&page=-2&sort=title'), 'supervisor');
    expect(s).toMatchObject({ view: 'triage', status: [], priority: '', category: '', assign: '', page: 1, sort: '-priority' });
    expect(parseQueue(new URLSearchParams('assign=mine'), 'officer').assign).toBe('mine');
  });

  it('keeps default values out of the URL', () => {
    expect(toSearch(parseQueue(new URLSearchParams(), 'officer'), 'officer').toString()).toBe('');
  });

  it('returns to page 1 when what is listed changes, but not on sort or refresh', () => {
    const s = parseQueue(new URLSearchParams('page=4'), 'admin');
    expect(applyPatch(s, { priority: 'high' }).page).toBe(1);
    expect(applyPatch(s, { q: 'drain' }).page).toBe(1);
    expect(applyPatch(s, { sort: 'due_at' }).page).toBe(4);
    expect(applyPatch(s, {}).page).toBe(4);
    expect(applyPatch(s, { priority: s.priority }).page).toBe(4); // unchanged value is not a change
    expect(lastPage(51)).toBe(3);
    expect(lastPage(0)).toBe(1);
  });

  it('builds the API query from view and filters', () => {
    const s = parseQueue(new URLSearchParams(`category=${CAT}&from=2026-10-01&to=2026-10-01&status=submitted`), 'supervisor');
    const q = apiParams(s);
    expect(q).toMatchObject({ unassigned: true, status: ['submitted'], category_id: CAT, sort: '-priority', page: 1, page_size: 25 });
    expect(Date.parse(q.created_to as string) - Date.parse(q.created_from as string)).toBe(86_400_000);
    expect(apiParams(parseQueue(new URLSearchParams(), 'officer'))).toMatchObject({ assigned_to_me: true });
    expect(activeFilterCount(s)).toBe(4);
    const none = parseQueue(new URLSearchParams('status=closed'), 'supervisor'); // triage view has no closed reports
    expect(impossibleStatus(none)).toBe(true);
  });

  it('exposes sort state for headers and flips direction on the second click', () => {
    expect(ariaSort('-priority', 'priority')).toBe('descending');
    expect(ariaSort('due_at', 'due_at')).toBe('ascending');
    expect(ariaSort('-created_at', 'priority')).toBe('none');
    expect(nextSort('-created_at', 'priority')).toBe('-priority');
    expect(nextSort('-priority', 'priority')).toBe('priority');
    expect(nextSort('due_at', 'due_at')).toBe('-due_at');
  });
});

describe('analytics', () => {
  const base = { sla_policies_active: 4, sla_policies_illustrative: true, sla_met: 0, sla_measured: 0 };

  it('never claims the target was met without a target and data', () => {
    expect(targetState({ ...base, sla_policies_active: 0, sla_met: 3, sla_measured: 3 })).toEqual({ kind: 'not_configured' });
    expect(targetState(base)).toEqual({ kind: 'insufficient' });
    expect(targetState({ ...base, sla_met: 1, sla_measured: 2 })).toMatchObject({ kind: 'value', fraction: 0.5, small: true });
    expect(targetState({ ...base, sla_met: 9, sla_measured: 12 })).toMatchObject({ kind: 'value', fraction: 0.75, small: false, illustrative: true });
  });

  it('scales bars to the largest value and keeps non-zero values visible', () => {
    expect(barPct(0, 10)).toBe(0);
    expect(barPct(5, 0)).toBe(0);
    expect(barPct(10, 10)).toBe(100);
    expect(barPct(5, 10)).toBe(50);
    expect(barPct(1, 1000)).toBe(1.5);
  });

  it('rolls categories up into families without double counting', () => {
    const codes: Record<string, string> = { a: 'roads.pothole', b: 'roads.footpath', c: 'electrical.exposed_wire' };
    const groups = [
      { key: 'a', total: 3, open: 2, resolved_or_closed: 1, overdue_open: 1 },
      { key: 'b', total: 1, open: 1, resolved_or_closed: 0, overdue_open: 0 },
      { key: 'c', total: 2, open: 2, resolved_or_closed: 0, overdue_open: 0 },
      { key: 'none', total: 1, open: 1, resolved_or_closed: 0, overdue_open: 0 },
    ];
    const fams = byFamily(groups, (id) => (id ? codes[id] ?? null : null));
    expect(fams.map((f) => [f.key, f.total])).toEqual([['roads', 4], ['electrical', 2], ['other', 1]]);
    expect(fams.reduce((n, f) => n + f.total, 0)).toBe(groups.reduce((n, g) => n + g.total, 0));
  });

  it('names the department furthest behind, or none', () => {
    const g = (key: string, open: number, overdue_open: number) => ({ key, total: open, open, resolved_or_closed: 0, overdue_open });
    expect(worstDepartment([g('a', 5, 1), g('b', 3, 2)])?.key).toBe('b');
    expect(worstDepartment([g('a', 5, 0)])).toBeNull();
  });

  it('validates custom ranges and builds stable presets', () => {
    expect(customWindow('2026-10-10', '2026-10-01').error).toBe('order');
    expect(customWindow('2024-01-01', '2026-01-01').error).toBe('tooLong');
    expect(customWindow('', '2026-01-01').error).toBe('missing');
    expect(customWindow('2026-10-01', '2026-10-01').window).not.toBeNull();
    const now = new Date(2026, 9, 24, 15, 30);
    const w = presetWindow('30', now);
    expect((Date.parse(w.date_to) - Date.parse(w.date_from)) / 86_400_000).toBeCloseTo(30, 0);
    expect(presetWindow('30', new Date(2026, 9, 24, 9))).toEqual(w);
  });
});

describe('staff moves', () => {
  it('offers only moves the workflow allows from each status', () => {
    expect(movesFor('submitted').map((m) => m.to)).toEqual(['under_review', 'rejected']);
    expect(movesFor('submitted').find((m) => m.to === 'rejected')).toMatchObject({ reason: true, danger: true });
    expect(movesFor('closed')).toEqual([]);
    expect(movesFor('resolved')).toEqual([]);
    expect(canResolve('in_progress')).toBe(true);
    expect(canResolve('submitted')).toBe(false);
  });
});
