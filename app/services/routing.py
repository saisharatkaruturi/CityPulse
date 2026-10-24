"""Routing: jurisdiction resolution + loading rules from the DB + the pure decision function."""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.errors import ValidationFailed
from app.domain import routing as rdomain
from app.domain.geo import point_in_polygon
from app.models import Category, Department, DepartmentWardCoverage, RoutingRule, Ward


@dataclass(frozen=True)
class Jurisdiction:
    ward_id: uuid.UUID | None
    out_of_area: bool
    method: str  # manual_ward | boundary_match | none | outside_boundaries


def resolve_jurisdiction(db: Session, ward_id: uuid.UUID | None, lat: float | None,
                         lng: float | None) -> Jurisdiction:
    """Uses only configured ward data. Reverse geocoding is never used as proof of jurisdiction."""
    if ward_id is not None:
        ward = db.get(Ward, ward_id)
        if ward is None or not ward.is_active:
            raise ValidationFailed("Unknown or inactive ward", code="invalid_ward",
                                   details=[{"field": "location.ward_id", "issue": "invalid"}])
        return Jurisdiction(ward.id, False, "manual_ward")
    if lat is None or lng is None:
        return Jurisdiction(None, False, "none")
    wards = db.scalars(select(Ward).where(Ward.is_active.is_(True), Ward.boundary.is_not(None))).all()
    if not wards:
        return Jurisdiction(None, False, "none")  # no boundary data configured: cannot judge
    for ward in wards:
        if ward.boundary and point_in_polygon(lat, lng, ward.boundary):
            return Jurisdiction(ward.id, False, "boundary_match")
    return Jurisdiction(None, True, "outside_boundaries")


def fallback_department(db: Session) -> Department | None:
    return db.scalar(select(Department).where(Department.is_fallback.is_(True), Department.is_active.is_(True))
                     .order_by(Department.created_at))


def decide(db: Session, category: Category | None, jurisdiction: Jurisdiction,
           now: datetime) -> rdomain.RoutingDecision:
    rules: list[RoutingRule] = []
    if category is not None and not category.is_triage:
        ids = [category.id] + ([category.parent_id] if category.parent_id else [])
        rules = list(db.scalars(select(RoutingRule).where(RoutingRule.category_id.in_(ids))).all())
    dept_ids = {r.department_id for r in rules}
    active = frozenset(db.scalars(select(Department.id).where(Department.id.in_(dept_ids),
                                                              Department.is_active.is_(True))).all()) \
        if dept_ids else frozenset()
    coverage: dict[uuid.UUID, set[uuid.UUID]] = {}
    if dept_ids:
        for row in db.execute(select(DepartmentWardCoverage).where(
                DepartmentWardCoverage.department_id.in_(dept_ids))).scalars():
            coverage.setdefault(row.department_id, set()).add(row.ward_id)
    inp = rdomain.RoutingInput(
        category_id=category.id if category else None,
        parent_category_id=category.parent_id if category else None,
        category_is_triage=bool(category and category.is_triage),
        ward_id=jurisdiction.ward_id,
        out_of_area=jurisdiction.out_of_area,
        now=now,
        active_departments=active,
        department_coverage={k: frozenset(v) for k, v in coverage.items()},
    )
    views = [rdomain.RuleView(r.id, r.category_id, r.ward_id, r.department_id, r.team_id, r.precedence,
                              r.effective_from, r.effective_to, r.is_active) for r in rules]
    return rdomain.decide(inp, views)
