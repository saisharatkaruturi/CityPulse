"""Admin configuration integrity and analytics correctness against known fixtures."""

from __future__ import annotations

import csv
import io
import uuid
from datetime import timedelta

from sqlalchemy import select

from app.core.time import utcnow
from app.models import AuditLog, Complaint, RoutingRule
from tests.conftest import window


def test_department_crud_audited_and_fallback_protected(api, db):
    r = api.post("/api/admin/departments", "muni.admin", {"code": "parks", "name": "Parks (demo)",
                                                          "covered_ward_ids": [api.ward("demo-w1")]})
    assert r.status_code == 201 and r.json()["covered_ward_ids"] == [api.ward("demo-w1")]
    assert api.post("/api/admin/departments", "muni.admin", {"code": "parks", "name": "Again"}).status_code == 409
    assert api.post("/api/admin/departments", "muni.admin", {"code": "BAD CODE", "name": "x"}).status_code == 422
    r = api.patch(f"/api/admin/departments/{api.dept('triage')}", "muni.admin",
                  {"is_active": False, "reason": "cleanup"})
    assert r.status_code == 409 and r.json()["error"]["code"] == "last_fallback_queue"
    assert db.scalar(select(AuditLog).where(AuditLog.action == "department.create"))


def test_department_deactivation_keeps_history_and_reroutes_new_reports(api, db):
    old = api.report("resident1", cat="water.leak")
    r = api.patch(f"/api/admin/departments/{api.dept('water')}", "muni.admin",
                  {"is_active": False, "reason": "Restructuring"})
    assert r.status_code == 200
    assert api.get(f"/api/complaints/{old['id']}", "resident1").json()["department_id"] == api.dept("water")
    new = api.report("resident1", cat="water.leak")
    assert new["routing_outcome"] == "fallback"
    staff = api.get(f"/api/complaints/{new['id']}", "admin").json()
    assert staff["initial_routing"]["reason_code"] == "department_inactive"
    r = api.post(f"/api/complaints/{old['id']}/reassign", "admin",
                 {"department_id": api.dept("water"), "reason": "retry"})
    assert r.status_code == 409


def test_inactive_officer_cannot_receive_work(api):
    off = api.officer("roads.officer2")
    assert api.patch(f"/api/admin/officers/{off}", "muni.admin",
                     {"is_active": False, "reason": "On leave"}).status_code == 200
    c = api.report()
    r = api.post(f"/api/complaints/{c['id']}/assign", "roads.supervisor", {"officer_id": off})
    assert r.status_code == 409 and r.json()["error"]["code"] == "officer_unavailable"
    r = api.post(f"/api/complaints/{c['id']}/assign", "roads.supervisor", {"officer_id": str(uuid.uuid4())})
    assert r.status_code == 422


def test_reassignment_requires_reason_and_records_history(api):
    c = api.report()
    cid = c["id"]
    api.post(f"/api/complaints/{cid}/assign", "roads.supervisor", {"officer_id": api.officer("roads.officer1")})
    r = api.post(f"/api/complaints/{cid}/assign", "roads.supervisor", {"officer_id": api.officer("roads.officer2")})
    assert r.json()["error"]["code"] == "already_assigned"
    r = api.post(f"/api/complaints/{cid}/reassign", "roads.supervisor", {"officer_id": api.officer("roads.officer2")})
    assert r.status_code == 422
    r = api.post(f"/api/complaints/{cid}/reassign", "roads.supervisor",
                 {"officer_id": api.officer("roads.officer2"), "reason": "Officer 1 on leave"})
    assert r.status_code == 200
    body = r.json()
    last = body["assignments"][-1]
    assert last["kind"] == "reassign" and last["from_officer_id"] == api.officer("roads.officer1")
    assert last["reason"] == "Officer 1 on leave" and body["reassignment_count"] == 1
    assert body["initial_routing"]["outcome"] == "routed"
    r = api.post(f"/api/complaints/{cid}/reassign", "roads.supervisor",
                 {"officer_id": api.officer("roads.officer2"), "reason": "again"})
    assert r.json()["error"]["code"] == "no_change"
    # Moving to another department's queue (admin) drops the officer and returns to review.
    r = api.post(f"/api/complaints/{cid}/reassign", "admin",
                 {"department_id": api.dept("drainage"), "reason": "It's actually a drain"})
    assert r.json()["department_id"] == api.dept("drainage") and r.json()["status"] == "under_review"
    assert r.json()["assigned_officer_id"] is None


def test_routing_rule_versioning_preserves_past_decisions(api, db):
    before = api.report(cat="lighting.streetlight")
    rule = db.scalar(select(RoutingRule).where(RoutingRule.is_active.is_(True),
                                               RoutingRule.department_id == uuid.UUID(api.dept("lighting"))))
    r = api.patch(f"/api/admin/routing-rules/{rule.id}", "muni.admin",
                  {"department_id": api.dept("roads"), "reason": "Roads now maintains lights"})
    assert r.status_code == 200
    new_rule = r.json()
    assert new_rule["version"] == 2 and new_rule["supersedes_id"] == str(rule.id)
    after = api.report(cat="lighting.streetlight")
    assert after["department_id"] == api.dept("roads")
    old_detail = api.get(f"/api/complaints/{before['id']}", "admin").json()
    assert old_detail["routing_rule_id"] == str(rule.id) and old_detail["department_id"] == api.dept("lighting")
    history = api.get("/api/admin/routing-rules", "muni.admin", params={"include_history": True}).json()
    assert {h["version"] for h in history if h["category_id"] == rule.category_id.__str__()} >= {1, 2}
    r = api.patch(f"/api/admin/routing-rules/{rule.id}", "muni.admin", {"precedence": 1, "reason": "stale"})
    assert r.json()["error"]["code"] == "rule_superseded"
    r = api.post("/api/admin/routing-rules", "muni.admin",
                 {"category_id": str(uuid.uuid4()), "department_id": api.dept("roads")})
    assert r.status_code == 422


def test_sla_policy_validation_and_versioning(api):
    r = api.post("/api/admin/sla-policies", "muni.admin",
                 {"name": "Bad", "acknowledge_hours": 50, "resolve_hours": 10})
    assert r.status_code == 422
    r = api.post("/api/admin/sla-policies", "muni.admin",
                 {"name": "Drains fast (illustrative)", "category_id": api.cat("drainage.blocked"),
                  "acknowledge_hours": 4, "resolve_hours": 24})
    assert r.status_code == 201 and r.json()["is_illustrative"]
    c = api.report(cat="drainage.blocked")
    staff = api.get(f"/api/complaints/{c['id']}", "admin").json()
    assert staff["sla_policy_id"] == r.json()["id"] and staff["sla_policy_version"] == 1
    v2 = api.patch(f"/api/admin/sla-policies/{r.json()['id']}", "muni.admin",
                   {"resolve_hours": 36, "reason": "Capacity review"}).json()
    assert v2["version"] == 2
    again = api.get(f"/api/complaints/{c['id']}", "admin").json()
    assert again["sla_policy_version"] == 1  # existing complaint keeps the version it was measured by


def test_category_and_service_admin(api):
    r = api.post("/api/admin/categories", "muni.admin",
                 {"code": "roads.speedbreaker", "label": "Damaged speed breaker", "parent_id": api.cat("roads"),
                  "synonyms": ["speed breaker", "hump"]})
    assert r.status_code == 201
    r = api.post("/api/admin/categories", "muni.admin",
                 {"code": "too.deep", "label": "Too deep", "parent_id": r.json()["id"]})
    assert r.json()["error"]["code"] == "category_depth"
    r = api.patch(f"/api/admin/categories/{api.cat('other.triage')}", "muni.admin",
                  {"is_active": False, "reason": "x tidy"})
    assert r.status_code == 409
    svc = api.post("/api/admin/services", "muni.admin",
                   {"code": "report-speedbreaker", "name": "Report a damaged speed breaker",
                    "summary": "Report damaged speed breakers", "service_type": "complaint",
                    "category_ids": [api.cat("roads.pothole")]})
    assert svc.status_code == 201 and svc.json()["state"] == "draft"
    found = api.get("/api/services", "resident1", params={"q": "speed breaker"}).json()
    assert all(i["service"]["code"] != "report-speedbreaker" for i in found["items"])  # draft hidden
    api.patch(f"/api/admin/services/{svc.json()['id']}", "muni.admin",
              {"state": "published", "mark_reviewed": True, "reason": "Verified with roads"})
    found = api.get("/api/services", "resident1", params={"q": "speed breaker"}).json()
    assert found["items"][0]["service"]["code"] == "report-speedbreaker"
    assert found["items"][0]["service"]["last_reviewed_at"]


def test_announcement_lifecycle(api):
    a = api.post("/api/admin/announcements", "muni.admin",
                 {"title": "Demo: water maintenance", "body": "DEMO notice, not official."}).json()
    assert api.get("/api/announcements", "resident1").json() == []
    assert api.post(f"/api/admin/announcements/{a['id']}/state", "muni.admin",
                    params={"state": "published"}).status_code == 200
    assert len(api.get("/api/announcements", "resident1").json()) == 1
    assert api.post(f"/api/admin/announcements/{a['id']}/state", "muni.admin",
                    params={"state": "draft"}).status_code == 409


# --- Analytics --------------------------------------------------------------------------------------

def test_analytics_metrics_match_fixture(api, db):
    # 3 roads complaints: one resolved in 10h within SLA, one resolved late, one open & overdue.
    ids = [api.report()["id"] for _ in range(3)]
    garbage = api.report(cat="sanitation.garbage")
    now = utcnow()
    for cid, created_h_ago, resolved_h_ago in ((ids[0], 20, 10), (ids[1], 300, 1)):
        api.post(f"/api/complaints/{cid}/assign", "roads.supervisor", {"officer_id": api.officer("roads.officer1")})
        api.post(f"/api/complaints/{cid}/resolve", "roads.officer1", {"resolution_notes": "fixed"})
        row = db.get(Complaint, uuid.UUID(cid))
        db.refresh(row)
        row.created_at = now - timedelta(hours=created_h_ago)
        row.resolved_at = now - timedelta(hours=resolved_h_ago)
        row.due_at = row.created_at + timedelta(hours=168)
    row = db.get(Complaint, uuid.UUID(ids[2]))
    db.refresh(row)
    row.is_overdue = True
    db.commit()

    a = api.get("/api/admin/analytics", "muni.admin", params=window()).json()
    assert a["issues_total"] == 4 and a["open"] == 2 and a["overdue_open"] == 1
    assert a["by_status"]["resolved"] == 2 and a["by_status"]["submitted"] == 2
    assert a["resolution_hours_avg"] == round((10 + 299) / 2, 2)
    assert a["resolution_hours_median"] == round((10 + 299) / 2, 2)
    assert a["sla_measured"] == 2 and a["sla_met"] == 1 and a["sla_compliance"] == 0.5
    by_dept = {g["key"]: g for g in a["by_department"]}
    assert by_dept[api.dept("roads")]["total"] == 3 and by_dept[api.dept("sanitation")]["total"] == 1

    scoped = api.get("/api/admin/analytics", "roads.supervisor", params=window()).json()
    assert scoped["issues_total"] == 3  # supervisor only sees own department
    empty = api.get("/api/admin/analytics", "muni.admin", params=window(days_back=400, days_forward=-200)).json()
    assert empty["issues_total"] == 0 and empty["sla_compliance"] is None
    bad = api.get("/api/admin/analytics", "muni.admin",
                  params={"date_from": "2026-01-01T00:00:00Z", "date_to": "2025-01-01T00:00:00Z"})
    assert bad.status_code == 422
    assert garbage["id"]


def test_csv_export_authorised_and_formula_safe(api, db):
    api.report(title="=HYPERLINK(\"http://evil\")", description="Formula injection attempt in title.")
    assert api.get("/api/admin/analytics/export.csv", "roads.supervisor", params=window()).status_code == 403
    r = api.get("/api/admin/analytics/export.csv", "auditor", params=window())
    assert r.status_code == 200 and r.headers["content-type"].startswith("text/csv")
    rows = list(csv.reader(io.StringIO(r.text)))
    assert rows[1][1].startswith("'=")
    assert db.scalar(select(AuditLog).where(AuditLog.action == "analytics.export"))
    too_long = api.get("/api/admin/analytics/export.csv", "auditor",
                       params={"date_from": "2020-01-01T00:00:00Z", "date_to": "2026-01-01T00:00:00Z"})
    assert too_long.status_code == 422
