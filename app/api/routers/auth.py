from __future__ import annotations

from fastapi import APIRouter, Request, status

from app.api.deps import DB, CurrentUser, SettingsDep
from app.core import ratelimit
from app.core.time import utcnow
from app.models import NotificationPreference
from app.schemas.auth import (
    LoginRequest,
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


def user_out(user) -> UserOut:  # noqa: ANN001
    return UserOut(id=user.id, email=user.email, display_name=user.display_name, phone=user.phone,
                   preferred_language=user.preferred_language, is_active=user.is_active,
                   roles=[RoleGrantOut.model_validate(r) for r in user.roles], created_at=user.created_at)


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


@router.get("/users/me", response_model=UserOut, tags=["users"])
def me(principal: CurrentUser) -> UserOut:
    return user_out(principal.user)


@router.patch("/users/me", response_model=UserOut, tags=["users"],
              summary="Update display name, phone or language (email/roles are not editable here)")
def update_me(req: UserUpdate, principal: CurrentUser, db: DB) -> UserOut:
    user = db.merge(principal.user)
    for field, value in req.model_dump(exclude_unset=True, exclude_none=True).items():
        setattr(user, field, value)
    db.commit()
    return user_out(user)


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
