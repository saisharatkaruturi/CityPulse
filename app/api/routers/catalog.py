"""Public-ish directory endpoints: services, categories, wards, routing suggestion, announcements."""

from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, Header, Query, Request
from sqlalchemy import or_, select

from app.api.deps import DB, MaybeUser
from app.core import ratelimit
from app.core.time import utcnow
from app.domain.enums import AnnouncementState, ServiceType
from app.models import Announcement, Category, Department, Service, Ward
from app.schemas.catalog import (
    AnnouncementOut,
    CategoryOut,
    CategorySuggestionOut,
    RoutingSuggestRequest,
    RoutingSuggestResponse,
    ServiceOut,
    ServiceSearchResponse,
    ServiceSearchResult,
    WardOut,
)
from app.schemas.common import ERROR_RESPONSES
from app.services import intelligence, routing

router = APIRouter(prefix="/api", responses=ERROR_RESPONSES)

EMERGENCY_NOTICE = ("This service does not dispatch emergency help. If anyone is in immediate danger, "
                    "contact your local emergency number (112 in India) first.")
NO_MATCH_GUIDANCE = ("No matching service was found. You can still submit a report without a category; "
                     "it will be reviewed manually and sent to the right department.")


def service_out(s: Service) -> ServiceOut:
    return ServiceOut(
        id=s.id, code=s.code, name=s.name, summary=s.summary, instructions=s.instructions,
        service_type=s.service_type, state=s.state, public_contact=s.public_contact,
        operating_hours=s.operating_hours, eligibility=s.eligibility, owner_department_id=s.owner_department_id,
        department_ids=[d.id for d in s.departments], category_ids=[c.id for c in s.categories],
        last_reviewed_at=s.last_reviewed_at, is_demo=s.is_demo)


def category_out(c: Category, lang: str | None) -> CategoryOut:
    out = CategoryOut.model_validate(c)
    if lang and lang != "en" and (c.labels_i18n or {}).get(lang):
        out.label = c.labels_i18n[lang]
    return out


def _lang(accept_language: str | None) -> str | None:
    if not accept_language:
        return None
    return accept_language.split(",")[0].split(";")[0].split("-")[0].strip().lower() or None


@router.get("/services", response_model=ServiceSearchResponse, tags=["services"],
            summary="Search or browse the service directory (public; deterministic keyword + taxonomy matching)")
def search_services(request: Request, principal: MaybeUser, db: DB,
                    q: Annotated[str | None, Query(max_length=200)] = None,
                    category_id: uuid.UUID | None = None, service_type: ServiceType | None = None,
                    limit: Annotated[int, Query(ge=1, le=50)] = 10,
                    accept_language: Annotated[str | None, Header()] = None) -> ServiceSearchResponse:
    ratelimit.enforce(ratelimit.SEARCH, request, key=f"user:{principal.id}" if principal else None)
    matches = intelligence.search_services(db, q.strip() if q else None, category_id,
                                           service_type.value if service_type else None, limit)
    lang = _lang(accept_language)
    items = [ServiceSearchResult(service=service_out(m.service), score=m.score, matched_on=m.matched_on,
                                 matched_category=category_out(m.matched_category, lang)
                                 if m.matched_category else None)
             for m in matches]
    return ServiceSearchResponse(items=items, total=len(items), no_match=not items,
                                 guidance=NO_MATCH_GUIDANCE if not items else None,
                                 used_provider="keyword")


@router.get("/categories", response_model=list[CategoryOut], tags=["categories"],
            summary="Active categories (public). Labels are localised via Accept-Language when a translation exists.")
def categories(principal: MaybeUser, db: DB,
               accept_language: Annotated[str | None, Header()] = None,
               include_inactive: bool = False) -> list[CategoryOut]:
    q = select(Category).order_by(Category.code)
    if not (include_inactive and principal is not None and principal.is_staff):
        q = q.where(Category.is_active.is_(True))
    lang = _lang(accept_language)
    return [category_out(c, lang) for c in db.scalars(q).all()]


@router.get("/wards", response_model=list[WardOut], tags=["wards"], summary="Supported areas (public)")
def wards(principal: MaybeUser, db: DB) -> list[WardOut]:
    rows = db.scalars(select(Ward).where(Ward.is_active.is_(True)).order_by(Ward.code)).all()
    return [WardOut(id=w.id, code=w.code, name=w.name, is_active=w.is_active, has_boundary=bool(w.boundary),
                    provenance=w.provenance, is_demo=w.is_demo) for w in rows]


@router.post("/routing/suggest", response_model=RoutingSuggestResponse, tags=["routing"],
             summary="Preview the category and department for a description (public). No data is saved.")
def suggest(req: RoutingSuggestRequest, request: Request, principal: MaybeUser,
            db: DB) -> RoutingSuggestResponse:
    ratelimit.enforce(ratelimit.AI_SUGGEST, request, key=f"user:{principal.id}" if principal else None)
    alternatives: list[CategorySuggestionOut] = []
    best = None
    classifier, simulated, needs_review = "none", False, False
    if req.category_id:
        category = db.get(Category, req.category_id)
        if category is None or not category.is_active:
            category = None
            needs_review = True
    elif req.description:
        outcome = intelligence.suggest_category(db, req.description)
        classifier, simulated = outcome.provider, outcome.simulated
        category = outcome.best.category if outcome.accepted and outcome.best else None
        needs_review = not outcome.accepted
        if outcome.best:
            best = CategorySuggestionOut(category_id=outcome.best.category.id,
                                         category_code=outcome.best.category.code,
                                         label=outcome.best.category.label, confidence=outcome.best.confidence)
        alternatives = [CategorySuggestionOut(category_id=s.category.id, category_code=s.category.code,
                                              label=s.category.label, confidence=s.confidence)
                        for s in outcome.alternatives]
    else:
        category, needs_review = None, True
    if category is not None and best is None:
        best = CategorySuggestionOut(category_id=category.id, category_code=category.code, label=category.label,
                                     confidence=1.0)
    jurisdiction = routing.resolve_jurisdiction(db, req.ward_id, req.latitude, req.longitude)
    decision = routing.decide(db, category, jurisdiction, utcnow())
    dept_id = decision.department_id
    if dept_id is None:
        fb = routing.fallback_department(db)
        dept_id = fb.id if fb else None
    dept = db.get(Department, dept_id) if dept_id else None
    return RoutingSuggestResponse(
        category=best, alternatives=alternatives, needs_manual_review=needs_review or decision.outcome.value
        == "fallback", classifier=classifier, classifier_simulated=simulated, ward_id=jurisdiction.ward_id,
        outcome=decision.outcome.value, department_id=dept_id, department_name=dept.name if dept else None,
        reason_code=decision.reason_code, explanation=decision.explanation, emergency_notice=EMERGENCY_NOTICE)


@router.get("/announcements", response_model=list[AnnouncementOut], tags=["announcements"],
            summary="Published, unexpired announcements (public; optionally for one ward)")
def announcements(principal: MaybeUser, db: DB, ward_id: uuid.UUID | None = None) -> list[AnnouncementOut]:
    now = utcnow()
    q = select(Announcement).where(Announcement.state == AnnouncementState.published,
                                   or_(Announcement.publish_until.is_(None), Announcement.publish_until > now))
    if ward_id:
        q = q.where(or_(Announcement.ward_id.is_(None), Announcement.ward_id == ward_id))
    return [AnnouncementOut.model_validate(a) for a in db.scalars(q.order_by(Announcement.publish_from.desc()))]
