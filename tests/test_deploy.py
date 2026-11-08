"""Serverless (Vercel) deployment support: DB URL normalisation, storage selection, cron endpoint."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.adapters.storage import LocalFileStorage, VercelBlobStorage
from app.core.config import ConfigurationError, Settings, get_settings, load_settings


@pytest.mark.parametrize("url", ["postgres://u:p@host/db?sslmode=require",
                                 "postgresql://u:p@host/db?sslmode=require"])
def test_hosted_postgres_urls_use_psycopg3(url):
    assert Settings(database_url=url).database_url == "postgresql+psycopg://u:p@host/db?sslmode=require"


def test_supabase_pooler_marker_is_stripped():
    url = "postgres://u:p@aws-0-ap-south-1.pooler.supabase.com:6543/postgres?sslmode=require&supa=base-pooler.x"
    assert Settings(database_url=url).database_url == (
        "postgresql+psycopg://u:p@aws-0-ap-south-1.pooler.supabase.com:6543/postgres?sslmode=require")


def test_postgres_url_env_alias(monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.setenv("POSTGRES_URL", "postgres://u:p@h/db")
    assert Settings().database_url == "postgresql+psycopg://u:p@h/db"


def test_sqlite_url_untouched():
    assert Settings(database_url="sqlite:///./x.db").database_url == "sqlite:///./x.db"


def test_storage_backend_auto_selects_blob_only_with_token():
    assert Settings().effective_storage_backend == "local"
    assert Settings(blob_read_write_token="vercel_blob_rw_x_y").effective_storage_backend == "vercel_blob"
    assert Settings(storage_backend="local", blob_read_write_token="t").effective_storage_backend == "local"


def test_production_requires_blob_token_when_blob_forced():
    with pytest.raises(ConfigurationError, match="BLOB_READ_WRITE_TOKEN"):
        load_settings(environment="production", jwt_secret="p" * 40, storage_backend="vercel_blob")


def test_blob_storage_refuses_non_blob_keys():
    store = VercelBlobStorage("vercel_blob_rw_x_y")
    for key in ("http://abc.public.blob.vercel-storage.com/a", "https://evil.example/a",
                "https://blob.vercel-storage.com.evil.example/a", "abc.jpg"):
        with pytest.raises(ValueError):
            store.get(key)
    with pytest.raises(ValueError):
        VercelBlobStorage("")
    assert isinstance(LocalFileStorage, type)


def test_cron_endpoint_hidden_without_secret(client: TestClient):
    assert client.get("/api/cron/worker").status_code == 404
    assert client.get("/api/cron/worker", headers={"Authorization": "Bearer "}).status_code == 404


def test_cron_endpoint_requires_matching_secret(engine, configure):
    from app.main import create_app

    configure(CRON_SECRET="c" * 32)
    with TestClient(create_app(get_settings()), raise_server_exceptions=False) as c:
        assert c.get("/api/cron/worker", headers={"Authorization": "Bearer wrong"}).status_code == 404
        ok = c.get("/api/cron/worker", headers={"Authorization": "Bearer " + "c" * 32})
        assert ok.status_code == 200
        body = ok.json()
        assert body["status"] == "ok" and "outbox" in body["results"]


def test_seed_allowed_in_production_only_with_explicit_demo_mode(db, configure):
    from app import seed

    configure(ENVIRONMENT="production", JWT_SECRET="p" * 40)
    with pytest.raises(SystemExit):
        seed.run(db)
    configure(ENVIRONMENT="production", JWT_SECRET="p" * 40, DEMO_MODE="true")
    assert "complaints_created" in seed.run(db)
