// The one icon set: 20px grid, 1.6px outline stroke, currentColor. Decorative by default (aria-hidden);
// controls that show only an icon must carry their own accessible name.
import type { ReactElement } from 'react';
import type { Family } from '../lib';

const P = { fill: 'none', stroke: 'currentColor', strokeWidth: 1.6, strokeLinecap: 'round', strokeLinejoin: 'round' } as const;

function make(paths: ReactElement) {
  return function I({ size = 20, className }: { size?: number; className?: string }) {
    return (
      <svg viewBox="0 0 20 20" width={size} height={size} className={className} aria-hidden="true" focusable="false" {...P}>
        {paths}
      </svg>
    );
  };
}

export const Icon = {
  reports: make(<><rect x="4" y="2.75" width="12" height="14.5" rx="2" /><path d="M7 7h6M7 10h6M7 13h3.5" /></>),
  plus: make(<path d="M10 4.5v11M4.5 10h11" />),
  search: make(<><circle cx="9" cy="9" r="5.25" /><path d="m13 13 3.75 3.75" /></>),
  bell: make(<><path d="M5 13.5V9a5 5 0 0 1 10 0v4.5l1.25 1.75H3.75z" /><path d="M8.25 17.25h3.5" /></>),
  queue: make(<path d="M3.5 5.5h13M3.5 10h13M3.5 14.5h8.5" />),
  chart: make(<path d="M3.5 16.5h13M6 13.5V10M10 13.5V5.5M14 13.5V8" />),
  menu: make(<path d="M3.5 6h13M3.5 10h13M3.5 14h13" />),
  close: make(<path d="m5 5 10 10M15 5 5 15" />),
  refresh: make(<><path d="M15.75 9.25A5.75 5.75 0 1 0 14 13.6" /><path d="M16 4.5v4.75h-4.75" /></>),
  download: make(<><path d="M10 3.5v9M6.25 9 10 12.75 13.75 9" /><path d="M4 16.25h12" /></>),
  upload: make(<><path d="M10 13V4M6.25 7.5 10 3.75 13.75 7.5" /><path d="M4 16.25h12" /></>),
  chevronRight: make(<path d="m8 5 5 5-5 5" />),
  chevronDown: make(<path d="m5 8 5 5 5-5" />),
  chevronLeft: make(<path d="m12 5-5 5 5 5" />),
  arrowRight: make(<path d="M4 10h12M11.5 5.5 16 10l-4.5 4.5" />),
  check: make(<path d="m4.5 10.5 3.5 3.5 7.5-8" />),
  alert: make(<><path d="M10 3 2.75 16h14.5z" /><path d="M10 8v3.5M10 13.75v.25" /></>),
  info: make(<><circle cx="10" cy="10" r="7" /><path d="M10 9v4.5M10 6.5v.25" /></>),
  pin: make(<><path d="M10 17.5s5.5-5 5.5-9.25a5.5 5.5 0 0 0-11 0C4.5 12.5 10 17.5 10 17.5z" /><circle cx="10" cy="8.25" r="2" /></>),
  image: make(<><rect x="3" y="4" width="14" height="12" rx="2" /><circle cx="7.5" cy="8.25" r="1.25" /><path d="m3.5 14.5 4-4 3 3 2-2 4 3.5" /></>),
  eye: make(<><path d="M2.5 10S5.25 4.75 10 4.75 17.5 10 17.5 10 14.75 15.25 10 15.25 2.5 10 2.5 10z" /><circle cx="10" cy="10" r="2.25" /></>),
  eyeOff: make(<><path d="M8.2 5a7.3 7.3 0 0 1 1.8-.25C14.75 4.75 17.5 10 17.5 10a12.3 12.3 0 0 1-2.1 2.75M12.1 12.2A2.25 2.25 0 0 1 8 10a2.2 2.2 0 0 1 .3-1.1M5.2 6.6A12 12 0 0 0 2.5 10S5.25 15.25 10 15.25a7 7 0 0 0 3.4-.85" /><path d="m3.5 3.5 13 13" /></>),
  user: make(<><circle cx="10" cy="7" r="3.25" /><path d="M4 16.5c.9-2.9 3.2-4.25 6-4.25s5.1 1.35 6 4.25" /></>),
  globe: make(<><circle cx="10" cy="10" r="7" /><path d="M3 10h14M10 3c2 2 2.75 4.5 2.75 7S12 15 10 17c-2-2-2.75-4.5-2.75-7S8 5 10 3z" /></>),
  clock: make(<><circle cx="10" cy="10" r="7" /><path d="M10 6v4.25l2.75 1.75" /></>),
  logout: make(<><path d="M8 4H4.75v12H8" /><path d="M11.5 6.5 15 10l-3.5 3.5M15 10H7.5" /></>),
  filter: make(<path d="M3.5 5h13M6 10h8M8.5 15h3" />),
  sortAsc: make(<path d="M10 15.5v-11M6 8.5l4-4 4 4" />),
  sortDesc: make(<path d="M10 4.5v11M6 11.5l4 4 4-4" />),
  sort: make(<path d="M7 4.5v11M4 7.5l3-3 3 3M13 15.5v-11M10 12.5l3 3 3-3" />),
  external: make(<><path d="M11.5 4h4.5v4.5M16 4l-7 7" /><path d="M14 11.5v4.5H4V6h4.5" /></>),
  trash: make(<><path d="M4 6h12M8 6V4h4v2M5.5 6l.75 10.25h7.5L14.5 6" /></>),
  merge: make(<><path d="M6 3.5v4c0 2.5 4 3 4 6v3M14 3.5v4c0 2.5-4 3-4 6" /></>),
  layers: make(<><path d="m10 3 7 3.75-7 3.75-7-3.75z" /><path d="m3 10.25 7 3.75 7-3.75M3 13.75l7 3.75 7-3.75" /></>),
};

/** One mark per issue family, so a category reads by shape as well as by name and colour. */
export const FamilyIcon: Record<Family, ReturnType<typeof make>> = {
  roads: make(<><path d="M7 3.5 4 16.5M13 3.5l3 13" /><path d="M10 4.5v2M10 9v2M10 13.5v2" /></>),
  sanitation: make(<><path d="M4.5 6h11M8 6V4.25h4V6M5.75 6l1 10.25h6.5l1-10.25" /><path d="M8.75 9v4.5M11.25 9v4.5" /></>),
  water: make(<path d="M10 3s5 5.4 5 9a5 5 0 0 1-10 0c0-3.6 5-9 5-9z" />),
  drainage: make(<><rect x="3.5" y="3.5" width="13" height="13" rx="2" /><path d="M7 3.5v13M10 3.5v13M13 3.5v13" /></>),
  lighting: make(<><path d="M7.5 13.25a5 5 0 1 1 5 0V15h-5z" /><path d="M8 17.5h4" /></>),
  electrical: make(<path d="M11.25 2.75 5 11h4.25l-.75 6.25L15 9h-4.25z" />),
  other: make(<><circle cx="10" cy="10" r="7" /><path d="M8 8a2 2 0 1 1 2.75 1.85c-.5.2-.75.6-.75 1.15v.5M10 13.75v.25" /></>),
};
