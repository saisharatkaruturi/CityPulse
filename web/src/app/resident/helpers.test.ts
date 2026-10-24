import { describe, expect, it } from 'vitest';
import type { Category } from '../../api';
import {
  checkFile, groupByDay, isClearBest, locationPayload, locationSummary, matchReasons, validateReport,
} from './helpers';

const cat = { id: 'c1', code: 'roads.pothole', label: 'Pothole' } as Category;

describe('report form validation', () => {
  it('matches the server limits', () => {
    expect(validateReport({ title: '', description: '' })).toEqual({
      title: 'resident.form.titleRequired', description: 'resident.form.descRequired',
    });
    expect(validateReport({ title: 'ab', description: 'too short' })).toEqual({
      title: 'resident.form.titleShort', description: 'resident.form.descShort',
    });
    expect(validateReport({ title: 'Pothole', description: 'A deep pothole near the gate.' })).toEqual({});
  });

  it('checks photo type and size before upload', () => {
    expect(checkFile({ type: 'image/jpeg', size: 1000 })).toBeNull();
    expect(checkFile({ type: 'image/gif', size: 1000 })).toBe('resident.photos.badType');
    expect(checkFile({ type: 'image/png', size: 5_000_001 })).toBe('resident.photos.tooBig');
    expect(checkFile({ type: 'image/webp', size: 0 })).toBe('resident.photos.empty');
  });
});

describe('location', () => {
  const none = { wardId: '', address: '', gps: null };

  it('attaches nothing unless chosen', () => {
    expect(locationPayload(none)).toBeUndefined();
    expect(locationSummary(none, () => '')).toEqual([{ key: 'resident.loc.sumNone' }]);
  });

  it('sends ward, landmark or GPS with the right source', () => {
    expect(locationPayload({ ...none, wardId: 'w1' })).toEqual({ ward_id: 'w1', source: 'ward_selection', address_text: undefined });
    expect(locationPayload({ ...none, address: ' Near the bus stop ' })).toEqual({ source: 'address', address_text: 'Near the bus stop' });
    const gps = { latitude: 17.41, longitude: 78.45, accuracy_m: 12 };
    expect(locationPayload({ ...none, gps })).toMatchObject({ ...gps, source: 'gps' });
  });

  it('describes GPS without printing coordinates', () => {
    const lines = locationSummary({ wardId: 'w1', address: '', gps: { latitude: 17.4123, longitude: 78.4567, accuracy_m: 14.6 } }, () => 'Demo Ward 1');
    expect(lines).toEqual([
      { key: 'resident.loc.sumWard', vars: { ward: 'Demo Ward 1' } },
      { key: 'resident.loc.sumGps', vars: { m: 15 } },
    ]);
    expect(JSON.stringify(lines)).not.toContain('17.41');
  });
});

describe('service matches', () => {
  it('explains a category match first, then text matches', () => {
    expect(matchReasons({ matched_on: ['category', 'synonyms'], matched_category: cat })).toEqual([
      { key: 'resident.svc.whyCategory', vars: { category: 'Pothole' } },
      { key: 'resident.svc.whySynonyms' },
    ]);
    expect(matchReasons({ matched_on: ['browse'], matched_category: null })).toEqual([]);
  });

  it('only calls a result the best match when it clearly leads', () => {
    expect(isClearBest([{ score: 9 }, { score: 2 }])).toBe(true);
    expect(isClearBest([{ score: 4 }, { score: 3.8 }])).toBe(false);
    expect(isClearBest([])).toBe(false);
  });
});

describe('notifications', () => {
  it('groups into today and earlier', () => {
    const now = new Date('2026-10-24T15:00:00');
    const g = groupByDay([{ created_at: '2026-10-24T09:00:00' }, { created_at: '2026-10-22T09:00:00' }], now);
    expect(g.today).toHaveLength(1);
    expect(g.earlier).toHaveLength(1);
  });
});
