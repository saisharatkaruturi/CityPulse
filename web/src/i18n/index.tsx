// Localisation. English is the source of truth; every other locale is a partial dictionary that falls back
// to English key by key, so a missing translation shows English text, never a raw key.
// Adding a language: add it to LOCALES and to MESSAGES with its own dictionary; nothing else changes.

import { createContext, useCallback, useContext, useEffect, useMemo, useState, type ReactNode } from 'react';
import { setApiLocale } from '../api';
import { en as enMessages, te as teMessages } from './messages';

export type Locale = 'en' | 'te';
export type MessageKey = keyof typeof enMessages;
export type Messages = Record<MessageKey, string>;
type Vars = Record<string, string | number>;

export const LOCALES: { code: Locale; native: string; english: string; intl: string }[] = [
  { code: 'en', native: 'English', english: 'English', intl: 'en-IN' },
  { code: 'te', native: 'తెలుగు', english: 'Telugu', intl: 'te-IN' },
];

const MESSAGES: Record<Locale, Partial<Messages>> = { en: enMessages, te: teMessages };
const STORAGE_KEY = 'ycys.locale';

function readStored(): Locale {
  try {
    const v = localStorage.getItem(STORAGE_KEY);
    return LOCALES.some((l) => l.code === v) ? (v as Locale) : 'en';
  } catch {
    return 'en';
  }
}

function interpolate(text: string, vars?: Vars): string {
  if (!vars) return text;
  return text.replace(/\{(\w+)\}/g, (m, k: string) => (k in vars ? String(vars[k]) : m));
}

/** Readable stand-in for a key that has no English text at all (a bug, but never shown as a raw key). */
export function humanizeKey(key: string): string {
  const last = key.split('.').pop() ?? key;
  const words = last.replace(/([A-Z])/g, ' $1').replace(/[_-]+/g, ' ').toLowerCase();
  return words.charAt(0).toUpperCase() + words.slice(1);
}

/** Pure lookup, exported for tests: locale → English → humanised key. */
export function translate(locale: Locale, key: string, vars?: Vars): string {
  const own = (MESSAGES[locale] as Record<string, string | undefined>)[key];
  const fallback = (MESSAGES.en as Record<string, string | undefined>)[key];
  const text = own ?? fallback;
  if (text === undefined) {
    if (import.meta.env.DEV) console.warn(`[i18n] missing message: ${key}`);
    return humanizeKey(key);
  }
  return interpolate(text, vars);
}

/** Picks `<key>.one` or `<key>.other` by count; `{n}` is the count, formatted for the locale. */
export function translatePlural(locale: Locale, key: string, n: number, vars?: Vars): string {
  const rules = new Intl.PluralRules(intlOf(locale));
  const form = rules.select(n) === 'one' ? 'one' : 'other';
  return translate(locale, `${key}.${form}`, { n: new Intl.NumberFormat(intlOf(locale)).format(n), ...vars });
}

export const intlOf = (l: Locale) => LOCALES.find((x) => x.code === l)?.intl ?? 'en-IN';

export interface I18n {
  locale: Locale;
  setLocale: (l: Locale) => void;
  t: (key: MessageKey, vars?: Vars) => string;
  /** For keys built at run time (status codes, category families). Falls back like `t`. */
  tk: (key: string, vars?: Vars) => string;
  plural: (key: string, n: number, vars?: Vars) => string;
  fmt: {
    date: (iso: string | null | undefined) => string;
    dateTime: (iso: string | null | undefined) => string;
    time: (d: Date) => string;
    number: (n: number) => string;
    percent: (fraction: number) => string;
    relative: (iso: string | null | undefined) => string;
    hours: (h: number | null | undefined) => string;
  };
}

const Ctx = createContext<I18n | null>(null);

export function LocaleProvider({ children }: { children: ReactNode }) {
  const [locale, setLocaleState] = useState<Locale>(readStored);

  useEffect(() => {
    document.documentElement.lang = locale;
    setApiLocale(locale);
  }, [locale]);

  const setLocale = useCallback((l: Locale) => {
    setLocaleState(l);
    try {
      localStorage.setItem(STORAGE_KEY, l);
    } catch {
      /* the choice lasts for this visit only */
    }
    window.dispatchEvent(new CustomEvent('ycys:locale', { detail: l }));
  }, []);

  const value = useMemo<I18n>(() => {
    const intl = intlOf(locale);
    const dateF = new Intl.DateTimeFormat(intl, { day: 'numeric', month: 'short', year: 'numeric' });
    const dateTimeF = new Intl.DateTimeFormat(intl, { day: 'numeric', month: 'short', hour: 'numeric', minute: '2-digit' });
    const timeF = new Intl.DateTimeFormat(intl, { hour: 'numeric', minute: '2-digit' });
    const numF = new Intl.NumberFormat(intl);
    const pctF = new Intl.NumberFormat(intl, { style: 'percent', maximumFractionDigits: 1 });
    const relF = new Intl.RelativeTimeFormat(intl, { numeric: 'auto' });
    const tk = (key: string, vars?: Vars) => translate(locale, key, vars);
    return {
      locale,
      setLocale,
      t: tk,
      tk,
      plural: (key, n, vars) => translatePlural(locale, key, n, vars),
      fmt: {
        date: (iso) => (iso ? dateF.format(new Date(iso)) : '—'),
        dateTime: (iso) => (iso ? dateTimeF.format(new Date(iso)) : '—'),
        time: (d) => timeF.format(d),
        number: (n) => numF.format(n),
        percent: (f) => pctF.format(f),
        relative: (iso) => {
          if (!iso) return '—';
          const diff = new Date(iso).getTime() - Date.now();
          const abs = Math.abs(diff);
          if (abs < 3_600_000) return relF.format(Math.round(diff / 60_000) || (diff < 0 ? -1 : 1), 'minute');
          if (abs < 172_800_000) return relF.format(Math.round(diff / 3_600_000), 'hour');
          return relF.format(Math.round(diff / 86_400_000), 'day');
        },
        hours: (h) => {
          if (h == null) return '—';
          return h >= 48 ? tk('unit.days', { n: numF.format(Math.round((h / 24) * 10) / 10) })
            : tk('unit.hours', { n: numF.format(Math.round(h * 10) / 10) });
        },
      },
    };
  }, [locale, setLocale]);

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useI18n(): I18n {
  const v = useContext(Ctx);
  if (!v) throw new Error('useI18n outside LocaleProvider');
  return v;
}
