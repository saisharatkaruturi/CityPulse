"""Test fixtures. Every test gets a fresh SQLite database file and local media dir.

External providers are mocks; no test sends real email/SMS or calls a real municipal system.
"""

from __future__ import annotations

import os
import uuid
from collections.abc import Iterator
from pathlib import Path

os.environ.update({
    "ENVIRONMENT": "test",
    "RATE_LIMIT_ENABLED": "false",
    "DATABASE_URL": "sqlite:///./var/never-used-by-tests.db",
    "EMAIL_PROVIDER": "disabled",
    "SMS_PROVIDER": "disabled",
    "MUNICIPAL_INTEGRATION": "disabled",
    "GEOCODING_PROVIDER": "disabled",
})

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from app.adapters import providers, storage
from app.core import ratelimit
from app.core.config import get_settings
from app.db import session as db_session
from app.db.base import Base
from app.models import Category, Department, Officer, User, Ward
from app.services import intelligence

DEMO_PASSWORD = "demo-password-123"


@pytest.fixture
def engine(tmp_path: Path):
    eng = db_session.build_engine(f"sqlite:///{tmp_path / 'test.db'}")
    Base.metadata.create_all(eng)
    db_session.set_engine(eng)
    yield eng
    eng.dispose()


@pytest.fixture(autouse=True)
def _isolate(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Iterator[None]:
    monkeypatch.setenv("MEDIA_ROOT", str(tmp_path / "media"))
    get_settings.cache_clear()
    storage.set_storage(None)
    providers.set_providers(None)
    intelligence.set_classifier(None)
    ratelimit.limiter.reset()
    yield
    get_settings.cache_clear()
    storage.set_storage(None)
    providers.set_providers(None)
    intelligence.set_classifier(None)


@pytest.fixture
def configure(monkeypatch: pytest.MonkeyPatch):
    """Override settings for one test: configure(EMAIL_PROVIDER='mock')."""

    def _apply(**env: str) -> None:
        for k, v in env.items():
            monkeypatch.setenv(k, v)
        get_settings.cache_clear()
        providers.set_providers(None)

    return _apply


@pytest.fixture
def factory(engine) -> sessionmaker[Session]:
    return sessionmaker(bind=engine, expire_on_commit=False, autoflush=False)


@pytest.fixture
def db(factory) -> Iterator[Session]:
    with factory() as s:
        yield s


@pytest.fixture
def seeded(db: Session) -> Session:
    from app import seed

    seed.seed_reference(db)
    return db


@pytest.fixture
def client(engine) -> Iterator[TestClient]:
    from app.main import create_app

    with TestClient(create_app(get_settings()), raise_server_exceptions=False) as c:
        yield c


class Api:
    """Small helper: logs in demo users and caches their bearer headers."""

    def __init__(self, client: TestClient, db: Session) -> None:
        self.c = client
        self.db = db
        self._tokens: dict[str, dict[str, str]] = {}

    def h(self, handle: str) -> dict[str, str]:
        if handle not in self._tokens:
            r = self.c.post("/api/auth/login", json={"email": f"{handle}@example.com", "password": DEMO_PASSWORD})
            assert r.status_code == 200, r.text
            self._tokens[handle] = {"Authorization": f"Bearer {r.json()['access_token']}"}
        return self._tokens[handle]

    def get(self, url: str, who: str, **kw):  # noqa: ANN201
        return self.c.get(url, headers={**self.h(who), **kw.pop("headers", {})}, **kw)

    def post(self, url: str, who: str, json=None, **kw):  # noqa: ANN001, ANN201
        return self.c.post(url, json=json, headers={**self.h(who), **kw.pop("headers", {})}, **kw)

    def patch(self, url: str, who: str, json=None, **kw):  # noqa: ANN001, ANN201
        return self.c.patch(url, json=json, headers={**self.h(who), **kw.pop("headers", {})}, **kw)

    def delete(self, url: str, who: str, **kw):  # noqa: ANN201
        return self.c.delete(url, headers={**self.h(who), **kw.pop("headers", {})}, **kw)

    # lookups
    def cat(self, code: str) -> str:
        return str(self.db.scalar(select(Category.id).where(Category.code == code)))

    def dept(self, code: str) -> str:
        return str(self.db.scalar(select(Department.id).where(Department.code == code)))

    def ward(self, code: str) -> str:
        return str(self.db.scalar(select(Ward.id).where(Ward.code == code)))

    def user_id(self, handle: str) -> uuid.UUID:
        return self.db.scalar(select(User.id).where(User.email == f"{handle}@example.com"))  # type: ignore[return-value]

    def officer(self, handle: str) -> str:
        return str(self.db.scalar(select(Officer.id).where(Officer.user_id == self.user_id(handle))))

    def report(self, who: str = "resident1", *, cat: str | None = "roads.pothole", ward: str | None = "demo-w1",
               offset: tuple[float, float] = (0.0, 0.0), expect: int = 201, **extra) -> dict:  # noqa: ANN003
        from app.seed import ward_center

        body: dict = {"title": "Pothole on main road", "description": "A deep pothole is damaging vehicles."}
        if cat:
            body["category_id"] = self.cat(cat)
        if ward:
            lat, lng = ward_center(ward)
            body["location"] = {"latitude": round(lat + offset[0], 6), "longitude": round(lng + offset[1], 6),
                                "source": "gps"}
        body.update(extra)
        r = self.post("/api/complaints", who, json=body)
        assert r.status_code == expect, r.text
        return r.json()


@pytest.fixture
def api(client: TestClient, seeded: Session) -> Api:
    return Api(client, seeded)


def run_worker(factory: sessionmaker[Session]) -> dict:
    from app.jobs.worker import run_once

    return run_once(factory)


def window(days_back: int = 30, days_forward: int = 1) -> dict[str, str]:
    from datetime import timedelta

    from app.core.time import utcnow

    now = utcnow()
    return {"date_from": (now - timedelta(days=days_back)).isoformat(),
            "date_to": (now + timedelta(days=days_forward)).isoformat()}
