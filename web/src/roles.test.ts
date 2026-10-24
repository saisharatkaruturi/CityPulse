import { describe, expect, it } from 'vitest';
import type { RoleGrant } from './api';
import { canAccess, capabilities, experienceOf, homeFor, navFor, roleTitleKey } from './roles';

const g = (role: RoleGrant['role'], department_code: string | null = null) => ({ role, department_code });
const ACCOUNTS = {
  resident: [g('resident')],
  roadOfficer: [g('field_officer', 'roads')],
  roadSupervisor: [g('supervisor', 'roads')],
  triageDesk: [g('supervisor', 'triage')],
  municipalAdmin: [g('municipal_admin')],
  auditor: [g('auditor')],
};
const RESIDENT_ONLY = ['nav.myReports', 'nav.report', 'nav.services'];

describe('role experiences', () => {
  it('maps each demo account to its experience and title', () => {
    expect(experienceOf(ACCOUNTS.resident)).toBe('resident');
    expect(experienceOf(ACCOUNTS.roadOfficer)).toBe('officer');
    expect(experienceOf(ACCOUNTS.roadSupervisor)).toBe('supervisor');
    expect(experienceOf(ACCOUNTS.triageDesk)).toBe('triage');
    expect(experienceOf(ACCOUNTS.municipalAdmin)).toBe('admin');
    expect(roleTitleKey(ACCOUNTS.roadOfficer).key).toBe('role.roadOfficer');
    expect(roleTitleKey(ACCOUNTS.roadSupervisor).key).toBe('role.roadSupervisor');
    expect(roleTitleKey(ACCOUNTS.triageDesk).key).toBe('role.triageDesk');
    expect(roleTitleKey(ACCOUNTS.municipalAdmin).key).toBe('role.municipalAdmin');
    expect(roleTitleKey([g('supervisor', 'water')])).toEqual({ key: 'role.supervisor', dept: 'water' });
  });

  it('gives residents My reports, Report an issue and Find a service', () => {
    const labels = navFor('resident').map((n) => n.label);
    expect(labels).toEqual(expect.arrayContaining(RESIDENT_ONLY));
    expect(labels).not.toContain('nav.queue');
  });

  it.each(['roadOfficer', 'roadSupervisor', 'triageDesk', 'municipalAdmin', 'auditor'] as const)(
    'hides all three resident-only items from %s', (who) => {
      const e = experienceOf(ACCOUNTS[who]);
      const labels = navFor(e).map((n) => n.label);
      for (const item of RESIDENT_ONLY) expect(labels).not.toContain(item);
      expect(labels).toContain('nav.queue');
      expect(canAccess('report', e)).toBe(false);
      expect(canAccess('services', e)).toBe(false);
      expect(canAccess('myReports', e)).toBe(false);
      expect(homeFor(e)).toBe('/app/queue');
    });

  it('blocks direct routes outside the role', () => {
    expect(canAccess('queue', 'resident')).toBe(false);
    expect(canAccess('analytics', 'resident')).toBe(false);
    expect(canAccess('analytics', 'officer')).toBe(false);
    expect(canAccess('analytics', 'supervisor')).toBe(true);
  });

  it('offers management and export only to roles the server allows', () => {
    expect(capabilities('officer')).toMatchObject({ manage: false, work: true, export: false });
    expect(capabilities('supervisor')).toMatchObject({ manage: true, export: true });
    expect(capabilities('auditor')).toMatchObject({ manage: false, work: false, readOnly: true, export: true });
    expect(capabilities('resident')).toMatchObject({ manage: false, work: false });
  });
});
