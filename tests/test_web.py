"""Public discovery endpoints used by the landing page, and serving of the built web UI."""

from __future__ import annotations

from pathlib import Path

from fastapi.testclient import TestClient
from sqlalchemy import func, select

from app.core.config import get_settings
from app.models import Complaint


def test_discovery_endpoints_work_without_sign_in(client, seeded):
    assert client.get("/api/categories").status_code == 200
    assert client.get("/api/wards").status_code == 200
    assert client.get("/api/services", params={"q": "streetlight"}).json()["items"]
    r = client.post("/api/routing/suggest", json={"description": "garbage pile and trash dumped near market"})
    assert r.status_code == 200 and r.json()["category"]["category_code"] == "sanitation.garbage"
    assert seeded.scalar(select(func.count()).select_from(Complaint)) == 0  # still no side effects


def test_discovery_rejects_a_bad_token(client, seeded):
    r = client.get("/api/categories", headers={"Authorization": "Bearer not-a-token"})
    assert r.status_code == 401


def test_everything_else_still_requires_sign_in(client, seeded):
    for method, path in [("get", "/api/complaints"), ("post", "/api/complaints"), ("get", "/api/notifications"),
                         ("get", "/api/complaints/nearby?lat=17.4&lng=78.4"), ("get", "/api/users/me")]:
        assert getattr(client, method)(path).status_code == 401, path


def test_spa_served_with_client_routing_fallback(tmp_path: Path, engine, monkeypatch):
    dist = tmp_path / "dist"
    (dist / "assets").mkdir(parents=True)
    (dist / "index.html").write_text("<!doctype html><title>app</title>", encoding="utf-8")
    (dist / "assets" / "app.js").write_text("console.log(1)", encoding="utf-8")
    monkeypatch.setenv("WEB_DIST_DIR", str(dist))
    get_settings.cache_clear()
    from app.main import create_app

    with TestClient(create_app(get_settings())) as c:
        assert "app" in c.get("/").text
        assert "app" in c.get("/app/reports/123").text  # client route falls back to index.html
        js = c.get("/assets/app.js")
        assert js.status_code == 200 and "immutable" in js.headers["cache-control"]
        assert c.get("/api/does-not-exist").json()["error"]["code"] == "not_found"  # API never falls back
        assert c.get("/health").json() == {"status": "ok"}
        assert c.get("/..%2F..%2Fpyproject.toml").text.startswith("<!doctype")  # no traversal out of dist
