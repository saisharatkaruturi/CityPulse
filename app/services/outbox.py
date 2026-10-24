"""Transactional outbox: events are written in the same transaction as the state change.

A worker (app/jobs/worker.py) delivers them after commit, so a notification is never sent for a
change that rolled back, and a provider outage never loses a complaint.
"""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.core.time import utcnow
from app.models import OutboxEvent

# Event types
COMPLAINT_SUBMITTED = "complaint.submitted"
COMPLAINT_ASSIGNED = "complaint.assigned"
COMPLAINT_REASSIGNED = "complaint.reassigned"
COMPLAINT_STATUS_CHANGED = "complaint.status_changed"
COMPLAINT_INFO_REQUESTED = "complaint.information_requested"
COMPLAINT_RESOLVED = "complaint.resolved"
COMPLAINT_REOPENED = "complaint.reopened"
COMPLAINT_MERGED = "complaint.merged"
COMPLAINT_HIGH_PRIORITY = "complaint.high_priority"
COMPLAINT_COMMENTED = "complaint.commented"
DEADLINE_APPROACHING = "complaint.deadline_approaching"
COMPLAINT_OVERDUE = "complaint.overdue"
EXTERNAL_SYNC_REQUESTED = "complaint.external_sync_requested"


def emit(db: Session, event_type: str, aggregate_id: uuid.UUID, payload: dict,
         dedup_key: str | None = None) -> OutboxEvent:
    now = utcnow()
    event = OutboxEvent(event_type=event_type, aggregate_id=aggregate_id, payload=payload, dedup_key=dedup_key,
                        next_attempt_at=now, created_at=now)
    db.add(event)
    return event
