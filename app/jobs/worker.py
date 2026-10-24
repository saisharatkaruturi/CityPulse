"""Background worker: outbox delivery, notification delivery, SLA reminders/escalation,
auto-close, external sync and orphan cleanup.

Every job is safe to run more than once and safe to run concurrently with itself:
  * outbox rows are claimed with a lease (`locked_until`; FOR UPDATE SKIP LOCKED on PostgreSQL);
  * notifications, escalations and reminder events have unique dedup keys / constraints;
  * a crashed worker's claimed events are retried when the lease expires, so committed work is
    never lost.
Run: `python -m app.cli worker` (loop) or `python -m app.cli worker --once`.
"""

from __future__ import annotations

import logging
import time
from datetime import timedelta

from sqlalchemy import or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from app.adapters.providers import ProviderRejected, ProviderUnavailable, get_providers
from app.core.config import get_settings
from app.core.time import utcnow
from app.domain import workflow
from app.domain.enums import (
    OPEN_STATUSES,
    ActorKind,
    ComplaintStatus,
    ExternalSyncState,
    OutboxState,
    Role,
)
from app.domain.sla import reminder_threshold
from app.models import (
    Category,
    Complaint,
    Department,
    EscalationHistory,
    OutboxEvent,
    UserRole,
)
from app.services import media, notifications
from app.services import outbox as ev
from app.services.complaints import _change_status

logger = logging.getLogger("app.worker")

LEASE = timedelta(minutes=5)


class PermanentFailure(Exception):
    pass


# --- Outbox ----------------------------------------------------------------------------------------

def _handle(db: Session, event: OutboxEvent) -> None:
    if event.event_type == ev.EXTERNAL_SYNC_REQUESTED:
        _external_sync(db, event)
        return
    notifications.fan_out(db, event)


def _external_sync(db: Session, event: OutboxEvent) -> None:
    c = db.get(Complaint, event.aggregate_id)
    if c is None or c.external_sync_state == ExternalSyncState.confirmed:
        return
    provider = get_providers().municipal
    if provider is None:
        c.external_sync_state = ExternalSyncState.not_configured
        return
    cat = db.get(Category, c.category_id) if c.category_id else None
    dept = db.get(Department, c.department_id) if c.department_id else None
    try:
        # Only the minimum is sent: reference, taxonomy codes and title (no reporter data).
        ack = provider.submit_case(c.reference, cat.code if cat else None, dept.code if dept else None, c.title)
    except ProviderRejected as exc:
        c.external_sync_state = ExternalSyncState.rejected
        raise PermanentFailure(str(exc)) from exc
    # External ID is stored only after the provider confirms.
    c.external_case_id = ack.external_case_id
    c.external_is_simulated = ack.simulated
    c.external_sync_state = ExternalSyncState.confirmed
    c.external_acknowledged_at = utcnow()


def _sanitize(exc: BaseException) -> str:
    return f"{type(exc).__name__}: {str(exc)[:200]}"


def process_outbox(db: Session, limit: int = 50) -> dict[str, int]:
    settings = get_settings()
    now = utcnow()
    stats = {"done": 0, "retry": 0, "failed": 0}
    q = (select(OutboxEvent)
         .where(or_(OutboxEvent.state == OutboxState.pending,
                    (OutboxEvent.state == OutboxState.processing) & (OutboxEvent.locked_until < now)),
                OutboxEvent.next_attempt_at <= now)
         .order_by(OutboxEvent.created_at).limit(limit).with_for_update(skip_locked=True))
    claimed = list(db.scalars(q).all())
    for e in claimed:
        e.state = OutboxState.processing
        e.locked_until = now + LEASE
        e.attempt_count += 1
    db.commit()

    for e in claimed:
        try:
            _handle(db, e)
            e.state = OutboxState.done
            e.processed_at = utcnow()
            e.last_error = None
            db.commit()
            stats["done"] += 1
        except PermanentFailure as exc:
            e.state = OutboxState.failed
            e.last_error = _sanitize(exc)
            db.commit()
            stats["failed"] += 1
        except Exception as exc:  # retried with backoff; never silently dropped
            db.rollback()
            e = db.get(OutboxEvent, e.id)  # type: ignore[assignment]
            assert e is not None
            e.last_error = _sanitize(exc)
            if e.attempt_count >= settings.outbox_max_attempts:
                e.state = OutboxState.failed
                if e.event_type == ev.EXTERNAL_SYNC_REQUESTED:
                    c = db.get(Complaint, e.aggregate_id)
                    if c is not None:
                        c.external_sync_state = ExternalSyncState.failed
                stats["failed"] += 1
                logger.error("outbox_event_failed", extra={"event_id": str(e.id), "type": e.event_type})
            else:
                e.state = OutboxState.pending
                e.next_attempt_at = utcnow() + timedelta(
                    seconds=settings.outbox_base_backoff_seconds * 2 ** (e.attempt_count - 1))
                stats["retry"] += 1
                if not isinstance(exc, ProviderUnavailable):
                    logger.exception("outbox_handler_error", extra={"event_id": str(e.id)})
            db.commit()
    return stats


# --- SLA -------------------------------------------------------------------------------------------

def _record_escalation(db: Session, row: EscalationHistory) -> bool:
    try:
        with db.begin_nested():
            db.add(row)
        return True
    except IntegrityError:
        return False  # another run already recorded it


def sla_scan(db: Session) -> dict[str, int]:
    settings = get_settings()
    now = utcnow()
    stats = {"reminders": 0, "escalations": 0}
    rows = db.scalars(select(Complaint).where(Complaint.status.in_(OPEN_STATUSES), Complaint.due_at.is_not(None),
                                              Complaint.sla_paused_at.is_(None))).all()
    admins = db.scalars(select(UserRole.user_id).where(UserRole.role == Role.municipal_admin)).all()
    for c in rows:
        due = c.due_at
        assert due is not None
        if now < due:
            if now >= reminder_threshold(c.created_at, due, settings.sla_reminder_lead_fraction):
                ok = _record_escalation(db, EscalationHistory(
                    complaint_id=c.id, trigger="deadline_approaching", level=0, due_at_snapshot=due,
                    sla_policy_id=c.sla_policy_id, target_officer_id=c.assigned_officer_id,
                    target_department_id=c.department_id, actor_kind=ActorKind.system,
                    result="reminder_queued", created_at=now))
                if ok:
                    ev.emit(db, ev.DEADLINE_APPROACHING, c.id, {"reference": c.reference},
                            dedup_key=f"reminder:{c.id}:{due.isoformat()}")
                    stats["reminders"] += 1
            continue
        if not c.is_overdue:
            c.is_overdue = True
            c.overdue_at = now
        step = max(timedelta(hours=1), (due - c.created_at) / 2)
        target_level = min(settings.escalation_max_level, 1 + int((now - due) / step))
        for level in range(c.escalation_level + 1, target_level + 1):
            if level == 1:
                notify = list(db.scalars(select(UserRole.user_id).where(
                    UserRole.role == Role.supervisor, UserRole.department_id == c.department_id)).all())
                result = "notified_department_supervisors"
            else:
                notify = list(admins)
                result = "notified_municipal_admins"
            ok = _record_escalation(db, EscalationHistory(
                complaint_id=c.id, trigger="overdue", level=level, due_at_snapshot=due,
                sla_policy_id=c.sla_policy_id, target_officer_id=c.assigned_officer_id,
                target_department_id=c.department_id, actor_kind=ActorKind.system,
                result=result if notify else "no_target_configured", created_at=now))
            c.escalation_level = level
            if ok:
                ev.emit(db, ev.COMPLAINT_OVERDUE, c.id,
                        {"reference": c.reference, "level": level, "notify_user_ids": [str(u) for u in notify]},
                        dedup_key=f"overdue:{c.id}:{level}:{due.isoformat()}")
                stats["escalations"] += 1
    db.commit()
    return stats


def auto_close(db: Session) -> int:
    settings = get_settings()
    cutoff = utcnow() - timedelta(days=settings.auto_close_resolved_after_days)
    rows = db.scalars(select(Complaint).where(Complaint.status == ComplaintStatus.resolved,
                                              Complaint.resolved_at < cutoff)).all()
    for c in rows:
        _change_status(db, c, ComplaintStatus.closed, actor=workflow.Actor.SYSTEM, actor_id=None,
                       reason=f"Auto-closed {settings.auto_close_resolved_after_days} days after resolution "
                              "without a reopen request", now=utcnow())
    db.commit()
    return len(rows)


def run_once(factory: sessionmaker[Session]) -> dict:
    results: dict = {}
    for name, job in (("outbox", process_outbox), ("sla", sla_scan), ("auto_close", auto_close),
                      ("outbox_after", process_outbox), ("deliveries", notifications.deliver_pending),
                      ("orphans", media.cleanup_orphans)):
        with factory() as db:
            try:
                results[name] = job(db)
            except Exception:
                db.rollback()
                logger.exception("job_failed", extra={"job": name})
                results[name] = "error"
    return results


def run_forever(factory: sessionmaker[Session]) -> None:
    interval = get_settings().worker_interval_seconds
    logger.info("worker_started", extra={"interval_s": interval})
    while True:
        results = run_once(factory)
        logger.info("worker_cycle", extra={"results": results})
        time.sleep(interval)
