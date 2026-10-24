"""Behaviour added for the redesign: electrical issues, service ranking, Telugu matching, demo-mode
configuration, role metadata, queue filters, scoped CSV export, analytics target fields, notifications."""

from __future__ import annotations

import csv
import io

import pytest
from sqlalchemy import select

from app.adapters.classifier import tokens
from app.core.config import Settings
from app.models import Category, Notification, RoutingRule
from app.services.analytics import EXPORT_COLUMNS
from tests.conftest import window

# --- electrical taxonomy -------------------------------------------------------------------------


def test_electrical_categories_seeded_with_translations_and_no_invented_route(seeded):
    cats = {c.code: c for c in seeded.scalars(select(Category)).all()}
    parent = cats["electrical"]
    for code in ("electrical.exposed_wire", "electrical.public_fixture"):
        assert cats[code].parent_id == parent.id and cats[code].safety_sensitive
        assert cats[code].labels_i18n.get("te")
    # No verified department mapping exists, so no routing rule is seeded for electrical issues.
    routed = set(seeded.scalars(select(RoutingRule.category_id)).all())
    assert not routed & {parent.id, cats["electrical.exposed_wire"].id, cats["electrical.public_fixture"].id}


def test_electrical_report_goes_to_a_person_and_is_filterable(api):
    c = api.report(cat="electrical.exposed_wire", title="Wire hanging low over the lane",
                   description="A loose wire hangs at head height near the bus stop.")
    assert c["routing_outcome"] == "fallback"
    assert c["department_id"] == api.dept("triage")
    api.report(cat="roads.pothole")
    by_parent = api.get("/api/complaints", "muni.admin", params={"category_id": api.cat("electrical")}).json()
    assert [i["reference"] for i in by_parent["items"]] == [c["reference"]]
    by_leaf = api.get("/api/complaints", "muni.admin",
                      params={"category_id": api.cat("electrical.exposed_wire")}).json()
    assert by_leaf["total"] == 1


# --- service ranking -----------------------------------------------------------------------------


@pytest.mark.parametrize(("query", "expected"), [
    ("pothole", "report-road-damage"),
    ("big pothole on the main road", "report-road-damage"),
    ("garbage not collected for a week", "report-garbage"),
    ("blocked drain overflowing", "report-blocked-drain"),
    ("streetlight not working", "report-streetlight"),
    ("exposed wire hanging from a pole", "report-electrical-hazard"),
    ("junction box left open", "report-electrical-hazard"),
    ("water pipe burst", "report-water-leak"),
])
def test_most_relevant_service_ranks_first(client, seeded, query, expected):
    r = client.get("/api/services", params={"q": query}).json()
    assert r["items"], query
    assert r["items"][0]["service"]["code"] == expected, [i["service"]["code"] for i in r["items"]]


def test_ranking_explains_the_category_and_is_stable(client, seeded):
    first = client.get("/api/services", params={"q": "pothole near school"}).json()
    again = client.get("/api/services", params={"q": "pothole near school"}).json()
    assert [i["service"]["code"] for i in first["items"]] == [i["service"]["code"] for i in again["items"]]
    top = first["items"][0]
    assert "category" in top["matched_on"] and top["matched_category"]["code"] == "roads.pothole"


def test_telugu_query_finds_the_service_and_explains_in_telugu(client, seeded):
    r = client.get("/api/services", params={"q": "రోడ్డు మీద పెద్ద గుంత"}, headers={"Accept-Language": "te"}).json()
    assert r["items"][0]["service"]["code"] == "report-road-damage"
    assert r["items"][0]["matched_category"]["label"] == "గుంత"


def test_telugu_words_are_tokenised_whole():
    assert {"గుంత", "రోడ్డు"} <= tokens("రోడ్డు మీద పెద్ద గుంత")


def test_unmatched_query_returns_guidance_not_a_random_service(client, seeded):
    r = client.get("/api/services", params={"q": "passport renewal appointment"}).json()
    assert r["no_match"] and r["items"] == [] and r["guidance"]


# --- demo mode and role metadata -----------------------------------------------------------------


def test_meta_lists_demo_accounts_only_in_demo_mode(client, seeded, configure):
    m = client.get("/api/meta").json()
    assert m["demo_mode"] is True
    groups = {a["group"] for a in m["demo_accounts"]}
    assert {"resident", "road_officer", "road_supervisor", "triage_desk", "municipal_admin"} <= groups
    configure(DEMO_MODE="false")
    off = client.get("/api/meta").json()
    assert off == {"app_name": "Your City, Your Services", "demo_mode": False, "demo_accounts": []}


def test_demo_mode_defaults_off_in_production():
    prod = Settings(environment="production", jwt_secret="x" * 40)
    assert prod.demo_mode_enabled is False
    assert Settings(environment="production", jwt_secret="x" * 40, demo_mode=True).demo_mode_enabled is True
    assert Settings(environment="development").demo_mode_enabled is True


def test_demo_account_listing_is_not_a_sign_in_bypass(client, seeded):
    assert client.get("/api/users/me").status_code == 401
    account = client.get("/api/meta").json()["demo_accounts"][0]
    bad = client.post("/api/auth/login", json={"email": account["email"], "password": "wrong-password"})
    assert bad.status_code == 401


def test_me_names_the_department_of_each_role(api):
    roles = api.get("/api/users/me", "triage.supervisor").json()["roles"]
    assert roles[0]["role"] == "supervisor" and roles[0]["department_code"] == "triage"
    assert api.get("/api/users/me", "resident1").json()["roles"][0]["department_code"] is None


# --- queue filters ---------------------------------------------------------------------------------


def test_assigned_to_me_filter(api):
    mine = api.report()
    other = api.report(title="Second pothole", description="Another pothole further down the road.")
    for c, who in ((mine, "roads.officer1"), (other, "roads.officer2")):
        r = api.post(f"/api/complaints/{c['id']}/assign", "roads.supervisor", json={"officer_id": api.officer(who)})
        assert r.status_code == 200, r.text
    got = api.get("/api/complaints", "roads.officer1", params={"assigned_to_me": True}).json()
    assert [i["id"] for i in got["items"]] == [mine["id"]]
    assert api.get("/api/complaints", "resident1", params={"assigned_to_me": True}).json()["total"] == 0


def test_resident_cannot_assign_or_correct(api):
    c = api.report()
    assert api.post(f"/api/complaints/{c['id']}/assign", "resident1",
                    json={"officer_id": api.officer("roads.officer1")}).status_code in (403, 404)
    r = api.patch(f"/api/complaints/{c['id']}", "resident1", json={"priority": "high", "reason": "urgent"},
                  headers={"If-Match": str(c["version"])})
    assert r.status_code in (403, 422)


# --- CSV export ----------------------------------------------------------------------------------


def _csv(r) -> list[list[str]]:  # noqa: ANN001
    assert r.content.startswith(b"\xef\xbb\xbf")  # UTF-8 BOM so spreadsheets keep Telugu text
    return list(csv.reader(io.StringIO(r.content.decode("utf-8-sig"))))


def test_csv_export_for_supervisor_is_scoped_and_readable(api):
    tricky = 'Pothole, "deep"\nnear రోడ్డు'
    api.report(title=tricky, description="A deep pothole is damaging vehicles near the market.")
    api.report(cat="sanitation.garbage", title="Garbage pile", description="Garbage has not been collected.")
    r = api.get("/api/admin/analytics/export.csv", "roads.supervisor", params=window())
    assert r.status_code == 200
    assert r.headers["content-disposition"].startswith('attachment; filename="ycys-reports_')
    rows = _csv(r)
    assert rows[0] == EXPORT_COLUMNS
    assert len(rows) == 2 and r.headers["x-row-count"] == "1"  # the garbage report is outside Roads scope
    row = dict(zip(rows[0], rows[1], strict=True))
    assert row["Title"] == tricky and row["Category"] == "Pothole" and row["Department"].startswith("Roads")
    assert not any("@" in v for v in rows[1])  # no resident email or identity columns

    admin = _csv(api.get("/api/admin/analytics/export.csv", "muni.admin", params=window()))
    assert len(admin) == 3


def test_csv_export_filters_and_empty_result(api):
    api.report()
    filtered = api.get("/api/admin/analytics/export.csv", "muni.admin",
                       params={**window(), "category_id": api.cat("electrical")})
    assert filtered.status_code == 200 and filtered.headers["x-row-count"] == "0"
    assert _csv(filtered) == [EXPORT_COLUMNS]


# --- analytics target fields ---------------------------------------------------------------------


def test_analytics_reports_target_configuration_and_assignment_time(api):
    c = api.report()
    api.post(f"/api/complaints/{c['id']}/assign", "roads.supervisor", json={"officer_id": api.officer("roads.officer1")})
    a = api.get("/api/admin/analytics", "muni.admin", params=window()).json()
    assert a["sla_policies_active"] >= 1 and a["sla_policies_illustrative"] is True
    assert a["assignment_measured"] == 1 and a["assignment_hours_median"] is not None
    assert a["sla_measured"] == 0 and a["sla_compliance"] is None  # nothing resolved: no claim either way


# --- notifications -------------------------------------------------------------------------------


def test_mark_all_read_persists_and_touches_only_own(api, db, factory):
    from tests.conftest import run_worker

    c = api.report()
    api.post(f"/api/complaints/{c['id']}/assign", "roads.supervisor", json={"officer_id": api.officer("roads.officer1")})
    api.report("resident2")
    run_worker(factory)
    mine = api.get("/api/notifications", "resident1", params={"unread_only": True}).json()["total"]
    theirs = api.get("/api/notifications", "resident2", params={"unread_only": True}).json()["total"]
    assert mine >= 1 and theirs >= 1
    r = api.post("/api/notifications/read-all", "resident1")
    assert r.status_code == 200 and r.json()["updated"] == mine
    assert api.get("/api/notifications", "resident1", params={"unread_only": True}).json()["total"] == 0
    assert api.get("/api/notifications", "resident2", params={"unread_only": True}).json()["total"] == theirs
    db.expire_all()
    assert db.scalar(select(Notification).where(Notification.read_at.is_(None)))
