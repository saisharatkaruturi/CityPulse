import { describe, expect, it } from 'vitest';
import { ApiError } from './api';
import { asFamily, comparePriority, dueState, errorKey, fieldErrors, filenameFrom } from './lib';

describe('lib helpers', () => {
  it('sorts priority by its defined order, not alphabetically', () => {
    expect(['low', 'critical', 'medium', 'high'].sort(comparePriority)).toEqual(['critical', 'high', 'medium', 'low']);
    expect(['mystery', 'low'].sort(comparePriority)).toEqual(['low', 'mystery']);
  });

  it('maps category codes to families, including electrical and unknowns', () => {
    expect(asFamily('electrical.exposed_wire')).toBe('electrical');
    expect(asFamily('roads.pothole')).toBe('roads');
    expect(asFamily('something.new')).toBe('other');
    expect(asFamily(null)).toBe('other');
  });

  it('describes targets against now', () => {
    const now = Date.parse('2026-10-24T12:00:00Z');
    expect(dueState('2026-10-27T12:00:00Z', null, now)).toMatchObject({ key: 'due.in.days', vars: { n: 3 }, overdue: false });
    expect(dueState('2026-10-24T09:00:00Z', null, now)).toMatchObject({ key: 'due.over.hours', vars: { n: 3 }, overdue: true });
    expect(dueState(null, null, now).key).toBe('due.none');
    expect(dueState('2026-10-20T00:00:00Z', '2026-10-19T00:00:00Z', now).key).toBe('due.paused');
  });

  it('turns API errors into plain messages and field errors', () => {
    expect(errorKey(new ApiError(0, 'network', 'x')).key).toBe('error.network');
    expect(errorKey(new ApiError(403, 'forbidden', 'x')).key).toBe('error.forbidden');
    expect(errorKey(new ApiError(409, 'version_conflict', 'x')).key).toBe('error.conflict');
    expect(errorKey(new Error('boom')).key).toBe('error.generic');
    const v = new ApiError(422, 'validation_failed', 'x', [{ field: 'body.description', message: 'Too short' }]);
    expect(fieldErrors(v)).toEqual({ description: 'Too short' });
  });

  it('builds a safe CSV filename', () => {
    expect(filenameFrom('attachment; filename="ycys-reports_2026-09-01_to_2026-10-01.csv"', 'x'))
      .toBe('ycys-reports_2026-09-01_to_2026-10-01.csv');
    expect(filenameFrom(null, 'reports ../evil')).toBe('reports_.._evil.csv');
  });
});
