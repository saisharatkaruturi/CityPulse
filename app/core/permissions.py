"""Centralised, deny-by-default authorisation.

Two layers:
  * role -> permission matrix (what kinds of action a caller may take at all);
  * row scope (which complaints a caller may see or act on), applied inside DB queries.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from enum import StrEnum

from sqlalchemy import ColumnElement, false, or_

from app.core.errors import Forbidden
from app.domain.enums import Role
from app.models import Complaint, Officer, User


class P(StrEnum):
    complaint_create = "complaint.create"
    complaint_read_scoped = "complaint.read_scoped"  # staff view within scope
    complaint_work = "complaint.work"  # transitions, comments, resolution within scope
    complaint_assign = "complaint.assign"
    complaint_priority_override = "complaint.priority_override"
    complaint_recategorize = "complaint.recategorize"
    complaint_merge = "complaint.merge"
    note_read = "note.read"
    note_write = "note.write"
    comment_moderate = "comment.moderate"
    analytics_read = "analytics.read"
    analytics_export = "analytics.export"
    admin_config = "admin.config"
    admin_roles = "admin.roles"
    audit_read = "audit.read"
    ops_outbox = "ops.outbox"


_STAFF_WORK = {P.complaint_read_scoped, P.complaint_work, P.note_read, P.note_write}
_MANAGER = _STAFF_WORK | {P.complaint_assign, P.complaint_priority_override, P.complaint_recategorize,
                          P.complaint_merge, P.comment_moderate, P.analytics_read}

ROLE_PERMISSIONS: dict[Role, frozenset[P]] = {
    Role.resident: frozenset({P.complaint_create}),
    Role.field_officer: frozenset(_STAFF_WORK | {P.complaint_create}),
    Role.supervisor: frozenset(_MANAGER | {P.complaint_create}),
    Role.municipal_admin: frozenset(_MANAGER | {P.complaint_create, P.analytics_export, P.admin_config}),
    Role.system_admin: frozenset(_MANAGER | {P.complaint_create, P.analytics_export, P.admin_config,
                                             P.admin_roles, P.audit_read, P.ops_outbox}),
    Role.auditor: frozenset({P.complaint_read_scoped, P.note_read, P.analytics_read, P.analytics_export,
                             P.audit_read}),
}

GLOBAL_SCOPE_ROLES = frozenset({Role.municipal_admin, Role.system_admin, Role.auditor})
GLOBAL_WRITE_ROLES = frozenset({Role.municipal_admin, Role.system_admin})


@dataclass
class Principal:
    user: User
    session_id: uuid.UUID | None
    roles: frozenset[Role]
    supervised_department_ids: frozenset[uuid.UUID] = field(default_factory=frozenset)
    officer: Officer | None = None

    @property
    def id(self) -> uuid.UUID:
        return self.user.id

    @property
    def is_staff(self) -> bool:
        return bool(self.roles - {Role.resident})

    @property
    def has_global_read(self) -> bool:
        return bool(self.roles & GLOBAL_SCOPE_ROLES)

    @property
    def has_global_write(self) -> bool:
        return bool(self.roles & GLOBAL_WRITE_ROLES)

    @property
    def permissions(self) -> frozenset[P]:
        perms: set[P] = set()
        for role in self.roles:
            perms |= ROLE_PERMISSIONS.get(role, frozenset())
        return frozenset(perms)

    def can(self, perm: P) -> bool:
        return perm in self.permissions

    def require(self, perm: P) -> None:
        if not self.can(perm):
            raise Forbidden("You do not have permission to perform this action")

    @property
    def scoped_department_ids(self) -> frozenset[uuid.UUID]:
        """Departments where the caller may manage (assign, merge, re-prioritise) complaints."""
        return self.supervised_department_ids


def staff_read_clause(principal: Principal) -> ColumnElement[bool]:
    """SQL predicate for complaints a staff caller may read (excluding own reports)."""
    if not principal.can(P.complaint_read_scoped):
        return false()
    if principal.has_global_read:
        return Complaint.id.is_not(None)
    clauses: list[ColumnElement[bool]] = []
    if principal.supervised_department_ids:
        clauses.append(Complaint.department_id.in_(principal.supervised_department_ids))
    if principal.officer is not None and principal.officer.is_active:
        clauses.append(Complaint.assigned_officer_id == principal.officer.id)
        if principal.officer.team_id is not None:
            clauses.append(Complaint.team_id == principal.officer.team_id)
    return or_(*clauses) if clauses else false()


def complaint_read_clause(principal: Principal) -> ColumnElement[bool]:
    return or_(Complaint.reporter_id == principal.id, staff_read_clause(principal))


def can_staff_read(principal: Principal, c: Complaint) -> bool:
    if not principal.can(P.complaint_read_scoped):
        return False
    if principal.has_global_read:
        return True
    if c.department_id is not None and c.department_id in principal.supervised_department_ids:
        return True
    off = principal.officer
    if off is not None and off.is_active:
        if c.assigned_officer_id == off.id:
            return True
        if off.team_id is not None and c.team_id == off.team_id:
            return True
    return False


def can_staff_work(principal: Principal, c: Complaint) -> bool:
    """Staff may act on a complaint (transition, comment, resolve). Auditors never can."""
    return principal.can(P.complaint_work) and can_staff_read(principal, c)


def can_manage(principal: Principal, c: Complaint, perm: P) -> bool:
    """Manager-level actions: global admins anywhere, supervisors within their departments."""
    if not principal.can(perm):
        return False
    if principal.has_global_write:
        return True
    return c.department_id is not None and c.department_id in principal.supervised_department_ids


def can_read(principal: Principal, c: Complaint) -> bool:
    return c.reporter_id == principal.id or can_staff_read(principal, c)
