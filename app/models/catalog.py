"""Categories, service directory, routing rules, SLA policies, announcements."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, Column, ForeignKey, Integer, String, Table, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IdMixin, TimestampMixin, UTCDateTime
from app.domain.enums import AnnouncementState, Priority, PublicationState, ServiceType
from app.models.identity import enum_col


class Category(IdMixin, TimestampMixin, Base):
    __tablename__ = "categories"

    # Stable taxonomy ID used across DB, API, seeds and tests, e.g. "roads.pothole".
    code: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("categories.id"), index=True)
    label: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    synonyms: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    examples: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    labels_i18n: Mapped[dict] = mapped_column(JSON, default=dict, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_triage: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    default_priority: Mapped[Priority] = mapped_column(enum_col(Priority), default=Priority.medium,
                                                      nullable=False)
    # Whether a resident-declared safety risk may raise priority for this category.
    safety_sensitive: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


service_departments = Table(
    "service_departments", Base.metadata,
    Column("service_id", ForeignKey("services.id"), primary_key=True),
    Column("department_id", ForeignKey("departments.id"), primary_key=True),
)

service_categories = Table(
    "service_categories", Base.metadata,
    Column("service_id", ForeignKey("services.id"), primary_key=True),
    Column("category_id", ForeignKey("categories.id"), primary_key=True),
)


class Service(IdMixin, TimestampMixin, Base):
    __tablename__ = "services"

    code: Mapped[str] = mapped_column(String(80), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    summary: Mapped[str] = mapped_column(String(500), nullable=False)
    instructions: Mapped[str | None] = mapped_column(Text)
    service_type: Mapped[ServiceType] = mapped_column(enum_col(ServiceType), nullable=False)
    state: Mapped[PublicationState] = mapped_column(enum_col(PublicationState),
                                                   default=PublicationState.draft, nullable=False)
    synonyms: Mapped[list] = mapped_column(JSON, default=list, nullable=False)
    # Only filled when verified; never invented.
    public_contact: Mapped[str | None] = mapped_column(String(255))
    operating_hours: Mapped[str | None] = mapped_column(String(255))
    eligibility: Mapped[str | None] = mapped_column(Text)
    owner_department_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("departments.id"))
    last_reviewed_at: Mapped[datetime | None] = mapped_column(UTCDateTime())
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    departments = relationship("Department", secondary=service_departments, lazy="selectin")
    categories = relationship("Category", secondary=service_categories, lazy="selectin")


class RoutingRule(IdMixin, TimestampMixin, Base):
    """Versioned routing rule. Updates create a new row and retire the old one."""

    __tablename__ = "routing_rules"

    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("categories.id"), nullable=False, index=True)
    ward_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("wards.id"))
    department_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("departments.id"), nullable=False)
    team_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("teams.id"))
    precedence: Mapped[int] = mapped_column(Integer, default=100, nullable=False)
    effective_from: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)
    effective_to: Mapped[datetime | None] = mapped_column(UTCDateTime())
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    supersedes_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("routing_rules.id"))
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    notes: Mapped[str | None] = mapped_column(String(500))


class SlaPolicy(IdMixin, TimestampMixin, Base):
    """Versioned SLA policy. Sample values are illustrative, not official guarantees."""

    __tablename__ = "sla_policies"

    name: Mapped[str] = mapped_column(String(160), nullable=False)
    category_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("categories.id"))
    department_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("departments.id"))
    priority: Mapped[Priority | None] = mapped_column(enum_col(Priority))
    acknowledge_hours: Mapped[int] = mapped_column(Integer, nullable=False)
    resolve_hours: Mapped[int] = mapped_column(Integer, nullable=False)
    pause_when_waiting: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    effective_from: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)
    effective_to: Mapped[datetime | None] = mapped_column(UTCDateTime())
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    supersedes_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("sla_policies.id"))
    is_illustrative: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_by_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))


class Announcement(IdMixin, TimestampMixin, Base):
    __tablename__ = "announcements"

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    ward_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("wards.id"))
    state: Mapped[AnnouncementState] = mapped_column(enum_col(AnnouncementState),
                                                    default=AnnouncementState.draft, nullable=False)
    publish_from: Mapped[datetime | None] = mapped_column(UTCDateTime())
    publish_until: Mapped[datetime | None] = mapped_column(UTCDateTime())
    publisher_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
