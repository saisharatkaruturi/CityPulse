"""Users, roles, sessions, departments, teams, officers, wards."""

from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import JSON, Boolean, Enum, ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, IdMixin, TimestampMixin, UTCDateTime
from app.domain.enums import Role


def enum_col(enum_cls: type, **kw: object) -> Enum:
    return Enum(enum_cls, native_enum=False, length=32, validate_strings=True,
                values_callable=lambda e: [m.value for m in e], **kw)


class User(IdMixin, TimestampMixin, Base):
    __tablename__ = "users"

    email: Mapped[str] = mapped_column(String(254), unique=True, nullable=False)
    phone: Mapped[str | None] = mapped_column(String(20))
    display_name: Mapped[str] = mapped_column(String(120), nullable=False)
    password_hash: Mapped[str | None] = mapped_column(String(255))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    preferred_language: Mapped[str] = mapped_column(String(8), default="en", nullable=False)
    deactivated_at: Mapped[datetime | None] = mapped_column(UTCDateTime())

    roles: Mapped[list[UserRole]] = relationship(back_populates="user", cascade="all, delete-orphan",
                                                 lazy="selectin", foreign_keys="UserRole.user_id")


class UserRole(IdMixin, Base):
    """Role grant, optionally scoped to a department or ward."""

    __tablename__ = "user_roles"
    __table_args__ = (UniqueConstraint("user_id", "role", "department_id", "ward_id"),)

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    role: Mapped[Role] = mapped_column(enum_col(Role), nullable=False)
    department_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("departments.id"))
    ward_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("wards.id"))
    granted_by_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)

    user: Mapped[User] = relationship(back_populates="roles", foreign_keys=[user_id])


class AuthSession(IdMixin, Base):
    """Server-side session backing each issued access token, so logout can revoke it."""

    __tablename__ = "auth_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    created_at: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(UTCDateTime(), nullable=False)
    revoked_at: Mapped[datetime | None] = mapped_column(UTCDateTime())


class Department(IdMixin, TimestampMixin, Base):
    __tablename__ = "departments"

    code: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    description: Mapped[str | None] = mapped_column(Text)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # Exactly the triage/fallback queue; protected from deactivation.
    is_fallback: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    public_email: Mapped[str | None] = mapped_column(String(254))
    public_phone: Mapped[str | None] = mapped_column(String(40))
    parent_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("departments.id"))
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class DepartmentWardCoverage(Base):
    """If a department has any coverage rows, it only serves those wards."""

    __tablename__ = "department_ward_coverage"

    department_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("departments.id"), primary_key=True)
    ward_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("wards.id"), primary_key=True)


class Team(IdMixin, TimestampMixin, Base):
    __tablename__ = "teams"
    __table_args__ = (UniqueConstraint("department_id", "name"),)

    department_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("departments.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(120), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Officer(IdMixin, TimestampMixin, Base):
    __tablename__ = "officers"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), unique=True, nullable=False)
    department_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("departments.id"), nullable=False, index=True)
    team_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("teams.id"), index=True)
    supervisor_officer_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("officers.id"))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    accepts_assignments: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    user: Mapped[User] = relationship(foreign_keys=[user_id], lazy="joined")


class Ward(IdMixin, TimestampMixin, Base):
    __tablename__ = "wards"

    code: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    # Polygon as [[lat, lng], ...]; only populated from verified or explicitly-labelled demo data.
    boundary: Mapped[list | None] = mapped_column(JSON)
    provenance: Mapped[str] = mapped_column(String(255), nullable=False)
    is_demo: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
