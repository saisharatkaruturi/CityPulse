import { useI18n } from '../i18n';

/**
 * The mark: a city block seen from above. Two quiet streets cross it, and one path runs from a resident's
 * corner to a lit service node — a report finding its way to the people who fix it. Drawn on a 32px grid
 * so it stays legible as a 16px favicon; `tone="dark"` adds an edge so it holds on the ink field.
 */
export function LogoMark({ size = 32, tone = 'light', title }: { size?: number; tone?: 'light' | 'dark'; title?: string }) {
  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 32 32"
      role={title ? 'img' : undefined}
      aria-label={title}
      aria-hidden={title ? undefined : true}
      focusable="false"
    >
      <rect x="0.75" y="0.75" width="30.5" height="30.5" rx="7.25" fill="#0e1a2b"
        stroke={tone === 'dark' ? '#f6f3ed' : '#0e1a2b'} strokeOpacity={tone === 'dark' ? 0.55 : 1} strokeWidth="1.5" />
      <path d="M6.5 20.5h19M12.5 6.5v19" stroke="#f6f3ed" strokeOpacity="0.32" strokeWidth="2" strokeLinecap="round" />
      <path d="M8 24.5c4.5 0 3.6-8.6 8.4-9.4 3.2-.5 4.6-2.7 6.2-5.6" fill="none" stroke="#f6f3ed" strokeWidth="2.4" strokeLinecap="round" />
      <circle cx="8" cy="24.5" r="1.9" fill="#f6f3ed" />
      <circle cx="23.6" cy="8.6" r="3.4" fill="#e8902f" />
    </svg>
  );
}

/** Mark plus wordmark. `compact` drops the second half of the name for narrow bars. */
export function Wordmark({ tone = 'light', compact = false, size = 32 }: { tone?: 'light' | 'dark'; compact?: boolean; size?: number }) {
  const { t } = useI18n();
  return (
    <span className={`wordmark wordmark-${tone}`}>
      <LogoMark size={size} tone={tone} />
      <span className="wordmark-text">
        {compact ? t('app.short') : (
          <>
            <span>Your City</span><span className="wordmark-2">, Your Services</span>
          </>
        )}
      </span>
    </span>
  );
}
