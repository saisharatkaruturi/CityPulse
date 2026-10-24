"""Uploads, operational endpoints, error contracts, configuration and migrations."""

from __future__ import annotations

import io
import json
import logging
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image

from app.adapters.storage import LocalFileStorage
from app.core.config import ConfigurationError, load_settings
from app.core.logging import JsonFormatter
from app.services.media import sanitize_filename


def _jpeg_with_exif() -> bytes:
    img = Image.new("RGB", (32, 32), (200, 10, 10))
    exif = Image.Exif()
    exif[0x010F] = "DemoCam"  # Make
    exif[0x8825] = {2: (17.0, 24.0, 0.0)}  # GPS IFD latitude
    buf = io.BytesIO()
    img.save(buf, format="JPEG", exif=exif)
    return buf.getvalue()


def _upload(api, who: str, data: bytes, name: str = "photo.jpg", **form):  # noqa: ANN001, ANN003, ANN202
    return api.c.post("/api/media", headers=api.h(who), files={"file": (name, data, "image/jpeg")}, data=form)


def test_upload_strips_exif_and_attaches_to_report(api):
    raw = _jpeg_with_exif()
    assert Image.open(io.BytesIO(raw)).getexif()
    r = _upload(api, "resident1", raw, name="../../etc/passwd.jpg")
    assert r.status_code == 201, r.text
    m = r.json()
    assert m["exif_stripped"] and m["scan_state"] == "not_scanned" and "/" not in m["original_filename"]
    c = api.report(media_ids=[m["id"]])
    files = api.get(f"/api/complaints/{c['id']}/media", "resident1").json()
    assert [f["id"] for f in files] == [m["id"]]
    content = api.get(f"/api/media/{m['id']}/content", "resident1")
    assert content.status_code == 200 and not Image.open(io.BytesIO(content.content)).getexif()
    assert api.get(f"/api/media/{m['id']}/content", "resident2").status_code == 404
    assert api.get(f"/api/media/{m['id']}/content", "roads.supervisor").status_code == 200
    # Media cannot be claimed twice or by someone else.
    assert api.report(media_ids=[m["id"]], expect=422)
    other = _upload(api, "resident2", raw).json()
    assert api.report("resident1", media_ids=[other["id"]], expect=422)


def test_upload_rejections(api, configure):
    assert _upload(api, "resident1", b"MZ\x90\x00 fake exe", name="x.jpg").json()["error"]["code"] == \
        "unsupported_media"
    assert _upload(api, "resident1", b"\xff\xd8\xff garbage not really jpeg").status_code == 422
    assert _upload(api, "resident1", b"").status_code == 422
    configure(MAX_UPLOAD_BYTES="1000")
    big = Image.new("RGB", (400, 400))
    buf = io.BytesIO()
    big.save(buf, format="PNG")
    r = _upload(api, "resident1", buf.getvalue() + b"\x00" * 2000, name="big.png")
    assert r.status_code == 413


def test_evidence_upload_is_staff_only(api):
    c = api.report()
    data = _jpeg_with_exif()
    assert _upload(api, "resident1", data, kind="resolution_evidence", complaint_id=c["id"]).status_code == 404
    api.post(f"/api/complaints/{c['id']}/assign", "roads.supervisor", {"officer_id": api.officer("roads.officer1")})
    ev = _upload(api, "roads.officer1", data, kind="resolution_evidence", complaint_id=c["id"]).json()
    r = api.post(f"/api/complaints/{c['id']}/resolve", "roads.officer1",
                 {"resolution_notes": "Fixed", "evidence_media_ids": [ev["id"]]})
    assert r.status_code == 200
    assert api.get(f"/api/media/{ev['id']}/content", "resident1").status_code == 200  # reporter sees evidence


def test_storage_rejects_traversal(tmp_path):
    s = LocalFileStorage(str(tmp_path))
    for key in ("../x", "a/b", "..", ""):
        with pytest.raises(ValueError):
            s.get(key)
    assert sanitize_filename("..\\..\\win.ini") == "win.ini"


def test_health_ready_request_id_and_error_envelope(client):
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/ready").json() == {"status": "ready"}
    r = client.get("/api/users/me", headers={"X-Request-ID": "abc12345-req"})
    assert r.headers["X-Request-ID"] == "abc12345-req"
    assert r.json()["error"]["request_id"] == "abc12345-req" and r.json()["error"]["code"] == "unauthenticated"
    assert client.get("/nope").json()["error"]["code"] == "not_found"
    assert r.headers["X-Content-Type-Options"] == "nosniff"


def test_request_size_limit(client):
    r = client.post("/api/auth/login", content=b"x" * 2_000_000, headers={"Content-Type": "application/json"})
    assert r.status_code == 413 and r.json()["error"]["code"] == "payload_too_large"


def test_openapi_documents_endpoints(client):
    spec = client.get("/openapi.json").json()
    for path in ("/api/complaints", "/api/complaints/{complaint_id}/transitions", "/api/services",
                 "/api/routing/suggest", "/api/admin/analytics", "/health"):
        assert path in spec["paths"]


def test_production_config_validation():
    with pytest.raises(ConfigurationError) as e:
        load_settings(environment="production", jwt_secret="short-secret-value", debug=True)
    assert "short-secret-value" not in str(e.value) and "JWT_SECRET" in str(e.value)
    assert e.value.__cause__ is None and e.value.__suppress_context__
    ok = load_settings(environment="production", jwt_secret="p" * 40, cors_origins="https://city.example.org")
    assert ok.cors_origins == ["https://city.example.org"] and not ok.debug


def test_logs_redact_secrets():
    rec = logging.LogRecord("t", logging.INFO, __file__, 1, "auth Bearer abc.def.ghi", None, None)
    rec.headers = {"Authorization": "Bearer xyz", "password": "hunter2"}
    out = json.loads(JsonFormatter().format(rec))
    assert "abc.def.ghi" not in out["msg"] and out["headers"]["password"] == "[REDACTED]"
    assert out["headers"]["Authorization"] == "[REDACTED]"


def test_migrations_apply_cleanly_and_match_models(tmp_path):
    root = Path(__file__).resolve().parents[1]
    url = f"sqlite:///{(tmp_path / 'mig.db').as_posix()}"
    env = {"DATABASE_URL": url, "ENVIRONMENT": "test", "PATH": ""}
    import os

    env = {**os.environ, **env}
    for args in (["upgrade", "head"], ["check"], ["downgrade", "base"], ["upgrade", "head"]):
        r = subprocess.run([sys.executable, "-m", "alembic", *args], cwd=root, env=env, capture_output=True,
                           text=True, timeout=120)
        assert r.returncode == 0, r.stderr


def test_seed_is_repeatable_and_refuses_production(db, monkeypatch):
    from app import seed
    from app.core.config import get_settings

    seed.seed_reference(db)
    first = seed.seed_complaints(db)
    assert first > 0 and seed.seed_complaints(db) == 0
    seed.seed_reference(db)  # no duplicate reference rows
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("JWT_SECRET", "p" * 40)
    get_settings.cache_clear()
    with pytest.raises(SystemExit):
        seed.run(db)
