"""Background jobs: outbox reliability, notification delivery, SLA reminders/escalation, external sync."""

from __future__ import annotations

import uuid
from datetime import timedelta

from sqlalchemy import func, select

from app.adapters.providers import get_providers
from app.core.time import utcnow
from app.domain.enums import DeliveryState, ExternalSyncState, OutboxState
from app.jobs import worker
from app.models import Complaint, EscalationHistory, Notification, NotificationPreference, OutboxEvent
from tests.conftest import run_worker


def _count(db, model, *where) -> int:  # noqa: ANN001
    return db.scalar(select(func.count()).select_from(model).where(*where)) or 0


def test_reprocessing_an_event_does_not_duplicate_notifications(api, factory, db):
    api.report("resident1")
    run_worker(factory)
    first = _count(db, Notification)
    assert first >= 1
    # Simulate a crash after delivery but before the event was marked done.
    for e in db.scalars(select(OutboxEvent)).all():
        e.state = OutboxState.processing
        e.locked_until = utcnow() - timedelta(seconds=1)
    db.commit()
    run_worker(factory)
    assert _count(db, Notification) == first
    assert _count(db, OutboxEvent, OutboxEvent.state != OutboxState.done) == 0


def test_claimed_event_lease_blocks_concurrent_worker(api, factory, db):
    api.report("resident1")
    e = db.scalar(select(OutboxEvent))
    e.state = OutboxState.processing
    e.locked_until = utcnow() + timedelta(minutes=5)  # another worker holds it
    db.commit()
    with factory() as s:
        assert worker.process_outbox(s)["done"] == 0


def test_handler_failure_retries_with_backoff_then_fails(api, factory, db, monkeypatch, configure):
    configure(OUTBOX_MAX_ATTEMPTS="2")
    api.report("resident1")

    def boom(*_a, **_k):  # noqa: ANN002, ANN003, ANN202
        raise RuntimeError("template store down")

    monkeypatch.setattr(worker.notifications, "fan_out", boom)
    with factory() as s:
        assert worker.process_outbox(s)["retry"] == 1
    e = db.scalar(select(OutboxEvent))
    db.refresh(e)
    assert e.state == OutboxState.pending and e.next_attempt_at > utcnow() and "RuntimeError" in e.last_error
    e.next_attempt_at = utcnow()
    db.commit()
    with factory() as s:
        assert worker.process_outbox(s)["failed"] == 1
    db.refresh(e)
    assert e.state == OutboxState.failed
    # The complaint itself is untouched by delivery failure.
    assert _count(db, Complaint) == 1
    # An operator can see and retry it.
    listed = api.get("/api/admin/outbox", "admin").json()
    assert listed["total"] == 1
    assert api.post(f"/api/admin/outbox/{e.id}/retry", "admin").json()["state"] == "pending"


def test_email_delivery_respects_preferences_and_retries(api, factory, db, configure):
    configure(EMAIL_PROVIDER="mock")
    r = api.c.put("/api/users/me/notification-preferences", headers=api.h("resident1"),
                  json={"email_enabled": True, "sms_enabled": False, "language": "en"})
    assert r.status_code == 200
    provider = get_providers().email
    provider.fail_next = 1  # first attempt hits a simulated outage
    api.report("resident1")
    run_worker(factory)
    email_row = db.scalar(select(Notification).where(Notification.channel == "email"))
    assert email_row.delivery_state == DeliveryState.pending and email_row.attempt_count == 1
    email_row.next_attempt_at = utcnow()
    db.commit()
    run_worker(factory)
    db.refresh(email_row)
    assert email_row.delivery_state == DeliveryState.sent and email_row.provider_reference.startswith("SIMULATED")
    assert len(provider.sent) == 1 and provider.sent[0][0] == "resident1@example.com"
    run_worker(factory)
    assert len(provider.sent) == 1  # no duplicate delivery
    # A user without email opt-in gets in-app only.
    api.report("resident2")
    run_worker(factory)
    assert not db.scalar(select(NotificationPreference).where(
        NotificationPreference.user_id == api.user_id("resident2")))
    assert _count(db, Notification, Notification.recipient_id == api.user_id("resident2"),
                  Notification.channel == "email") == 0


def test_provider_disabled_marks_skipped(api, factory, db):
    api.c.put("/api/users/me/notification-preferences", headers=api.h("resident1"),
              json={"email_enabled": True, "sms_enabled": False})
    api.report("resident1")
    run_worker(factory)
    row = db.scalar(select(Notification).where(Notification.channel == "email"))
    assert row.delivery_state == DeliveryState.skipped and row.last_error == "provider_disabled"


def _backdate(db, cid: str, hours: int) -> Complaint:  # noqa: ANN001
    from app.services import sla

    c = db.get(Complaint, uuid.UUID(cid))
    db.refresh(c)
    c.created_at = utcnow() - timedelta(hours=hours)
    sla.apply_policy(db, c, utcnow())
    db.commit()
    return c


def test_reminder_once_then_overdue_escalation_idempotent(api, factory, db):
    c = api.report("resident1")  # default illustrative policy: 168h resolution
    _backdate(db, c["id"], 150)  # inside the final 20% window
    for _ in range(3):
        run_worker(factory)
    assert _count(db, EscalationHistory, EscalationHistory.trigger == "deadline_approaching") == 1
    assert _count(db, OutboxEvent, OutboxEvent.event_type == "complaint.deadline_approaching") == 1

    row = _backdate(db, c["id"], 170)
    for _ in range(3):
        run_worker(factory)
    db.refresh(row)
    assert row.is_overdue and row.escalation_level == 1
    esc = db.scalars(select(EscalationHistory).where(EscalationHistory.trigger == "overdue")).all()
    assert len(esc) == 1 and esc[0].result == "notified_department_supervisors"
    sup_notes = api.get("/api/notifications", "roads.supervisor").json()
    assert any("overdue" in n["title"] for n in sup_notes["items"])
    # Much later: escalates once more to municipal admins, never beyond the max level.
    _backdate(db, c["id"], 168 + 24 * 30)
    for _ in range(2):
        run_worker(factory)
    db.refresh(row)
    assert row.escalation_level == 2
    assert _count(db, EscalationHistory, EscalationHistory.trigger == "overdue") == 2
    assert any("overdue" in n["title"] for n in api.get("/api/notifications", "muni.admin").json()["items"])
    overdue = api.get("/api/complaints", "roads.supervisor", params={"overdue": True}).json()
    assert overdue["total"] == 1


def test_paused_complaints_are_not_escalated(api, factory, db):
    c = api.report("resident1")
    api.post(f"/api/complaints/{c['id']}/assign", "roads.supervisor", {"officer_id": api.officer("roads.officer1")})
    api.post(f"/api/complaints/{c['id']}/transitions", "roads.officer1", {"to_status": "on_hold",
                                                                         "reason": "Waiting for material"})
    _backdate(db, c["id"], 500)
    run_worker(factory)
    assert _count(db, EscalationHistory) == 0


def test_auto_close_after_resolution_window(api, factory, db):
    c = api.report("resident1")
    api.post(f"/api/complaints/{c['id']}/assign", "roads.supervisor", {"officer_id": api.officer("roads.officer1")})
    api.post(f"/api/complaints/{c['id']}/resolve", "roads.officer1", {"resolution_notes": "Done"})
    row = db.get(Complaint, uuid.UUID(c["id"]))
    db.refresh(row)
    row.resolved_at = utcnow() - timedelta(days=8)
    db.commit()
    run_worker(factory)
    db.refresh(row)
    assert row.status.value == "closed" and row.resident_confirmed_at is None


def test_external_sync_mock_success_is_labelled_simulated(api, factory, db, configure):
    configure(MUNICIPAL_INTEGRATION="mock")
    c = api.report("resident1")
    assert c["external_sync_state"] == "pending" and c["external_case_id"] is None
    run_worker(factory)
    got = api.get(f"/api/complaints/{c['id']}", "resident1").json()
    assert got["external_sync_state"] == "confirmed" and got["external_is_simulated"]
    assert got["external_case_id"].startswith("SIMULATED-") and "SIMULATED" in got["progress"]["summary"]


def test_external_sync_outage_keeps_complaint_and_retries(api, factory, db, configure):
    configure(MUNICIPAL_INTEGRATION="mock", OUTBOX_MAX_ATTEMPTS="2")
    get_providers().municipal.mode = "timeout"
    c = api.report("resident1")
    run_worker(factory)
    row = db.get(Complaint, uuid.UUID(c["id"]))
    db.refresh(row)
    assert row.external_case_id is None and row.external_sync_state == ExternalSyncState.pending
    ev = db.scalar(select(OutboxEvent).where(OutboxEvent.event_type == "complaint.external_sync_requested"))
    assert ev.state == OutboxState.pending and "ProviderUnavailable" in ev.last_error
    get_providers().municipal.mode = "ok"  # provider recovers: reconciliation on retry
    ev.next_attempt_at = utcnow()
    db.commit()
    run_worker(factory)
    db.refresh(row)
    assert row.external_sync_state == ExternalSyncState.confirmed


def test_external_sync_rejection_is_permanent(api, factory, db, configure):
    configure(MUNICIPAL_INTEGRATION="mock")
    get_providers().municipal.mode = "reject"
    c = api.report("resident1")
    run_worker(factory)
    got = api.get(f"/api/complaints/{c['id']}", "resident1").json()
    assert got["external_sync_state"] == "rejected" and got["external_case_id"] is None
    assert got["progress"]["externally_acknowledged"] is False
