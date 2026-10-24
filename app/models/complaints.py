"""Complaint aggregate and its history/child records."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    JSON,
    Boolean,
    CheckConstraint,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, IdMixin, TimestampMixin, UTCDateTime
from app.domain.enums import (
    ActorKind,
    ComplaintStatus,
    ExternalSyncState,
    LinkType,
    LocationSource,
    MediaKind,
    Priority,
    RoutingOutcome,
    ScanState,
    SourceChannel,
    Visibility,
)
from app.models.identity import enum_col


class Complaint(IdMixin, TimestampMixin, Base):
    __tablename__ = "complaints"
    __table_args__ = (
        CheckConstraint("latitude IS NULL OR (latitude >= -90 AND latitude <= 90)", name="lat_range"),
        CheckConstraint("longitude IS NULL OR (longitude >= -180 AND longitude <= 180)", name="lng_range"),
        CheckConstraint("merged_into_id IS NULL OR merged_into_id <> id", name="no_self_merge"),
        Index("ix_complaints_status_created", "status", "created_at"),
        Index("ix_complaints_department_status", "department_id", "status"),
        Index("ix_complaints_category_created", "category_id", "created_at"),
        Index("ix_complaints_lat_lng", "latitude", "longitude"),
    )

    # Public, human-readable tracking reference. Not an access secret: access is always authorised.
    reference: Mapped[str] = mapped_column(String(20), unique=True, nullable=False)
    reporter_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    original_language: Mapped[str] = mapped_column(String(8), default="en", nullable=False)

    reported_category_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("categories.id"))
    category_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("categories.id"))
    category_source: Mapped[str] = mapped_column(String(32), default="resident", nullable=False)

    ward_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("wards.id"), index=True)
    latitude: Mapped[float | None] = mapped_column(Float)
    longitude: Mapped[float | None] = mapped_column(Float)
    location_accuracy_m: Mapped[float | None] = mapped_column(Float)
    location_source: Mapped[LocationSource] = mapped_column(enum_col(LocationSource),
                                                           default=LocationSource.none, nullable=False)
    address_text: Mapped[str | None] = mapped_column(String(300))

    visibility: Mapped[Visibility] = mapped_column(enum_col(Visibility), default=Visibility.private,
                                                  nullable=False)
    priority: Mapped[Priority] = mapped_column(enum_col(Priority), nullable=False, index=True)
    priority_reason: Mapped[str | None] = mapped_column(String(300))
    safety_risk_reported: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    status: Mapped[ComplaintStatus] = mapped_column(enum_col(ComplaintStatus), nullable=False)
    source_channel: Mapped[SourceChannel] = mapped_column(enum_col(SourceChannel), default=SourceChannel.api,
                                                         nullable=False)

    department_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("departments.id"))
    team_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("teams.id"), index=True)
    assigned_officer_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("officers.id"), index=True)

    # Routing decision snapshot (the initial one is preserved forever in initial_routing).
    routing_rule_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("routing_rules.id"))
    routing_outcome: Mapped[RoutingOutcome] = mapped_column(enum_col(RoutingOutcome), nullable=False)
    routing_explanation: Mapped[str] = mapped_column(String(500), nullable=False)
    initial_routing: Mapped[dict] = mapped_column(JSON, nullable=False)
    routed_at: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)

    # SLA
    sla_policy_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("sla_policies.id"))
    sla_policy_version: Mapped[int | None] = mapped_column(Integer)
    acknowledge_due_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    due_at: Mapped[datetime | None] = mapped_column(UTCDateTime(), index=True)
    sla_paused_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    sla_paused_seconds: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_overdue: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    overdue_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    escalation_level: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    acknowledged_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    resolved_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    closed_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    resident_confirmed_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    resolution_notes: Mapped[str | None] = mapped_column(Text)
    reopen_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    reassignment_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    merged_into_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("complaints.id"), index=True)

    external_sync_state: Mapped[ExternalSyncState] = mapped_column(
        enum_col(ExternalSyncState), default=ExternalSyncState.not_configured, nullable=False)
    external_case_id: Mapped[str | None] = mapped_column(String(100))
    external_is_simulated: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    external_acknowledged_at: Mapped[datetime | None] = mapped_column(UTCDateTime())

    # Optimistic concurrency control.
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    __mapper_args__ = {"version_id_col": version}


class ComplaintStatusHistory(IdMixin, Base):
    __tablename__ = "complaint_status_history"

    complaint_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("complaints.id"), nullable=False, index=True)
    from_status: Mapped[ComplaintStatus | None] = mapped_column(enum_col(ComplaintStatus))
    to_status: Mapped[ComplaintStatus] = mapped_column(enum_col(ComplaintStatus), nullable=False)
    actor_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    actor_kind: Mapped[ActorKind] = mapped_column(enum_col(ActorKind), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(1000))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)


class ComplaintAssignment(IdMixin, Base):
    __tablename__ = "complaint_assignments"

    complaint_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("complaints.id"), nullable=False, index=True)
    from_department_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("departments.id"))
    to_department_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("departments.id"))
    from_team_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("teams.id"))
    to_team_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("teams.id"))
    from_officer_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("officers.id"))
    to_officer_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("officers.id"))
    kind: Mapped[str] = mapped_column(String(32), nullable=False)  # routing | assign | reassign | escalation
    routing_rule_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("routing_rules.id"))
    actor_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    actor_kind: Mapped[ActorKind] = mapped_column(enum_col(ActorKind), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(1000))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)


class ComplaintCategoryChange(IdMixin, Base):
    __tablename__ = "complaint_category_changes"

    complaint_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("complaints.id"), nullable=False, index=True)
    from_category_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("categories.id"))
    to_category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("categories.id"), nullable=False)
    actor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    reason: Mapped[str] = mapped_column(String(1000), nullable=False)
    rerouted: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)


class ComplaintPriorityChange(IdMixin, Base):
    __tablename__ = "complaint_priority_changes"

    complaint_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("complaints.id"), nullable=False, index=True)
    from_priority: Mapped[Priority] = mapped_column(enum_col(Priority), nullable=False)
    to_priority: Mapped[Priority] = mapped_column(enum_col(Priority), nullable=False)
    actor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    reason: Mapped[str] = mapped_column(String(1000), nullable=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)


class ComplaintComment(IdMixin, TimestampMixin, Base):
    """Resident-visible conversation on a complaint."""

    __tablename__ = "complaint_comments"

    complaint_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("complaints.id"), nullable=False, index=True)
    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    author_is_staff: Mapped[bool] = mapped_column(Boolean, nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    is_information_request: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_hidden: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)  # moderation


class ComplaintInternalNote(IdMixin, Base):
    """Staff-only notes. Never returned by resident endpoints or included in notifications."""

    __tablename__ = "complaint_internal_notes"

    complaint_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("complaints.id"), nullable=False, index=True)
    author_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)


class ComplaintLink(IdMixin, Base):
    __tablename__ = "complaint_links"
    __table_args__ = (UniqueConstraint("source_id", "target_id", "link_type"),
                      CheckConstraint("source_id <> target_id", name="no_self_link"))

    source_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("complaints.id"), nullable=False, index=True)
    target_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("complaints.id"), nullable=False, index=True)
    link_type: Mapped[LinkType] = mapped_column(enum_col(LinkType), nullable=False)
    reason: Mapped[str] = mapped_column(String(1000), nullable=False)
    actor_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)


class ComplaintSupporter(IdMixin, Base):
    __tablename__ = "complaint_supporters"
    __table_args__ = (UniqueConstraint("complaint_id", "user_id"),)

    complaint_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("complaints.id"), nullable=False, index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)


class ComplaintMedia(IdMixin, Base):
    __tablename__ = "complaint_media"

    complaint_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("complaints.id"), index=True)
    uploader_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    storage_key: Mapped[str] = mapped_column(String(200), unique=True, nullable=False)
    original_filename: Mapped[str] = mapped_column(String(200), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)
    size_bytes: Mapped[int] = mapped_column(Integer, nullable=False)
    kind: Mapped[MediaKind] = mapped_column(enum_col(MediaKind), nullable=False)
    visibility: Mapped[Visibility] = mapped_column(enum_col(Visibility), default=Visibility.private,
                                                  nullable=False)
    scan_state: Mapped[ScanState] = mapped_column(enum_col(ScanState), default=ScanState.not_scanned,
                                                 nullable=False)
    exif_stripped: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)
    attached_at: Mapped[datetime | None] = mapped_column(UTCDateTime())


class Feedback(IdMixin, Base):
    __tablename__ = "feedback"
    __table_args__ = (UniqueConstraint("complaint_id"),
                      CheckConstraint("rating >= 1 AND rating <= 5", name="rating_range"))

    complaint_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("complaints.id"), nullable=False)
    reporter_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    comment: Mapped[str | None] = mapped_column(String(2000))
    confirmed_resolved: Mapped[bool] = mapped_column(Boolean, nullable=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)


class EscalationHistory(IdMixin, Base):
    __tablename__ = "escalation_history"
    # Uniqueness makes the overdue/reminder jobs idempotent even if runs overlap.
    __table_args__ = (UniqueConstraint("complaint_id", "trigger", "level", "due_at_snapshot"),)

    complaint_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("complaints.id"), nullable=False, index=True)
    trigger: Mapped[str] = mapped_column(String(40), nullable=False)  # deadline_approaching | overdue
    level: Mapped[int] = mapped_column(Integer, nullable=False)
    due_at_snapshot: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)
    sla_policy_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("sla_policies.id"))
    target_officer_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("officers.id"))
    target_department_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("departments.id"))
    actor_kind: Mapped[ActorKind] = mapped_column(enum_col(ActorKind), nullable=False)
    result: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)


class AiClassification(IdMixin, Base):
    __tablename__ = "ai_classifications"

    complaint_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("complaints.id"), index=True)
    query_hash: Mapped[str | None] = mapped_column(String(64))
    provider: Mapped[str] = mapped_column(String(60), nullable=False)
    model_version: Mapped[str] = mapped_column(String(60), nullable=False)
    suggested_category_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("categories.id"))
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    accepted: Mapped[bool] = mapped_column(Boolean, nullable=False)
    final_category_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("categories.id"))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)
