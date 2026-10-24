"""Audit trail for privileged and policy-relevant actions (separate from operational logs)."""

from __future__ import annotations

import uuid

from sqlalchemy.orm import Session

from app.core.logging import redact, request_id_var
from app.core.time import utcnow
from app.models import AuditLog


def record(db: Session, *, actor_id: uuid.UUID | None, action: str, entity_type: str,
           entity_id: uuid.UUID | str, reason: str | None = None, before: dict | None = None,
           after: dict | None = None) -> AuditLog:
    entry = AuditLog(
        actor_id=actor_id, action=action, entity_type=entity_type, entity_id=str(entity_id), reason=reason,
        request_id=request_id_var.get(),
        before=redact(before) if before else None,  # type: ignore[arg-type]
        after=redact(after) if after else None,  # type: ignore[arg-type]
        created_at=utcnow(),
    )
    db.add(entry)
    return entry


def snapshot(obj: object, fields: list[str]) -> dict:
    out: dict = {}
    for f in fields:
        v = getattr(obj, f)
        out[f] = str(v) if isinstance(v, uuid.UUID) else (v.isoformat() if hasattr(v, "isoformat") else v)
    return out
