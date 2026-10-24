"""SLA policy selection and complaint clock maintenance."""

from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.domain import sla as sdomain
from app.domain.enums import SLA_PAUSED_STATUSES, ComplaintStatus
from app.models import Complaint, SlaPolicy


def select_policy(db: Session, complaint: Complaint, now: datetime) -> SlaPolicy | None:
    """Most specific active policy wins: category, then department, then priority match.

    Policies with a NULL scope field act as wildcards for that field.
    """
    q = select(SlaPolicy).where(
        SlaPolicy.is_active.is_(True),
        SlaPolicy.effective_from <= now,
        or_(SlaPolicy.effective_to.is_(None), SlaPolicy.effective_to > now),
        or_(SlaPolicy.category_id.is_(None), SlaPolicy.category_id == complaint.category_id),
        or_(SlaPolicy.department_id.is_(None), SlaPolicy.department_id == complaint.department_id),
        or_(SlaPolicy.priority.is_(None), SlaPolicy.priority == complaint.priority),
    )
    policies = db.scalars(q).all()
    if not policies:
        return None

    def score(p: SlaPolicy) -> tuple[int, int, int, datetime]:
        return (p.category_id is not None, p.department_id is not None, p.priority is not None,
                p.effective_from)

    return max(policies, key=score)


def apply_policy(db: Session, complaint: Complaint, now: datetime) -> None:
    """(Re)compute targets from creation time. Called at creation and after category/priority change."""
    policy = select_policy(db, complaint, now)
    if policy is None:
        complaint.sla_policy_id = None
        complaint.sla_policy_version = None
        complaint.acknowledge_due_at = None
        complaint.due_at = None
        return
    targets = sdomain.compute_targets(complaint.created_at, policy.acknowledge_hours, policy.resolve_hours)
    complaint.sla_policy_id = policy.id
    complaint.sla_policy_version = policy.version
    complaint.acknowledge_due_at = targets.acknowledge_due_at
    complaint.due_at = targets.due_at + timedelta(seconds=complaint.sla_paused_seconds)
    complaint.is_overdue = sdomain.is_overdue(complaint.due_at, now, complaint.sla_paused_at is not None)


def on_status_change(db: Session, complaint: Complaint, old: ComplaintStatus, new: ComplaintStatus,
                     now: datetime) -> None:
    """Pause the clock entering a waiting state, resume (extend due_at) when leaving it."""
    policy = db.get(SlaPolicy, complaint.sla_policy_id) if complaint.sla_policy_id else None
    pauses = policy.pause_when_waiting if policy else False
    if pauses and new in SLA_PAUSED_STATUSES and complaint.sla_paused_at is None:
        complaint.sla_paused_at = now
    elif complaint.sla_paused_at is not None and new not in SLA_PAUSED_STATUSES:
        if complaint.due_at is not None:
            complaint.due_at, paused = sdomain.resume_due_at(complaint.due_at, complaint.sla_paused_at, now)
            complaint.sla_paused_seconds += paused
        complaint.sla_paused_at = None
    if new == ComplaintStatus.reopened and policy is not None:
        # A reopened case gets a fresh resolution window from now under the same policy.
        complaint.due_at = sdomain.compute_targets(now, policy.acknowledge_hours, policy.resolve_hours).due_at
        complaint.is_overdue = False
        complaint.escalation_level = 0
