"""SLA calculations.

Semantics (documented in README):
  * Targets are wall-clock hours in UTC. No working-hour or holiday calendar is applied,
    because no verified calendar data is configured.
  * Clock starts at complaint creation (`created_at`).
  * While status is on_hold / awaiting_resident (and the policy pauses), the clock stops:
    on resume, the paused duration is added to `due_at`.
  * A reminder fires once when the remaining time drops below `lead_fraction` of the target.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass(frozen=True)
class SlaTargets:
    acknowledge_due_at: datetime
    due_at: datetime


def compute_targets(start: datetime, acknowledge_hours: int, resolve_hours: int) -> SlaTargets:
    return SlaTargets(start + timedelta(hours=acknowledge_hours), start + timedelta(hours=resolve_hours))


def resume_due_at(due_at: datetime, paused_at: datetime, resumed_at: datetime) -> tuple[datetime, int]:
    paused = max(0, int((resumed_at - paused_at).total_seconds()))
    return due_at + timedelta(seconds=paused), paused


def reminder_threshold(created_at: datetime, due_at: datetime, lead_fraction: float) -> datetime:
    total = due_at - created_at
    return due_at - total * lead_fraction


def is_overdue(due_at: datetime | None, now: datetime, paused: bool) -> bool:
    return due_at is not None and not paused and now > due_at
