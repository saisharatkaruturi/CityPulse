"""Administrative endpoints. Every route checks permissions in the service layer."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Query, Response, status
from sqlalchemy import func, select

from app.api.deps import DB, CurrentUser, PageParams
from app.api.routers.auth import user_out
from app.api.routers.catalog import category_out, service_out
from app.core.errors import NotFound, ValidationFailed
from app.core.permissions import P
from app.core.time import utcnow
from app.domain.enums import AnnouncementState, OutboxState
from app.models import (
    AuditLog,
    Department,
    Officer,
    OutboxEvent,
    RoutingRule,
    SlaPolicy,
    Team,
)
from app.schemas import catalog as s
from app.schemas.auth import UserOut
from app.schemas.common import ERROR_RESPONSES, Page, Reason, StrictInput
from app.services import admin, analytics, audit

router = APIRouter(prefix="/api/admin", tags=["admin"], responses=ERROR_RESPONSES)


def _aware(*dts: datetime | None) -> None:
    for dt in dts:
        if dt is not None and dt.tzinfo is None:
            raise ValidationFailed("Datetimes must include a timezone", code="naive_datetime")


# --- Analytics -------------------------------------------------------------------------------------

@router.get("/analytics", response_model=s.AnalyticsOut,
            summary="Role-scoped metrics computed from stored records (see README definitions)")
def get_analytics(principal: CurrentUser, db: DB, date_from: datetime, date_to: datetime,
                  department_id: uuid.UUID | None = None, category_id: uuid.UUID | None = None,
                  ward_id: uuid.UUID | None = None) -> s.AnalyticsOut:
    _aware(date_from, date_to)
    return s.AnalyticsOut(**analytics.compute(db, principal, date_from, date_to, department_id, category_id,
                                              ward_id))


@router.get("/analytics/export.csv", summary="CSV export (bounded range; formula-injection safe)",
            responses={200: {"content": {"text/csv": {}}}})
def export_csv(principal: CurrentUser, db: DB, date_from: datetime, date_to: datetime,
               department_id: uuid.UUID | None = None) -> Response:
    _aware(date_from, date_to)
    body = analytics.export_csv(db, principal, date_from, date_to, department_id)
    audit.record(db, actor_id=principal.id, action="analytics.export", entity_type="export", entity_id="csv",
                 after={"date_from": date_from.isoformat(), "date_to": date_to.isoformat(),
                        "department_id": str(department_id) if department_id else None})
    db.commit()
    return Response(body, media_type="text/csv",
                    headers={"Content-Disposition": 'attachment; filename="complaints.csv"',
                             "Cache-Control": "no-store"})


# --- Departments, teams, officers -----------------------------------------------------------------

def _dept_out(db: DB, d: Department) -> s.DepartmentOut:
    out = s.DepartmentOut.model_validate(d)
    out.covered_ward_ids = admin.coverage_ids(db, d.id)
    return out


@router.get("/departments", response_model=list[s.DepartmentOut])
def list_departments(principal: CurrentUser, db: DB) -> list[s.DepartmentOut]:
    if not (principal.can(P.admin_config) or principal.can(P.analytics_read)):
        principal.require(P.admin_config)
    q = select(Department).order_by(Department.code)
    if not principal.has_global_read:
        q = q.where(Department.id.in_(principal.supervised_department_ids))
    return [_dept_out(db, d) for d in db.scalars(q).all()]


@router.post("/departments", response_model=s.DepartmentOut, status_code=status.HTTP_201_CREATED)
def create_department(req: s.DepartmentCreate, principal: CurrentUser, db: DB) -> s.DepartmentOut:
    return _dept_out(db, admin.create_department(db, principal, req))


@router.patch("/departments/{dept_id}", response_model=s.DepartmentOut)
def update_department(dept_id: uuid.UUID, req: s.DepartmentUpdate, principal: CurrentUser,
                      db: DB) -> s.DepartmentOut:
    return _dept_out(db, admin.update_department(db, principal, dept_id, req))


@router.get("/teams", response_model=list[s.TeamOut])
def list_teams(principal: CurrentUser, db: DB, department_id: uuid.UUID | None = None) -> list[s.TeamOut]:
    if not principal.can(P.complaint_assign):
        principal.require(P.admin_config)
    q = select(Team).order_by(Team.name)
    if department_id:
        q = q.where(Team.department_id == department_id)
    return [s.TeamOut.model_validate(t) for t in db.scalars(q).all()]


@router.post("/teams", response_model=s.TeamOut, status_code=status.HTTP_201_CREATED)
def create_team(req: s.TeamCreate, principal: CurrentUser, db: DB) -> s.TeamOut:
    return s.TeamOut.model_validate(admin.create_team(db, principal, req))


def _officer_out(o: Officer) -> s.OfficerOut:
    out = s.OfficerOut.model_validate(o)
    out.display_name = o.user.display_name if o.user else None
    return out


@router.get("/officers", response_model=list[s.OfficerOut],
            summary="Officers (supervisors see their departments; admins see all)")
def list_officers(principal: CurrentUser, db: DB, department_id: uuid.UUID | None = None) -> list[s.OfficerOut]:
    if not principal.can(P.complaint_assign):
        principal.require(P.admin_config)
    q = select(Officer)
    if not principal.has_global_read:
        q = q.where(Officer.department_id.in_(principal.supervised_department_ids))
    if department_id:
        q = q.where(Officer.department_id == department_id)
    return [_officer_out(o) for o in db.scalars(q).all()]


@router.post("/officers", response_model=s.OfficerOut, status_code=status.HTTP_201_CREATED)
def create_officer(req: s.OfficerCreate, principal: CurrentUser, db: DB) -> s.OfficerOut:
    return _officer_out(admin.create_officer(db, principal, req))


@router.patch("/officers/{officer_id}", response_model=s.OfficerOut)
def update_officer(officer_id: uuid.UUID, req: s.OfficerUpdate, principal: CurrentUser, db: DB) -> s.OfficerOut:
    return _officer_out(admin.update_officer(db, principal, officer_id, req))


# --- Users & roles ----------------------------------------------------------------------------------

@router.post("/users/{user_id}/roles", response_model=UserOut, summary="Grant a role (system admin only)")
def grant_role(user_id: uuid.UUID, req: s.RoleGrantRequest, principal: CurrentUser, db: DB) -> UserOut:
    return user_out(admin.grant_role(db, principal, user_id, req))


@router.post("/users/{user_id}/roles/revoke", response_model=UserOut, summary="Revoke a role grant")
def revoke_role(user_id: uuid.UUID, req: s.RoleGrantRequest, principal: CurrentUser, db: DB) -> UserOut:
    return user_out(admin.revoke_role(db, principal, user_id, req))


class ActivationRequest(StrictInput):
    active: bool
    reason: Reason


@router.post("/users/{user_id}/activation", response_model=UserOut,
             summary="Deactivate/reactivate an account; history is kept")
def set_activation(user_id: uuid.UUID, req: ActivationRequest, principal: CurrentUser, db: DB) -> UserOut:
    return user_out(admin.set_user_active(db, principal, user_id, req.active, req.reason))


# --- Taxonomy & directory ----------------------------------------------------------------------------

@router.post("/wards", response_model=s.WardOut, status_code=status.HTTP_201_CREATED)
def create_ward(req: s.WardCreate, principal: CurrentUser, db: DB) -> s.WardOut:
    w = admin.create_ward(db, principal, req)
    return s.WardOut(id=w.id, code=w.code, name=w.name, is_active=w.is_active, has_boundary=bool(w.boundary),
                     provenance=w.provenance, is_demo=w.is_demo)


@router.post("/categories", response_model=s.CategoryOut, status_code=status.HTTP_201_CREATED)
def create_category(req: s.CategoryCreate, principal: CurrentUser, db: DB) -> s.CategoryOut:
    return category_out(admin.create_category(db, principal, req), None)


@router.patch("/categories/{category_id}", response_model=s.CategoryOut)
def update_category(category_id: uuid.UUID, req: s.CategoryUpdate, principal: CurrentUser,
                    db: DB) -> s.CategoryOut:
    return category_out(admin.update_category(db, principal, category_id, req), None)


@router.post("/services", response_model=s.ServiceOut, status_code=status.HTTP_201_CREATED,
             summary="Create a service in draft state; publish it with PATCH state=published")
def create_service(req: s.ServiceCreate, principal: CurrentUser, db: DB) -> s.ServiceOut:
    return service_out(admin.create_service(db, principal, req))


@router.patch("/services/{service_id}", response_model=s.ServiceOut)
def update_service(service_id: uuid.UUID, req: s.ServiceUpdate, principal: CurrentUser, db: DB) -> s.ServiceOut:
    return service_out(admin.update_service(db, principal, service_id, req))


# --- Routing & SLA -----------------------------------------------------------------------------------

@router.get("/routing-rules", response_model=list[s.RoutingRuleOut])
def list_rules(principal: CurrentUser, db: DB, include_history: bool = False,
               category_id: uuid.UUID | None = None) -> list[s.RoutingRuleOut]:
    principal.require(P.admin_config)
    q = select(RoutingRule).order_by(RoutingRule.category_id, RoutingRule.precedence, RoutingRule.version)
    if not include_history:
        q = q.where(RoutingRule.is_active.is_(True))
    if category_id:
        q = q.where(RoutingRule.category_id == category_id)
    return [s.RoutingRuleOut.model_validate(r) for r in db.scalars(q).all()]


@router.post("/routing-rules", response_model=s.RoutingRuleOut, status_code=status.HTTP_201_CREATED)
def create_rule(req: s.RoutingRuleCreate, principal: CurrentUser, db: DB) -> s.RoutingRuleOut:
    _aware(req.effective_from, req.effective_to)
    return s.RoutingRuleOut.model_validate(admin.create_rule(db, principal, req))


@router.patch("/routing-rules/{rule_id}", response_model=s.RoutingRuleOut,
              summary="Creates a new version and retires the old one (or deactivates)")
def update_rule(rule_id: uuid.UUID, req: s.RoutingRuleUpdate, principal: CurrentUser, db: DB) -> s.RoutingRuleOut:
    _aware(req.effective_to)
    return s.RoutingRuleOut.model_validate(admin.update_rule(db, principal, rule_id, req))


@router.get("/sla-policies", response_model=list[s.SlaPolicyOut])
def list_sla(principal: CurrentUser, db: DB, include_history: bool = False) -> list[s.SlaPolicyOut]:
    if not principal.can(P.analytics_read):
        principal.require(P.admin_config)
    q = select(SlaPolicy).order_by(SlaPolicy.name, SlaPolicy.version)
    if not include_history:
        q = q.where(SlaPolicy.is_active.is_(True))
    return [s.SlaPolicyOut.model_validate(p) for p in db.scalars(q).all()]


@router.post("/sla-policies", response_model=s.SlaPolicyOut, status_code=status.HTTP_201_CREATED)
def create_sla(req: s.SlaPolicyCreate, principal: CurrentUser, db: DB) -> s.SlaPolicyOut:
    _aware(req.effective_from)
    return s.SlaPolicyOut.model_validate(admin.create_sla(db, principal, req))


@router.patch("/sla-policies/{policy_id}", response_model=s.SlaPolicyOut)
def update_sla(policy_id: uuid.UUID, req: s.SlaPolicyUpdate, principal: CurrentUser, db: DB) -> s.SlaPolicyOut:
    return s.SlaPolicyOut.model_validate(admin.update_sla(db, principal, policy_id, req))


# --- Announcements ------------------------------------------------------------------------------------

@router.post("/announcements", response_model=s.AnnouncementOut, status_code=status.HTTP_201_CREATED)
def create_announcement(req: s.AnnouncementCreate, principal: CurrentUser, db: DB) -> s.AnnouncementOut:
    _aware(req.publish_until)
    return s.AnnouncementOut.model_validate(admin.create_announcement(db, principal, req))


@router.post("/announcements/{ann_id}/state", response_model=s.AnnouncementOut,
             summary="draft -> published -> expired")
def announcement_state(ann_id: uuid.UUID, state: AnnouncementState, principal: CurrentUser,
                       db: DB) -> s.AnnouncementOut:
    return s.AnnouncementOut.model_validate(admin.set_announcement_state(db, principal, ann_id, state))


# --- Audit & operations ----------------------------------------------------------------------------------

@router.get("/audit-logs", response_model=Page[s.AuditLogOut], summary="Audit trail (auditor/system admin)")
def audit_logs(principal: CurrentUser, db: DB, pg: PageParams, entity_type: str | None = None,
               entity_id: Annotated[str | None, Query(max_length=64)] = None) -> Page[s.AuditLogOut]:
    principal.require(P.audit_read)
    q = select(AuditLog)
    if entity_type:
        q = q.where(AuditLog.entity_type == entity_type)
    if entity_id:
        q = q.where(AuditLog.entity_id == entity_id)
    total = db.scalar(select(func.count()).select_from(q.subquery())) or 0
    rows = db.scalars(q.order_by(AuditLog.created_at.desc(), AuditLog.id).offset(pg.offset).limit(pg.page_size))
    return Page[s.AuditLogOut](items=[s.AuditLogOut.model_validate(a) for a in rows], total=total, page=pg.page,
                               page_size=pg.page_size)


@router.get("/outbox", response_model=Page[s.OutboxEventOut], summary="Inspect background events (ops)")
def outbox(principal: CurrentUser, db: DB, pg: PageParams,
           state: OutboxState | None = OutboxState.failed) -> Page[s.OutboxEventOut]:
    principal.require(P.ops_outbox)
    q = select(OutboxEvent)
    if state:
        q = q.where(OutboxEvent.state == state)
    total = db.scalar(select(func.count()).select_from(q.subquery())) or 0
    rows = db.scalars(q.order_by(OutboxEvent.created_at.desc()).offset(pg.offset).limit(pg.page_size))
    return Page[s.OutboxEventOut](items=[s.OutboxEventOut.model_validate(e) for e in rows], total=total,
                                  page=pg.page, page_size=pg.page_size)


@router.post("/outbox/{event_id}/retry", response_model=s.OutboxEventOut,
             summary="Re-queue a failed event after fixing the cause")
def retry_event(event_id: uuid.UUID, principal: CurrentUser, db: DB) -> s.OutboxEventOut:
    principal.require(P.ops_outbox)
    e = db.get(OutboxEvent, event_id)
    if e is None:
        raise NotFound("Event not found")
    if e.state != OutboxState.failed:
        raise ValidationFailed("Only failed events can be retried", code="not_failed")
    e.state = OutboxState.pending
    e.attempt_count = 0
    e.next_attempt_at = utcnow()
    audit.record(db, actor_id=principal.id, action="outbox.retry", entity_type="outbox_event", entity_id=e.id)
    db.commit()
    return s.OutboxEventOut.model_validate(e)
