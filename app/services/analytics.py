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
  * sla_policies_active / sla_policies_illustrative: target policies in force now, and whether any of
    them is flagged illustrative. With no policy in force, "met the target" is reported as not configured.
  * assignment_hours_median: (first assignment to an officer - created_at), over issues that have one.
  * The CSV export lists reports (not just issues) in the same scope and range, with readable names.
"""

from __future__ import annotations

import csv
import io
import statistics
import uuid
from collections import Counter, defaultdict
from datetime import datetime, timedelta

from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.core.errors import Forbidden, ValidationFailed
from app.core.permissions import P, Principal
from app.core.time import utcnow
from app.domain.enums import OPEN_STATUSES, ComplaintStatus, Priority
from app.models import Category, Complaint, ComplaintAssignment, Department, SlaPolicy, Ward

MAX_RANGE = timedelta(days=366)


def _validate_range(date_from: datetime, date_to: datetime) -> None:
    if date_to <= date_from:
        raise ValidationFailed("date_to must be after date_from", code="invalid_range")
    if date_to - date_from > MAX_RANGE:
        raise ValidationFailed("Date range may not exceed 366 days", code="range_too_large")


def _scoped_rows(db: Session, principal: Principal, date_from: datetime, date_to: datetime,
                 department_id: uuid.UUID | None, category_id: uuid.UUID | None,
                 ward_id: uuid.UUID | None, statuses: list[ComplaintStatus] | None = None,
                 priority: Priority | None = None) -> list[Complaint]:
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
        q = q.where(Complaint.category_id.in_(
            select(Category.id).where(or_(Category.id == category_id, Category.parent_id == category_id))))
    if ward_id:
        q = q.where(Complaint.ward_id == ward_id)
    if statuses:
        q = q.where(Complaint.status.in_(statuses))
    if priority:
        q = q.where(Complaint.priority == priority)
    return list(db.scalars(q).all())


def _first_assignment_hours(db: Session, issues: list[Complaint]) -> list[float]:
    if not issues:
        return []
    by_id = {c.id: c for c in issues}
    rows = db.execute(select(ComplaintAssignment.complaint_id, func.min(ComplaintAssignment.created_at))
                      .where(ComplaintAssignment.complaint_id.in_(by_id),
                             ComplaintAssignment.to_officer_id.is_not(None))
                      .group_by(ComplaintAssignment.complaint_id)).all()
    out = []
    for cid, first in rows:
        c = by_id[cid]
        if first is not None and first >= c.created_at:
            out.append(_hours(c.created_at, first))
    return out


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
    now = utcnow()
    policies = list(db.scalars(select(SlaPolicy).where(
        SlaPolicy.effective_from <= now,
        or_(SlaPolicy.effective_to.is_(None), SlaPolicy.effective_to > now))).all())
    assign_hours = _first_assignment_hours(db, issues)
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
        "sla_policies_active": len(policies),
        "sla_policies_illustrative": any(p.is_illustrative for p in policies),
        "assignment_hours_median": round(statistics.median(assign_hours), 2) if assign_hours else None,
        "assignment_measured": len(assign_hours),
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


EXPORT_COLUMNS = ["Reference", "Title", "Status", "Priority", "Category", "Department", "Ward",
                  "Submitted (UTC)", "Target due (UTC)", "Past target", "Marked resolved (UTC)", "Merged into"]


def export_csv(db: Session, principal: Principal, date_from: datetime, date_to: datetime,
               department_id: uuid.UUID | None = None, category_id: uuid.UUID | None = None,
               statuses: list[ComplaintStatus] | None = None,
               priority: Priority | None = None) -> tuple[str, int]:
    """Reports in the caller's scope as CSV text (without BOM) and the row count.

    Columns hold readable names, not internal ids. Resident identity, descriptions, comments and exact
    coordinates are never exported. Free text is protected against spreadsheet formula injection.
    """
    principal.require(P.analytics_export)
    _validate_range(date_from, date_to)
    rows = _scoped_rows(db, principal, date_from, date_to, department_id, category_id, None, statuses, priority)
    cats = {c.id: c.label for c in db.scalars(select(Category)).all()}
    depts = {d.id: d.name for d in db.scalars(select(Department)).all()}
    wards = {w.id: w.name for w in db.scalars(select(Ward)).all()}
    merged_ids = {c.merged_into_id for c in rows if c.merged_into_id}
    refs = dict(db.execute(select(Complaint.id, Complaint.reference).where(Complaint.id.in_(merged_ids))).tuples()
                ) if merged_ids else {}
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\r\n")
    w.writerow(EXPORT_COLUMNS)
    for c in sorted(rows, key=lambda c: (c.created_at, c.reference)):
        w.writerow([_csv_safe(v) for v in (
            c.reference, c.title, c.status.value, c.priority.value,
            cats.get(c.category_id, "") if c.category_id else "",
            depts.get(c.department_id, "") if c.department_id else "",
            wards.get(c.ward_id, "") if c.ward_id else "",
            c.created_at.isoformat(), c.due_at.isoformat() if c.due_at else "",
            "yes" if c.is_overdue and c.status in OPEN_STATUSES else "no",
            c.resolved_at.isoformat() if c.resolved_at else "",
            refs.get(c.merged_into_id, "") if c.merged_into_id else "")])
    return buf.getvalue(), len(rows)
