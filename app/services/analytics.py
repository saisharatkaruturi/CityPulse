"""Analytics computed from persisted records. Definitions (also in README):

Population: complaints with created_at in [date_from, date_to) (UTC), within the caller's scope.
  * reports_total: every report in the population, including merged duplicates.
  * issues_total: reports excluding those merged into another report (avoids double counting).
  All other metrics use the issues population.
  * by_status: count per current status.
  * open: status in submitted/under_review/assigned/in_progress/awaiting_resident/on_hold/reopened.
  * overdue_open: open and is_overdue.
  * reopened: reopen_count > 0.
  * resolution_hours avg/median: (resolved_at - created_at) for issues with resolved_at set.
    resolved_at is the latest time staff marked the case resolved.
  * sla_compliance: numerator = resolved issues with due_at set and resolved_at <= due_at;
    denominator = resolved issues with due_at set. null when the denominator is 0.
"""

from __future__ import annotations

import csv
import io
import statistics
import uuid
from collections import Counter, defaultdict
from datetime import datetime, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import Forbidden, ValidationFailed
from app.core.permissions import P, Principal
from app.domain.enums import OPEN_STATUSES, ComplaintStatus
from app.models import Complaint

MAX_RANGE = timedelta(days=366)


def _validate_range(date_from: datetime, date_to: datetime) -> None:
    if date_to <= date_from:
        raise ValidationFailed("date_to must be after date_from", code="invalid_range")
    if date_to - date_from > MAX_RANGE:
        raise ValidationFailed("Date range may not exceed 366 days", code="range_too_large")


def _scoped_rows(db: Session, principal: Principal, date_from: datetime, date_to: datetime,
                 department_id: uuid.UUID | None, category_id: uuid.UUID | None,
                 ward_id: uuid.UUID | None) -> list[Complaint]:
    principal.require(P.analytics_read)
    q = select(Complaint).where(Complaint.created_at >= date_from, Complaint.created_at < date_to)
    if not principal.has_global_read:
        if not principal.supervised_department_ids:
            raise Forbidden("No analytics scope")
        if department_id and department_id not in principal.supervised_department_ids:
            raise Forbidden("Department outside your scope")
        q = q.where(Complaint.department_id.in_(principal.supervised_department_ids))
    if department_id:
        q = q.where(Complaint.department_id == department_id)
    if category_id:
        q = q.where(Complaint.category_id == category_id)
    if ward_id:
        q = q.where(Complaint.ward_id == ward_id)
    return list(db.scalars(q).all())


def _hours(a: datetime, b: datetime) -> float:
    return (b - a).total_seconds() / 3600


def _group(rows: list[Complaint], key: str) -> list[dict]:
    groups: dict[str, list[Complaint]] = defaultdict(list)
    for c in rows:
        v = getattr(c, key)
        groups[str(v.value if hasattr(v, "value") else v) if v is not None else "none"].append(c)
    out = []
    for k, items in sorted(groups.items()):
        out.append({
            "key": k, "total": len(items),
            "open": sum(1 for c in items if c.status in OPEN_STATUSES),
            "resolved_or_closed": sum(1 for c in items if c.resolved_at is not None and c.status in (
                ComplaintStatus.resolved, ComplaintStatus.closed)),
            "overdue_open": sum(1 for c in items if c.status in OPEN_STATUSES and c.is_overdue),
        })
    return out


def compute(db: Session, principal: Principal, date_from: datetime, date_to: datetime,
            department_id: uuid.UUID | None = None, category_id: uuid.UUID | None = None,
            ward_id: uuid.UUID | None = None) -> dict:
    _validate_range(date_from, date_to)
    reports = _scoped_rows(db, principal, date_from, date_to, department_id, category_id, ward_id)
    issues = [c for c in reports if c.merged_into_id is None]
    status_counts = Counter(c.status.value for c in issues)
    resolved = [c for c in issues if c.resolved_at is not None]
    durations = [_hours(c.created_at, c.resolved_at) for c in resolved]  # type: ignore[arg-type]
    with_due = [c for c in resolved if c.due_at is not None]
    met = [c for c in with_due if c.resolved_at <= c.due_at]  # type: ignore[operator]
    return {
        "date_from": date_from, "date_to": date_to,
        "reports_total": len(reports),
        "issues_total": len(issues),
        "merged_duplicates": len(reports) - len(issues),
        "by_status": {s.value: status_counts.get(s.value, 0) for s in ComplaintStatus},
        "open": sum(1 for c in issues if c.status in OPEN_STATUSES),
        "overdue_open": sum(1 for c in issues if c.status in OPEN_STATUSES and c.is_overdue),
        "reopened": sum(1 for c in issues if c.reopen_count > 0),
        "resolution_hours_avg": round(statistics.fmean(durations), 2) if durations else None,
        "resolution_hours_median": round(statistics.median(durations), 2) if durations else None,
        "sla_met": len(met),
        "sla_measured": len(with_due),
        "sla_compliance": round(len(met) / len(with_due), 4) if with_due else None,
        "by_department": _group(issues, "department_id"),
        "by_category": _group(issues, "category_id"),
        "by_ward": _group(issues, "ward_id"),
        "by_priority": _group(issues, "priority"),
    }


def _csv_safe(value: object) -> str:
    """Neutralise spreadsheet formula injection for user-controlled strings."""
    text = "" if value is None else str(value)
    if text and text[0] in ("=", "+", "-", "@", "\t", "\r"):
        return "'" + text
    return text


def export_csv(db: Session, principal: Principal, date_from: datetime, date_to: datetime,
               department_id: uuid.UUID | None = None) -> str:
    principal.require(P.analytics_export)
    _validate_range(date_from, date_to)
    rows = _scoped_rows(db, principal, date_from, date_to, department_id, None, None)
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["reference", "title", "status", "priority", "category_id", "department_id", "ward_id",
                "created_at", "resolved_at", "due_at", "is_overdue", "merged_into_id"])
    for c in sorted(rows, key=lambda c: (c.created_at, c.reference)):
        w.writerow([_csv_safe(v) for v in (
            c.reference, c.title, c.status.value, c.priority.value, c.category_id, c.department_id, c.ward_id,
            c.created_at.isoformat(), c.resolved_at.isoformat() if c.resolved_at else "",
            c.due_at.isoformat() if c.due_at else "", c.is_overdue, c.merged_into_id or "")])
    return buf.getvalue()
