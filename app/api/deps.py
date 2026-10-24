"""FastAPI dependencies: DB session, settings, current principal, pagination."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Query, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import Settings, get_settings
from app.core.errors import Unauthenticated
from app.core.permissions import Principal
from app.db.session import get_db
from app.services.auth import authenticate_token

_bearer = HTTPBearer(auto_error=False)

DB = Annotated[Session, Depends(get_db)]
SettingsDep = Annotated[Settings, Depends(get_settings)]


def current_principal(
    request: Request,
    db: DB,
    settings: SettingsDep,
    creds: Annotated[HTTPAuthorizationCredentials | None, Depends(_bearer)],
) -> Principal:
    if creds is None or creds.scheme.lower() != "bearer" or not creds.credentials:
        raise Unauthenticated("Authentication required")
    principal = authenticate_token(db, settings, creds.credentials)
    request.state.user_id = str(principal.id)
    return principal


CurrentUser = Annotated[Principal, Depends(current_principal)]


@dataclass(frozen=True)
class Pagination:
    page: int
    page_size: int

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


def pagination(
    settings: SettingsDep,
    page: Annotated[int, Query(ge=1, le=100_000)] = 1,
    page_size: Annotated[int | None, Query(ge=1)] = None,
) -> Pagination:
    size = min(page_size or settings.default_page_size, settings.max_page_size)
    return Pagination(page, size)


PageParams = Annotated[Pagination, Depends(pagination)]
