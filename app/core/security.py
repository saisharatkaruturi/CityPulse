"""Password hashing and access-token handling."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta

import jwt
from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerificationError

from app.core.config import Settings

_hasher = PasswordHasher()
# Used to equalise timing when the account does not exist.
_DUMMY_HASH = _hasher.hash("dummy-password-for-timing")


def hash_password(password: str) -> str:
    return _hasher.hash(password)


def verify_password(password: str, password_hash: str | None) -> bool:
    try:
        return _hasher.verify(password_hash or _DUMMY_HASH, password) and password_hash is not None
    except (VerificationError, InvalidHashError):
        return False


def issue_access_token(settings: Settings, user_id: uuid.UUID, session_id: uuid.UUID,
                       now: datetime) -> tuple[str, datetime]:
    expires = now + timedelta(minutes=settings.access_token_ttl_minutes)
    claims = {
        "sub": str(user_id),
        "sid": str(session_id),
        "iss": settings.jwt_issuer,
        "aud": settings.jwt_audience,
        "iat": int(now.timestamp()),
        "exp": int(expires.timestamp()),
    }
    return jwt.encode(claims, settings.jwt_secret, algorithm="HS256"), expires


def decode_access_token(settings: Settings, token: str) -> dict:
    """Validates signature, expiry, issuer and audience. Raises jwt.PyJWTError on failure."""
    return jwt.decode(token, settings.jwt_secret, algorithms=["HS256"], audience=settings.jwt_audience,
                      issuer=settings.jwt_issuer, options={"require": ["exp", "sub", "sid", "iss", "aud"]})
