"""Duplicate candidates, merge, public nearby search and community support."""

from __future__ import annotations

from tests.conftest import window


def test_candidates_nearby_same_category_only(api):
    a = api.report("resident1", ward="demo-w2", visibility="public")
    near = api.report("resident2", ward="demo-w2", offset=(0.0003, 0.0002))  # ~40 m
    far = api.report("resident3", ward="demo-w2", offset=(0.008, 0.0))  # ~900 m
    other_cat = api.report("resident3", ward="demo-w2", cat="sanitation.garbage")
    cands = api.get(f"/api/complaints/{a['id']}/possible-duplicates", "roads.supervisor").json()
    refs = {c["reference"] for c in cands}
    assert near["reference"] in refs
    assert far["reference"] not in refs and other_cat["reference"] not in refs
    assert all(c["distance_m"] <= 150 for c in cands)


def test_candidates_hide_private_data_from_residents(api):
    a = api.report("resident1", ward="demo-w2")
    api.report("resident2", ward="demo-w2", offset=(0.0002, 0.0))  # private, someone else's
    cands = api.get(f"/api/complaints/{a['id']}/possible-duplicates", "resident1").json()
    assert len(cands) == 1
    assert cands[0]["id"] is None and cands[0]["title"] is None  # reference only
    assert "description" not in cands[0] and "reporter_id" not in cands[0]


def test_merge_flow_and_cycle_prevention(api):
    a = api.report("resident1", ward="demo-w2")
    b = api.report("resident2", ward="demo-w2", offset=(0.0003, 0.0))
    c = api.report("resident3", ward="demo-w2", offset=(0.0001, 0.0))
    # Unauthorised merges.
    assert api.post(f"/api/complaints/{b['id']}/merge", "resident2",
                    {"target_id": a["id"], "reason": "same pothole"}).status_code == 403
    assert api.post(f"/api/complaints/{b['id']}/merge", "roads.officer1",
                    {"target_id": a["id"], "reason": "same pothole"}).status_code == 403
    assert api.post(f"/api/complaints/{b['id']}/merge", "roads.supervisor",
                    {"target_id": b["id"], "reason": "same pothole"}).json()["error"]["code"] == "self_merge"
    assert api.post(f"/api/complaints/{b['id']}/merge", "roads.supervisor",
                    {"target_id": a["id"], "reason": ""}).status_code == 422
    r = api.post(f"/api/complaints/{b['id']}/merge", "roads.supervisor",
                 {"target_id": a["id"], "reason": "Same pothole, verified on site"})
    assert r.status_code == 200, r.text
    merged = r.json()
    assert merged["status"] == "closed" and merged["merged_into_id"] == a["id"]
    # Reporter keeps access to their original report and sees where it went.
    mine = api.get(f"/api/complaints/{b['id']}", "resident2").json()
    assert mine["merged_into_reference"] == a["reference"] and "Merged" in mine["progress"]["summary"]
    # Cycles / chains are refused.
    r = api.post(f"/api/complaints/{a['id']}/merge", "roads.supervisor", {"target_id": b["id"], "reason": "reverse"})
    assert r.json()["error"]["code"] in ("target_merged", "merge_chain")
    r = api.post(f"/api/complaints/{c['id']}/merge", "roads.supervisor", {"target_id": b["id"], "reason": "chain"})
    assert r.json()["error"]["code"] == "target_merged"
    r = api.post(f"/api/complaints/{a['id']}/merge", "roads.supervisor", {"target_id": c["id"], "reason": "chain"})
    assert r.json()["error"]["code"] == "merge_chain"
    # Analytics counts underlying issues, not duplicate reports.
    an = api.get("/api/admin/analytics", "roads.supervisor", params=window()).json()
    assert an["reports_total"] == 3 and an["issues_total"] == 2 and an["merged_duplicates"] == 1


def test_nearby_public_is_privacy_filtered(api):
    pub = api.report("resident1", ward="demo-w1", visibility="public")
    api.report("resident2", ward="demo-w1", offset=(0.0001, 0))  # private
    lat, lng = pub["latitude"], pub["longitude"]
    rows = api.get("/api/complaints/nearby", "resident3", params={"lat": lat, "lng": lng, "radius_m": 500}).json()
    assert [r["reference"] for r in rows] == [pub["reference"]]
    assert rows[0]["approx_latitude"] == round(lat, 3) and "description" not in rows[0]
    assert api.get("/api/complaints/nearby", "resident3",
                   params={"lat": lat, "lng": lng, "radius_m": 50_000}).status_code == 422


def test_support_once_and_anonymous(api):
    pub = api.report("resident1", visibility="public")
    priv = api.report("resident1")
    r = api.post(f"/api/complaints/{pub['id']}/support", "resident2")
    assert r.status_code == 201 and r.json()["support_count"] == 1
    again = api.post(f"/api/complaints/{pub['id']}/support", "resident2")
    assert again.status_code == 409 and again.json()["error"]["code"] == "already_supported"
    assert api.post(f"/api/complaints/{pub['id']}/support", "resident1").json()["error"]["code"] == "own_report"
    assert api.post(f"/api/complaints/{priv['id']}/support", "resident2").status_code == 404
    detail = api.get(f"/api/complaints/{pub['id']}", "roads.supervisor").text
    assert str(api.user_id("resident2")) not in detail  # supporter identity never exposed
    assert api.delete(f"/api/complaints/{pub['id']}/support", "resident2").json()["support_count"] == 0
