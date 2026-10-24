"""Build explicit response schemas from models. Never return ORM objects directly."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.permissions import Principal, can_staff_read
from app.domain.enums import ComplaintStatus, ExternalSyncState
from app.domain.geo import fuzz
from app.models import Complaint, ComplaintAssignment, ComplaintStatusHistory, Department
from app.schemas.complaints import (
    AssignmentOut,
    ComplaintResidentOut,
    ComplaintStaffOut,
    ProgressOut,
    PublicComplaintSummary,
    StatusEventOut,
)
from app.services.complaints import support_count


def progress(db: Session, c: Complaint) -> ProgressOut:
    dept = db.get(Department, c.department_id) if c.department_id else None
    routed = dept is not None and not dept.is_fallback
    resolved = c.status in (ComplaintStatus.resolved, ComplaintStatus.closed) and c.resolved_at is not None
    ext = c.external_sync_state == ExternalSyncState.confirmed
    if c.merged_into_id:
        summary = "Merged into another report that tracks the same issue."
    elif c.status == ComplaintStatus.withdrawn:
        summary = "Withdrawn."
    elif c.status == ComplaintStatus.rejected:
        summary = "Not accepted by staff (see timeline for the reason)."
    elif c.resident_confirmed_at:
        summary = "You confirmed this issue is resolved."
    elif resolved:
        summary = "Staff marked this resolved. This has not been independently verified."
    elif c.acknowledged_at:
        summary = "A department has picked up this report."
    elif routed:
        summary = "Received by this platform and placed in a department queue; not yet acknowledged."
    else:
        summary = "Received by this platform; awaiting manual triage to find the right department."
    if ext:
        summary += " A municipal case system confirmed receipt" + (
            " (SIMULATED integration)." if c.external_is_simulated else ".")
    return ProgressOut(
        received_locally=True, routed_to_department=routed, department_acknowledged=c.acknowledged_at is not None,
        externally_acknowledged=ext, external_is_simulated=c.external_is_simulated, marked_resolved=resolved,
        resident_confirmed=c.resident_confirmed_at is not None, summary=summary)


def _timeline(db: Session, c: Complaint) -> list[StatusEventOut]:
    rows = db.scalars(select(ComplaintStatusHistory).where(ComplaintStatusHistory.complaint_id == c.id)
                      .order_by(ComplaintStatusHistory.created_at, ComplaintStatusHistory.id)).all()
    out = []
    for h in rows:
        out.append(StatusEventOut(from_status=h.from_status, to_status=h.to_status,
                                  actor_kind=h.actor_kind.value,
                                  actor_is_staff=None if h.actor_id is None else h.actor_id != c.reporter_id,
                                  reason=h.reason, created_at=h.created_at))
    return out


def _merged_ref(db: Session, c: Complaint) -> str | None:
    if not c.merged_into_id:
        return None
    t = db.get(Complaint, c.merged_into_id)
    return t.reference if t else None


def resident_view(db: Session, c: Complaint) -> ComplaintResidentOut:
    return ComplaintResidentOut(
        id=c.id, reference=c.reference, title=c.title, description=c.description,
        original_language=c.original_language, category_id=c.category_id,
        reported_category_id=c.reported_category_id, ward_id=c.ward_id, latitude=c.latitude,
        longitude=c.longitude, address_text=c.address_text, visibility=c.visibility, priority=c.priority,
        status=c.status, department_id=c.department_id, routing_outcome=c.routing_outcome, due_at=c.due_at,
        created_at=c.created_at, updated_at=c.updated_at, resolved_at=c.resolved_at, closed_at=c.closed_at,
        resolution_notes=c.resolution_notes, merged_into_reference=_merged_ref(db, c),
        external_sync_state=c.external_sync_state, external_case_id=c.external_case_id,
        external_is_simulated=c.external_is_simulated, version=c.version, progress=progress(db, c),
        timeline=_timeline(db, c))


def staff_view(db: Session, c: Complaint) -> ComplaintStaffOut:
    r = resident_view(db, c)
    assignments = db.scalars(select(ComplaintAssignment).where(ComplaintAssignment.complaint_id == c.id)
                             .order_by(ComplaintAssignment.created_at, ComplaintAssignment.id)).all()
    return ComplaintStaffOut(
        **r.model_dump(), reporter_id=c.reporter_id, category_source=c.category_source,
        priority_reason=c.priority_reason, safety_risk_reported=c.safety_risk_reported,
        source_channel=c.source_channel, team_id=c.team_id, assigned_officer_id=c.assigned_officer_id,
        routing_rule_id=c.routing_rule_id, routing_explanation=c.routing_explanation,
        initial_routing=c.initial_routing, sla_policy_id=c.sla_policy_id, sla_policy_version=c.sla_policy_version,
        acknowledge_due_at=c.acknowledge_due_at, sla_paused_at=c.sla_paused_at, is_overdue=c.is_overdue,
        escalation_level=c.escalation_level, reopen_count=c.reopen_count,
        reassignment_count=c.reassignment_count, merged_into_id=c.merged_into_id,
        location_source=c.location_source, location_accuracy_m=c.location_accuracy_m,
        assignments=[AssignmentOut.model_validate(a) for a in assignments])


def detail_view(db: Session, principal: Principal, c: Complaint) -> ComplaintResidentOut | ComplaintStaffOut:
    """Callers must have checked visibility first (get_visible). A staff member who is not the
    reporter only reaches here with staff scope, possibly lost by their own action (e.g. a reroute
    to another department); they still get the staff view of the result of that action."""
    if can_staff_read(principal, c) or (principal.is_staff and c.reporter_id != principal.id):
        return staff_view(db, c)
    return resident_view(db, c)


def public_summary(db: Session, c: Complaint, distance_m: float | None = None) -> PublicComplaintSummary:
    d = get_settings().public_coordinate_decimals
    return PublicComplaintSummary(
        id=c.id, reference=c.reference, title=c.title, category_id=c.category_id, status=c.status,
        ward_id=c.ward_id, approx_latitude=fuzz(c.latitude, d) if c.latitude is not None else None,
        approx_longitude=fuzz(c.longitude, d) if c.longitude is not None else None,
        distance_m=int(round(distance_m / 10) * 10) if distance_m is not None else None,
        support_count=support_count(db, c.id), created_at=c.created_at)
