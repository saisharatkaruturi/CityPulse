"""Notification fan-out and delivery (runs in the worker, after commit).

In-app notifications are the baseline. Email/SMS go through optional provider adapters and
respect user preferences. Templates contain only the reference, category label, and status:
never private contact details, internal notes, descriptions, or tokens.
"""

from __future__ import annotations

import logging
import uuid
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.adapters.providers import ProviderRejected, ProviderUnavailable, get_providers
from app.core.config import get_settings
from app.core.time import utcnow
from app.domain.enums import DeliveryState, NotificationChannel, Role
from app.models import Complaint, Notification, NotificationPreference, Officer, OutboxEvent, User, UserRole
from app.services import outbox as ev

logger = logging.getLogger("app.notifications")

TEMPLATE_VERSION = 1

# event_type -> (title, body). Placeholders are filled with safe, escaped values only.
TEMPLATES: dict[str, tuple[str, str]] = {
    ev.COMPLAINT_SUBMITTED: ("Report {ref} received",
                             "Your report {ref} was received by this platform and {routing}. "
                             "This is not yet confirmation from a municipal department."),
    ev.COMPLAINT_ASSIGNED: ("Report {ref} assigned", "Report {ref} has been assigned for action."),
    ev.COMPLAINT_REASSIGNED: ("Report {ref} reassigned", "Report {ref} was reassigned."),
    ev.COMPLAINT_STATUS_CHANGED: ("Report {ref} updated", "Report {ref} is now: {status}."),
    ev.COMPLAINT_INFO_REQUESTED: ("More information needed for {ref}",
                                  "Staff have asked a question about report {ref}. Please reply in the app."),
    ev.COMPLAINT_RESOLVED: ("Report {ref} marked resolved",
                            "Staff marked report {ref} as resolved. Please confirm or request reopening."),
    ev.COMPLAINT_REOPENED: ("Report {ref} reopened", "Report {ref} was reopened."),
    ev.COMPLAINT_MERGED: ("Report {ref} linked to an existing report",
                          "Report {ref} was merged into report {target} which tracks the same issue."),
    ev.COMPLAINT_HIGH_PRIORITY: ("High-priority report {ref}", "Report {ref} has priority {priority}."),
    ev.COMPLAINT_COMMENTED: ("New message on {ref}", "There is a new message on report {ref}."),
    ev.DEADLINE_APPROACHING: ("Target time approaching for {ref}",
                              "Report {ref} is approaching its internal target time."),
    ev.COMPLAINT_OVERDUE: ("Report {ref} is overdue", "Report {ref} has passed its internal target time "
                                                      "(escalation level {level})."),
}

STATUS_LABELS = {
    "submitted": "submitted", "under_review": "under review", "assigned": "assigned",
    "in_progress": "in progress", "awaiting_resident": "waiting for your reply", "on_hold": "on hold",
    "resolved": "marked resolved", "closed": "closed", "rejected": "not accepted", "withdrawn": "withdrawn",
    "reopened": "reopened",
}


def _safe(value: object) -> str:
    text = str(value)
    # Plain-text channels; strip control characters and angle brackets for safe rendering anywhere.
    return "".join(ch for ch in text if ch.isprintable() and ch not in "<>")[:120]


def render(event_type: str, payload: dict) -> tuple[str, str]:
    title_t, body_t = TEMPLATES[event_type]
    status = str(payload.get("to_status") or "")
    values = {
        "ref": _safe(payload.get("reference", "")),
        "status": _safe(STATUS_LABELS.get(status, status)),
        "routing": "sent to the responsible department queue" if payload.get("routed")
        else "placed in the triage queue for manual review",
        "priority": _safe(payload.get("priority", "")),
        "target": _safe(payload.get("target_reference", "")),
        "level": _safe(payload.get("level", "")),
    }
    return title_t.format(**values), body_t.format(**values)


def _department_supervisors(db: Session, department_id: uuid.UUID | None) -> list[uuid.UUID]:
    if department_id is None:
        return []
    return list(db.scalars(select(UserRole.user_id).where(UserRole.role == Role.supervisor,
                                                          UserRole.department_id == department_id)).all())


def _officer_user(db: Session, officer_id: uuid.UUID | None) -> list[uuid.UUID]:
    if officer_id is None:
        return []
    off = db.get(Officer, officer_id)
    return [off.user_id] if off and off.is_active else []


def recipients_for(db: Session, event: OutboxEvent, complaint: Complaint) -> list[uuid.UUID]:
    t = event.event_type
    p = event.payload
    reporter = [complaint.reporter_id]
    if t in (ev.COMPLAINT_SUBMITTED, ev.COMPLAINT_STATUS_CHANGED, ev.COMPLAINT_INFO_REQUESTED,
             ev.COMPLAINT_RESOLVED, ev.COMPLAINT_MERGED):
        return reporter
    if t in (ev.COMPLAINT_ASSIGNED, ev.COMPLAINT_REASSIGNED):
        staff = _officer_user(db, complaint.assigned_officer_id)
        return reporter + staff
    if t == ev.COMPLAINT_REOPENED:
        return _officer_user(db, complaint.assigned_officer_id) + _department_supervisors(
            db, complaint.department_id)
    if t == ev.COMPLAINT_HIGH_PRIORITY:
        return _department_supervisors(db, complaint.department_id)
    if t == ev.COMPLAINT_COMMENTED:
        if p.get("author_is_staff"):
            return reporter
        return _officer_user(db, complaint.assigned_officer_id)
    if t == ev.DEADLINE_APPROACHING:
        return _officer_user(db, complaint.assigned_officer_id) or _department_supervisors(
            db, complaint.department_id)
    if t == ev.COMPLAINT_OVERDUE:
        targets = [uuid.UUID(x) for x in p.get("notify_user_ids", [])]
        return targets or _department_supervisors(db, complaint.department_id)
    return []


def fan_out(db: Session, event: OutboxEvent) -> int:
    """Create notification rows for an event. Idempotent via unique dedup keys."""
    if event.event_type not in TEMPLATES:
        return 0
    complaint = db.get(Complaint, event.aggregate_id)
    if complaint is None:
        return 0
    title, body = render(event.event_type, event.payload)
    created = 0
    now = utcnow()
    for user_id in dict.fromkeys(recipients_for(db, event, complaint)):
        actor = event.payload.get("actor_id")
        if actor and str(user_id) == actor and event.event_type != ev.COMPLAINT_SUBMITTED:
            continue  # do not notify people about their own actions
        user = db.get(User, user_id)
        if user is None or not user.is_active:
            continue
        prefs = db.get(NotificationPreference, user_id)
        channels = [NotificationChannel.in_app]
        if prefs and prefs.email_enabled:
            channels.append(NotificationChannel.email)
        if prefs and prefs.sms_enabled and user.phone:
            channels.append(NotificationChannel.sms)
        for channel in channels:
            dedup = f"{event.id}:{user_id}:{channel.value}"
            if db.scalar(select(Notification.id).where(Notification.dedup_key == dedup)):
                continue
            state = DeliveryState.sent if channel == NotificationChannel.in_app else DeliveryState.pending
            n = Notification(recipient_id=user_id, complaint_id=complaint.id,
                             complaint_reference=complaint.reference, event_type=event.event_type,
                             channel=channel, template=event.event_type, template_version=TEMPLATE_VERSION,
                             title=title, body=body, delivery_state=state, dedup_key=dedup, created_at=now,
                             sent_at=now if state == DeliveryState.sent else None,
                             next_attempt_at=now if state == DeliveryState.pending else None)
            try:
                with db.begin_nested():
                    db.add(n)
            except IntegrityError:
                continue  # concurrent duplicate; the other insert wins
            created += 1
    return created


def deliver_pending(db: Session, limit: int = 100) -> dict[str, int]:
    """Deliver external-channel notifications with bounded retries and backoff."""
    settings = get_settings()
    providers = get_providers()
    now = utcnow()
    stats = {"sent": 0, "failed": 0, "retry": 0, "skipped": 0}
    rows = db.scalars(select(Notification).where(Notification.delivery_state == DeliveryState.pending,
                                                 Notification.next_attempt_at <= now)
                      .order_by(Notification.created_at).limit(limit)).all()
    for n in rows:
        provider = providers.email if n.channel == NotificationChannel.email else providers.sms
        if provider is None:
            n.delivery_state = DeliveryState.skipped
            n.last_error = "provider_disabled"
            stats["skipped"] += 1
            continue
        user = db.get(User, n.recipient_id)
        to = (user.email if n.channel == NotificationChannel.email else user.phone) if user else None
        if not to:
            n.delivery_state = DeliveryState.skipped
            n.last_error = "no_address"
            stats["skipped"] += 1
            continue
        n.attempt_count += 1
        try:
            receipt = provider.send(to, n.title, n.body)
        except ProviderRejected as exc:
            n.delivery_state = DeliveryState.failed
            n.last_error = _safe(exc)
            stats["failed"] += 1
        except ProviderUnavailable as exc:
            n.last_error = _safe(exc)
            if n.attempt_count >= settings.outbox_max_attempts:
                n.delivery_state = DeliveryState.failed
                stats["failed"] += 1
            else:
                n.next_attempt_at = now + timedelta(
                    seconds=settings.outbox_base_backoff_seconds * 2 ** (n.attempt_count - 1))
                stats["retry"] += 1
        else:
            n.delivery_state = DeliveryState.sent
            n.provider_reference = receipt.provider_reference
            n.sent_at = now
            stats["sent"] += 1
    db.commit()
    return stats
