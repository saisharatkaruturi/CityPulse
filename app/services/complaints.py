"""Complaint use cases. HTTP handlers stay thin and call into here.

Every state-changing use case:
  * checks authorisation and row scope server-side;
  * validates the workflow transition through app/domain/workflow.py;
  * writes the change, its history row(s), audit entry and outbox event in ONE transaction.
"""

from __future__ import annotations

import hashlib
import json
import logging
import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta

from sqlalchemy import Select, case, func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.adapters.providers import ProviderUnavailable, get_providers
from app.core.config import get_settings
from app.core.errors import AppError, Conflict, Forbidden, NotFound, ValidationFailed
from app.core.permissions import (
    P,
    Principal,
    can_manage,
    can_read,
    can_staff_read,
    can_staff_work,
    complaint_read_clause,
)
from app.core.time import utcnow
from app.domain import workflow
from app.domain.enums import (
    OPEN_STATUSES,
    PRIORITY_ORDER,
    ActorKind,
    ComplaintStatus,
    ExternalSyncState,
    LinkType,
    LocationSource,
    MediaKind,
    Priority,
    RoutingOutcome,
    SourceChannel,
    Visibility,
)
from app.domain.priority import default_priority, is_alert_priority
from app.models import (
    Category,
    Complaint,
    ComplaintAssignment,
    ComplaintCategoryChange,
    ComplaintComment,
    ComplaintInternalNote,
    ComplaintLink,
    ComplaintMedia,
    ComplaintPriorityChange,
    ComplaintStatusHistory,
    ComplaintSupporter,
    Department,
    Feedback,
    IdempotencyRecord,
    Officer,
    Team,
    User,
)
from app.schemas.complaints import (
    AssignRequest,
    ComplaintCreate,
    FeedbackCreate,
    ResidentComplaintUpdate,
    StaffComplaintUpdate,
)
from app.services import audit, intelligence, routing, sla
from app.services import outbox as ev

logger = logging.getLogger("app.complaints")

REFERENCE_ALPHABET = "23456789ABCDEFGHJKMNPQRSTVWXYZ"  # no 0/O/1/I/L/U ambiguity
MAX_REASSIGNMENTS = 10
IDEMPOTENCY_TTL = timedelta(hours=24)
RESIDENT_EDITABLE = {ComplaintStatus.submitted, ComplaintStatus.under_review}


def new_reference() -> str:
    return "YCS-" + "".join(secrets.choice(REFERENCE_ALPHABET) for _ in range(8))


# --- Loading & visibility --------------------------------------------------------------------------

def get_visible(db: Session, principal: Principal, complaint_id: uuid.UUID) -> Complaint:
    """404 (not 403) for complaints the caller may not see, to avoid confirming existence."""
    c = db.get(Complaint, complaint_id)
    if c is None or not can_read(principal, c):
        raise NotFound("Complaint not found")
    return c


def _check_version(c: Complaint, expected_version: int | None) -> None:
    if expected_version is not None and expected_version != c.version:
        raise Conflict("The complaint changed since you loaded it; reload and retry", code="stale_version")


def _actor_for(principal: Principal, c: Complaint) -> str:
    if can_staff_work(principal, c):
        return workflow.Actor.STAFF
    if c.reporter_id == principal.id:
        return workflow.Actor.RESIDENT
    raise NotFound("Complaint not found") if not can_read(principal, c) else Forbidden(
        "You may not change this complaint")


def _change_status(db: Session, c: Complaint, to: ComplaintStatus, *, actor: str, actor_id: uuid.UUID | None,
                   reason: str | None, now: datetime, emit: bool = True) -> None:
    try:
        workflow.check_transition(c.status, to, actor, reason)
    except workflow.TransitionError as exc:
        raise Conflict(exc.message, code=exc.code) if exc.code != "reason_required" else ValidationFailed(
            exc.message, code=exc.code, details=[{"field": "reason", "issue": "required"}]) from None
    old = c.status
    c.status = to
    if to in (ComplaintStatus.under_review, ComplaintStatus.assigned, ComplaintStatus.in_progress) \
            and c.acknowledged_at is None and actor != workflow.Actor.RESIDENT:
        c.acknowledged_at = now
    if to == ComplaintStatus.resolved:
        c.resolved_at = now
    elif to == ComplaintStatus.closed:
        c.closed_at = now
    elif to == ComplaintStatus.reopened:
        c.reopen_count += 1
        c.closed_at = None
        c.resident_confirmed_at = None
    sla.on_status_change(db, c, old, to, now)
    db.add(ComplaintStatusHistory(
        complaint_id=c.id, from_status=old, to_status=to, actor_id=actor_id,
        actor_kind=ActorKind.system if actor == workflow.Actor.SYSTEM else ActorKind.human,
        reason=reason, created_at=now))
    if emit:
        event = {ComplaintStatus.resolved: ev.COMPLAINT_RESOLVED,
                 ComplaintStatus.reopened: ev.COMPLAINT_REOPENED,
                 ComplaintStatus.awaiting_resident: ev.COMPLAINT_INFO_REQUESTED}.get(to, ev.COMPLAINT_STATUS_CHANGED)
        ev.emit(db, event, c.id, {"reference": c.reference, "from_status": old.value, "to_status": to.value,
                                  "actor_id": str(actor_id) if actor_id else None})


# --- Creation --------------------------------------------------------------------------------------

def _fingerprint(req: ComplaintCreate) -> str:
    return hashlib.sha256(json.dumps(req.model_dump(mode="json"), sort_keys=True).encode()).hexdigest()


def _find_idempotent(db: Session, user_id: uuid.UUID, key: str, fingerprint: str) -> Complaint | None:
    rec = db.scalar(select(IdempotencyRecord).where(IdempotencyRecord.user_id == user_id,
                                                    IdempotencyRecord.operation == "complaint.create",
                                                    IdempotencyRecord.key == key))
    if rec is None or rec.expires_at <= utcnow():
        if rec is not None:
            db.delete(rec)
            db.flush()
        return None
    if rec.request_fingerprint != fingerprint:
        raise ValidationFailed("Idempotency-Key was already used with a different request",
                               code="idempotency_key_reuse")
    return db.get(Complaint, rec.resource_id)


def _validated_category(db: Session, category_id: uuid.UUID | None, field: str = "category_id") -> Category | None:
    if category_id is None:
        return None
    cat = db.get(Category, category_id)
    if cat is None or not cat.is_active:
        raise ValidationFailed("Unknown or inactive category", code="invalid_category",
                               details=[{"field": field, "issue": "invalid"}])
    return cat


def _claim_media(db: Session, principal: Principal, media_ids: list[uuid.UUID], kind: MediaKind,
                 complaint_id: uuid.UUID, now: datetime, field: str) -> None:
    if not media_ids:
        return
    if len(set(media_ids)) != len(media_ids):
        raise ValidationFailed("Duplicate media ids", code="invalid_media", details=[{"field": field}])
    rows = db.scalars(select(ComplaintMedia).where(ComplaintMedia.id.in_(media_ids))).all()
    by_id = {m.id: m for m in rows}
    for mid in media_ids:
        m = by_id.get(mid)
        if m is None or m.uploader_id != principal.id or m.complaint_id is not None or m.kind != kind:
            raise ValidationFailed("Media not found, not yours, already attached, or wrong kind",
                                   code="invalid_media", details=[{"field": field, "issue": str(mid)}])
        m.complaint_id = complaint_id
        m.attached_at = now


def create_complaint(db: Session, principal: Principal, req: ComplaintCreate,
                     idempotency_key: str | None) -> tuple[Complaint, bool]:
    principal.require(P.complaint_create)
    fingerprint = _fingerprint(req)
    if idempotency_key:
        existing = _find_idempotent(db, principal.id, idempotency_key, fingerprint)
        if existing is not None:
            return existing, True
    for attempt in range(3):
        try:
            return _create_once(db, principal, req, idempotency_key, fingerprint), False
        except IntegrityError as exc:
            db.rollback()
            if idempotency_key:
                existing = _find_idempotent(db, principal.id, idempotency_key, fingerprint)
                if existing is not None:
                    return existing, True
            if "reference" not in str(exc.orig).lower() or attempt == 2:
                raise
    raise AppError("Could not allocate a reference", code="internal_error", status_code=500)


def _create_once(db: Session, principal: Principal, req: ComplaintCreate, idempotency_key: str | None,
                 fingerprint: str) -> Complaint:
    settings = get_settings()
    now = utcnow()
    reported = _validated_category(db, req.category_id)
    loc = req.location
    lat = loc.latitude if loc else None
    lng = loc.longitude if loc else None
    jurisdiction = routing.resolve_jurisdiction(db, loc.ward_id if loc else None, lat, lng)

    category = reported
    category_source = "resident"
    suggestion = None
    if category is None:
        suggestion = intelligence.suggest_category(db, f"{req.title}. {req.description}")
        if suggestion.accepted and suggestion.best:
            category = suggestion.best.category
            category_source = f"auto:{suggestion.provider}"
        else:
            category_source = "none"

    decision = routing.decide(db, category, jurisdiction, now)
    department_id = decision.department_id
    if decision.outcome == RoutingOutcome.fallback:
        fb = routing.fallback_department(db)
        department_id = fb.id if fb else None

    priority, priority_reason = default_priority(category.default_priority if category else None,
                                                 bool(category and category.safety_sensitive), req.safety_risk)
    address = loc.address_text if loc else None
    geocoder = get_providers().geocoder
    if address is None and lat is not None and lng is not None and geocoder is not None:
        try:
            address = geocoder.reverse(lat, lng)  # display hint only
        except ProviderUnavailable:
            logger.warning("geocoder_unavailable")

    location_source = loc.source if loc else LocationSource.none
    if loc and loc.ward_id and lat is None:
        location_source = LocationSource.ward_selection

    c = Complaint(
        id=uuid.uuid4(), reference=new_reference(), reporter_id=principal.id, title=req.title,
        description=req.description, original_language=req.language,
        reported_category_id=reported.id if reported else None,
        category_id=category.id if category else None, category_source=category_source,
        ward_id=jurisdiction.ward_id, latitude=lat, longitude=lng,
        location_accuracy_m=loc.accuracy_m if loc else None, location_source=location_source,
        address_text=address, visibility=req.visibility, priority=priority, priority_reason=priority_reason,
        safety_risk_reported=req.safety_risk, status=ComplaintStatus.submitted,
        source_channel=SourceChannel.staff_entry if principal.is_staff else req.source_channel,
        department_id=department_id, team_id=decision.team_id, routing_rule_id=decision.rule_id,
        routing_outcome=decision.outcome, routing_explanation=decision.explanation,
        initial_routing={**decision.as_dict(), "jurisdiction": jurisdiction.method,
                         "category_source": category_source, "decided_at": now.isoformat()},
        routed_at=now, created_at=now, updated_at=now,
        external_sync_state=ExternalSyncState.pending if settings.municipal_integration != "disabled"
        else ExternalSyncState.not_configured,
    )
    db.add(c)
    db.flush()
    sla.apply_policy(db, c, now)
    db.add(ComplaintStatusHistory(complaint_id=c.id, from_status=None, to_status=ComplaintStatus.submitted,
                                  actor_id=principal.id, actor_kind=ActorKind.human,
                                  reason=None, created_at=now))
    db.add(ComplaintAssignment(complaint_id=c.id, to_department_id=department_id, to_team_id=decision.team_id,
                               kind="routing", routing_rule_id=decision.rule_id, actor_kind=ActorKind.system,
                               reason=f"{decision.reason_code}: {decision.explanation}", created_at=now))
    if suggestion is not None:
        intelligence.record_classification(db, suggestion, c.id, req.description,
                                           category.id if category else None)
    _claim_media(db, principal, req.media_ids, MediaKind.report_photo, c.id, now, "media_ids")
    if idempotency_key:
        db.add(IdempotencyRecord(user_id=principal.id, operation="complaint.create", key=idempotency_key,
                                 request_fingerprint=fingerprint, resource_id=c.id, created_at=now,
                                 expires_at=now + IDEMPOTENCY_TTL))
    ev.emit(db, ev.COMPLAINT_SUBMITTED, c.id, {
        "reference": c.reference, "routed": decision.outcome == RoutingOutcome.routed,
        "actor_id": str(principal.id)})
    if is_alert_priority(priority):
        ev.emit(db, ev.COMPLAINT_HIGH_PRIORITY, c.id, {"reference": c.reference, "priority": priority.value})
    if c.external_sync_state == ExternalSyncState.pending:
        ev.emit(db, ev.EXTERNAL_SYNC_REQUESTED, c.id, {"reference": c.reference})
    db.commit()
    return c


# --- Listing ---------------------------------------------------------------------------------------

@dataclass
class ComplaintFilters:
    status: list[ComplaintStatus] | None = None
    category_id: uuid.UUID | None = None
    department_id: uuid.UUID | None = None
    assigned_officer_id: uuid.UUID | None = None
    priority: Priority | None = None
    ward_id: uuid.UUID | None = None
    created_from: datetime | None = None
    created_to: datetime | None = None
    q: str | None = None
    overdue: bool | None = None
    mine: bool = False
    unassigned: bool | None = None
    sort: str = "-created_at"


SORTS = {"created_at", "-created_at", "priority", "-priority", "due_at", "-due_at", "updated_at", "-updated_at"}


def _priority_rank():  # noqa: ANN202
    return case({p.value: r for p, r in PRIORITY_ORDER.items()}, value=Complaint.priority)


def list_query(principal: Principal, f: ComplaintFilters) -> Select:
    q = select(Complaint).where(complaint_read_clause(principal))
    if f.mine:
        q = q.where(Complaint.reporter_id == principal.id)
    if f.status:
        q = q.where(Complaint.status.in_(f.status))
    if f.category_id:
        q = q.where(Complaint.category_id == f.category_id)
    if f.department_id:
        q = q.where(Complaint.department_id == f.department_id)
    if f.assigned_officer_id:
        q = q.where(Complaint.assigned_officer_id == f.assigned_officer_id)
    if f.unassigned is not None:
        q = q.where(Complaint.assigned_officer_id.is_(None) if f.unassigned
                    else Complaint.assigned_officer_id.is_not(None))
    if f.priority:
        q = q.where(Complaint.priority == f.priority)
    if f.ward_id:
        q = q.where(Complaint.ward_id == f.ward_id)
    if f.created_from:
        q = q.where(Complaint.created_at >= f.created_from)
    if f.created_to:
        q = q.where(Complaint.created_at < f.created_to)
    if f.overdue is not None:
        q = q.where(Complaint.is_overdue.is_(f.overdue))
    if f.q:
        term = f"%{f.q.strip()[:100].replace('%', '').replace('_', '')}%"
        q = q.where(or_(Complaint.title.ilike(term), Complaint.description.ilike(term),
                        Complaint.reference.ilike(term)))
    col = f.sort.lstrip("-")
    expr = _priority_rank() if col == "priority" else getattr(Complaint, col)
    order = expr.desc() if f.sort.startswith("-") else expr.asc()
    return q.order_by(order, Complaint.id)


def list_complaints(db: Session, principal: Principal, f: ComplaintFilters, offset: int,
                    limit: int) -> tuple[list[Complaint], int]:
    q = list_query(principal, f)
    total = db.scalar(select(func.count()).select_from(q.order_by(None).subquery())) or 0
    return list(db.scalars(q.offset(offset).limit(limit)).all()), total


# --- Edits ------------------------------------------------------------------------------------------

def resident_update(db: Session, principal: Principal, c: Complaint, req: ResidentComplaintUpdate,
                    expected_version: int | None) -> Complaint:
    if c.reporter_id != principal.id:
        raise Forbidden("Only the reporter can edit these fields")
    if c.status not in RESIDENT_EDITABLE:
        raise Conflict("The report can no longer be edited; add a comment instead", code="not_editable")
    _check_version(c, expected_version)
    data = req.model_dump(exclude_unset=True, exclude_none=True)
    if not data:
        raise ValidationFailed("No changes supplied", code="no_changes")
    before = audit.snapshot(c, list(data))
    for k, v in data.items():
        setattr(c, k, v)
    audit.record(db, actor_id=principal.id, action="complaint.resident_edit", entity_type="complaint",
                 entity_id=c.id, before=before, after=audit.snapshot(c, list(data)))
    db.commit()
    return c


def staff_update(db: Session, principal: Principal, c: Complaint, req: StaffComplaintUpdate,
                 expected_version: int | None) -> Complaint:
    if not can_staff_read(principal, c):
        raise Forbidden("Only staff can change category, priority or visibility")
    _check_version(c, expected_version)
    now = utcnow()
    changed = False
    if req.category_id is not None and req.category_id != c.category_id:
        if not can_manage(principal, c, P.complaint_recategorize):
            raise Forbidden("You may not change the category of this complaint")
        new_cat = _validated_category(db, req.category_id)
        assert new_cat is not None
        rerouted = False
        old_cat = c.category_id
        c.category_id = new_cat.id
        c.category_source = "staff"
        if req.reroute and c.status in OPEN_STATUSES:
            rerouted = _reroute(db, principal, c, new_cat, req.reason, now)
        db.add(ComplaintCategoryChange(complaint_id=c.id, from_category_id=old_cat, to_category_id=new_cat.id,
                                       actor_id=principal.id, reason=req.reason, rerouted=rerouted,
                                       created_at=now))
        sla.apply_policy(db, c, now)
        changed = True
    if req.priority is not None and req.priority != c.priority:
        if not can_manage(principal, c, P.complaint_priority_override):
            raise Forbidden("You may not change the priority of this complaint")
        db.add(ComplaintPriorityChange(complaint_id=c.id, from_priority=c.priority, to_priority=req.priority,
                                       actor_id=principal.id, reason=req.reason, created_at=now))
        raised = PRIORITY_ORDER[req.priority] > PRIORITY_ORDER[c.priority]
        c.priority = req.priority
        c.priority_reason = f"staff override: {req.reason}"[:300]
        sla.apply_policy(db, c, now)
        if raised and is_alert_priority(req.priority):
            ev.emit(db, ev.COMPLAINT_HIGH_PRIORITY, c.id, {"reference": c.reference,
                                                          "priority": req.priority.value,
                                                          "actor_id": str(principal.id)})
        changed = True
    if req.visibility is not None and req.visibility != c.visibility:
        if not can_manage(principal, c, P.comment_moderate):
            raise Forbidden("You may not change the visibility of this complaint")
        audit.record(db, actor_id=principal.id, action="complaint.visibility", entity_type="complaint",
                     entity_id=c.id, reason=req.reason, before={"visibility": c.visibility.value},
                     after={"visibility": req.visibility.value})
        c.visibility = req.visibility
        changed = True
    if not changed:
        raise ValidationFailed("No changes supplied", code="no_changes")
    audit.record(db, actor_id=principal.id, action="complaint.staff_edit", entity_type="complaint",
                 entity_id=c.id, reason=req.reason,
                 after={"category_id": str(c.category_id) if c.category_id else None,
                        "priority": c.priority.value, "department_id": str(c.department_id)
                        if c.department_id else None})
    db.commit()
    return c


def _reroute(db: Session, principal: Principal, c: Complaint, category: Category, reason: str,
             now: datetime) -> bool:
    jurisdiction = routing.Jurisdiction(c.ward_id, False, "existing")
    decision = routing.decide(db, category, jurisdiction, now)
    if decision.outcome != RoutingOutcome.routed or decision.department_id == c.department_id:
        c.routing_explanation = f"Re-evaluated after category change: {decision.explanation}"[:500]
        return False
    db.add(ComplaintAssignment(
        complaint_id=c.id, from_department_id=c.department_id, to_department_id=decision.department_id,
        from_team_id=c.team_id, to_team_id=decision.team_id, from_officer_id=c.assigned_officer_id,
        to_officer_id=None, kind="reroute", routing_rule_id=decision.rule_id, actor_id=principal.id,
        actor_kind=ActorKind.human, reason=reason, created_at=now))
    c.department_id = decision.department_id
    c.team_id = decision.team_id
    c.assigned_officer_id = None
    c.routing_rule_id = decision.rule_id
    c.routing_outcome = decision.outcome
    c.routing_explanation = f"Re-routed after category change: {decision.explanation}"[:500]
    if c.status in (ComplaintStatus.assigned, ComplaintStatus.in_progress):
        _change_status(db, c, ComplaintStatus.under_review, actor=workflow.Actor.STAFF, actor_id=principal.id,
                       reason=f"Re-routed: {reason}", now=now)
    ev.emit(db, ev.COMPLAINT_REASSIGNED, c.id, {"reference": c.reference, "actor_id": str(principal.id)})
    return True


# --- Workflow use cases ----------------------------------------------------------------------------

def transition(db: Session, principal: Principal, c: Complaint, to: ComplaintStatus, reason: str | None,
               expected_version: int | None) -> Complaint:
    """Generic validated transition. Resolution, reopening and closing have dedicated use cases."""
    if to in (ComplaintStatus.resolved, ComplaintStatus.reopened, ComplaintStatus.closed,
              ComplaintStatus.assigned):
        raise ValidationFailed(f"Use the dedicated endpoint to move to {to.value}", code="use_dedicated_endpoint")
    actor = _actor_for(principal, c)
    _check_version(c, expected_version)
    if to == ComplaintStatus.in_progress and c.assigned_officer_id is None:
        raise Conflict("Assign an officer before starting work", code="not_assigned")
    _change_status(db, c, to, actor=actor, actor_id=principal.id, reason=reason, now=utcnow())
    db.commit()
    return c


def withdraw(db: Session, principal: Principal, c: Complaint, reason: str | None) -> Complaint:
    actor = workflow.Actor.RESIDENT if c.reporter_id == principal.id else _actor_for(principal, c)
    _change_status(db, c, ComplaintStatus.withdrawn, actor=actor, actor_id=principal.id, reason=reason,
                   now=utcnow())
    db.commit()
    return c


def _validate_target(db: Session, principal: Principal, c: Complaint, req: AssignRequest
                     ) -> tuple[uuid.UUID | None, uuid.UUID | None, uuid.UUID | None]:
    officer = team = None
    dept_id = req.department_id or c.department_id
    if req.officer_id:
        officer = db.get(Officer, req.officer_id)
        if officer is None:
            raise ValidationFailed("Unknown officer", code="invalid_officer",
                                   details=[{"field": "officer_id", "issue": "not_found"}])
        user = db.get(User, officer.user_id)
        if not officer.is_active or not officer.accepts_assignments or user is None or not user.is_active:
            raise Conflict("Officer is inactive or not accepting assignments", code="officer_unavailable")
        if req.department_id and officer.department_id != req.department_id:
            raise ValidationFailed("Officer does not belong to that department", code="officer_department_mismatch")
        dept_id = officer.department_id
    if req.team_id:
        team = db.get(Team, req.team_id)
        if team is None or not team.is_active:
            raise ValidationFailed("Unknown or inactive team", code="invalid_team")
        if dept_id and team.department_id != dept_id:
            raise ValidationFailed("Team does not belong to that department", code="team_department_mismatch")
        dept_id = team.department_id
        if officer and officer.team_id and officer.team_id != team.id:
            raise ValidationFailed("Officer is not in that team", code="officer_team_mismatch")
    if dept_id is None:
        raise ValidationFailed("A department is required", code="department_required")
    dept = db.get(Department, dept_id)
    if dept is None or not dept.is_active:
        raise Conflict("Department is inactive", code="department_inactive")
    if not principal.has_global_write and dept_id not in principal.supervised_department_ids:
        raise Forbidden("Target department is outside your scope")
    team_id = team.id if team else (officer.team_id if officer else None)
    return dept_id, team_id, (officer.id if officer else None)


def assign(db: Session, principal: Principal, c: Complaint, req: AssignRequest, reason: str | None,
           *, reassign: bool, expected_version: int | None) -> Complaint:
    if not can_staff_read(principal, c):
        raise NotFound("Complaint not found")
    if not can_manage(principal, c, P.complaint_assign):
        raise Forbidden("You may not assign this complaint")
    if c.status not in OPEN_STATUSES:
        raise Conflict(f"Cannot assign a complaint that is {c.status.value}", code="invalid_state")
    _check_version(c, expected_version)
    if not reassign and c.assigned_officer_id is not None:
        raise Conflict("Already assigned; use reassign with a reason", code="already_assigned")
    if reassign and not (reason and reason.strip()):
        raise ValidationFailed("A reason is required to reassign", code="reason_required")
    dept_id, team_id, officer_id = _validate_target(db, principal, c, req)
    if (dept_id, team_id, officer_id) == (c.department_id, c.team_id, c.assigned_officer_id):
        raise Conflict("Complaint is already assigned to that target", code="no_change")
    if reassign and c.reassignment_count >= MAX_REASSIGNMENTS:
        raise Conflict("Reassignment limit reached; escalate to an administrator", code="reassignment_limit")
    now = utcnow()
    db.add(ComplaintAssignment(
        complaint_id=c.id, from_department_id=c.department_id, to_department_id=dept_id,
        from_team_id=c.team_id, to_team_id=team_id, from_officer_id=c.assigned_officer_id,
        to_officer_id=officer_id, kind="reassign" if reassign else "assign", actor_id=principal.id,
        actor_kind=ActorKind.human, reason=reason, created_at=now))
    if reassign:
        c.reassignment_count += 1
    dept_changed = dept_id != c.department_id
    c.department_id, c.team_id, c.assigned_officer_id = dept_id, team_id, officer_id
    if dept_changed:
        dept = db.get(Department, dept_id)
        c.routing_outcome = RoutingOutcome.fallback if dept and dept.is_fallback else RoutingOutcome.routed
        c.routing_explanation = f"Manually {'re' if reassign else ''}assigned by staff"
    if officer_id and c.status in (ComplaintStatus.submitted, ComplaintStatus.under_review,
                                   ComplaintStatus.reopened, ComplaintStatus.awaiting_resident):
        _change_status(db, c, ComplaintStatus.assigned, actor=workflow.Actor.STAFF, actor_id=principal.id,
                       reason=reason, now=now, emit=False)
    elif officer_id is None and c.status in (ComplaintStatus.assigned, ComplaintStatus.in_progress):
        _change_status(db, c, ComplaintStatus.under_review, actor=workflow.Actor.STAFF, actor_id=principal.id,
                       reason=reason or "Assignment moved to a queue", now=now, emit=False)
    elif c.status == ComplaintStatus.submitted:
        _change_status(db, c, ComplaintStatus.under_review, actor=workflow.Actor.STAFF, actor_id=principal.id,
                       reason=None, now=now, emit=False)
    ev.emit(db, ev.COMPLAINT_REASSIGNED if reassign else ev.COMPLAINT_ASSIGNED, c.id,
            {"reference": c.reference, "actor_id": str(principal.id)})
    audit.record(db, actor_id=principal.id, action="complaint.reassign" if reassign else "complaint.assign",
                 entity_type="complaint", entity_id=c.id, reason=reason,
                 after={"department_id": str(dept_id), "team_id": str(team_id) if team_id else None,
                        "officer_id": str(officer_id) if officer_id else None})
    db.commit()
    return c


def resolve(db: Session, principal: Principal, c: Complaint, notes: str | None,
            evidence_ids: list[uuid.UUID], expected_version: int | None) -> Complaint:
    if not can_staff_work(principal, c):
        raise NotFound("Complaint not found") if not can_read(principal, c) else Forbidden(
            "Only assigned staff can resolve this complaint")
    _check_version(c, expected_version)
    if get_settings().require_resolution_notes and not (notes and notes.strip()):
        raise ValidationFailed("Resolution notes are required", code="resolution_notes_required",
                               details=[{"field": "resolution_notes", "issue": "required"}])
    now = utcnow()
    _change_status(db, c, ComplaintStatus.resolved, actor=workflow.Actor.STAFF, actor_id=principal.id,
                   reason=notes, now=now)
    c.resolution_notes = notes
    _claim_media(db, principal, evidence_ids, MediaKind.resolution_evidence, c.id, now, "evidence_media_ids")
    db.commit()
    return c


def close(db: Session, principal: Principal, c: Complaint, reason: str | None) -> Complaint:
    actor = _actor_for(principal, c)
    now = utcnow()
    _change_status(db, c, ComplaintStatus.closed, actor=actor, actor_id=principal.id, reason=reason, now=now)
    if actor == workflow.Actor.RESIDENT:
        c.resident_confirmed_at = now
    db.commit()
    return c


def reopen(db: Session, principal: Principal, c: Complaint, reason: str) -> Complaint:
    actor = _actor_for(principal, c)
    if c.merged_into_id is not None:
        raise Conflict("This report was merged; follow the report it was merged into", code="merged")
    now = utcnow()
    if actor == workflow.Actor.RESIDENT:
        window = timedelta(days=get_settings().reopen_window_days)
        if c.resolved_at is None or now - c.resolved_at > window:
            raise Conflict("The reopening window has passed; please submit a new report",
                           code="reopen_window_expired")
    _change_status(db, c, ComplaintStatus.reopened, actor=actor, actor_id=principal.id, reason=reason, now=now)
    db.commit()
    return c


# --- Comments & notes ------------------------------------------------------------------------------

def add_comment(db: Session, principal: Principal, c: Complaint, body: str,
                request_information: bool) -> ComplaintComment:
    staff = can_staff_work(principal, c)
    if not staff and c.reporter_id != principal.id:
        if can_read(principal, c):
            raise Forbidden("You may not comment on this complaint")
        raise NotFound("Complaint not found")
    if c.status in (ComplaintStatus.rejected, ComplaintStatus.withdrawn) or c.merged_into_id:
        raise Conflict("Comments are closed for this complaint", code="comments_closed")
    if request_information and not staff:
        raise Forbidden("Only staff can request information")
    now = utcnow()
    comment = ComplaintComment(complaint_id=c.id, author_id=principal.id, author_is_staff=staff, body=body,
                               is_information_request=request_information, created_at=now, updated_at=now)
    db.add(comment)
    if request_information:
        _change_status(db, c, ComplaintStatus.awaiting_resident, actor=workflow.Actor.STAFF,
                       actor_id=principal.id, reason=body[:1000], now=now)
    elif not staff and c.status == ComplaintStatus.awaiting_resident:
        back = ComplaintStatus.in_progress if c.assigned_officer_id else ComplaintStatus.under_review
        _change_status(db, c, back, actor=workflow.Actor.SYSTEM, actor_id=None,
                       reason="Resident replied to information request", now=now)
    else:
        ev.emit(db, ev.COMPLAINT_COMMENTED, c.id, {"reference": c.reference, "author_is_staff": staff,
                                                   "actor_id": str(principal.id)})
    db.commit()
    return comment


def list_comments(db: Session, principal: Principal, c: Complaint) -> list[ComplaintComment]:
    q = select(ComplaintComment).where(ComplaintComment.complaint_id == c.id)
    if not can_staff_read(principal, c):
        q = q.where(ComplaintComment.is_hidden.is_(False))
    return list(db.scalars(q.order_by(ComplaintComment.created_at, ComplaintComment.id)).all())


def add_note(db: Session, principal: Principal, c: Complaint, body: str) -> ComplaintInternalNote:
    if not (principal.can(P.note_write) and can_staff_work(principal, c)):
        raise NotFound("Complaint not found")
    note = ComplaintInternalNote(complaint_id=c.id, author_id=principal.id, body=body, created_at=utcnow())
    db.add(note)
    db.commit()
    return note


def list_notes(db: Session, principal: Principal, c: Complaint) -> list[ComplaintInternalNote]:
    if not (principal.can(P.note_read) and can_staff_read(principal, c)):
        raise NotFound("Complaint not found")
    return list(db.scalars(select(ComplaintInternalNote).where(ComplaintInternalNote.complaint_id == c.id)
                           .order_by(ComplaintInternalNote.created_at)).all())


# --- Feedback, support, merge ----------------------------------------------------------------------

def submit_feedback(db: Session, principal: Principal, c: Complaint, req: FeedbackCreate) -> Feedback:
    if c.reporter_id != principal.id:
        raise Forbidden("Only the reporter can give feedback")
    if c.status not in (ComplaintStatus.resolved, ComplaintStatus.closed) or c.resolved_at is None:
        raise Conflict("Feedback is accepted once the complaint is resolved", code="feedback_not_eligible")
    if db.scalar(select(Feedback.id).where(Feedback.complaint_id == c.id)):
        raise Conflict("Feedback was already submitted", code="feedback_exists")
    now = utcnow()
    fb = Feedback(complaint_id=c.id, reporter_id=principal.id, rating=req.rating, comment=req.comment,
                  confirmed_resolved=req.confirm_resolved, created_at=now)
    db.add(fb)
    if req.confirm_resolved and c.status == ComplaintStatus.resolved:
        _change_status(db, c, ComplaintStatus.closed, actor=workflow.Actor.RESIDENT, actor_id=principal.id,
                       reason="Reporter confirmed resolution", now=now)
        c.resident_confirmed_at = now
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise Conflict("Feedback was already submitted", code="feedback_exists") from None
    return fb


def support_count(db: Session, complaint_id: uuid.UUID) -> int:
    return db.scalar(select(func.count()).select_from(ComplaintSupporter)
                     .where(ComplaintSupporter.complaint_id == complaint_id)) or 0


def add_support(db: Session, principal: Principal, complaint_id: uuid.UUID) -> int:
    c = db.get(Complaint, complaint_id)
    if c is None or (c.visibility != Visibility.public and not can_read(principal, c)):
        raise NotFound("Complaint not found")
    if c.visibility != Visibility.public:
        raise Conflict("Only public reports can be supported", code="not_public")
    if c.status not in OPEN_STATUSES or c.merged_into_id:
        raise Conflict("This report is no longer open", code="not_open")
    if c.reporter_id == principal.id:
        raise Conflict("You cannot support your own report", code="own_report")
    db.add(ComplaintSupporter(complaint_id=c.id, user_id=principal.id, created_at=utcnow()))
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise Conflict("You already support this report", code="already_supported") from None
    return support_count(db, c.id)


def remove_support(db: Session, principal: Principal, complaint_id: uuid.UUID) -> int:
    row = db.scalar(select(ComplaintSupporter).where(ComplaintSupporter.complaint_id == complaint_id,
                                                     ComplaintSupporter.user_id == principal.id))
    if row is None:
        raise NotFound("You do not support this report")
    db.delete(row)
    db.commit()
    return support_count(db, complaint_id)


def merge(db: Session, principal: Principal, source: Complaint, target_id: uuid.UUID, reason: str) -> Complaint:
    if not can_staff_read(principal, source):
        raise NotFound("Complaint not found")
    target = db.get(Complaint, target_id)
    if target is None or not can_staff_read(principal, target):
        raise ValidationFailed("Target complaint not found", code="invalid_target")
    if not (can_manage(principal, source, P.complaint_merge) and can_manage(principal, target, P.complaint_merge)):
        raise Forbidden("You may not merge these complaints")
    if source.id == target.id:
        raise ValidationFailed("Cannot merge a complaint into itself", code="self_merge")
    if source.merged_into_id is not None:
        raise Conflict("Complaint is already merged", code="already_merged")
    if target.merged_into_id is not None:
        raise Conflict("Target is itself merged; merge into its primary report instead", code="target_merged")
    if target.status in (ComplaintStatus.rejected, ComplaintStatus.withdrawn):
        raise Conflict("Cannot merge into a rejected or withdrawn report", code="invalid_target_state")
    if source.status not in OPEN_STATUSES:
        raise Conflict("Only open complaints can be merged", code="invalid_state")
    if db.scalar(select(Complaint.id).where(Complaint.merged_into_id == source.id).limit(1)):
        raise Conflict("Other reports are merged into this one; it must stay primary", code="merge_chain")
    now = utcnow()
    db.add(ComplaintLink(source_id=source.id, target_id=target.id, link_type=LinkType.duplicate_of,
                         reason=reason, actor_id=principal.id, created_at=now))
    source.merged_into_id = target.id
    _change_status(db, source, ComplaintStatus.closed, actor=workflow.Actor.SYSTEM, actor_id=principal.id,
                   reason=f"Merged into {target.reference}: {reason}", now=now, emit=False)
    ev.emit(db, ev.COMPLAINT_MERGED, source.id, {"reference": source.reference,
                                                 "target_reference": target.reference,
                                                 "actor_id": str(principal.id)})
    audit.record(db, actor_id=principal.id, action="complaint.merge", entity_type="complaint",
                 entity_id=source.id, reason=reason, after={"merged_into": str(target.id)})
    db.commit()
    return source
