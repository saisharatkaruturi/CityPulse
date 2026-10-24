from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated

from pydantic import Field, StringConstraints, model_validator

from app.domain.enums import AnnouncementState, Priority, PublicationState, Role, ServiceType
from app.schemas.common import Reason, Schema, StrictInput

Code = Annotated[str, StringConstraints(strip_whitespace=True, pattern=r"^[a-z0-9][a-z0-9_.\-]{1,79}$")]
Name = Annotated[str, StringConstraints(strip_whitespace=True, min_length=2, max_length=160)]


class DepartmentOut(Schema):
    id: uuid.UUID
    code: str
    name: str
    description: str | None
    is_active: bool
    is_fallback: bool
    public_email: str | None
    public_phone: str | None
    parent_id: uuid.UUID | None
    is_demo: bool
    covered_ward_ids: list[uuid.UUID] = Field(default_factory=list)


class DepartmentCreate(StrictInput):
    code: Code
    name: Name
    description: str | None = Field(default=None, max_length=2000)
    public_email: str | None = Field(default=None, max_length=254)
    public_phone: str | None = Field(default=None, max_length=40)
    parent_id: uuid.UUID | None = None
    covered_ward_ids: list[uuid.UUID] = Field(default_factory=list)


class DepartmentUpdate(StrictInput):
    name: Name | None = None
    description: str | None = Field(default=None, max_length=2000)
    public_email: str | None = Field(default=None, max_length=254)
    public_phone: str | None = Field(default=None, max_length=40)
    is_active: bool | None = None
    covered_ward_ids: list[uuid.UUID] | None = None
    reason: Reason


class TeamOut(Schema):
    id: uuid.UUID
    department_id: uuid.UUID
    name: str
    is_active: bool


class TeamCreate(StrictInput):
    department_id: uuid.UUID
    name: Name


class OfficerOut(Schema):
    id: uuid.UUID
    user_id: uuid.UUID
    department_id: uuid.UUID
    team_id: uuid.UUID | None
    supervisor_officer_id: uuid.UUID | None
    is_active: bool
    accepts_assignments: bool
    display_name: str | None = None


class OfficerCreate(StrictInput):
    user_id: uuid.UUID
    department_id: uuid.UUID
    team_id: uuid.UUID | None = None
    supervisor_officer_id: uuid.UUID | None = None


class OfficerUpdate(StrictInput):
    team_id: uuid.UUID | None = None
    is_active: bool | None = None
    accepts_assignments: bool | None = None
    reason: Reason


class RoleGrantRequest(StrictInput):
    role: Role
    department_id: uuid.UUID | None = None
    ward_id: uuid.UUID | None = None
    reason: Reason


class WardOut(Schema):
    id: uuid.UUID
    code: str
    name: str
    is_active: bool
    has_boundary: bool
    provenance: str
    is_demo: bool


class WardCreate(StrictInput):
    code: Code
    name: Name
    provenance: str = Field(min_length=3, max_length=255)
    boundary: list[list[float]] | None = Field(default=None, description="[[lat, lng], ...] polygon")

    @model_validator(mode="after")
    def _poly(self) -> WardCreate:
        if self.boundary is not None:
            if len(self.boundary) < 3 or any(len(p) != 2 for p in self.boundary):
                raise ValueError("boundary must have at least 3 [lat, lng] points")
            for lat, lng in self.boundary:
                if not (-90 <= lat <= 90 and -180 <= lng <= 180):
                    raise ValueError("boundary coordinates out of range")
        return self


class CategoryOut(Schema):
    id: uuid.UUID
    code: str
    parent_id: uuid.UUID | None
    label: str
    description: str | None
    synonyms: list[str]
    examples: list[str]
    is_active: bool
    is_triage: bool
    default_priority: Priority


class CategoryCreate(StrictInput):
    code: Code
    label: Name
    parent_id: uuid.UUID | None = None
    description: str | None = Field(default=None, max_length=2000)
    synonyms: list[Annotated[str, StringConstraints(min_length=1, max_length=60)]] = Field(
        default_factory=list, max_length=50)
    examples: list[Annotated[str, StringConstraints(min_length=1, max_length=200)]] = Field(
        default_factory=list, max_length=20)
    labels_i18n: dict[str, str] = Field(default_factory=dict)
    default_priority: Priority = Priority.medium
    safety_sensitive: bool = False


class CategoryUpdate(StrictInput):
    label: Name | None = None
    description: str | None = Field(default=None, max_length=2000)
    synonyms: list[str] | None = None
    labels_i18n: dict[str, str] | None = None
    default_priority: Priority | None = None
    safety_sensitive: bool | None = None
    is_active: bool | None = None
    reason: Reason

    @model_validator(mode="after")
    def _no_auto_critical(self) -> CategoryUpdate:
        if self.default_priority == Priority.critical:
            raise ValueError("critical cannot be a category default; staff set it per case")
        return self


class ServiceOut(Schema):
    id: uuid.UUID
    code: str
    name: str
    summary: str
    instructions: str | None
    service_type: ServiceType
    state: PublicationState
    public_contact: str | None
    operating_hours: str | None
    eligibility: str | None
    owner_department_id: uuid.UUID | None
    department_ids: list[uuid.UUID]
    category_ids: list[uuid.UUID]
    last_reviewed_at: datetime | None
    is_demo: bool


class ServiceSearchResult(Schema):
    service: ServiceOut
    score: float
    matched_on: list[str]
    # The category that made this service relevant, when the ranking used one (explains the match).
    matched_category: CategoryOut | None = None


class ServiceSearchResponse(Schema):
    items: list[ServiceSearchResult]
    total: int
    no_match: bool
    guidance: str | None = None
    used_provider: str


class ServiceCreate(StrictInput):
    code: Code
    name: Name
    summary: str = Field(min_length=5, max_length=500)
    instructions: str | None = Field(default=None, max_length=5000)
    service_type: ServiceType
    synonyms: list[str] = Field(default_factory=list, max_length=50)
    public_contact: str | None = Field(default=None, max_length=255)
    operating_hours: str | None = Field(default=None, max_length=255)
    eligibility: str | None = Field(default=None, max_length=2000)
    owner_department_id: uuid.UUID | None = None
    department_ids: list[uuid.UUID] = Field(default_factory=list)
    category_ids: list[uuid.UUID] = Field(default_factory=list)


class ServiceUpdate(StrictInput):
    name: Name | None = None
    summary: str | None = Field(default=None, min_length=5, max_length=500)
    instructions: str | None = Field(default=None, max_length=5000)
    state: PublicationState | None = None
    synonyms: list[str] | None = None
    public_contact: str | None = Field(default=None, max_length=255)
    operating_hours: str | None = Field(default=None, max_length=255)
    mark_reviewed: bool = False
    reason: Reason


class RoutingRuleOut(Schema):
    id: uuid.UUID
    category_id: uuid.UUID
    ward_id: uuid.UUID | None
    department_id: uuid.UUID
    team_id: uuid.UUID | None
    precedence: int
    effective_from: datetime
    effective_to: datetime | None
    is_active: bool
    version: int
    supersedes_id: uuid.UUID | None
    notes: str | None
    created_at: datetime


class RoutingRuleCreate(StrictInput):
    category_id: uuid.UUID
    ward_id: uuid.UUID | None = None
    department_id: uuid.UUID
    team_id: uuid.UUID | None = None
    precedence: int = Field(default=100, ge=0, le=10_000)
    effective_from: datetime | None = None
    effective_to: datetime | None = None
    notes: str | None = Field(default=None, max_length=500)


class RoutingRuleUpdate(StrictInput):
    department_id: uuid.UUID | None = None
    team_id: uuid.UUID | None = None
    ward_id: uuid.UUID | None = None
    precedence: int | None = Field(default=None, ge=0, le=10_000)
    effective_to: datetime | None = None
    deactivate: bool = False
    reason: Reason


class RoutingSuggestRequest(StrictInput):
    description: str | None = Field(default=None, max_length=5000)
    category_id: uuid.UUID | None = None
    ward_id: uuid.UUID | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)


class CategorySuggestionOut(Schema):
    category_id: uuid.UUID
    category_code: str
    label: str
    confidence: float


class RoutingSuggestResponse(Schema):
    category: CategorySuggestionOut | None
    alternatives: list[CategorySuggestionOut]
    needs_manual_review: bool
    classifier: str
    classifier_simulated: bool
    ward_id: uuid.UUID | None
    outcome: str
    department_id: uuid.UUID | None
    department_name: str | None
    reason_code: str
    explanation: str
    emergency_notice: str


class SlaPolicyOut(Schema):
    id: uuid.UUID
    name: str
    category_id: uuid.UUID | None
    department_id: uuid.UUID | None
    priority: Priority | None
    acknowledge_hours: int
    resolve_hours: int
    pause_when_waiting: bool
    effective_from: datetime
    effective_to: datetime | None
    is_active: bool
    version: int
    supersedes_id: uuid.UUID | None
    is_illustrative: bool


class SlaPolicyCreate(StrictInput):
    name: Name
    category_id: uuid.UUID | None = None
    department_id: uuid.UUID | None = None
    priority: Priority | None = None
    acknowledge_hours: int = Field(ge=1, le=24 * 90)
    resolve_hours: int = Field(ge=1, le=24 * 365)
    pause_when_waiting: bool = True
    effective_from: datetime | None = None
    is_illustrative: bool = True

    @model_validator(mode="after")
    def _order(self) -> SlaPolicyCreate:
        if self.acknowledge_hours > self.resolve_hours:
            raise ValueError("acknowledge_hours cannot exceed resolve_hours")
        return self


class SlaPolicyUpdate(StrictInput):
    acknowledge_hours: int | None = Field(default=None, ge=1, le=24 * 90)
    resolve_hours: int | None = Field(default=None, ge=1, le=24 * 365)
    pause_when_waiting: bool | None = None
    deactivate: bool = False
    reason: Reason


class AnnouncementOut(Schema):
    id: uuid.UUID
    title: str
    body: str
    ward_id: uuid.UUID | None
    state: AnnouncementState
    publish_from: datetime | None
    publish_until: datetime | None
    is_demo: bool


class AnnouncementCreate(StrictInput):
    title: str = Field(min_length=3, max_length=200)
    body: str = Field(min_length=3, max_length=5000)
    ward_id: uuid.UUID | None = None
    publish_until: datetime | None = None


class AuditLogOut(Schema):
    id: uuid.UUID
    actor_id: uuid.UUID | None
    action: str
    entity_type: str
    entity_id: str
    reason: str | None
    request_id: str | None
    before: dict | None
    after: dict | None
    created_at: datetime


class OutboxEventOut(Schema):
    id: uuid.UUID
    event_type: str
    aggregate_id: uuid.UUID
    state: str
    attempt_count: int
    last_error: str | None
    created_at: datetime
    processed_at: datetime | None


class NotificationOut(Schema):
    id: uuid.UUID
    complaint_id: uuid.UUID | None
    complaint_reference: str | None
    event_type: str
    channel: str
    title: str
    body: str
    delivery_state: str
    created_at: datetime
    read_at: datetime | None


class AnalyticsGroup(Schema):
    key: str
    total: int
    open: int
    resolved_or_closed: int
    overdue_open: int


class AnalyticsOut(Schema):
    date_from: datetime
    date_to: datetime
    reports_total: int
    issues_total: int
    merged_duplicates: int
    by_status: dict[str, int]
    open: int
    overdue_open: int
    reopened: int
    resolution_hours_avg: float | None
    resolution_hours_median: float | None
    sla_met: int
    sla_measured: int
    sla_compliance: float | None
    sla_policies_active: int
    sla_policies_illustrative: bool
    assignment_hours_median: float | None
    assignment_measured: int
    by_department: list[AnalyticsGroup]
    by_category: list[AnalyticsGroup]
    by_ward: list[AnalyticsGroup]
    by_priority: list[AnalyticsGroup]
