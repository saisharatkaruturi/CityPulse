"""End-to-end complaint lifecycle through the HTTP API, plus validation and edits."""

from __future__ import annotations

import uuid

from sqlalchemy import func, select

from app.models import Complaint, ComplaintStatusHistory, Notification, OutboxEvent
from tests.conftest import run_worker, window


def test_resident_report_full_lifecycle(api, factory):
    # 1. Resident submits; reference is returned only after persistence.
    c = api.report("resident1", safety_risk=True)
    cid = c["id"]
    assert c["reference"].startswith("YCS-") and c["status"] == "submitted"
    assert c["routing_outcome"] == "routed"
    assert c["department_id"] == api.dept("roads")
    assert c["priority"] == "high"  # pothole is safety-sensitive + resident-reported risk
    assert c["progress"]["received_locally"] and not c["progress"]["department_acknowledged"]
    assert "reporter_id" not in c and "routing_explanation" not in c  # resident view
    assert api.db.scalar(select(func.count()).select_from(Complaint).where(Complaint.id == uuid.UUID(cid))) == 1

    # 2. Outbox event exists; notification is created only by the worker after commit.
    assert api.db.scalar(select(func.count()).select_from(Notification)) == 0
    run_worker(factory)
    notes = api.get("/api/notifications", "resident1").json()
    assert notes["total"] >= 1 and "received by this platform" in notes["items"][0]["body"]
    assert "not yet confirmation" in notes["items"][0]["body"]

    # 3. Supervisor views (staff view) and assigns.
    staff_view = api.get(f"/api/complaints/{cid}", "roads.supervisor").json()
    assert staff_view["routing_explanation"] and staff_view["initial_routing"]["outcome"] == "routed"
    r = api.post(f"/api/complaints/{cid}/assign", "roads.supervisor", {"officer_id": api.officer("roads.officer1")})
    assert r.status_code == 200, r.text
    assert r.json()["status"] == "assigned" and r.json()["assigned_officer_id"] == api.officer("roads.officer1")

    # 4. Officer starts work; history records actor/reason/timestamp.
    r = api.post(f"/api/complaints/{cid}/transitions", "roads.officer1",
                 {"to_status": "in_progress", "reason": "Crew dispatched"})
    assert r.status_code == 200 and r.json()["status"] == "in_progress"

    # 5. Officer resolves with notes.
    r = api.post(f"/api/complaints/{cid}/resolve", "roads.officer1", {"resolution_notes": "Patched with asphalt"})
    assert r.status_code == 200 and r.json()["status"] == "resolved"
    assert r.json()["progress"]["marked_resolved"] and not r.json()["progress"]["resident_confirmed"]

    # 6. Resident sees the real timeline and gives feedback, which closes the case.
    detail = api.get(f"/api/complaints/{cid}", "resident1").json()
    statuses = [e["to_status"] for e in detail["timeline"]]
    assert statuses == ["submitted", "assigned", "in_progress", "resolved"]
    assert detail["timeline"][2]["reason"] == "Crew dispatched" and detail["timeline"][2]["actor_is_staff"]
    r = api.post(f"/api/complaints/{cid}/feedback", "resident1", {"rating": 4, "comment": "Thanks"})
    assert r.status_code == 201
    assert api.get(f"/api/complaints/{cid}", "resident1").json()["status"] == "closed"

    # 7. Analytics reflect persisted records.
    a = api.get("/api/admin/analytics", "muni.admin", params=window()).json()
    assert a["issues_total"] == 1 and a["by_status"]["closed"] == 1 and a["sla_measured"] == 1


def test_unknown_category_goes_to_triage_and_is_rerouted(api):
    c = api.report("resident2", cat=None, title="Something odd", description="Hard to describe the issue here.")
    assert c["routing_outcome"] == "fallback" and c["department_id"] == api.dept("triage")
    assert c["category_id"] is None and c["reference"]
    # Triage supervisor corrects the category; routing is re-evaluated and audited.
    r = api.patch(f"/api/complaints/{c['id']}", "triage.supervisor",
                  {"category_id": api.cat("water.leak"), "reason": "Photo shows a leaking pipe"})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["department_id"] == api.dept("water") and body["category_source"] == "staff"
    assert body["initial_routing"]["outcome"] == "fallback"  # original decision preserved
    kinds = [a["kind"] for a in body["assignments"]]
    assert kinds == ["routing", "reroute"]
    logs = api.get("/api/admin/audit-logs", "auditor", params={"entity_id": c["id"]}).json()
    assert any(entry["action"] == "complaint.staff_edit" for entry in logs["items"])


def test_category_with_no_rule_goes_to_triage(api):
    c = api.report(cat="other.stray_animals")
    assert c["routing_outcome"] == "fallback"
    staff = api.get(f"/api/complaints/{c['id']}", "triage.supervisor").json()
    assert staff["initial_routing"]["reason_code"] == "no_matching_rule"


def test_auto_classification_high_confidence(api):
    c = api.report(cat=None, title="Blocked drain overflowing",
                   description="The blocked drain is overflowing and the sewer smells")
    assert c["category_id"] == api.cat("drainage.blocked") and c["routing_outcome"] == "routed"
    staff = api.get(f"/api/complaints/{c['id']}", "admin").json()
    assert staff["category_source"].startswith("auto:")


def test_out_of_area_location_goes_to_triage(api):
    r = api.post("/api/complaints", "resident1", json={
        "title": "Pothole far away", "description": "Pothole somewhere outside the city area.",
        "category_id": api.cat("roads.pothole"), "location": {"latitude": 10.0, "longitude": 70.0}})
    assert r.status_code == 201 and r.json()["routing_outcome"] == "fallback"


def test_manual_ward_selection_without_gps(api):
    r = api.post("/api/complaints", "resident1", json={
        "title": "Streetlight off", "description": "Streetlight on my street is off.",
        "category_id": api.cat("lighting.streetlight"), "location": {"ward_id": api.ward("demo-w3")}})
    assert r.status_code == 201 and r.json()["ward_id"] == api.ward("demo-w3")
    assert r.json()["latitude"] is None


def test_ward_specific_rule_routes_to_team(api):
    c = api.report(ward="demo-w4")
    staff = api.get(f"/api/complaints/{c['id']}", "roads.supervisor").json()
    assert staff["team_id"] is not None and "ward-specific" in staff["routing_explanation"]


# --- Validation -----------------------------------------------------------------------------------

def test_validation_errors_are_field_level(api):
    r = api.post("/api/complaints", "resident1", json={"title": "ok title", "description": "     "})
    assert r.status_code == 422
    err = r.json()["error"]
    assert err["code"] == "validation_error" and any(d["field"] == "description" for d in err["details"])
    assert err["request_id"]


def test_rejects_protected_fields_and_bad_values(api):
    base = {"title": "Pothole", "description": "A pothole on the road here."}
    for extra in ({"status": "resolved"}, {"reporter_id": str(uuid.uuid4())}, {"priority": "critical"},
                  {"department_id": str(uuid.uuid4())}, {"created_at": "2020-01-01T00:00:00Z"}):
        assert api.post("/api/complaints", "resident1", json={**base, **extra}).status_code == 422
    assert api.post("/api/complaints", "resident1",
                    json={**base, "location": {"latitude": 91, "longitude": 0}}).status_code == 422
    assert api.post("/api/complaints", "resident1",
                    json={**base, "location": {"latitude": 17.4}}).status_code == 422
    r = api.post("/api/complaints", "resident1", json={**base, "category_id": str(uuid.uuid4())})
    assert r.status_code == 422 and r.json()["error"]["code"] == "invalid_category"
    r = api.post("/api/complaints", "resident1", json={**base, "location": {"ward_id": str(uuid.uuid4())}})
    assert r.json()["error"]["code"] == "invalid_ward"
    assert api.post("/api/complaints", "resident1", json={**base, "source_channel": "seed"}).status_code == 422


def test_inactive_category_rejected(api):
    r = api.patch(f"/api/admin/categories/{api.cat('roads.footpath')}", "muni.admin",
                  {"is_active": False, "reason": "Merged into pothole"})
    assert r.status_code == 200
    r = api.post("/api/complaints", "resident1", json={
        "title": "Footpath", "description": "Footpath tiles broken badly.", "category_id": api.cat("roads.footpath")})
    assert r.status_code == 422


def test_idempotent_creation(api):
    body = {"title": "Garbage pile", "description": "Garbage pile near the market corner.",
            "category_id": api.cat("sanitation.garbage")}
    key = {"Idempotency-Key": "retry-key-0001"}
    r1 = api.post("/api/complaints", "resident1", json=body, headers=key)
    r2 = api.post("/api/complaints", "resident1", json=body, headers=key)
    assert r1.status_code == 201 and r2.status_code == 200
    assert r2.headers["Idempotent-Replay"] == "true" and r1.json()["id"] == r2.json()["id"]
    assert api.db.scalar(select(func.count()).select_from(Complaint)) == 1
    r3 = api.post("/api/complaints", "resident1", json={**body, "title": "Different"}, headers=key)
    assert r3.status_code == 422 and r3.json()["error"]["code"] == "idempotency_key_reuse"
    # Same key from another user is independent.
    assert api.post("/api/complaints", "resident2", json=body, headers=key).status_code == 201


def test_unicode_telugu_text_round_trip_and_search(api):
    desc = "రోడ్డు మీద పెద్ద గుంత ఉంది, వాహనాలు ఇబ్బంది పడుతున్నాయి"
    c = api.report(title="రోడ్డు గుంత", description=desc, language="te")
    got = api.get(f"/api/complaints/{c['id']}", "resident1").json()
    assert got["description"] == desc and got["original_language"] == "te"
    found = api.get("/api/complaints", "resident1", params={"q": "గుంత"}).json()
    assert found["total"] == 1
    cats = api.get("/api/categories", "resident1", headers={"Accept-Language": "te-IN"}).json()
    assert any(c["label"] == "గుంత" for c in cats)


# --- Listing, filters, pagination ----------------------------------------------------------------

def test_list_filters_and_pagination(api):
    for _ in range(3):
        api.report("resident1")
    api.report("resident1", cat="sanitation.garbage")
    api.report("resident2")
    mine = api.get("/api/complaints", "resident1", params={"page_size": 2}).json()
    assert mine["total"] == 4 and len(mine["items"]) == 2 and mine["page_size"] == 2
    page2 = api.get("/api/complaints", "resident1", params={"page_size": 2, "page": 2}).json()
    assert {i["id"] for i in mine["items"]}.isdisjoint({i["id"] for i in page2["items"]})
    assert api.get("/api/complaints", "resident1", params={"page": 99}).json()["items"] == []
    cat = api.get("/api/complaints", "resident1", params={"category_id": api.cat("sanitation.garbage")}).json()
    assert cat["total"] == 1
    big = api.get("/api/complaints", "resident1", params={"page_size": 10_000}).json()
    assert big["page_size"] == 100  # capped
    roads = api.get("/api/complaints", "roads.supervisor",
                    params={"status": ["submitted"], "sort": "-priority"}).json()
    assert roads["total"] == 4
    assert api.get("/api/complaints", "resident1", params={"sort": "reporter_id"}).status_code == 422
    assert api.get("/api/complaints", "resident1",
                   params={"created_from": "2020-01-01T00:00:00"}).status_code == 422


# --- Edits, versions, workflow use cases ------------------------------------------------------------

def test_resident_edit_rules_and_stale_version(api):
    c = api.report("resident1")
    r = api.patch(f"/api/complaints/{c['id']}", "resident1", {"title": "Updated title"},
                  headers={"If-Match": str(c["version"])})
    assert r.status_code == 200 and r.json()["title"] == "Updated title"
    stale = api.patch(f"/api/complaints/{c['id']}", "resident1", {"title": "Again"},
                      headers={"If-Match": str(c["version"])})
    assert stale.status_code == 409 and stale.json()["error"]["code"] == "stale_version"
    # Residents cannot touch staff fields.
    r = api.patch(f"/api/complaints/{c['id']}", "resident1", {"priority": "critical", "reason": "please"})
    assert r.status_code == 403
    r = api.patch(f"/api/complaints/{c['id']}", "resident1", {"status": "resolved"})
    assert r.status_code == 422
    # After pickup, the resident can no longer edit.
    api.post(f"/api/complaints/{c['id']}/assign", "roads.supervisor", {"officer_id": api.officer("roads.officer1")})
    r = api.patch(f"/api/complaints/{c['id']}", "resident1", {"title": "Late edit"})
    assert r.status_code == 409 and r.json()["error"]["code"] == "not_editable"


def test_generic_transition_guards(api):
    c = api.report()
    cid = c["id"]
    r = api.post(f"/api/complaints/{cid}/transitions", "roads.supervisor", {"to_status": "resolved"})
    assert r.json()["error"]["code"] == "use_dedicated_endpoint"
    r = api.post(f"/api/complaints/{cid}/transitions", "roads.supervisor", {"to_status": "in_progress"})
    assert r.status_code == 409
    r = api.post(f"/api/complaints/{cid}/transitions", "roads.supervisor", {"to_status": "rejected"})
    assert r.status_code == 422 and r.json()["error"]["code"] == "reason_required"
    r = api.post(f"/api/complaints/{cid}/transitions", "resident1",
                 {"to_status": "rejected", "reason": "I reject it myself"})
    assert r.status_code == 409 and r.json()["error"]["code"] == "transition_not_permitted"
    r = api.post(f"/api/complaints/{cid}/transitions", "roads.supervisor", {"to_status": "bogus"})
    assert r.status_code == 422


def test_resolution_notes_required(api):
    c = api.report()
    api.post(f"/api/complaints/{c['id']}/assign", "roads.supervisor", {"officer_id": api.officer("roads.officer1")})
    r = api.post(f"/api/complaints/{c['id']}/resolve", "roads.officer1", {"resolution_notes": "  "})
    assert r.status_code == 422 and r.json()["error"]["code"] == "resolution_notes_required"


def test_withdraw_and_terminal(api):
    c = api.report()
    r = api.post(f"/api/complaints/{c['id']}/withdraw", "resident1", {"reason": "Fixed by neighbours"})
    assert r.status_code == 200 and r.json()["status"] == "withdrawn"
    r = api.post(f"/api/complaints/{c['id']}/withdraw", "resident1", {})
    assert r.status_code == 409
    assert api.post(f"/api/complaints/{c['id']}/comments", "resident1", {"body": "hi"}).status_code == 409


def test_reopen_window_and_feedback_rules(api, db, monkeypatch):
    c = api.report()
    cid = c["id"]
    assert api.post(f"/api/complaints/{cid}/feedback", "resident1", {"rating": 3}).json()["error"]["code"] \
        == "feedback_not_eligible"
    api.post(f"/api/complaints/{cid}/assign", "roads.supervisor", {"officer_id": api.officer("roads.officer1")})
    api.post(f"/api/complaints/{cid}/resolve", "roads.officer1", {"resolution_notes": "Done"})
    assert api.post(f"/api/complaints/{cid}/feedback", "resident2", {"rating": 3}).status_code == 404
    assert api.post(f"/api/complaints/{cid}/feedback", "resident1", {"rating": 9}).status_code == 422
    r = api.post(f"/api/complaints/{cid}/reopen", "resident1", {"reason": "Pothole is back already"})
    assert r.status_code == 200 and r.json()["status"] == "reopened"
    api.post(f"/api/complaints/{cid}/resolve", "roads.officer1", {"resolution_notes": "Done properly"})
    assert api.post(f"/api/complaints/{cid}/feedback", "resident1",
                    {"rating": 2, "confirm_resolved": False}).status_code == 201
    assert api.post(f"/api/complaints/{cid}/feedback", "resident1", {"rating": 5}).json()["error"]["code"] \
        == "feedback_exists"
    # Outside the reopen window the resident is told to file a new report.
    from datetime import timedelta

    row = db.get(Complaint, uuid.UUID(cid))
    db.refresh(row)
    row.resolved_at = row.resolved_at - timedelta(days=60)
    db.commit()
    r = api.post(f"/api/complaints/{cid}/reopen", "resident1", {"reason": "Still broken here"})
    assert r.json()["error"]["code"] == "reopen_window_expired"
    # Staff may still reopen.
    assert api.post(f"/api/complaints/{cid}/reopen", "roads.supervisor",
                    {"reason": "Inspection failed"}).status_code == 200


def test_information_request_pauses_sla_and_resident_reply_resumes(api, db):
    c = api.report()
    cid = c["id"]
    api.post(f"/api/complaints/{cid}/assign", "roads.supervisor", {"officer_id": api.officer("roads.officer1")})
    due_before = api.get(f"/api/complaints/{cid}", "roads.officer1").json()["due_at"]
    r = api.post(f"/api/complaints/{cid}/comments", "roads.officer1",
                 {"body": "Which side of the road is it on?", "request_information": True})
    assert r.status_code == 201
    staff = api.get(f"/api/complaints/{cid}", "roads.officer1").json()
    assert staff["status"] == "awaiting_resident" and staff["sla_paused_at"] is not None
    assert api.post(f"/api/complaints/{cid}/comments", "resident1",
                    {"body": "Left side", "request_information": True}).status_code == 403
    assert api.post(f"/api/complaints/{cid}/comments", "resident1", {"body": "Left side near shop"}).status_code == 201
    staff = api.get(f"/api/complaints/{cid}", "roads.officer1").json()
    assert staff["status"] == "in_progress" and staff["sla_paused_at"] is None
    assert staff["due_at"] >= due_before
    hist = db.scalars(select(ComplaintStatusHistory).where(
        ComplaintStatusHistory.complaint_id == uuid.UUID(cid))).all()
    assert hist[-1].actor_kind.value == "system"


def test_notification_only_after_commit(api, factory, db):
    # A failed (rolled back) creation leaves no outbox event behind.
    before = db.scalar(select(func.count()).select_from(OutboxEvent))
    r = api.post("/api/complaints", "resident1", json={
        "title": "x" * 3, "description": "valid description here", "media_ids": [str(uuid.uuid4())]})
    assert r.status_code == 422
    assert db.scalar(select(func.count()).select_from(OutboxEvent)) == before
    assert db.scalar(select(func.count()).select_from(Complaint)) == 0
