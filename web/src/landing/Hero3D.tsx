import { lazy, Suspense, useCallback, useEffect, useState } from 'react';
import { FamilyIcon, Icon } from '../components/Icon';
import { useI18n, type MessageKey } from '../i18n';
import { IsoCity } from './IsoCity';

const HeroScene = lazy(() => import('./HeroScene'));

// The three example stages the floating card cycles through. Labelled "Example" — not live data.
const STEPS: { label: MessageKey; tone: 'neutral' | 'info' | 'ok' }[] = [
  { label: 'stage.submitted', tone: 'neutral' },
  { label: 'stage.routed', tone: 'info' },
  { label: 'stage.pickedUp', tone: 'ok' },
];

/**
 * Hero art: the WebGL city when the browser supports it, otherwise the CSS isometric city. Floating glass
 * cards show an example report moving through its stages. All of it is decorative (aria-hidden); a
 * visually hidden caption says what the picture shows.
 */
export function Hero3D() {
  const { t, tk } = useI18n();
  const [webgl, setWebgl] = useState<boolean | null>(null);
  const [step, setStep] = useState(0);
  const fail = useCallback(() => setWebgl(false), []);

  useEffect(() => {
    import('./HeroScene').then((m) => setWebgl(m.supportsWebGL())).catch(() => setWebgl(false));
  }, []);

  useEffect(() => {
    if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return;
    const id = window.setInterval(() => { if (!document.hidden) setStep((s) => (s + 1) % STEPS.length); }, 2600);
    return () => window.clearInterval(id);
  }, []);

  const Road = FamilyIcon.roads;
  return (
    <figure className="hero-art">
      <div className="hero-art-stage" aria-hidden="true">
        {webgl ? (
          <Suspense fallback={<div className="hero-scene" />}><HeroScene onFail={fail} /></Suspense>
        ) : webgl === false ? <IsoCity /> : <div className="hero-scene" />}
        <div className="float-card float-report glass">
          <span className="float-icon cat-roads"><Road size={18} /></span>
          <span className="float-text">
            <span className="float-kicker">{t('landing.art.example')}</span>
            <strong>{t('landing.art.reportTitle')}</strong>
          </span>
        </div>
        <div className="float-card float-status glass">
          <span className="float-kicker">{t('landing.art.status')}</span>
          <span key={step} className={`float-step tone-${STEPS[step].tone}`}>
            <Icon.check size={16} /> {tk(STEPS[step].label)}
          </span>
          <span className="float-dots">
            {STEPS.map((s, i) => <span key={s.label} className={i <= step ? 'on' : ''} />)}
          </span>
        </div>
        <div className="float-card float-desk glass">
          <span className="float-pulse" />
          <span>{t('landing.art.desk')}</span>
        </div>
      </div>
      <figcaption className="visually-hidden">{t('landing.art.caption')}</figcaption>
    </figure>
  );
}
