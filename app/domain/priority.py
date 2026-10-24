"""Deterministic default priority.

Illustrative rules (not official municipal policy):
  * start from the category's configured default priority;
  * if the resident reports a safety risk AND the category is marked safety-sensitive,
    raise one level, capped at `high`;
  * never assign `critical` automatically: only authorised staff may set it, with a reason.
Free-text keywords never change priority on their own.
"""

from __future__ import annotations

from app.domain.enums import PRIORITY_ORDER, Priority

_BY_RANK = {v: k for k, v in PRIORITY_ORDER.items()}


def default_priority(category_default: Priority | None, safety_sensitive: bool,
                     safety_risk_reported: bool) -> tuple[Priority, str]:
    base = category_default or Priority.medium
    if base == Priority.critical:
        base = Priority.high
    if safety_risk_reported and safety_sensitive:
        raised = _BY_RANK[min(PRIORITY_ORDER[base] + 1, PRIORITY_ORDER[Priority.high])]
        return raised, f"category default {base.value}; raised for reported safety risk"
    if category_default is None:
        return base, "no confirmed category; standard priority pending triage"
    return base, f"category default {base.value}"


def is_alert_priority(priority: Priority) -> bool:
    return PRIORITY_ORDER[priority] >= PRIORITY_ORDER[Priority.high]
