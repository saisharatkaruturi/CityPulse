import { useEffect, useRef } from 'react';
import { useI18n } from '../i18n';
import type { Family } from '../lib';

/**
 * The hero's 3D art: an isometric city block built from CSS boxes (no WebGL, so nothing can fail to load).
 * Each building is an issue family in its colour with ink edges; the dark one in the middle is the desk where
 * reports arrive. Purely decorative (aria-hidden) — the meaning is in the page text. Under reduced motion it
 * is a still picture; otherwise it tilts a few degrees with the pointer and the pin bobs.
 */
const BUILDINGS: { family: Family | 'desk'; x: number; y: number; w: number; d: number; h: number }[] = [
  { family: 'roads', x: 4, y: 6, w: 26, d: 22, h: 44 },
  { family: 'water', x: 70, y: 4, w: 24, d: 26, h: 70 },
  { family: 'lighting', x: 70, y: 70, w: 22, d: 24, h: 52 },
  { family: 'sanitation', x: 6, y: 72, w: 24, d: 22, h: 34 },
  { family: 'electrical', x: 38, y: 4, w: 20, d: 18, h: 92 },
  { family: 'drainage', x: 40, y: 78, w: 20, d: 18, h: 26 },
  { family: 'desk', x: 38, y: 38, w: 24, d: 24, h: 60 },
];

export function IsoCity() {
  const { tk } = useI18n();
  const stage = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = stage.current;
    if (!el) return;
    const fine = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
    const still = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    if (!fine || still) return;
    let frame = 0;
    const onMove = (e: PointerEvent) => {
      const r = el.getBoundingClientRect();
      const clamp = (v: number) => Math.max(-5, Math.min(5, v));
      const dx = clamp(((e.clientX - r.left) / r.width - 0.5) * 10);
      const dy = clamp(((e.clientY - r.top) / r.height - 0.5) * 10);
      cancelAnimationFrame(frame);
      frame = requestAnimationFrame(() => {
        el.style.setProperty('--tilt-x', `${-dy}deg`);
        el.style.setProperty('--tilt-z', `${dx}deg`);
      });
    };
    const onLeave = () => { el.style.setProperty('--tilt-x', '0deg'); el.style.setProperty('--tilt-z', '0deg'); };
    window.addEventListener('pointermove', onMove, { passive: true });
    document.addEventListener('pointerleave', onLeave);
    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener('pointermove', onMove);
      document.removeEventListener('pointerleave', onLeave);
    };
  }, []);

  return (
    <div className="iso-stage" ref={stage} aria-hidden="true">
      <div className="iso-world">
        <div className="iso-ground">
          <span className="iso-road iso-road-h" />
          <span className="iso-road iso-road-v" />
          {BUILDINGS.map((b) => (
            <div key={b.family} className={`iso-box iso-${b.family}`}
              style={{ left: `${b.x}%`, top: `${b.y}%`, width: `${b.w}%`, height: `${b.d}%`, ['--h' as string]: `${b.h}px` }}>
              <span className="iso-face iso-top" />
              <span className="iso-face iso-front" />
              <span className="iso-face iso-side" />
            </div>
          ))}
        </div>
      </div>
      <span className="iso-pin">
        <svg viewBox="0 0 80 110" focusable="false">
          <path d="M40 106S8 66 8 40a32 32 0 0 1 64 0c0 26-32 66-32 66z" fill="#ffb340" stroke="#0d1626" strokeWidth="5" />
          <circle cx="40" cy="40" r="12" fill="#0d1626" />
        </svg>
      </span>
      {(['roads', 'water', 'electrical', 'lighting'] as Family[]).map((f) => (
        <span key={f} className={`iso-chip iso-chip-${f}`}>{tk(`family.${f}`)}</span>
      ))}
    </div>
  );
}
