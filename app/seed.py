"""Repeatable DEMO seed data. Everything here is fictional.

* Departments, wards, people, and complaints are invented for demonstration.
* Ward polygons are a FICTIONAL grid, not real municipal boundaries.
* SLA targets are ILLUSTRATIVE, not official service guarantees.
* Telugu labels are demo translations and have not been reviewed by a native speaker.
Reference data is upserted by stable code; demo complaints are created once (through the
real service layer, so histories, routing decisions, and events are genuine).
"""

from __future__ import annotations

import io
import logging
from datetime import timedelta

from PIL import Image
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.permissions import Principal
from app.core.security import hash_password
from app.core.time import utcnow
from app.domain.enums import (
    ComplaintStatus,
    LocationSource,
    MediaKind,
    Priority,
    PublicationState,
    Role,
    ServiceType,
    SourceChannel,
    Visibility,
)
from app.models import (
    Category,
    Complaint,
    Department,
    Officer,
    RoutingRule,
    Service,
    SlaPolicy,
    Team,
    User,
    UserRole,
    Ward,
)
from app.schemas.complaints import (
    AssignRequest,
    ComplaintCreate,
    FeedbackCreate,
    LocationIn,
)
from app.services import complaints as svc
from app.services import media
from app.services.auth import load_principal

logger = logging.getLogger("app.seed")

DEMO_DOMAIN = "example.com"

DEPARTMENTS = [
    ("triage", "Triage Desk (demo)", "Manual review queue for reports without a confident route.", True),
    ("roads", "Roads Department (demo)", "Fictional roads and footpaths department.", False),
    ("sanitation", "Sanitation Department (demo)", "Fictional solid-waste department.", False),
    ("water", "Water Supply Department (demo)", "Fictional water supply department.", False),
    ("drainage", "Drainage Department (demo)", "Fictional storm-water and drainage department.", False),
    ("lighting", "Street Lighting Department (demo)", "Fictional street lighting department.", False),
]

TEAMS = [("roads", "Roads Crew A"), ("roads", "Roads Crew East"), ("sanitation", "Sanitation Crew"),
         ("water", "Water Crew"), ("drainage", "Drainage Crew"), ("lighting", "Lighting Crew")]

# Fictional 2x2 grid. lat 17.400-17.440, lng 78.440-78.480.
_LAT0, _LNG0, _STEP = 17.400, 78.440, 0.020
WARDS = [(f"demo-w{i + 1}", f"Demo Ward {i + 1}", r, c) for i, (r, c) in enumerate([(0, 0), (0, 1), (1, 0), (1, 1)])]
WARD_PROVENANCE = "FICTIONAL demo grid generated for development; not an official ward boundary"

# code, label, parent code, synonyms, default priority, safety sensitive, telugu label
# Telugu labels are everyday wording drafted for the demo; they have not been reviewed by a native speaker.
CATEGORIES: list[tuple[str, str, str | None, list[str], Priority, bool, str | None]] = [
    ("roads", "Roads & footpaths", None, ["road"], Priority.medium, False, "రోడ్లు, ఫుట్‌పాత్‌లు"),
    ("roads.pothole", "Pothole", "roads", ["pothole", "potholes", "crater", "road damage", "broken road"],
     Priority.medium, True, "గుంత"),
    ("roads.footpath", "Damaged footpath", "roads", ["footpath", "sidewalk", "pavement"], Priority.low, False,
     "పాడైన ఫుట్‌పాత్"),
    ("sanitation", "Sanitation", None, [], Priority.medium, False, "పారిశుద్ధ్యం"),
    ("sanitation.garbage", "Garbage not collected", "sanitation",
     ["garbage", "trash", "waste", "rubbish", "litter", "dump", "garbage pile"], Priority.medium, False,
     "చెత్త సేకరణ లేదు"),
    ("water", "Water supply", None, [], Priority.medium, False, "నీటి సరఫరా"),
    ("water.leak", "Water leakage", "water", ["leak", "leakage", "pipe burst", "burst pipe", "water leaking"],
     Priority.medium, False, "నీటి లీకేజీ"),
    ("water.no_supply", "No water supply", "water", ["no water", "water supply", "dry tap"], Priority.high, False,
     "నీళ్లు రావడం లేదు"),
    ("drainage", "Drainage", None, [], Priority.medium, False, "డ్రైనేజీ"),
    ("drainage.blocked", "Blocked drain", "drainage",
     ["drain", "drainage", "sewer", "clogged", "overflow", "blocked drain", "manhole"], Priority.medium, True,
     "మూసుకుపోయిన కాలువ"),
    ("lighting", "Street lighting", None, [], Priority.low, False, "వీధి దీపాలు"),
    ("lighting.streetlight", "Broken streetlight", "lighting",
     ["streetlight", "street light", "lamp", "light not working", "dark street"], Priority.low, True,
     "పనిచేయని వీధి దీపం"),
    # Electrical hazards on public infrastructure. No routing rule is seeded for these: without verified data
    # about which office handles them, they go to the triage desk, where a person decides.
    ("electrical", "Electrical hazards", None, [], Priority.high, True,
     "విద్యుత్ ప్రమాదాలు"),
    ("electrical.exposed_wire", "Exposed or hanging wires", "electrical",
     ["exposed wire", "hanging wire", "live wire", "loose wire", "fallen wire", "sparking", "sparks",
      "electric wire", "wires", "wire", "shock", "కరెంటు తీగ", "తీగలు"], Priority.high, True,
     "బయటపడిన లేదా వేలాడుతున్న కరెంటు తీగలు"),
    ("electrical.public_fixture", "Damaged electric pole or box", "electrical",
     ["electric pole", "electrical pole", "current pole", "junction box", "electric box", "fuse box",
      "meter box", "transformer", "pole leaning", "కరెంటు స్తంభం"], Priority.high, True,
     "పాడైన కరెంటు స్తంభం లేదా బాక్స్"),
    ("other.stray_animals", "Stray animals", None, ["stray", "dogs", "cattle"], Priority.medium, False,
     "వీధి జంతువులు"),
    ("other.triage", "Other / not sure", None, [], Priority.medium, False, "ఇతర / తెలియదు"),
]

RULES: list[tuple[str, str, str | None, str | None, int]] = [
         ("roads", "roads", None, None, 100), ("sanitation", "sanitation", None, None, 100),
         ("water", "water", None, None, 100), ("drainage", "drainage", None, None, 100),
         ("lighting", "lighting", None, None, 100),
         ("roads.pothole", "roads", "demo-w4", "Roads Crew East", 10)]

SLA: list[tuple[str, str | None, Priority | None, int, int]] = [
       ("Default (illustrative)", None, None, 48, 168), ("High priority (illustrative)", None, Priority.high, 12, 72),
       ("Critical (illustrative)", None, Priority.critical, 2, 24),
       ("Water leakage (illustrative)", "water.leak", None, 12, 48)]

DEFAULT_SERVICE_INSTRUCTIONS = ("DEMO: submit a report through this app. No official contact details are listed "
                                "because none have been verified.")
ELECTRICAL_SAFETY = ("Keep away and keep others away. Do not touch it or try to fix it. If wires are sparking, "
                     "someone is hurt, or anyone is in immediate danger, call 112 or your electricity provider's "
                     "emergency line first. Reports here go to a person at the triage desk; this platform does "
                     "not send emergency help.")

# code, name, type, summary, synonyms, category codes, owner department, instructions (optional)
SERVICES: list[tuple] = [
    ("report-road-damage", "Report a pothole or damaged road", ServiceType.complaint,
     "Report potholes, broken roads or damaged footpaths for repair.", ["pothole", "road repair"],
     ["roads.pothole", "roads.footpath"], "roads"),
    ("report-garbage", "Report uncollected garbage", ServiceType.complaint,
     "Report missed garbage collection or illegal dumping.", ["garbage", "waste pickup"],
     ["sanitation.garbage"], "sanitation"),
    ("report-water-leak", "Report a water leak", ServiceType.complaint,
     "Report leaking or burst water pipes in public areas.", ["leak", "pipe"], ["water.leak"], "water"),
    ("report-no-water", "Report no water supply", ServiceType.complaint,
     "Report an interruption to piped water supply.", ["no water"], ["water.no_supply"], "water"),
    ("report-blocked-drain", "Report a blocked drain", ServiceType.complaint,
     "Report blocked or overflowing drains and open manholes.", ["drain", "sewer"], ["drainage.blocked"],
     "drainage"),
    ("report-streetlight", "Report a broken streetlight", ServiceType.complaint,
     "Report streetlights that are off, flickering or damaged.", ["streetlight", "lamp"],
     ["lighting.streetlight"], "lighting"),
    ("report-electrical-hazard", "Report an electrical hazard in a public place", ServiceType.complaint,
     "Report exposed or hanging wires, a damaged electric pole, or an open junction box on a street or in a "
     "public space.", ["electrical", "wire", "electric pole", "junction box", "sparking"],
     ["electrical.exposed_wire", "electrical.public_fixture"], "triage", ELECTRICAL_SAFETY),
    ("water-connection-info", "New water connection (information)", ServiceType.information,
     "General information about requesting a new water connection. DEMO placeholder: eligibility, fees and "
     "documents are NOT listed because no verified source is configured.", ["water connection", "new tap"],
     ["water.no_supply"], "water"),
]

USERS: list[tuple[str, str, list[tuple[Role, str | None]]]] = [
    ("admin", "Demo System Admin", [(Role.system_admin, None)]),
    ("muni.admin", "Demo Municipal Admin", [(Role.municipal_admin, None)]),
    ("auditor", "Demo Auditor", [(Role.auditor, None)]),
    ("triage.supervisor", "Demo Triage Supervisor", [(Role.supervisor, "triage")]),
    ("roads.supervisor", "Demo Roads Supervisor", [(Role.supervisor, "roads")]),
    ("sanitation.supervisor", "Demo Sanitation Supervisor", [(Role.supervisor, "sanitation")]),
    ("water.supervisor", "Demo Water Supervisor", [(Role.supervisor, "water")]),
    ("drainage.supervisor", "Demo Drainage Supervisor", [(Role.supervisor, "drainage")]),
    ("lighting.supervisor", "Demo Lighting Supervisor", [(Role.supervisor, "lighting")]),
    ("roads.officer1", "Demo Roads Officer 1", [(Role.field_officer, "roads")]),
    ("roads.officer2", "Demo Roads Officer 2", [(Role.field_officer, "roads")]),
    ("sanitation.officer", "Demo Sanitation Officer", [(Role.field_officer, "sanitation")]),
    ("water.officer", "Demo Water Officer", [(Role.field_officer, "water")]),
    ("drainage.officer", "Demo Drainage Officer", [(Role.field_officer, "drainage")]),
    ("lighting.officer", "Demo Lighting Officer", [(Role.field_officer, "lighting")]),
    ("resident1", "Asha (demo resident)", [(Role.resident, None)]),
    ("resident2", "Ravi (demo resident)", [(Role.resident, None)]),
    ("resident3", "Meena (demo resident)", [(Role.resident, None)]),
]
# The accounts offered on the sign-in page in demo mode, grouped by the role experience they open.
# (group, handle, one-line description). Served by GET /api/meta only when demo mode is on.
DEMO_ACCOUNTS: list[tuple[str, str, str]] = [
    ("resident", "resident1", "Reports issues, finds services and follows their own reports."),
    ("resident", "resident2", "A second resident, for checking that reports stay private."),
    ("road_officer", "roads.officer1", "Field officer in the Roads department; works the cases assigned to them."),
    ("road_supervisor", "roads.supervisor", "Assigns, corrects and reviews Roads cases; sees Roads analytics."),
    ("triage_desk", "triage.supervisor", "Reviews reports no rule could route, and sends them on."),
    ("municipal_admin", "muni.admin", "Oversees every department, with city-wide analytics and export."),
    ("auditor", "auditor", "Read-only access for checking records and history."),
]

OFFICER_TEAMS = {"roads.officer1": "Roads Crew A", "roads.officer2": "Roads Crew East",
                 "sanitation.officer": "Sanitation Crew", "water.officer": "Water Crew",
                 "drainage.officer": "Drainage Crew", "lighting.officer": "Lighting Crew"}


def email(handle: str) -> str:
    return f"{handle}@{DEMO_DOMAIN}"


def _ward_polygon(r: int, c: int) -> list[list[float]]:
    lat, lng = _LAT0 + r * _STEP, _LNG0 + c * _STEP
    return [[lat, lng], [lat, lng + _STEP], [lat + _STEP, lng + _STEP], [lat + _STEP, lng]]


def ward_center(code: str) -> tuple[float, float]:
    for wc, _, r, c in WARDS:
        if wc == code:
            return _LAT0 + r * _STEP + _STEP / 2, _LNG0 + c * _STEP + _STEP / 2
    raise KeyError(code)


def seed_reference(db: Session) -> None:
    now = utcnow()
    depts = {d.code: d for d in db.scalars(select(Department)).all()}
    for code, name, desc, fallback in DEPARTMENTS:
        if code not in depts:
            depts[code] = Department(code=code, name=name, description=desc, is_fallback=fallback, is_demo=True)
            db.add(depts[code])
    db.flush()
    teams = {(t.department_id, t.name): t for t in db.scalars(select(Team)).all()}
    for dcode, name in TEAMS:
        key = (depts[dcode].id, name)
        if key not in teams:
            teams[key] = Team(department_id=depts[dcode].id, name=name)
            db.add(teams[key])
    wards = {w.code: w for w in db.scalars(select(Ward)).all()}
    for code, name, r, c in WARDS:
        if code not in wards:
            wards[code] = Ward(code=code, name=name, boundary=_ward_polygon(r, c), provenance=WARD_PROVENANCE,
                               is_demo=True)
            db.add(wards[code])
    db.flush()
    cats = {c.code: c for c in db.scalars(select(Category)).all()}
    for code, label, parent, syn, prio, safety, te in CATEGORIES:
        if code not in cats:
            cats[code] = Category(code=code, label=label, parent_id=cats[parent].id if parent else None,
                                  synonyms=syn, examples=[], labels_i18n={"te": te} if te else {},
                                  default_priority=prio, safety_sensitive=safety,
                                  is_triage=code == "other.triage",
                                  description=f"Demo category: {label}")
            db.add(cats[code])
            db.flush()
        elif te and "te" not in (cats[code].labels_i18n or {}):
            # Fill a missing translation without overwriting one an administrator has set.
            cats[code].labels_i18n = {**(cats[code].labels_i18n or {}), "te": te}
    if not db.scalar(select(RoutingRule.id).limit(1)):
        for cat, dept, ward, team, prec in RULES:
            team_id = teams[(depts[dept].id, team)].id if team else None
            db.add(RoutingRule(category_id=cats[cat].id, department_id=depts[dept].id,
                               ward_id=wards[ward].id if ward else None, team_id=team_id, precedence=prec,
                               effective_from=now - timedelta(days=365), notes="Demo rule"))
    if not db.scalar(select(SlaPolicy.id).limit(1)):
        for pol_name, pol_cat, pol_prio, ack, res in SLA:
            db.add(SlaPolicy(name=pol_name, category_id=cats[pol_cat].id if pol_cat else None, priority=pol_prio,
                             acknowledge_hours=ack, resolve_hours=res, effective_from=now - timedelta(days=365),
                             is_illustrative=True))
    existing_services = set(db.scalars(select(Service.code)).all())
    for code, name, stype, summary, syn, cat_codes, dept, *extra in SERVICES:
        if code in existing_services:
            continue
        s = Service(code=code, name=name, summary=summary, service_type=stype, state=PublicationState.published,
                    synonyms=syn, owner_department_id=depts[dept].id, is_demo=True,
                    instructions=extra[0] if extra else DEFAULT_SERVICE_INSTRUCTIONS)
        s.departments = [depts[dept]]
        s.categories = [cats[c] for c in cat_codes]
        db.add(s)
    users = {u.email: u for u in db.scalars(select(User)).all()}
    pw = hash_password(get_settings().demo_password)
    for handle, name, roles in USERS:
        if email(handle) in users:
            continue
        u = User(email=email(handle), display_name=name, password_hash=pw)
        for role, role_dept in roles:
            u.roles.append(UserRole(role=role, department_id=depts[role_dept].id if role_dept else None,
                                    created_at=now))
        db.add(u)
        users[u.email] = u
    db.flush()
    officers = {o.user_id for o in db.scalars(select(Officer)).all()}
    for handle, team_name in OFFICER_TEAMS.items():
        u = users[email(handle)]
        if u.id in officers:
            continue
        dept_id = next(r.department_id for r in u.roles if r.role == Role.field_officer)
        assert dept_id is not None
        db.add(Officer(user_id=u.id, department_id=dept_id, team_id=teams[(dept_id, team_name)].id))
    db.commit()


def _p(db: Session, handle: str) -> Principal:
    u = db.scalar(select(User).where(User.email == email(handle)))
    assert u is not None
    return load_principal(db, u, None)


def _cat(db: Session, code: str):  # noqa: ANN202
    return db.scalar(select(Category).where(Category.code == code))


def _officer(db: Session, handle: str) -> Officer:
    u = db.scalar(select(User).where(User.email == email(handle)))
    assert u is not None
    o = db.scalar(select(Officer).where(Officer.user_id == u.id))
    assert o is not None
    return o


def _report(db: Session, handle: str, title: str, desc: str, cat: str | None, ward: str | None,
            offset: tuple[float, float] = (0, 0), public: bool = False, safety: bool = False) -> Complaint:
    loc = None
    if ward:
        lat, lng = ward_center(ward)
        loc = LocationIn(latitude=round(lat + offset[0], 6), longitude=round(lng + offset[1], 6),
                         source=LocationSource.gps, accuracy_m=15)
    req = ComplaintCreate(title=title, description=desc, category_id=_cat(db, cat).id if cat else None,
                          location=loc, visibility=Visibility.public if public else Visibility.private,
                          safety_risk=safety)
    c, _ = svc.create_complaint(db, _p(db, handle), req, None)
    c.source_channel = SourceChannel.seed
    db.commit()
    return c


def _png() -> bytes:
    buf = io.BytesIO()
    Image.new("RGB", (64, 48), (90, 140, 90)).save(buf, format="PNG")
    return buf.getvalue()


def seed_complaints(db: Session) -> int:
    if db.scalar(select(Complaint.id).where(Complaint.source_channel == SourceChannel.seed).limit(1)):
        return 0
    roads_sup, admin = _p(db, "roads.supervisor"), _p(db, "muni.admin")
    created = 0

    c1 = _report(db, "resident1", "Large pothole near demo bus stop",
                 "Deep pothole on the main road near the bus stop, two-wheelers are swerving.", "roads.pothole",
                 "demo-w1", public=True, safety=True)
    svc.assign(db, roads_sup, c1, AssignRequest(officer_id=_officer(db, "roads.officer1").id), None,
               reassign=False, expected_version=None)
    svc.transition(db, _p(db, "roads.officer1"), c1, ComplaintStatus.in_progress, "Crew scheduled", None)
    created += 1

    _report(db, "resident2", "Garbage not picked up for days",
            "Garbage bins on our lane have not been collected and are overflowing.", "sanitation.garbage",
            "demo-w2")
    created += 1

    c3 = _report(db, "resident1", "Water pipe leaking at junction",
                 "Clean water has been leaking from a pipe at the junction since morning.", "water.leak", "demo-w3")
    svc.assign(db, _p(db, "water.supervisor"), c3, AssignRequest(officer_id=_officer(db, "water.officer").id),
               None, reassign=False, expected_version=None)
    officer = _p(db, "water.officer")
    svc.transition(db, officer, c3, ComplaintStatus.in_progress, None, None)
    evidence = media.upload(db, officer, _png(), "after_repair.png", MediaKind.resolution_evidence, c3.id)
    svc.resolve(db, officer, c3, "DEMO: Replaced the faulty pipe joint (fictional resolution).", [evidence.id],
                None)
    created += 1

    c4 = _report(db, "resident3", "Streetlight off on park road",
                 "The streetlight next to the park gate has been off for a week.", "lighting.streetlight",
                 "demo-w2")
    svc.assign(db, _p(db, "lighting.supervisor"), c4,
               AssignRequest(officer_id=_officer(db, "lighting.officer").id), None, reassign=False,
               expected_version=None)
    lo = _p(db, "lighting.officer")
    svc.transition(db, lo, c4, ComplaintStatus.in_progress, None, None)
    svc.resolve(db, lo, c4, "DEMO: Replaced lamp (fictional).", [], None)
    svc.submit_feedback(db, _p(db, "resident3"), c4, FeedbackCreate(rating=5, comment="Fixed quickly",
                                                                    confirm_resolved=True))
    created += 1

    # Unmapped: category without a routing rule, and a report with no category.
    _report(db, "resident2", "Stray cattle blocking lane",
            "A group of stray cattle sits in the lane every evening.", "other.stray_animals", "demo-w1")
    _report(db, "resident3", "Strange smell near the community hall",
            "There is an unusual smell near the community hall since yesterday.", None, "demo-w4")
    created += 2

    # Potential duplicates: two public pothole reports ~40 m apart.
    _report(db, "resident2", "Pothole outside the school gate",
            "There is a big pothole outside the school gate filling with water.", "roads.pothole", "demo-w2",
            public=True)
    _report(db, "resident3", "Big pothole near school",
            "Pothole near the school entrance, children have to walk around it.", "roads.pothole", "demo-w2",
            offset=(0.0003, 0.0002), public=True)
    created += 2

    # Overdue: blocked drain backdated 10 days (seed-only backdating, clearly labelled).
    c9 = _report(db, "resident1", "Blocked drain overflowing onto road",
                 "The drain is blocked and dirty water is overflowing onto the road.", "drainage.blocked",
                 "demo-w3")
    svc.assign(db, _p(db, "drainage.supervisor"), c9,
               AssignRequest(officer_id=_officer(db, "drainage.officer").id), None, reassign=False,
               expected_version=None)
    past = utcnow() - timedelta(days=10)
    c9.created_at = past
    from app.services import sla

    sla.apply_policy(db, c9, utcnow())
    c9.routing_explanation += " [demo: created_at backdated by seed to demonstrate overdue handling]"
    db.commit()
    created += 1

    # Rejected and withdrawn examples.
    c10 = _report(db, "resident2", "Neighbour's music is loud",
                  "My neighbour plays loud music at night which is not a civic infrastructure issue.", None,
                  "demo-w1")
    svc.transition(db, admin, c10, ComplaintStatus.rejected,
                   "Noise complaints are not handled by this demo platform; contact local police.", None)
    c11 = _report(db, "resident3", "Garbage pile on corner",
                  "Garbage pile on the corner near the shop.", "sanitation.garbage", "demo-w4")
    svc.withdraw(db, _p(db, "resident3"), c11, "Cleared by neighbours")
    created += 2
    db.commit()
    return created


def run(db: Session) -> dict:
    settings = get_settings()
    if settings.is_production:
        raise SystemExit("Refusing to seed demo data in production")
    seed_reference(db)
    n = seed_complaints(db)
    return {"complaints_created": n}
