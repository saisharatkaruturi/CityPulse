// Role experiences and what each one may open. This decides navigation and client routes; the server
// enforces every permission on its own (app/core/permissions.py), so hiding a link is never the only guard.

import type { RoleGrant } from './api';
import type { MessageKey } from './i18n';

export type Experience = 'resident' | 'officer' | 'supervisor' | 'triage' | 'admin' | 'auditor';

export type RouteKey =
  | 'myReports' | 'report' | 'services' | 'reportDetail' | 'notifications' | 'queue' | 'analytics';

const STAFF: Experience[] = ['officer', 'supervisor', 'triage', 'admin', 'auditor'];
const MANAGERS: Experience[] = ['supervisor', 'triage', 'admin'];

/** Which experiences may open each signed-in route. */
export const ROUTE_ACCESS: Record<RouteKey, Experience[]> = {
  myReports: ['resident'],
  report: ['resident'],
  services: ['resident'],
  reportDetail: ['resident', ...STAFF],
  notifications: ['resident', ...STAFF],
  queue: STAFF,
  analytics: ['supervisor', 'triage', 'admin', 'auditor'],
};

export interface NavItem {
  key: RouteKey;
  to: string;
  label: MessageKey;
  icon: 'reports' | 'plus' | 'search' | 'bell' | 'queue' | 'chart';
  end?: boolean;
  count?: 'unread' | 'waiting';
}

const NAV: NavItem[] = [
  { key: 'myReports', to: '/app', label: 'nav.myReports', icon: 'reports', end: true },
  { key: 'report', to: '/app/report', label: 'nav.report', icon: 'plus' },
  { key: 'services', to: '/app/services', label: 'nav.services', icon: 'search' },
  { key: 'queue', to: '/app/queue', label: 'nav.queue', icon: 'queue', count: 'waiting' },
  { key: 'analytics', to: '/app/analytics', label: 'nav.analytics', icon: 'chart' },
  { key: 'notifications', to: '/app/notifications', label: 'nav.notifications', icon: 'bell', count: 'unread' },
];

export function experienceOf(roles: Pick<RoleGrant, 'role' | 'department_code'>[]): Experience {
  const has = (r: RoleGrant['role']) => roles.some((g) => g.role === r);
  if (has('municipal_admin') || has('system_admin')) return 'admin';
  if (roles.some((g) => g.role === 'supervisor' && g.department_code === 'triage')) return 'triage';
  if (has('supervisor')) return 'supervisor';
  if (has('field_officer')) return 'officer';
  if (has('auditor')) return 'auditor';
  return 'resident';
}

export const isStaff = (e: Experience) => e !== 'resident';
export const canAccess = (route: RouteKey, e: Experience) => ROUTE_ACCESS[route].includes(e);
export const navFor = (e: Experience): NavItem[] => NAV.filter((n) => canAccess(n.key, e));
export const homeFor = (e: Experience) => (isStaff(e) ? '/app/queue' : '/app');

/** Client hints for which controls to offer. The server re-checks scope (department) on every request. */
export const capabilities = (e: Experience) => ({
  manage: MANAGERS.includes(e),          // assign, reassign, correct category/priority, merge
  work: e !== 'auditor' && isStaff(e),   // transitions, resolve, notes, staff messages
  export: ['supervisor', 'triage', 'admin', 'auditor'].includes(e),
  readOnly: e === 'auditor',
});

/** The role title shown in the shell, e.g. "Road Supervisor", "Triage Desk". */
export function roleTitleKey(roles: Pick<RoleGrant, 'role' | 'department_code'>[]): { key: MessageKey; dept?: string } {
  const e = experienceOf(roles);
  const grant = (r: RoleGrant['role']) => roles.find((g) => g.role === r);
  if (e === 'admin') return { key: grant('municipal_admin') ? 'role.municipalAdmin' : 'role.systemAdmin' };
  if (e === 'triage') return { key: 'role.triageDesk' };
  if (e === 'supervisor') {
    const d = grant('supervisor')?.department_code;
    return d === 'roads' ? { key: 'role.roadSupervisor' } : { key: 'role.supervisor', dept: d ?? undefined };
  }
  if (e === 'officer') {
    const d = grant('field_officer')?.department_code;
    return d === 'roads' ? { key: 'role.roadOfficer' } : { key: 'role.fieldOfficer', dept: d ?? undefined };
  }
  if (e === 'auditor') return { key: 'role.auditor' };
  return { key: 'role.resident' };
}
