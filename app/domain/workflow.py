"""Central complaint state machine.

This module is the single source of truth for which status changes are allowed, who may
perform them, and which ones need a reason. Services call `check_transition` before writing.

Resolved vs closed:
  * `resolved` means staff marked the work done. It is NOT independent verification.
  * `closed` happens when the reporter confirms the fix (feedback), when staff close it, or
    when the auto-close job runs after `AUTO_CLOSE_RESOLVED_AFTER_DAYS` without a reopen.

System closure with a reason (`closed` from any open state) is used only when a verified
duplicate is merged into another report.

SLA clock: paused while status is `on_hold` or `awaiting_resident` (see app/domain/sla.py).
"""

from __future__ import annotations

from dataclasses import dataclass

from app.domain.enums import ComplaintStatus as S


class Actor:
    RESIDENT = "resident"  # the complaint's reporter
    STAFF = "staff"  # officer/supervisor/admin with scope over the complaint
    SYSTEM = "system"  # background jobs and internal automation


@dataclass(frozen=True)
class Transition:
    to: S
    actors: frozenset[str]
    reason_required: bool = False


def _t(to: S, *actors: str, reason: bool = False) -> Transition:
    return Transition(to, frozenset(actors), reason)


R, ST, SY = Actor.RESIDENT, Actor.STAFF, Actor.SYSTEM

TRANSITIONS: dict[S, dict[S, Transition]] = {
    S.submitted: {t.to: t for t in [
        _t(S.under_review, ST, SY), _t(S.assigned, ST, SY), _t(S.rejected, ST, reason=True),
        _t(S.withdrawn, R, ST), _t(S.awaiting_resident, ST, reason=True), _t(S.closed, SY, reason=True),
    ]},
    S.under_review: {t.to: t for t in [
        _t(S.assigned, ST, SY), _t(S.rejected, ST, reason=True), _t(S.withdrawn, R, ST),
        _t(S.awaiting_resident, ST, reason=True), _t(S.on_hold, ST, reason=True),
        _t(S.closed, SY, reason=True),
    ]},
    S.assigned: {t.to: t for t in [
        _t(S.in_progress, ST), _t(S.awaiting_resident, ST, reason=True), _t(S.on_hold, ST, reason=True),
        _t(S.under_review, ST, reason=True), _t(S.rejected, ST, reason=True), _t(S.withdrawn, R, ST),
        _t(S.resolved, ST), _t(S.closed, SY, reason=True),
    ]},
    S.in_progress: {t.to: t for t in [
        _t(S.awaiting_resident, ST, reason=True), _t(S.on_hold, ST, reason=True), _t(S.resolved, ST),
        _t(S.withdrawn, R, ST), _t(S.under_review, ST, reason=True), _t(S.closed, SY, reason=True),
    ]},
    S.awaiting_resident: {t.to: t for t in [
        _t(S.in_progress, ST, SY), _t(S.under_review, ST, SY), _t(S.assigned, ST, SY),
        _t(S.withdrawn, R, ST), _t(S.rejected, ST, reason=True), _t(S.closed, SY, reason=True),
    ]},
    S.on_hold: {t.to: t for t in [
        _t(S.in_progress, ST), _t(S.assigned, ST), _t(S.under_review, ST), _t(S.withdrawn, R, ST),
        _t(S.rejected, ST, reason=True), _t(S.closed, SY, reason=True),
    ]},
    S.resolved: {t.to: t for t in [
        _t(S.closed, R, ST, SY), _t(S.reopened, R, ST, reason=True),
    ]},
    S.reopened: {t.to: t for t in [
        _t(S.under_review, ST), _t(S.assigned, ST, SY), _t(S.in_progress, ST), _t(S.resolved, ST),
        _t(S.on_hold, ST, reason=True), _t(S.withdrawn, R, ST), _t(S.closed, SY, reason=True),
    ]},
    S.closed: {t.to: t for t in [
        _t(S.reopened, R, ST, reason=True),
    ]},
    S.rejected: {},
    S.withdrawn: {},
}


class TransitionError(Exception):
    def __init__(self, code: str, message: str) -> None:
        super().__init__(message)
        self.code = code
        self.message = message


def allowed_targets(current: S, actor: str) -> list[S]:
    return [to for to, t in TRANSITIONS[current].items() if actor in t.actors]


def check_transition(current: S, target: S, actor: str, reason: str | None) -> Transition:
    if current == target:
        raise TransitionError("invalid_transition", f"Complaint is already {current.value}")
    transition = TRANSITIONS[current].get(target)
    if transition is None:
        raise TransitionError("invalid_transition",
                              f"Cannot move from {current.value} to {target.value}")
    if actor not in transition.actors:
        raise TransitionError("transition_not_permitted",
                              f"This actor may not move a complaint from {current.value} to {target.value}")
    if transition.reason_required and not (reason and reason.strip()):
        raise TransitionError("reason_required", f"A reason is required to move to {target.value}")
    return transition
