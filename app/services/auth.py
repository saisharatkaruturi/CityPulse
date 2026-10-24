"""Registration, login, logout, and principal resolution."""

from __future__ import annotations

import uuid

import jwt
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.core.config import Settings
from app.core.errors import AppError, Conflict, Forbidden, Unauthenticated
from app.core.permissions import Principal
from app.core.security import decode_access_token, hash_password, issue_access_token, verify_password
from app.core.time import utcnow
from app.domain.enums import Role
from app.models import AuthSession, Officer, User, UserRole
from app.schemas.auth import RegisterRequest


def normalize_email(email: str) -> str:
    return email.strip().lower()


def register_resident(db: Session, settings: Settings, req: RegisterRequest) -> User:
    if not settings.allow_self_registration:
        raise Forbidden("Self-registration is disabled", code="registration_disabled")
    now = utcnow()
    user = User(email=normalize_email(req.email), display_name=req.display_name.strip(), phone=req.phone,
                preferred_language=req.preferred_language, password_hash=hash_password(req.password))
    user.roles.append(UserRole(role=Role.resident, created_at=now))
    db.add(user)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # Same message as other registration failures would be ideal for enumeration
        # resistance, but a resident needs to know to log in instead; we keep it generic.
        raise Conflict("Registration could not be completed. If you already have an account, sign in.",
                       code="registration_failed") from None
    return user


def login(db: Session, settings: Settings, email: str, password: str) -> tuple[str, AuthSession]:
    user = db.scalar(select(User).where(User.email == normalize_email(email)))
    ok = verify_password(password, user.password_hash if user else None)
    if not user or not ok or not user.is_active:
        raise Unauthenticated("Invalid email or password", code="invalid_credentials")
    now = utcnow()
    session = AuthSession(user_id=user.id, created_at=now,
                          expires_at=now)  # expiry set below once the token is issued
    db.add(session)
    db.flush()
    token, expires = issue_access_token(settings, user.id, session.id, now)
    session.expires_at = expires
    db.commit()
    return token, session


def logout(db: Session, principal: Principal) -> None:
    if principal.session_id is None:
        return
    session = db.get(AuthSession, principal.session_id)
    if session and session.revoked_at is None:
        session.revoked_at = utcnow()
        db.commit()


def load_principal(db: Session, user: User, session_id: uuid.UUID | None) -> Principal:
    roles = frozenset(r.role for r in user.roles)
    supervised = frozenset(r.department_id for r in user.roles
                           if r.role == Role.supervisor and r.department_id is not None)
    officer = db.scalar(select(Officer).where(Officer.user_id == user.id))
    return Principal(user=user, session_id=session_id, roles=roles, supervised_department_ids=supervised,
                     officer=officer)


def authenticate_token(db: Session, settings: Settings, token: str) -> Principal:
    try:
        claims = decode_access_token(settings, token)
        user_id = uuid.UUID(claims["sub"])
        session_id = uuid.UUID(claims["sid"])
    except (jwt.PyJWTError, ValueError, KeyError):
        raise Unauthenticated("Invalid or expired credentials", code="invalid_token") from None
    session = db.get(AuthSession, session_id)
    now = utcnow()
    if session is None or session.user_id != user_id or session.revoked_at is not None \
            or session.expires_at <= now:
        raise Unauthenticated("Session is no longer valid", code="session_revoked")
    user = db.get(User, user_id)
    if user is None or not user.is_active:
        raise Unauthenticated("Account is not active", code="account_inactive")
    return load_principal(db, user, session_id)


def ensure_not_last_system_admin(db: Session, user_id: uuid.UUID) -> None:
    admins = db.scalars(select(UserRole.user_id).where(UserRole.role == Role.system_admin)).all()
    if set(admins) == {user_id}:
        raise AppError("Cannot remove the last system administrator", code="last_admin", status_code=409)
