from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated

from pydantic import Field, StringConstraints, model_validator

from app.domain.enums import (
    ComplaintStatus,
    ExternalSyncState,
    LinkType,
    LocationSource,
    MediaKind,
    Priority,
    RoutingOutcome,
    SourceChannel,
    Visibility,
)
from app.schemas.common import OptionalReason, Reason, Schema, StrictInput

Title = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=200)]
Description = Annotated[str, StringConstraints(strip_whitespace=True, min_length=10, max_length=5000)]
CommentBody = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1, max_length=2000)]


class LocationIn(StrictInput):
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    accuracy_m: float | None = Field(default=None, ge=0, le=100_000)
    source: LocationSource = LocationSource.none
    ward_id: uuid.UUID | None = None
    address_text: str | None = Field(default=None, max_length=300)

    @model_validator(mode="after")
    def _pair(self) -> LocationIn:
        if (self.latitude is None) != (self.longitude is None):
            raise ValueError("latitude and longitude must be provided together")
        return self


class ComplaintCreate(StrictInput):
    title: Title
    description: Description
    category_id: uuid.UUID | None = Field(
        default=None, description="Resident-selected category. Omit if unsure; the case goes to triage.")
    location: LocationIn | None = None
    visibility: Visibility = Visibility.private
    safety_risk: bool = Field(default=False, description="Resident reports an immediate safety risk")
    language: Annotated[str, StringConstraints(pattern=r"^[a-z]{2}$")] = "en"
    media_ids: list[uuid.UUID] = Field(default_factory=list, max_length=5)
    source_channel: SourceChannel = SourceChannel.api

    @model_validator(mode="after")
    def _channel(self) -> ComplaintCreate:
        if self.source_channel in (SourceChannel.seed, SourceChannel.staff_entry):
            raise ValueError("source_channel not permitted")
        return self


class ResidentComplaintUpdate(StrictInput):
    """Fields a reporter may edit while the complaint has not yet been picked up."""

    title: Title | None = None
    description: Description | None = None
    visibility: Visibility | None = None


class StaffComplaintUpdate(StrictInput):
    category_id: uuid.UUID | None = None
    priority: Priority | None = None
    visibility: Visibility | None = None
    reason: Reason
    reroute: bool = Field(default=True, description="Re-evaluate routing after a category change")


class TransitionRequest(StrictInput):
    to_status: ComplaintStatus
    reason: OptionalReason = None


class AssignRequest(StrictInput):
    officer_id: uuid.UUID | None = None
    team_id: uuid.UUID | None = None
    department_id: uuid.UUID | None = None

    @model_validator(mode="after")
    def _target(self) -> AssignRequest:
        if not (self.officer_id or self.team_id or self.department_id):
            raise ValueError("Provide officer_id, team_id or department_id")
        return self


class ReassignRequest(AssignRequest):
    reason: Reason


class ResolveRequest(StrictInput):
    resolution_notes: Annotated[str, StringConstraints(strip_whitespace=True, max_length=5000)] | None = None
    evidence_media_ids: list[uuid.UUID] = Field(default_factory=list, max_length=10)


class CloseRequest(StrictInput):
    reason: OptionalReason = None


class ReopenRequest(StrictInput):
    reason: Reason


class WithdrawRequest(StrictInput):
    reason: OptionalReason = None


class CommentCreate(StrictInput):
    body: CommentBody
    request_information: bool = Field(default=False,
                                      description="Staff only: ask the resident for more information")


class NoteCreate(StrictInput):
    body: CommentBody


class FeedbackCreate(StrictInput):
    rating: int = Field(ge=1, le=5)
    comment: str | None = Field(default=None, max_length=2000)
    confirm_resolved: bool = Field(default=True, description="Reporter confirms the issue is fixed")


class MergeRequest(StrictInput):
    target_id: uuid.UUID = Field(description="The complaint to keep; this complaint is merged into it")
    reason: Reason


# --- Responses ---------------------------------------------------------------------------------

class StatusEventOut(Schema):
    from_status: ComplaintStatus | None
    to_status: ComplaintStatus
    actor_kind: str
    actor_is_staff: bool | None = None
    reason: str | None
    created_at: datetime


class CommentOut(Schema):
    id: uuid.UUID
    author_id: uuid.UUID
    author_is_staff: bool
    body: str
    is_information_request: bool
    created_at: datetime


class NoteOut(Schema):
    id: uuid.UUID
    author_id: uuid.UUID
    body: str
    created_at: datetime


class MediaOut(Schema):
    id: uuid.UUID
    complaint_id: uuid.UUID | None
    original_filename: str
    content_type: str
    size_bytes: int
    kind: MediaKind
    scan_state: str
    exif_stripped: bool
    created_at: datetime


class AssignmentOut(Schema):
    kind: str
    from_department_id: uuid.UUID | None
    to_department_id: uuid.UUID | None
    from_team_id: uuid.UUID | None
    to_team_id: uuid.UUID | None
    from_officer_id: uuid.UUID | None
    to_officer_id: uuid.UUID | None
    routing_rule_id: uuid.UUID | None
    actor_kind: str
    reason: str | None
    created_at: datetime


class ProgressOut(Schema):
    """Distinguishes what has actually happened. `externally_acknowledged` is only true when a
    configured municipal integration confirmed receipt (and `external_is_simulated` says if mock)."""

    received_locally: bool
    routed_to_department: bool
    department_acknowledged: bool
    externally_acknowledged: bool
    external_is_simulated: bool
    marked_resolved: bool
    resident_confirmed: bool
    summary: str


class ComplaintResidentOut(Schema):
    id: uuid.UUID
    reference: str
    title: str
    description: str
    original_language: str
    category_id: uuid.UUID | None
    reported_category_id: uuid.UUID | None
    ward_id: uuid.UUID | None
    latitude: float | None
    longitude: float | None
    address_text: str | None
    visibility: Visibility
    priority: Priority
    status: ComplaintStatus
    department_id: uuid.UUID | None
    routing_outcome: RoutingOutcome
    due_at: datetime | None
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None
    closed_at: datetime | None
    resolution_notes: str | None
    merged_into_reference: str | None = None
    external_sync_state: ExternalSyncState
    external_case_id: str | None
    external_is_simulated: bool
    version: int
    progress: ProgressOut
    timeline: list[StatusEventOut] = Field(default_factory=list)


class ComplaintStaffOut(ComplaintResidentOut):
    reporter_id: uuid.UUID
    category_source: str
    priority_reason: str | None
    safety_risk_reported: bool
    source_channel: SourceChannel
    team_id: uuid.UUID | None
    assigned_officer_id: uuid.UUID | None
    routing_rule_id: uuid.UUID | None
    routing_explanation: str
    initial_routing: dict
    sla_policy_id: uuid.UUID | None
    sla_policy_version: int | None
    acknowledge_due_at: datetime | None
    sla_paused_at: datetime | None
    is_overdue: bool
    escalation_level: int
    reopen_count: int
    reassignment_count: int
    merged_into_id: uuid.UUID | None
    location_source: LocationSource
    location_accuracy_m: float | None
    assignments: list[AssignmentOut] = Field(default_factory=list)


class ComplaintListItem(Schema):
    id: uuid.UUID
    reference: str
    title: str
    status: ComplaintStatus
    priority: Priority
    category_id: uuid.UUID | None
    department_id: uuid.UUID | None
    ward_id: uuid.UUID | None
    assigned_officer_id: uuid.UUID | None = None
    is_overdue: bool
    due_at: datetime | None
    created_at: datetime
    updated_at: datetime


class PublicComplaintSummary(Schema):
    """Safe public view: no reporter, no description, coordinates rounded."""

    id: uuid.UUID
    reference: str
    title: str
    category_id: uuid.UUID | None
    status: ComplaintStatus
    ward_id: uuid.UUID | None
    approx_latitude: float | None
    approx_longitude: float | None
    distance_m: int | None = None
    support_count: int
    created_at: datetime


class DuplicateCandidate(Schema):
    id: uuid.UUID | None = Field(default=None, description="Only present when the caller may open it")
    reference: str
    title: str | None
    category_id: uuid.UUID | None
    status: ComplaintStatus
    distance_m: int | None
    text_similarity: float
    created_at: datetime


class LinkOut(Schema):
    source_id: uuid.UUID
    target_id: uuid.UUID
    link_type: LinkType
    reason: str
    created_at: datetime


class FeedbackOut(Schema):
    complaint_id: uuid.UUID
    rating: int
    comment: str | None
    confirmed_resolved: bool
    created_at: datetime


class SupportOut(Schema):
    complaint_id: uuid.UUID
    support_count: int
    supported: bool
