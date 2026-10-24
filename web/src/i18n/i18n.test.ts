import { describe, expect, it } from 'vitest';
import { humanizeKey, translate, translatePlural } from './index';
import { en, te } from './messages';

const EN = en as Record<string, string>;

describe('localisation', () => {
  it('has a Telugu message for every English key', () => {
    const missing = Object.keys(en).filter((k) => !(k in te) && EN[k] !== '');
    expect(missing).toEqual([]);
  });

  it('keeps the same {placeholders} in both languages', () => {
    const vars = (s: string) => (s.match(/\{\w+\}/g) ?? []).sort().join(',');
    const mismatched = Object.entries(te)
      .filter(([k, v]) => v !== undefined && vars(v) !== vars(EN[k] ?? ''))
      .map(([k]) => k);
    expect(mismatched).toEqual([]);
  });

  it('has no Telugu entry for a key English does not have', () => {
    expect(Object.keys(te).filter((k) => !(k in en))).toEqual([]);
  });

  it('falls back to English, then to readable words, never to a raw key', () => {
    expect(translate('te', 'nav.queue')).toBe('పని జాబితా');
    expect(translate('te', 'definitely.notAKey')).toBe('Not a key');
    expect(humanizeKey('queue.lastRefreshed')).toBe('Last refreshed');
  });

  it('interpolates and pluralises', () => {
    expect(translate('en', 'nav.signedInAs', { name: 'Asha' })).toBe('Signed in as Asha');
    expect(translatePlural('en', 'nav.unread', 1)).toBe('1 unread notification');
    expect(translatePlural('en', 'nav.unread', 3)).toBe('3 unread notifications');
  });

  it('uses the exact copyright line', () => {
    expect(EN['app.copyright']).toBe('© 2026 Your City, Your Services');
  });
});
