"""Authentication, authorisation (IDOR, cross-department, privilege escalation) and privacy."""

from __future__ import annotations

import uuid
from datetime import timedelta

import jwt
from sqlalchemy import select

from app.core.config import get_settings
from app.core.time import utcnow
from app.models import Notification, User
from tests.conftest import run_worker, window

# --- Authentication ---------------------------------------------------------------------------------

def test_register_login_me_logout(client, seeded):
    r = client.post("/api/auth/register", json={"email": "New.User@Example.com", "password": "long-password-1",
                                                 "display_name": "New"})
    assert r.status_code == 201 and r.json()["email"] == "new.user@example.com"
    assert "password_hash" not in r.text and "password" not in r.json()
    assert [x["role"] for x in r.json()["roles"]] == ["resident"]
    dup = client.post("/api/auth/register", json={"email": "new.user@example.com", "password": "long-password-1",
                                                   "display_name": "Dup"})
    assert dup.status_code == 409
    tok = client.post("/api/auth/login", json={"email": "new.user@example.com", "password": "long-password-1"})
    h = {"Authorization": f"Bearer {tok.json()['access_token']}"}
    assert client.get("/api/users/me", headers=h).json()["display_name"] == "New"
    assert client.post("/api/auth/logout", headers=h).status_code == 204
    r = client.get("/api/users/me", headers=h)
    assert r.status_code == 401 and r.json()["error"]["code"] == "session_revoked"


def test_register_cannot_choose_role(client, seeded):
    r = client.post("/api/auth/register", json={"email": "x@example.com", "password": "long-password-1",
                                                 "display_name": "X", "roles": ["system_admin"]})
    assert r.status_code == 422


def test_login_failures_are_generic(client, seeded):
    a = client.post("/api/auth/login", json={"email": "resident1@example.com", "password": "wrong-password"})
    b = client.post("/api/auth/login", json={"email": "nobody@example.com", "password": "wrong-password"})
    assert a.status_code == b.status_code == 401
    assert a.json()["error"]["message"] == b.json()["error"]["message"]


def test_missing_invalid_expired_and_wrong_audience_tokens(client, seeded, api):
    assert client.get("/api/users/me").status_code == 401
    assert client.get("/api/users/me", headers={"Authorization": "Bearer nonsense"}).status_code == 401
    assert client.get("/api/users/me", headers={"Authorization": "Basic abc"}).status_code == 401
    s = get_settings()
    uid = api.user_id("resident1")
    base = {"sub": str(uid), "sid": str(uuid.uuid4()), "iss": s.jwt_issuer, "aud": s.jwt_audience,
            "exp": int((utcnow() + timedelta(minutes=5)).timestamp())}
    for claims, secret in [
        ({**base, "exp": int((utcnow() - timedelta(minutes=1)).timestamp())}, s.jwt_secret),
        ({**base, "aud": "someone-else"}, s.jwt_secret),
        ({**base, "iss": "evil"}, s.jwt_secret),
        (base, "x" * 40),  # wrong signature
        (base, s.jwt_secret),  # valid signature but unknown session
    ]:
        token = jwt.encode(claims, secret, algorithm="HS256")
        assert client.get("/api/users/me", headers={"Authorization": f"Bearer {token}"}).status_code == 401
    none_alg = jwt.encode(base, key=None, algorithm="none")  # type: ignore[arg-type]
    assert client.get("/api/users/me", headers={"Authorization": f"Bearer {none_alg}"}).status_code == 401


def test_deactivated_account_rejected(api):
    h = api.h("resident2")
    r = api.post(f"/api/admin/users/{api.user_id('resident2')}/activation", "admin",
                 {"active": False, "reason": "Spam account"})
    assert r.status_code == 200
    assert api.c.get("/api/users/me", headers=h).status_code == 401
    assert api.c.post("/api/auth/login", json={"email": "resident2@example.com",
                                               "password": "demo-password-123"}).status_code == 401


def test_profile_update_cannot_change_email_or_roles(api):
    assert api.patch("/api/users/me", "resident1", {"email": "evil@example.com"}).status_code == 422
    assert api.patch("/api/users/me", "resident1", {"roles": ["system_admin"]}).status_code == 422
    r = api.patch("/api/users/me", "resident1", {"display_name": "Asha K", "preferred_language": "te"})
    assert r.status_code == 200 and r.json()["preferred_language"] == "te"


def test_login_rate_limited(client, seeded, configure):
    configure(RATE_LIMIT_ENABLED="true")
    codes = [client.post("/api/auth/login", json={"email": "resident1@example.com", "password": "bad-pass"})
             .status_code for _ in range(12)]
    assert codes[:10] == [401] * 10 and codes[-1] == 429


# --- Authorisation ------------------------------------------------------------------------------------

def test_resident_cannot_read_others_private_complaint(api):
    c = api.report("resident1")
    r = api.get(f"/api/complaints/{c['id']}", "resident2")
    assert r.status_code == 404  # not 403: do not confirm existence
    assert api.get("/api/complaints", "resident2").json()["total"] == 0
    for path in ("comments", "media", "possible-duplicates"):
        assert api.get(f"/api/complaints/{c['id']}/{path}", "resident2").status_code == 404
    assert api.post(f"/api/complaints/{c['id']}/withdraw", "resident2", {}).status_code == 404
    assert api.post(f"/api/complaints/{c['id']}/comments", "resident2", {"body": "hi"}).status_code == 404


def test_public_summary_hides_private_data(api):
    c = api.report("resident1", visibility="public")
    s = api.get(f"/api/complaints/public/{c['reference']}", "resident2").json()
    assert "description" not in s and "reporter_id" not in s
    assert s["approx_latitude"] == round(c["latitude"], 3)
    private = api.report("resident1")
    assert api.get(f"/api/complaints/public/{private['reference']}", "resident2").status_code == 404


def test_officer_scope(api):
    c = api.report("resident1")
    other = api.report("resident1", cat="sanitation.garbage")
    # Unassigned roads complaint: officer2 (different team, not assigned) cannot see it.
    assert api.get(f"/api/complaints/{c['id']}", "roads.officer2").status_code == 404
    api.post(f"/api/complaints/{c['id']}/assign", "roads.supervisor", {"officer_id": api.officer("roads.officer1")})
    assert api.get(f"/api/complaints/{c['id']}", "roads.officer1").status_code == 200
    assert api.get(f"/api/complaints/{other['id']}", "roads.officer1").status_code == 404
    listed = api.get("/api/complaints", "roads.officer1").json()
    assert [i["id"] for i in listed["items"]] == [c["id"]]
    # Officers cannot assign or merge.
    r = api.post(f"/api/complaints/{c['id']}/reassign", "roads.officer1",
                 {"officer_id": api.officer("roads.officer2"), "reason": "swap please"})
    assert r.status_code == 403


def test_cross_department_supervisor_denied(api):
    c = api.report("resident1")  # roads
    assert api.get(f"/api/complaints/{c['id']}", "water.supervisor").status_code == 404
    r = api.post(f"/api/complaints/{c['id']}/assign", "water.supervisor", {"officer_id": api.officer("water.officer")})
    assert r.status_code == 404
    # Roads supervisor cannot push work to an officer in another department.
    r = api.post(f"/api/complaints/{c['id']}/assign", "roads.supervisor", {"officer_id": api.officer("water.officer")})
    assert r.status_code == 403
    a = api.get("/api/admin/analytics", "water.supervisor",
                params={**window(), "department_id": api.dept("roads")})
    assert a.status_code == 403


def test_auditor_is_read_only(api):
    c = api.report("resident1")
    assert api.get(f"/api/complaints/{c['id']}", "auditor").status_code == 200
    assert api.post(f"/api/complaints/{c['id']}/assign", "auditor",
                    {"officer_id": api.officer("roads.officer1")}).status_code == 403
    assert api.post(f"/api/complaints/{c['id']}/transitions", "auditor",
                    {"to_status": "under_review"}).status_code == 403
    assert api.post(f"/api/complaints/{c['id']}/notes", "auditor", {"body": "note"}).status_code == 404
    assert api.post("/api/admin/departments", "auditor", {"code": "x1", "name": "X dept"}).status_code == 403


def test_privilege_escalation_blocked(api):
    uid = api.user_id("resident1")
    body = {"role": "system_admin", "reason": "self promotion"}
    assert api.post(f"/api/admin/users/{uid}/roles", "resident1", body).status_code == 403
    assert api.post(f"/api/admin/users/{uid}/roles", "muni.admin", body).status_code == 403
    for path, payload in [("/api/admin/departments", {"code": "zz", "name": "ZZ dept"}),
                          ("/api/admin/routing-rules", {"category_id": api.cat("roads.pothole"),
                                                        "department_id": api.dept("water")}),
                          ("/api/admin/sla-policies", {"name": "x sla", "acknowledge_hours": 1,
                                                       "resolve_hours": 2})]:
        assert api.post(path, "resident1", payload).status_code == 403
        assert api.post(path, "roads.supervisor", payload).status_code == 403
    assert api.get("/api/admin/audit-logs", "muni.admin").status_code == 403
    assert api.get("/api/admin/outbox", "muni.admin").status_code == 403
    assert api.get("/api/admin/analytics", "resident1", params=window()).status_code == 403
    r = api.post(f"/api/admin/users/{uid}/roles", "admin", {"role": "supervisor", "reason": "promotion"})
    assert r.status_code == 422  # supervisor grants must be scoped to a department


def test_last_system_admin_cannot_be_removed(api):
    uid = api.user_id("admin")
    r = api.post(f"/api/admin/users/{uid}/roles/revoke", "admin", {"role": "system_admin", "reason": "oops"})
    assert r.status_code == 409 and r.json()["error"]["code"] == "last_admin"


def test_internal_notes_never_reach_resident(api, factory):
    c = api.report("resident1")
    cid = c["id"]
    secret = "INTERNAL-ONLY: reporter seems to be a repeat caller"
    api.post(f"/api/complaints/{cid}/assign", "roads.supervisor", {"officer_id": api.officer("roads.officer1")})
    assert api.post(f"/api/complaints/{cid}/notes", "roads.officer1", {"body": secret}).status_code == 201
    assert api.get(f"/api/complaints/{cid}/notes", "resident1").status_code == 404
    assert api.get(f"/api/complaints/{cid}/notes", "roads.officer1").json()[0]["body"] == secret
    api.post(f"/api/complaints/{cid}/resolve", "roads.officer1", {"resolution_notes": "Patched"})
    run_worker(factory)
    surfaces = [api.get(f"/api/complaints/{cid}", "resident1").text,
                api.get(f"/api/complaints/{cid}/comments", "resident1").text,
                api.get("/api/notifications", "resident1").text,
                api.get("/api/complaints", "resident1").text]
    assert all(secret not in s for s in surfaces)


def test_notifications_are_owner_only(api, factory, db):
    api.report("resident1")
    run_worker(factory)
    n = db.scalar(select(Notification).where(Notification.recipient_id == api.user_id("resident1")))
    assert api.patch(f"/api/notifications/{n.id}/read", "resident2").status_code == 404
    r = api.patch(f"/api/notifications/{n.id}/read", "resident1")
    assert r.status_code == 200 and r.json()["read_at"]
    assert api.get("/api/notifications", "resident1", params={"unread_only": True}).json()["total"] == 0


def test_notification_content_excludes_private_details(api, factory, db):
    c = api.report("resident1", description="My phone is 9999999999, pothole near my house at 12 Demo St")
    run_worker(factory)
    rows = db.scalars(select(Notification)).all()
    assert rows and all("9999999999" not in n.body and "Demo St" not in n.body for n in rows)
    assert all(c["reference"] in n.body for n in rows)
    user = db.scalar(select(User).where(User.email == "resident1@example.com"))
    assert all(user.email not in n.body for n in rows)
