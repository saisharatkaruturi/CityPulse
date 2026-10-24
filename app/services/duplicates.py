"""Duplicate candidates and public nearby search. Bounded by radius, time window, and result count."""

from __future__ import annotations

import uuid
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.adapters.classifier import tokens
from app.core.config import get_settings
from app.core.permissions import Principal, can_read
from app.core.time import utcnow
from app.domain.enums import OPEN_STATUSES, Visibility
from app.domain.geo import bounding_box, haversine_m
from app.models import Category, Complaint
from app.schemas.complaints import DuplicateCandidate


def _related_category_ids(db: Session, category_id: uuid.UUID | None) -> set[uuid.UUID]:
    if category_id is None:
        return set()
    cat = db.get(Category, category_id)
    if cat is None:
        return {category_id}
    ids = {cat.id}
    if cat.parent_id:
        ids.add(cat.parent_id)
        ids |= set(db.scalars(select(Category.id).where(Category.parent_id == cat.parent_id)).all())
    ids |= set(db.scalars(select(Category.id).where(Category.parent_id == cat.id)).all())
    return ids


def _jaccard(a: str, b: str) -> float:
    ta, tb = tokens(a), tokens(b)
    if not ta or not tb:
        return 0.0
    return round(len(ta & tb) / len(ta | tb), 3)


def find_candidates(db: Session, principal: Principal, c: Complaint) -> list[DuplicateCandidate]:
    """Open complaints with related category, near the same spot, created within the window.

    Without coordinates, falls back to same ward + related category. Never auto-merges.
    """
    s = get_settings()
    cats = _related_category_ids(db, c.category_id)
    if not cats:
        return []
    since = c.created_at - timedelta(days=s.duplicate_window_days)
    q = select(Complaint).where(Complaint.id != c.id, Complaint.category_id.in_(cats),
                                Complaint.status.in_(OPEN_STATUSES), Complaint.merged_into_id.is_(None),
                                Complaint.created_at >= since)
    if c.latitude is not None and c.longitude is not None:
        min_lat, max_lat, min_lng, max_lng = bounding_box(c.latitude, c.longitude, s.duplicate_radius_m)
        q = q.where(Complaint.latitude.between(min_lat, max_lat), Complaint.longitude.between(min_lng, max_lng))
    elif c.ward_id is not None:
        q = q.where(Complaint.ward_id == c.ward_id)
    else:
        return []
    rows = db.scalars(q.order_by(Complaint.created_at.desc()).limit(s.duplicate_max_results * 5)).all()
    out: list[tuple[float, DuplicateCandidate]] = []
    for o in rows:
        dist = None
        if (c.latitude is not None and c.longitude is not None and o.latitude is not None
                and o.longitude is not None):
            dist = haversine_m(c.latitude, c.longitude, o.latitude, o.longitude)
            if dist > s.duplicate_radius_m:
                continue
        sim = _jaccard(f"{c.title} {c.description}", f"{o.title} {o.description}")
        visible = can_read(principal, o)
        public = o.visibility == Visibility.public
        out.append(((dist or 0) - sim * 100, DuplicateCandidate(
            id=o.id if visible else None, reference=o.reference,
            title=o.title if (visible or public) else None, category_id=o.category_id, status=o.status,
            distance_m=int(round(dist)) if dist is not None else None, text_similarity=sim,
            created_at=o.created_at)))
    out.sort(key=lambda x: x[0])
    return [d for _, d in out[: s.duplicate_max_results]]


def nearby_public(db: Session, lat: float, lng: float, radius_m: int, category_id: uuid.UUID | None,
                  limit: int) -> list[tuple[Complaint, float]]:
    s = get_settings()
    radius_m = min(radius_m, s.nearby_max_radius_m)
    min_lat, max_lat, min_lng, max_lng = bounding_box(lat, lng, radius_m)
    q = select(Complaint).where(Complaint.visibility == Visibility.public,
                                Complaint.status.in_(OPEN_STATUSES), Complaint.merged_into_id.is_(None),
                                Complaint.latitude.between(min_lat, max_lat),
                                Complaint.longitude.between(min_lng, max_lng),
                                Complaint.created_at >= utcnow() - timedelta(days=90))
    if category_id:
        q = q.where(Complaint.category_id.in_(_related_category_ids(db, category_id)))
    rows = db.scalars(q.limit(500)).all()
    hits = [(c, haversine_m(lat, lng, c.latitude, c.longitude)) for c in rows
            if c.latitude is not None and c.longitude is not None]
    hits = [h for h in hits if h[1] <= radius_m]
    hits.sort(key=lambda h: h[1])
    return hits[:limit]
