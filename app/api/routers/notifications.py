from __future__ import annotations

import uuid

from fastapi import APIRouter
from sqlalchemy import func, select

from app.api.deps import DB, CurrentUser, PageParams
from app.core.errors import NotFound
from app.core.time import utcnow
from app.domain.enums import NotificationChannel
from app.models import Notification
from app.schemas.catalog import NotificationOut
from app.schemas.common import ERROR_RESPONSES, Page

router = APIRouter(prefix="/api/notifications", tags=["notifications"], responses=ERROR_RESPONSES)


@router.get("", response_model=Page[NotificationOut], summary="Your in-app notifications, newest first")
def list_(principal: CurrentUser, db: DB, pg: PageParams, unread_only: bool = False) -> Page[NotificationOut]:
    q = select(Notification).where(Notification.recipient_id == principal.id,
                                   Notification.channel == NotificationChannel.in_app)
    if unread_only:
        q = q.where(Notification.read_at.is_(None))
    total = db.scalar(select(func.count()).select_from(q.subquery())) or 0
    rows = db.scalars(q.order_by(Notification.created_at.desc(), Notification.id)
                      .offset(pg.offset).limit(pg.page_size)).all()
    return Page[NotificationOut](items=[NotificationOut.model_validate(n) for n in rows], total=total,
                                 page=pg.page, page_size=pg.page_size)


@router.post("/read-all", summary="Mark all of your in-app notifications read; returns how many changed")
def mark_all_read(principal: CurrentUser, db: DB) -> dict[str, int]:
    rows = db.scalars(select(Notification).where(Notification.recipient_id == principal.id,
                                                 Notification.channel == NotificationChannel.in_app,
                                                 Notification.read_at.is_(None))).all()
    now = utcnow()
    for n in rows:
        n.read_at = now
    db.commit()
    return {"updated": len(rows)}


@router.patch("/{notification_id}/read", response_model=NotificationOut, summary="Mark your notification read")
def mark_read(notification_id: uuid.UUID, principal: CurrentUser, db: DB) -> NotificationOut:
    n = db.get(Notification, notification_id)
    if n is None or n.recipient_id != principal.id:
        raise NotFound("Notification not found")
    if n.read_at is None:
        n.read_at = utcnow()
        db.commit()
    return NotificationOut.model_validate(n)
