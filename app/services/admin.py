"""Administrative configuration use cases. Every change is authorised and audited.

Referenced records are deactivated, never deleted. Routing rules and SLA policies are versioned:
an update creates a new row (version + 1) and retires the old one, so past decisions remain
explainable from `complaints.routing_rule_id` / `sla_policy_id`.
"""

from __future__ import annotations

import uuid

from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.errors import Conflict, NotFound, ValidationFailed
from app.core.permissions import P, Principal
from app.core.time import utcnow
from app.domain.enums import AnnouncementState, Role
from app.models import (
    Announcement,
    Category,
    Department,
    DepartmentWardCoverage,
    Officer,
    RoutingRule,
    Service,
    SlaPolicy,
    Team,
    User,
    UserRole,
    Ward,
)
from app.schemas import catalog as s
from app.services import audit
from app.services.auth import ensure_not_last_system_admin


def _get(db: Session, model: type, id_: uuid.UUID, what: str):  # noqa: ANN202
    obj = db.get(model, id_)
    if obj is None:
        raise NotFound(f"{what} not found")
    return obj


def _ref(db: Session, model: type, id_: uuid.UUID | None, field: str, *, active: bool = True) -> None:
    if id_ is None:
        return
    obj = db.get(model, id_)
    if obj is None or (active and hasattr(obj, "is_active") and not obj.is_active):
        raise ValidationFailed(f"Invalid {field}", code="invalid_reference",
                               details=[{"field": field, "issue": "not_found_or_inactive"}])


def _commit(db: Session, what: str) -> None:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise Conflict(f"{what} conflicts with an existing record", code="duplicate") from None


# --- Departments / teams / officers / roles -------------------------------------------------------

def coverage_ids(db: Session, department_id: uuid.UUID) -> list[uuid.UUID]:
    return list(db.scalars(select(DepartmentWardCoverage.ward_id)
                           .where(DepartmentWardCoverage.department_id == department_id)).all())


def _set_coverage(db: Session, dept_id: uuid.UUID, ward_ids: list[uuid.UUID]) -> None:
    for w in ward_ids:
        _ref(db, Ward, w, "covered_ward_ids")
    db.execute(delete(DepartmentWardCoverage).where(DepartmentWardCoverage.department_id == dept_id))
    for w in set(ward_ids):
        db.add(DepartmentWardCoverage(department_id=dept_id, ward_id=w))


def create_department(db: Session, p: Principal, req: s.DepartmentCreate) -> Department:
    p.require(P.admin_config)
    _ref(db, Department, req.parent_id, "parent_id")
    d = Department(code=req.code, name=req.name, description=req.description, public_email=req.public_email,
                   public_phone=req.public_phone, parent_id=req.parent_id)
    db.add(d)
    db.flush()
    _set_coverage(db, d.id, req.covered_ward_ids)
    audit.record(db, actor_id=p.id, action="department.create", entity_type="department", entity_id=d.id,
                 after=req.model_dump(mode="json"))
    _commit(db, "Department")
    return d


def update_department(db: Session, p: Principal, dept_id: uuid.UUID, req: s.DepartmentUpdate) -> Department:
    p.require(P.admin_config)
    d: Department = _get(db, Department, dept_id, "Department")
    fields = ["name", "description", "public_email", "public_phone", "is_active"]
    before = audit.snapshot(d, fields)
    if req.is_active is False and d.is_fallback:
        others = db.scalar(select(Department.id).where(Department.is_fallback.is_(True),
                                                       Department.is_active.is_(True), Department.id != d.id))
        if others is None:
            raise Conflict("Cannot deactivate the only triage/fallback queue", code="last_fallback_queue")
    for f in fields:
        v = getattr(req, f)
        if v is not None:
            setattr(d, f, v)
    if req.covered_ward_ids is not None:
        _set_coverage(db, d.id, req.covered_ward_ids)
    audit.record(db, actor_id=p.id, action="department.update", entity_type="department", entity_id=d.id,
                 reason=req.reason, before=before, after=audit.snapshot(d, fields))
    _commit(db, "Department")
    return d


def create_team(db: Session, p: Principal, req: s.TeamCreate) -> Team:
    p.require(P.admin_config)
    _ref(db, Department, req.department_id, "department_id")
    t = Team(department_id=req.department_id, name=req.name)
    db.add(t)
    db.flush()
    audit.record(db, actor_id=p.id, action="team.create", entity_type="team", entity_id=t.id,
                 after=req.model_dump(mode="json"))
    _commit(db, "Team")
    return t


def create_officer(db: Session, p: Principal, req: s.OfficerCreate) -> Officer:
    p.require(P.admin_config)
    user = db.get(User, req.user_id)
    if user is None or not user.is_active:
        raise ValidationFailed("Unknown or inactive user", code="invalid_reference")
    _ref(db, Department, req.department_id, "department_id")
    if req.team_id:
        team = db.get(Team, req.team_id)
        if team is None or team.department_id != req.department_id:
            raise ValidationFailed("Team does not belong to the department", code="team_department_mismatch")
    _ref(db, Officer, req.supervisor_officer_id, "supervisor_officer_id")
    o = Officer(user_id=req.user_id, department_id=req.department_id, team_id=req.team_id,
                supervisor_officer_id=req.supervisor_officer_id)
    db.add(o)
    if not any(r.role == Role.field_officer for r in user.roles):
        user.roles.append(UserRole(role=Role.field_officer, department_id=req.department_id,
                                   granted_by_id=p.id, created_at=utcnow()))
    db.flush()
    audit.record(db, actor_id=p.id, action="officer.create", entity_type="officer", entity_id=o.id,
                 after=req.model_dump(mode="json"))
    _commit(db, "Officer")
    return o


def update_officer(db: Session, p: Principal, officer_id: uuid.UUID, req: s.OfficerUpdate) -> Officer:
    p.require(P.admin_config)
    o: Officer = _get(db, Officer, officer_id, "Officer")
    fields = ["team_id", "is_active", "accepts_assignments"]
    before = audit.snapshot(o, fields)
    if req.team_id is not None:
        team = db.get(Team, req.team_id)
        if team is None or team.department_id != o.department_id:
            raise ValidationFailed("Team does not belong to the officer's department",
                                   code="team_department_mismatch")
        o.team_id = req.team_id
    if req.is_active is not None:
        o.is_active = req.is_active
    if req.accepts_assignments is not None:
        o.accepts_assignments = req.accepts_assignments
    audit.record(db, actor_id=p.id, action="officer.update", entity_type="officer", entity_id=o.id,
                 reason=req.reason, before=before, after=audit.snapshot(o, fields))
    db.commit()
    return o


def grant_role(db: Session, p: Principal, user_id: uuid.UUID, req: s.RoleGrantRequest) -> User:
    p.require(P.admin_roles)
    user: User = _get(db, User, user_id, "User")
    if req.role == Role.supervisor and req.department_id is None:
        raise ValidationFailed("Supervisor grants require a department_id", code="department_required")
    _ref(db, Department, req.department_id, "department_id")
    _ref(db, Ward, req.ward_id, "ward_id")
    user.roles.append(UserRole(role=req.role, department_id=req.department_id, ward_id=req.ward_id,
                               granted_by_id=p.id, created_at=utcnow()))
    audit.record(db, actor_id=p.id, action="role.grant", entity_type="user", entity_id=user.id, reason=req.reason,
                 after=req.model_dump(mode="json", exclude={"reason"}))
    _commit(db, "Role grant")
    return user


def revoke_role(db: Session, p: Principal, user_id: uuid.UUID, req: s.RoleGrantRequest) -> User:
    p.require(P.admin_roles)
    user: User = _get(db, User, user_id, "User")
    match = [r for r in user.roles if r.role == req.role and r.department_id == req.department_id
             and r.ward_id == req.ward_id]
    if not match:
        raise NotFound("Role grant not found")
    if req.role == Role.system_admin:
        ensure_not_last_system_admin(db, user.id)
    for r in match:
        user.roles.remove(r)
    audit.record(db, actor_id=p.id, action="role.revoke", entity_type="user", entity_id=user.id,
                 reason=req.reason, before=req.model_dump(mode="json", exclude={"reason"}))
    db.commit()
    return user


def set_user_active(db: Session, p: Principal, user_id: uuid.UUID, active: bool, reason: str) -> User:
    p.require(P.admin_roles)
    user: User = _get(db, User, user_id, "User")
    if not active and any(r.role == Role.system_admin for r in user.roles):
        ensure_not_last_system_admin(db, user.id)
    user.is_active = active
    user.deactivated_at = None if active else utcnow()
    audit.record(db, actor_id=p.id, action="user.activate" if active else "user.deactivate",
                 entity_type="user", entity_id=user.id, reason=reason)
    db.commit()
    return user


# --- Wards / categories / services ----------------------------------------------------------------

def create_ward(db: Session, p: Principal, req: s.WardCreate) -> Ward:
    p.require(P.admin_config)
    w = Ward(code=req.code, name=req.name, provenance=req.provenance, boundary=req.boundary)
    db.add(w)
    db.flush()
    audit.record(db, actor_id=p.id, action="ward.create", entity_type="ward", entity_id=w.id,
                 after={"code": req.code, "name": req.name, "provenance": req.provenance,
                        "has_boundary": req.boundary is not None})
    _commit(db, "Ward")
    return w


def create_category(db: Session, p: Principal, req: s.CategoryCreate) -> Category:
    p.require(P.admin_config)
    if req.default_priority.value == "critical":
        raise ValidationFailed("critical cannot be a category default", code="invalid_priority")
    if req.parent_id:
        parent = db.get(Category, req.parent_id)
        if parent is None or not parent.is_active:
            raise ValidationFailed("Invalid parent_id", code="invalid_reference")
        if parent.parent_id is not None:
            raise ValidationFailed("Only two category levels are supported", code="category_depth")
    c = Category(code=req.code, label=req.label, parent_id=req.parent_id, description=req.description,
                 synonyms=req.synonyms, examples=req.examples, labels_i18n=req.labels_i18n,
                 default_priority=req.default_priority, safety_sensitive=req.safety_sensitive)
    db.add(c)
    db.flush()
    audit.record(db, actor_id=p.id, action="category.create", entity_type="category", entity_id=c.id,
                 after=req.model_dump(mode="json"))
    _commit(db, "Category")
    return c


def update_category(db: Session, p: Principal, cat_id: uuid.UUID, req: s.CategoryUpdate) -> Category:
    p.require(P.admin_config)
    c: Category = _get(db, Category, cat_id, "Category")
    fields = ["label", "description", "synonyms", "labels_i18n", "default_priority", "safety_sensitive",
              "is_active"]
    if req.is_active is False and c.is_triage:
        raise Conflict("The triage category cannot be deactivated", code="last_fallback_queue")
    before = audit.snapshot(c, fields)
    for f in fields:
        v = getattr(req, f)
        if v is not None:
            setattr(c, f, v)
    audit.record(db, actor_id=p.id, action="category.update", entity_type="category", entity_id=c.id,
                 reason=req.reason, before=before, after=audit.snapshot(c, fields))
    db.commit()
    return c


def create_service(db: Session, p: Principal, req: s.ServiceCreate) -> Service:
    p.require(P.admin_config)
    _ref(db, Department, req.owner_department_id, "owner_department_id")
    depts = [db.get(Department, d) for d in req.department_ids]
    cats = [db.get(Category, c) for c in req.category_ids]
    if any(x is None for x in depts) or any(x is None for x in cats):
        raise ValidationFailed("Unknown department or category", code="invalid_reference")
    svc = Service(code=req.code, name=req.name, summary=req.summary, instructions=req.instructions,
                  service_type=req.service_type, synonyms=req.synonyms, public_contact=req.public_contact,
                  operating_hours=req.operating_hours, eligibility=req.eligibility,
                  owner_department_id=req.owner_department_id)
    svc.departments = depts
    svc.categories = cats
    db.add(svc)
    db.flush()
    audit.record(db, actor_id=p.id, action="service.create", entity_type="service", entity_id=svc.id,
                 after=req.model_dump(mode="json"))
    _commit(db, "Service")
    return svc


def update_service(db: Session, p: Principal, svc_id: uuid.UUID, req: s.ServiceUpdate) -> Service:
    p.require(P.admin_config)
    svc: Service = _get(db, Service, svc_id, "Service")
    fields = ["name", "summary", "instructions", "state", "synonyms", "public_contact", "operating_hours"]
    before = audit.snapshot(svc, fields)
    for f in fields:
        v = getattr(req, f)
        if v is not None:
            setattr(svc, f, v)
    if req.mark_reviewed:
        svc.last_reviewed_at = utcnow()
    audit.record(db, actor_id=p.id, action="service.update", entity_type="service", entity_id=svc.id,
                 reason=req.reason, before=before, after=audit.snapshot(svc, fields))
    db.commit()
    return svc


# --- Routing rules & SLA policies (versioned) ---------------------------------------------------------

_RULE_FIELDS = ["category_id", "ward_id", "department_id", "team_id", "precedence", "effective_from",
                "effective_to", "is_active", "version"]


def _validate_rule_refs(db: Session, category_id: uuid.UUID, ward_id: uuid.UUID | None, department_id: uuid.UUID,
                        team_id: uuid.UUID | None) -> None:
    _ref(db, Category, category_id, "category_id")
    _ref(db, Ward, ward_id, "ward_id")
    _ref(db, Department, department_id, "department_id")
    if team_id:
        team = db.get(Team, team_id)
        if team is None or team.department_id != department_id or not team.is_active:
            raise ValidationFailed("Team must be active and belong to the department", code="invalid_reference")


def create_rule(db: Session, p: Principal, req: s.RoutingRuleCreate) -> RoutingRule:
    p.require(P.admin_config)
    _validate_rule_refs(db, req.category_id, req.ward_id, req.department_id, req.team_id)
    start = req.effective_from or utcnow()
    if req.effective_to is not None and req.effective_to <= start:
        raise ValidationFailed("effective_to must be after effective_from", code="invalid_range")
    r = RoutingRule(category_id=req.category_id, ward_id=req.ward_id, department_id=req.department_id,
                    team_id=req.team_id, precedence=req.precedence, effective_from=start,
                    effective_to=req.effective_to, notes=req.notes, created_by_id=p.id)
    db.add(r)
    db.flush()
    audit.record(db, actor_id=p.id, action="routing_rule.create", entity_type="routing_rule", entity_id=r.id,
                 after=audit.snapshot(r, _RULE_FIELDS))
    db.commit()
    return r


def update_rule(db: Session, p: Principal, rule_id: uuid.UUID, req: s.RoutingRuleUpdate) -> RoutingRule:
    p.require(P.admin_config)
    old: RoutingRule = _get(db, RoutingRule, rule_id, "Routing rule")
    if not old.is_active:
        raise Conflict("Only the current version of a rule can be changed", code="rule_superseded")
    now = utcnow()
    before = audit.snapshot(old, _RULE_FIELDS)
    old.is_active = False
    old.effective_to = now if old.effective_to is None or old.effective_to > now else old.effective_to
    result = old
    if not req.deactivate:
        dept = req.department_id or old.department_id
        team = req.team_id if req.team_id is not None else (old.team_id if dept == old.department_id else None)
        ward = req.ward_id if req.ward_id is not None else old.ward_id
        _validate_rule_refs(db, old.category_id, ward, dept, team)
        result = RoutingRule(category_id=old.category_id, ward_id=ward, department_id=dept, team_id=team,
                             precedence=req.precedence if req.precedence is not None else old.precedence,
                             effective_from=now, effective_to=req.effective_to, version=old.version + 1,
                             supersedes_id=old.id, notes=old.notes, created_by_id=p.id)
        db.add(result)
        db.flush()
    audit.record(db, actor_id=p.id, action="routing_rule.deactivate" if req.deactivate else "routing_rule.version",
                 entity_type="routing_rule", entity_id=old.id, reason=req.reason, before=before,
                 after=audit.snapshot(result, _RULE_FIELDS) | {"id": str(result.id)})
    db.commit()
    return result


_SLA_FIELDS = ["name", "category_id", "department_id", "priority", "acknowledge_hours", "resolve_hours",
               "pause_when_waiting", "is_active", "version"]


def create_sla(db: Session, p: Principal, req: s.SlaPolicyCreate) -> SlaPolicy:
    p.require(P.admin_config)
    _ref(db, Category, req.category_id, "category_id")
    _ref(db, Department, req.department_id, "department_id")
    pol = SlaPolicy(name=req.name, category_id=req.category_id, department_id=req.department_id,
                    priority=req.priority, acknowledge_hours=req.acknowledge_hours,
                    resolve_hours=req.resolve_hours, pause_when_waiting=req.pause_when_waiting,
                    effective_from=req.effective_from or utcnow(), is_illustrative=req.is_illustrative,
                    created_by_id=p.id)
    db.add(pol)
    db.flush()
    audit.record(db, actor_id=p.id, action="sla_policy.create", entity_type="sla_policy", entity_id=pol.id,
                 after=audit.snapshot(pol, _SLA_FIELDS))
    db.commit()
    return pol


def update_sla(db: Session, p: Principal, pol_id: uuid.UUID, req: s.SlaPolicyUpdate) -> SlaPolicy:
    p.require(P.admin_config)
    old: SlaPolicy = _get(db, SlaPolicy, pol_id, "SLA policy")
    if not old.is_active:
        raise Conflict("Only the current version of a policy can be changed", code="policy_superseded")
    now = utcnow()
    before = audit.snapshot(old, _SLA_FIELDS)
    old.is_active = False
    old.effective_to = now
    result = old
    if not req.deactivate:
        ack = req.acknowledge_hours or old.acknowledge_hours
        res = req.resolve_hours or old.resolve_hours
        if ack > res:
            raise ValidationFailed("acknowledge_hours cannot exceed resolve_hours", code="invalid_policy")
        result = SlaPolicy(name=old.name, category_id=old.category_id, department_id=old.department_id,
                           priority=old.priority, acknowledge_hours=ack, resolve_hours=res,
                           pause_when_waiting=old.pause_when_waiting if req.pause_when_waiting is None
                           else req.pause_when_waiting, effective_from=now, version=old.version + 1,
                           supersedes_id=old.id, is_illustrative=old.is_illustrative, created_by_id=p.id)
        db.add(result)
        db.flush()
    audit.record(db, actor_id=p.id, action="sla_policy.version", entity_type="sla_policy", entity_id=old.id,
                 reason=req.reason, before=before, after=audit.snapshot(result, _SLA_FIELDS))
    db.commit()
    return result


# --- Announcements ---------------------------------------------------------------------------------

def create_announcement(db: Session, p: Principal, req: s.AnnouncementCreate) -> Announcement:
    p.require(P.admin_config)
    _ref(db, Ward, req.ward_id, "ward_id")
    a = Announcement(title=req.title, body=req.body, ward_id=req.ward_id, publish_until=req.publish_until,
                     publisher_id=p.id)
    db.add(a)
    db.flush()
    audit.record(db, actor_id=p.id, action="announcement.create", entity_type="announcement", entity_id=a.id)
    db.commit()
    return a


def set_announcement_state(db: Session, p: Principal, ann_id: uuid.UUID, state: AnnouncementState) -> Announcement:
    p.require(P.admin_config)
    a: Announcement = _get(db, Announcement, ann_id, "Announcement")
    allowed = {AnnouncementState.draft: {AnnouncementState.published},
               AnnouncementState.published: {AnnouncementState.expired}, AnnouncementState.expired: set()}
    if state not in allowed[a.state]:
        raise Conflict(f"Cannot move announcement from {a.state.value} to {state.value}", code="invalid_transition")
    before = {"state": a.state.value}
    a.state = state
    if state == AnnouncementState.published:
        a.publish_from = utcnow()
    audit.record(db, actor_id=p.id, action="announcement.state", entity_type="announcement", entity_id=a.id,
                 before=before, after={"state": state.value})
    db.commit()
    return a
