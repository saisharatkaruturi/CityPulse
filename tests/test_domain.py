"""Unit tests for pure domain rules: workflow, routing, priority, SLA, geo, classifier."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

import pytest

from app.adapters.classifier import CategoryOption, KeywordClassifier
from app.domain import routing as r
from app.domain import sla
from app.domain.enums import ComplaintStatus as S
from app.domain.enums import Priority, RoutingOutcome
from app.domain.geo import bounding_box, haversine_m, point_in_polygon
from app.domain.priority import default_priority
from app.domain.workflow import TRANSITIONS, Actor, TransitionError, allowed_targets, check_transition

NOW = datetime(2026, 1, 1, tzinfo=UTC)

# --- Workflow -------------------------------------------------------------------------------------


@pytest.mark.parametrize("current,target,actor", [
    (cur, to, actor) for cur, targets in TRANSITIONS.items() for to, t in targets.items() for actor in t.actors
])
def test_every_allowed_transition_passes(current, target, actor):
    t = check_transition(current, target, actor, "a sufficient reason")
    assert t.to == target


@pytest.mark.parametrize("current,target,actor", [
    (S.submitted, S.resolved, Actor.STAFF),
    (S.submitted, S.in_progress, Actor.STAFF),
    (S.closed, S.in_progress, Actor.STAFF),
    (S.rejected, S.under_review, Actor.STAFF),
    (S.withdrawn, S.submitted, Actor.RESIDENT),
    (S.in_progress, S.resolved, Actor.RESIDENT),
    (S.submitted, S.rejected, Actor.RESIDENT),
    (S.resolved, S.closed, "anonymous"),
])
def test_forbidden_transitions(current, target, actor):
    with pytest.raises(TransitionError):
        check_transition(current, target, actor, "reason")


@pytest.mark.parametrize("target", [S.rejected, S.on_hold, S.awaiting_resident])
def test_reason_required(target):
    with pytest.raises(TransitionError) as e:
        check_transition(S.under_review, target, Actor.STAFF, "  ")
    assert e.value.code == "reason_required"


def test_same_state_rejected():
    with pytest.raises(TransitionError):
        check_transition(S.assigned, S.assigned, Actor.STAFF, None)


def test_terminal_states_have_no_exits():
    assert allowed_targets(S.rejected, Actor.STAFF) == []
    assert allowed_targets(S.withdrawn, Actor.RESIDENT) == []


def test_every_status_is_in_state_machine():
    assert set(TRANSITIONS) == set(S)


# --- Routing --------------------------------------------------------------------------------------

CAT, PARENT, WARD, OTHER_WARD = (uuid.uuid4() for _ in range(4))
D1, D2 = uuid.uuid4(), uuid.uuid4()


def rule(cat=CAT, ward=None, dept=D1, prec=100, active=True, start=NOW - timedelta(days=1), end=None):  # noqa: ANN001, ANN201
    return r.RuleView(uuid.uuid4(), cat, ward, dept, None, prec, start, end, active)


def inp(**kw):  # noqa: ANN003, ANN201
    base = dict(category_id=CAT, parent_category_id=PARENT, category_is_triage=False, ward_id=WARD,
                out_of_area=False, now=NOW, active_departments=frozenset({D1, D2}))
    base.update(kw)
    return r.RoutingInput(**base)


def test_route_valid_mapping():
    d = r.decide(inp(), [rule()])
    assert d.outcome == RoutingOutcome.routed and d.department_id == D1 and d.rule_id is not None


def test_route_unknown_category_goes_to_triage():
    d = r.decide(inp(category_id=None), [rule()])
    assert d.outcome == RoutingOutcome.fallback and d.reason_code == "unknown_category"
    assert r.decide(inp(category_is_triage=True), [rule()]).reason_code == "unknown_category"


def test_route_no_match():
    assert r.decide(inp(), [rule(cat=uuid.uuid4())]).reason_code == "no_matching_rule"


def test_route_inactive_department():
    d = r.decide(inp(active_departments=frozenset()), [rule()])
    assert d.reason_code == "department_inactive" and d.department_id is None


def test_route_conflicting_rules_go_to_triage():
    d = r.decide(inp(), [rule(dept=D1, prec=50), rule(dept=D2, prec=50)])
    assert d.reason_code == "conflicting_rules"


def test_route_precedence_breaks_ties():
    d = r.decide(inp(), [rule(dept=D1, prec=50), rule(dept=D2, prec=10)])
    assert d.department_id == D2


def test_route_specificity_beats_precedence():
    ward_rule = rule(dept=D2, ward=WARD, prec=500)
    assert r.decide(inp(), [rule(dept=D1, prec=1), ward_rule]).department_id == D2
    parent_rule = rule(cat=PARENT, dept=D2, prec=1)
    assert r.decide(inp(), [parent_rule, rule(dept=D1, prec=999)]).department_id == D1


def test_route_parent_category_fallback():
    assert r.decide(inp(), [rule(cat=PARENT, dept=D2)]).department_id == D2


def test_route_outside_jurisdiction():
    assert r.decide(inp(out_of_area=True), [rule()]).reason_code == "outside_jurisdiction"


def test_route_ward_rule_skipped_for_other_ward():
    assert r.decide(inp(ward_id=OTHER_WARD), [rule(ward=WARD)]).reason_code == "no_matching_rule"


def test_route_effective_dates_and_inactive_rule():
    assert r.decide(inp(), [rule(start=NOW + timedelta(days=1))]).outcome == RoutingOutcome.fallback
    assert r.decide(inp(), [rule(end=NOW)]).outcome == RoutingOutcome.fallback
    assert r.decide(inp(), [rule(active=False)]).outcome == RoutingOutcome.fallback


def test_route_department_coverage():
    cov = {D1: frozenset({OTHER_WARD})}
    assert r.decide(inp(department_coverage=cov), [rule()]).outcome == RoutingOutcome.fallback
    assert r.decide(inp(department_coverage=cov, ward_id=OTHER_WARD), [rule()]).department_id == D1


# --- Priority -------------------------------------------------------------------------------------

def test_priority_is_deterministic_and_never_auto_critical():
    assert default_priority(Priority.medium, True, True)[0] == Priority.high
    assert default_priority(Priority.high, True, True)[0] == Priority.high
    assert default_priority(Priority.medium, False, True)[0] == Priority.medium
    assert default_priority(Priority.critical, True, True)[0] == Priority.high
    assert default_priority(None, False, False)[0] == Priority.medium


# --- SLA ------------------------------------------------------------------------------------------

def test_sla_targets_and_pause():
    t = sla.compute_targets(NOW, 12, 48)
    assert t.acknowledge_due_at == NOW + timedelta(hours=12) and t.due_at == NOW + timedelta(hours=48)
    due, paused = sla.resume_due_at(t.due_at, NOW + timedelta(hours=1), NOW + timedelta(hours=4))
    assert paused == 3 * 3600 and due == t.due_at + timedelta(hours=3)
    assert sla.is_overdue(t.due_at, t.due_at + timedelta(seconds=1), paused=False)
    assert not sla.is_overdue(t.due_at, t.due_at + timedelta(seconds=1), paused=True)
    assert sla.reminder_threshold(NOW, t.due_at, 0.25) == NOW + timedelta(hours=36)


# --- Geo & classifier -----------------------------------------------------------------------------

def test_geo_helpers():
    square = [[0, 0], [0, 1], [1, 1], [1, 0]]
    assert point_in_polygon(0.5, 0.5, square)
    assert not point_in_polygon(1.5, 0.5, square)
    assert 1100 < haversine_m(17.4, 78.4, 17.41, 78.4) < 1120
    lo, hi, _, _ = bounding_box(17.4, 78.4, 1000)
    assert lo < 17.4 < hi


def test_keyword_classifier():
    opts = [CategoryOption("roads.pothole", "Pothole", ("pothole", "road damage")),
            CategoryOption("lighting.streetlight", "Streetlight", ("streetlight", "lamp"))]
    res = KeywordClassifier().classify("Huge POTHOLE and road damage here", opts)
    assert res.suggestions[0].category_code == "roads.pothole" and res.suggestions[0].confidence >= 0.6
    weak = KeywordClassifier().classify("a lamp", opts)
    assert weak.suggestions[0].confidence < 0.6  # single weak keyword never decides with certainty
    assert KeywordClassifier().classify("nothing relevant", opts).suggestions == []
