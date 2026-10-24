from __future__ import annotations

from fastapi import APIRouter, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import DB, CurrentUser, SettingsDep
from app.core import ratelimit
from app.core.time import utcnow
from app.models import Department, NotificationPreference, User
from app.schemas.auth import (
    DemoAccountOut,
    LoginRequest,
    MetaOut,
    NotificationPreferencesIn,
    NotificationPreferencesOut,
    RegisterRequest,
    RoleGrantOut,
    TokenResponse,
    UserOut,
    UserUpdate,
)
from app.schemas.common import ERROR_RESPONSES
from app.services import auth as auth_service

router = APIRouter(prefix="/api", responses=ERROR_RESPONSES)


def user_out(user, db: Session | None = None) -> UserOut:  # noqa: ANN001
    grants = []
    for r in user.roles:
        g = RoleGrantOut.model_validate(r)
        dept = db.get(Department, r.department_id) if db is not None and r.department_id else None
        if dept is not None:
            g.department_code, g.department_name = dept.code, dept.name
        grants.append(g)
    return UserOut(id=user.id, email=user.email, display_name=user.display_name, phone=user.phone,
                   preferred_language=user.preferred_language, is_active=user.is_active,
                   roles=grants, created_at=user.created_at)


@router.post("/auth/register", response_model=UserOut, status_code=status.HTTP_201_CREATED, tags=["auth"],
             summary="Register a resident account (when self-registration is enabled)")
def register(req: RegisterRequest, request: Request, db: DB, settings: SettingsDep) -> UserOut:
    ratelimit.enforce(ratelimit.REGISTER, request)
    return user_out(auth_service.register_resident(db, settings, req))


@router.post("/auth/login", response_model=TokenResponse, tags=["auth"],
             summary="Exchange email + password for a bearer token")
def login(req: LoginRequest, request: Request, db: DB, settings: SettingsDep) -> TokenResponse:
    ratelimit.enforce(ratelimit.LOGIN, request)
    ratelimit.enforce(ratelimit.LOGIN, request, key=f"email:{req.email.lower()}")
    token, session = auth_service.login(db, settings, req.email, req.password)
    return TokenResponse(access_token=token, expires_at=session.expires_at)


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT, tags=["auth"],
             summary="Revoke the current session token")
def logout(principal: CurrentUser, db: DB) -> None:
    auth_service.logout(db, principal)


@router.get("/meta", response_model=MetaOut, tags=["meta"],
            summary="Public client configuration: demo mode and, only in demo mode, the fictional demo accounts")
def meta(db: DB, settings: SettingsDep) -> MetaOut:
    accounts: list[DemoAccountOut] = []
    if settings.demo_mode_enabled:
        from app import seed  # local import: seed data is only consulted in demo mode

        names = {h: n for h, n, _ in seed.USERS}
        emails = [seed.email(h) for _, h, _ in seed.DEMO_ACCOUNTS]
        existing = set(db.scalars(select(User.email).where(User.email.in_(emails), User.is_active.is_(True))))
        accounts = [DemoAccountOut(group=g, email=seed.email(h), display_name=names.get(h, h), description=d,
                                   password=settings.demo_password)
                    for g, h, d in seed.DEMO_ACCOUNTS if seed.email(h) in existing]
    return MetaOut(app_name=settings.app_name, demo_mode=settings.demo_mode_enabled, demo_accounts=accounts)


@router.get("/users/me", response_model=UserOut, tags=["users"])
def me(principal: CurrentUser, db: DB) -> UserOut:
    return user_out(principal.user, db)


@router.patch("/users/me", response_model=UserOut, tags=["users"],
              summary="Update display name, phone or language (email/roles are not editable here)")
def update_me(req: UserUpdate, principal: CurrentUser, db: DB) -> UserOut:
    user = db.merge(principal.user)
    for field, value in req.model_dump(exclude_unset=True, exclude_none=True).items():
        setattr(user, field, value)
    db.commit()
    return user_out(user, db)


@router.get("/users/me/notification-preferences", response_model=NotificationPreferencesOut, tags=["users"])
def get_prefs(principal: CurrentUser, db: DB) -> NotificationPreferencesOut:
    prefs = db.get(NotificationPreference, principal.id)
    if prefs is None:
        return NotificationPreferencesOut(email_enabled=False, sms_enabled=False,
                                          language=principal.user.preferred_language, updated_at=utcnow())
    return NotificationPreferencesOut.model_validate(prefs)


@router.put("/users/me/notification-preferences", response_model=NotificationPreferencesOut, tags=["users"],
            summary="Opt in/out of email and SMS. In-app notifications are always on.")
def put_prefs(req: NotificationPreferencesIn, principal: CurrentUser, db: DB) -> NotificationPreferencesOut:
    prefs = db.get(NotificationPreference, principal.id) or NotificationPreference(user_id=principal.id)
    prefs.email_enabled = req.email_enabled
    prefs.sms_enabled = req.sms_enabled
    prefs.language = req.language
    prefs.updated_at = utcnow()
    db.add(prefs)
    db.commit()
    return NotificationPreferencesOut.model_validate(prefs)
