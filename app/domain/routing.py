"""Deterministic routing decision (pure function; persistence lives in app/services/routing.py).

Precedence, highest first:
  1. Rule for the exact category beats a rule inherited from the parent category.
  2. A ward-specific rule beats a ward-agnostic rule.
  3. Lower `precedence` number wins.
If two or more rules still tie and point at different departments, the case is ambiguous
and goes to the triage queue rather than being guessed. Rules whose department is inactive,
or whose department's ward coverage excludes the complaint's ward, are skipped.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime

from app.domain.enums import RoutingOutcome


@dataclass(frozen=True)
class RuleView:
    id: uuid.UUID
    category_id: uuid.UUID
    ward_id: uuid.UUID | None
    department_id: uuid.UUID
    team_id: uuid.UUID | None
    precedence: int
    effective_from: datetime
    effective_to: datetime | None
    is_active: bool


@dataclass(frozen=True)
class RoutingInput:
    category_id: uuid.UUID | None
    parent_category_id: uuid.UUID | None
    category_is_triage: bool
    ward_id: uuid.UUID | None
    out_of_area: bool
    now: datetime
    active_departments: frozenset[uuid.UUID]
    # department_id -> wards covered; departments absent from the map cover every ward.
    department_coverage: dict[uuid.UUID, frozenset[uuid.UUID]] = field(default_factory=dict)


@dataclass(frozen=True)
class RoutingDecision:
    outcome: RoutingOutcome
    department_id: uuid.UUID | None
    team_id: uuid.UUID | None
    rule_id: uuid.UUID | None
    reason_code: str
    explanation: str

    def as_dict(self) -> dict:
        return {
            "outcome": self.outcome.value,
            "department_id": str(self.department_id) if self.department_id else None,
            "team_id": str(self.team_id) if self.team_id else None,
            "rule_id": str(self.rule_id) if self.rule_id else None,
            "reason_code": self.reason_code,
            "explanation": self.explanation,
        }


def _fallback(code: str, explanation: str) -> RoutingDecision:
    return RoutingDecision(RoutingOutcome.fallback, None, None, None, code, explanation)


def decide(inp: RoutingInput, rules: list[RuleView]) -> RoutingDecision:
    if inp.category_id is None or inp.category_is_triage:
        return _fallback("unknown_category", "No confirmed category; sent to triage for manual review")
    if inp.out_of_area:
        return _fallback("outside_jurisdiction",
                         "Location is outside the configured service area; sent to triage")

    candidates: list[tuple[tuple[int, int, int], RuleView]] = []
    skipped_inactive = False
    for rule in rules:
        if not rule.is_active or rule.effective_from > inp.now:
            continue
        if rule.effective_to is not None and rule.effective_to <= inp.now:
            continue
        if rule.category_id == inp.category_id:
            cat_rank = 0
        elif inp.parent_category_id is not None and rule.category_id == inp.parent_category_id:
            cat_rank = 1
        else:
            continue
        if rule.ward_id is not None and rule.ward_id != inp.ward_id:
            continue
        if rule.department_id not in inp.active_departments:
            skipped_inactive = True
            continue
        coverage = inp.department_coverage.get(rule.department_id)
        if coverage is not None and (inp.ward_id is None or inp.ward_id not in coverage):
            continue
        ward_rank = 0 if rule.ward_id is not None else 1
        candidates.append(((cat_rank, ward_rank, rule.precedence), rule))

    if not candidates:
        if skipped_inactive:
            return _fallback("department_inactive",
                             "Matching rule points at an inactive department; sent to triage")
        return _fallback("no_matching_rule", "No active routing rule matches; sent to triage")

    candidates.sort(key=lambda c: c[0])
    best_key = candidates[0][0]
    best = [r for k, r in candidates if k == best_key]
    if len({r.department_id for r in best}) > 1:
        return _fallback("conflicting_rules",
                         "Multiple equally specific rules target different departments; sent to triage")
    rule = best[0]
    specificity = ("exact category" if best_key[0] == 0 else "parent category") + (
        ", ward-specific" if best_key[1] == 0 else ", any ward")
    return RoutingDecision(RoutingOutcome.routed, rule.department_id, rule.team_id, rule.id, "rule_match",
                           f"Matched routing rule (precedence {rule.precedence}; {specificity})")
