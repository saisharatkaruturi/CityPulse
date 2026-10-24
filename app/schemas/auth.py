from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated

from pydantic import EmailStr, Field, StringConstraints

from app.domain.enums import Role
from app.schemas.common import Schema, StrictInput

Lang = Annotated[str, StringConstraints(pattern=r"^[a-z]{2}(-[A-Z]{2})?$")]
Phone = Annotated[str, StringConstraints(pattern=r"^\+?[0-9 ]{7,20}$")]


class RegisterRequest(StrictInput):
    email: EmailStr
    password: str = Field(min_length=10, max_length=128)
    display_name: str = Field(min_length=1, max_length=120)
    phone: Phone | None = None
    preferred_language: Lang = "en"


class LoginRequest(StrictInput):
    email: EmailStr
    password: str = Field(min_length=1, max_length=128)


class TokenResponse(Schema):
    access_token: str
    token_type: str = "bearer"
    expires_at: datetime


class RoleGrantOut(Schema):
    role: Role
    department_id: uuid.UUID | None
    ward_id: uuid.UUID | None
    # Lets the client name the role experience ("Road Supervisor", "Triage Desk") without a staff-only lookup.
    department_code: str | None = None
    department_name: str | None = None


class DemoAccountOut(Schema):
    group: str
    email: str
    display_name: str
    description: str
    password: str


class MetaOut(Schema):
    """Public runtime configuration for the web client. Holds no personal data."""

    app_name: str
    demo_mode: bool
    demo_accounts: list[DemoAccountOut]


class UserOut(Schema):
    """Safe profile. Never includes password hashes."""

    id: uuid.UUID
    email: str
    display_name: str
    phone: str | None
    preferred_language: str
    is_active: bool
    roles: list[RoleGrantOut]
    created_at: datetime


class UserUpdate(StrictInput):
    display_name: str | None = Field(default=None, min_length=1, max_length=120)
    phone: Phone | None = None
    preferred_language: Lang | None = None


class NotificationPreferencesIn(StrictInput):
    email_enabled: bool
    sms_enabled: bool
    language: Lang = "en"


class NotificationPreferencesOut(Schema):
    email_enabled: bool
    sms_enabled: bool
    language: str
    updated_at: datetime
