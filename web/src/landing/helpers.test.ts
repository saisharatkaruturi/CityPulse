import { describe, expect, it } from 'vitest';
import { afterSignIn, groupCategories, looksLikeEmail, matchReasons, reportTarget } from './helpers';

const cat = (id: string, code: string, parent_id: string | null = null, label = code) =>
  ({ id, code, label, parent_id, is_active: true });

describe('public page helpers', () => {
  it('groups reportable categories by family, electrical included, parents excluded', () => {
    const groups = groupCategories([
      cat('e', 'electrical'), cat('e1', 'electrical.exposed_wire', 'e'), cat('r', 'roads'), cat('r1', 'roads.pothole', 'r'),
      cat('t', 'other.triage'), cat('s', 'other.stray_animals'),
    ]);
    expect(groups.map((g) => g.family)).toEqual(['roads', 'electrical', 'other']);
    expect(groups[1].rows.map((r) => r.code)).toEqual(['electrical.exposed_wire']);
    expect(groups[2].rows.map((r) => r.code)).toEqual(['other.stray_animals', 'other.triage']);
  });

  it('falls back to the standard list when categories fail to load', () => {
    const codes = groupCategories(null).flatMap((g) => g.rows.map((r) => r.code));
    expect(codes).toContain('electrical.exposed_wire');
    expect(codes).toContain('electrical.public_fixture');
    expect(codes).toHaveLength(11);
  });

  it('explains matches strongest first', () => {
    expect(matchReasons(['description', 'name_terms', 'category'])).toEqual(['category', 'name', 'description']);
    expect(matchReasons(['mystery'])).toEqual([]);
  });

  it('never redirects off-site and keeps roles on their own pages', () => {
    expect(afterSignIn('https://evil.example', 'resident')).toBe('/app');
    expect(afterSignIn('//evil.example', 'resident')).toBe('/app');
    expect(afterSignIn(null, 'supervisor')).toBe('/app/queue');
    expect(afterSignIn('/app/report?category=roads.pothole', 'resident')).toBe('/app/report?category=roads.pothole');
    expect(afterSignIn('/app/report', 'officer')).toBe('/app/queue');
    expect(afterSignIn('/app/services/x', 'admin')).toBe('/app/queue');
    expect(afterSignIn('/app/reports/abc', 'officer')).toBe('/app/reports/abc');
    expect(afterSignIn('/app/queue', 'resident')).toBe('/app');
  });

  it('sends staff to the queue and residents to the form with the category', () => {
    expect(reportTarget(true, 'roads.pothole')).toBe('/app/queue');
    expect(reportTarget(false, 'electrical.exposed_wire')).toBe('/app/report?category=electrical.exposed_wire');
  });

  it('checks email shape', () => {
    expect(looksLikeEmail('a@b.co')).toBe(true);
    expect(looksLikeEmail('nope')).toBe(false);
  });
});
