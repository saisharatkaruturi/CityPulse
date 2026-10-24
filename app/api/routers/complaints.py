"""Complaint endpoints. Handlers only parse input, call the service, and shape output."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Header, Path, Query, Request, Response, status
from sqlalchemy import select

from app.api.deps import DB, CurrentUser, PageParams
from app.core import ratelimit
from app.core.errors import NotFound, ValidationFailed
from app.core.permissions import P, can_staff_read
from app.domain.enums import ComplaintStatus, Priority, Visibility
from app.models import Complaint
from app.schemas.common import ERROR_RESPONSES, Page
from app.schemas.complaints import (
    AssignRequest,
    CloseRequest,
    CommentCreate,
    CommentOut,
    ComplaintCreate,
    ComplaintListItem,
    ComplaintResidentOut,
    ComplaintStaffOut,
    DuplicateCandidate,
    FeedbackCreate,
    FeedbackOut,
    MediaOut,
    MergeRequest,
    NoteCreate,
    NoteOut,
    PublicComplaintSummary,
    ReassignRequest,
    ReopenRequest,
    ResidentComplaintUpdate,
    ResolveRequest,
    StaffComplaintUpdate,
    SupportOut,
    TransitionRequest,
    WithdrawRequest,
)
from app.services import complaints as svc
from app.services import duplicates, media, views

router = APIRouter(prefix="/api/complaints", tags=["complaints"], responses=ERROR_RESPONSES)

Detail = ComplaintStaffOut | ComplaintResidentOut
IfMatch = Annotated[str | None, Header(alias="If-Match", description="Expected complaint version")]
IdemKey = Annotated[str | None, Header(alias="Idempotency-Key", min_length=8, max_length=100,
                                       pattern=r"^[A-Za-z0-9_\-:.]+$")]


def _version(if_match: str | None) -> int | None:
    if if_match is None:
        return None
    try:
        return int(if_match.strip().strip('W/').strip('"'))
    except ValueError:
        raise ValidationFailed("If-Match must be the integer complaint version", code="invalid_if_match") from None


def _detail(db: DB, principal: CurrentUser, c: Complaint, response: Response | None = None) -> Detail:
    if response is not None:
        response.headers["ETag"] = f'"{c.version}"'
    return views.detail_view(db, principal, c)


@router.post("", response_model=Detail, status_code=status.HTTP_201_CREATED,
             summary="Submit a report. Returns the tracking reference only after it is saved.",
             description="Send an `Idempotency-Key` header to make retries safe. Reusing a key with a "
                         "different body is rejected with `idempotency_key_reuse`.")
def create(req: ComplaintCreate, request: Request, response: Response, principal: CurrentUser, db: DB,
           idempotency_key: IdemKey = None) -> Detail:
    ratelimit.enforce(ratelimit.COMPLAINT_CREATE, request, key=f"user:{principal.id}")
    c, replayed = svc.create_complaint(db, principal, req, idempotency_key)
    if replayed:
        response.status_code = status.HTTP_200_OK
        response.headers["Idempotent-Replay"] = "true"
    response.headers["Location"] = f"/api/complaints/{c.id}"
    return _detail(db, principal, c, response)


@router.get("", response_model=Page[ComplaintListItem],
            summary="List complaints visible to the caller (own reports + staff scope)")
def list_(principal: CurrentUser, db: DB, pg: PageParams,
          status_: Annotated[list[ComplaintStatus] | None, Query(alias="status")] = None,
          category_id: uuid.UUID | None = None, department_id: uuid.UUID | None = None,
          assigned_officer_id: uuid.UUID | None = None, priority: Priority | None = None,
          ward_id: uuid.UUID | None = None, created_from: datetime | None = None,
          created_to: datetime | None = None, q: Annotated[str | None, Query(max_length=100)] = None,
          overdue: bool | None = None, unassigned: bool | None = None, mine: bool = False,
          assigned_to_me: bool = False,
          sort: Annotated[str, Query(pattern="^-?(created_at|updated_at|priority|due_at)$")] = "-created_at",
          ) -> Page[ComplaintListItem]:
    for dt in (created_from, created_to):
        if dt is not None and dt.tzinfo is None:
            raise ValidationFailed("Datetimes must include a timezone", code="naive_datetime")
    f = svc.ComplaintFilters(status=status_, category_id=category_id, department_id=department_id,
                             assigned_officer_id=assigned_officer_id, priority=priority, ward_id=ward_id,
                             created_from=created_from, created_to=created_to, q=q, overdue=overdue, mine=mine,
                             unassigned=unassigned, assigned_to_me=assigned_to_me, sort=sort)
    rows, total = svc.list_complaints(db, principal, f, pg.offset, pg.page_size)
    items = []
    for c in rows:
        item = ComplaintListItem.model_validate(c)
        if not can_staff_read(principal, c):
            item.assigned_officer_id = None
        items.append(item)
    return Page[ComplaintListItem](items=items, total=total, page=pg.page, page_size=pg.page_size)


@router.get("/nearby", response_model=list[PublicComplaintSummary],
            summary="Public, privacy-filtered open issues near a point (approximate coordinates only)")
def nearby(request: Request, principal: CurrentUser, db: DB,
           lat: Annotated[float, Query(ge=-90, le=90)], lng: Annotated[float, Query(ge=-180, le=180)],
           radius_m: Annotated[int, Query(ge=10, le=2000)] = 300, category_id: uuid.UUID | None = None,
           limit: Annotated[int, Query(ge=1, le=50)] = 20) -> list[PublicComplaintSummary]:
    ratelimit.enforce(ratelimit.SEARCH, request, key=f"user:{principal.id}")
    return [views.public_summary(db, c, d) for c, d in duplicates.nearby_public(db, lat, lng, radius_m,
                                                                                 category_id, limit)]


@router.get("/public/{reference}", response_model=PublicComplaintSummary,
            summary="Public summary of a report that was submitted as public")
def public_by_reference(reference: Annotated[str, Path(max_length=20)], principal: CurrentUser,
                        db: DB) -> PublicComplaintSummary:
    c = db.scalar(select(Complaint).where(Complaint.reference == reference.upper()))
    if c is None or c.visibility != Visibility.public:
        raise NotFound("Complaint not found")
    return views.public_summary(db, c)


@router.get("/{complaint_id}", response_model=Detail,
            summary="Complaint detail with real status timeline. Staff in scope see routing/SLA fields.")
def get(complaint_id: uuid.UUID, response: Response, principal: CurrentUser, db: DB) -> Detail:
    return _detail(db, principal, svc.get_visible(db, principal, complaint_id), response)


@router.patch("/{complaint_id}", response_model=Detail,
              summary="Reporter edits title/description/visibility before pickup; staff correct category, "
                      "priority or visibility with a reason",
              description="Body must match ONE of the schemas: ResidentComplaintUpdate (reporter) or "
                          "StaffComplaintUpdate (staff, requires `reason`). Unknown fields are rejected.")
def patch(complaint_id: uuid.UUID, body: StaffComplaintUpdate | ResidentComplaintUpdate, response: Response,
          principal: CurrentUser, db: DB, if_match: IfMatch = None) -> Detail:
    c = svc.get_visible(db, principal, complaint_id)
    if isinstance(body, StaffComplaintUpdate):
        c = svc.staff_update(db, principal, c, body, _version(if_match))
    else:
        c = svc.resident_update(db, principal, c, body, _version(if_match))
    return _detail(db, principal, c, response)


@router.post("/{complaint_id}/transitions", response_model=Detail,
             summary="Apply a validated workflow transition (under_review, in_progress, awaiting_resident, "
                     "on_hold, rejected, withdrawn)")
def transition(complaint_id: uuid.UUID, req: TransitionRequest, response: Response, principal: CurrentUser,
               db: DB, if_match: IfMatch = None) -> Detail:
    c = svc.get_visible(db, principal, complaint_id)
    return _detail(db, principal, svc.transition(db, principal, c, req.to_status, req.reason, _version(if_match)),
                   response)


@router.post("/{complaint_id}/withdraw", response_model=Detail, summary="Reporter withdraws the report")
def withdraw(complaint_id: uuid.UUID, req: WithdrawRequest, response: Response, principal: CurrentUser,
             db: DB) -> Detail:
    c = svc.get_visible(db, principal, complaint_id)
    return _detail(db, principal, svc.withdraw(db, principal, c, req.reason), response)


@router.post("/{complaint_id}/assign", response_model=Detail,
             summary="Supervisor/admin assigns to an officer, team or department queue")
def assign(complaint_id: uuid.UUID, req: AssignRequest, response: Response, principal: CurrentUser, db: DB,
           if_match: IfMatch = None) -> Detail:
    c = svc.get_visible(db, principal, complaint_id)
    return _detail(db, principal, svc.assign(db, principal, c, req, None, reassign=False,
                                             expected_version=_version(if_match)), response)


@router.post("/{complaint_id}/reassign", response_model=Detail, summary="Reassign with a mandatory reason")
def reassign(complaint_id: uuid.UUID, req: ReassignRequest, response: Response, principal: CurrentUser,
             db: DB, if_match: IfMatch = None) -> Detail:
    c = svc.get_visible(db, principal, complaint_id)
    target = AssignRequest(officer_id=req.officer_id, team_id=req.team_id, department_id=req.department_id)
    return _detail(db, principal, svc.assign(db, principal, c, target, req.reason, reassign=True,
                                             expected_version=_version(if_match)), response)


@router.post("/{complaint_id}/resolve", response_model=Detail,
             summary="Staff record resolution notes and evidence; status becomes resolved (not verified)")
def resolve(complaint_id: uuid.UUID, req: ResolveRequest, response: Response, principal: CurrentUser, db: DB,
            if_match: IfMatch = None) -> Detail:
    c = svc.get_visible(db, principal, complaint_id)
    return _detail(db, principal, svc.resolve(db, principal, c, req.resolution_notes, req.evidence_media_ids,
                                              _version(if_match)), response)


@router.post("/{complaint_id}/close", response_model=Detail,
             summary="Close a resolved complaint (reporter confirmation or staff)")
def close(complaint_id: uuid.UUID, req: CloseRequest, response: Response, principal: CurrentUser,
          db: DB) -> Detail:
    c = svc.get_visible(db, principal, complaint_id)
    return _detail(db, principal, svc.close(db, principal, c, req.reason), response)


@router.post("/{complaint_id}/reopen", response_model=Detail,
             summary="Reporter (within the reopen window) or staff reopen a resolved/closed complaint")
def reopen(complaint_id: uuid.UUID, req: ReopenRequest, response: Response, principal: CurrentUser,
           db: DB) -> Detail:
    c = svc.get_visible(db, principal, complaint_id)
    return _detail(db, principal, svc.reopen(db, principal, c, req.reason), response)


@router.get("/{complaint_id}/comments", response_model=list[CommentOut])
def comments(complaint_id: uuid.UUID, principal: CurrentUser, db: DB) -> list[CommentOut]:
    c = svc.get_visible(db, principal, complaint_id)
    return [CommentOut.model_validate(x) for x in svc.list_comments(db, principal, c)]


@router.post("/{complaint_id}/comments", response_model=CommentOut, status_code=status.HTTP_201_CREATED,
             summary="Resident-visible comment. Staff may set request_information to ask the resident.")
def add_comment(complaint_id: uuid.UUID, req: CommentCreate, principal: CurrentUser, db: DB) -> CommentOut:
    c = svc.get_visible(db, principal, complaint_id)
    return CommentOut.model_validate(svc.add_comment(db, principal, c, req.body, req.request_information))


@router.get("/{complaint_id}/notes", response_model=list[NoteOut], summary="Staff-only internal notes")
def notes(complaint_id: uuid.UUID, principal: CurrentUser, db: DB) -> list[NoteOut]:
    c = svc.get_visible(db, principal, complaint_id)
    return [NoteOut.model_validate(n) for n in svc.list_notes(db, principal, c)]


@router.post("/{complaint_id}/notes", response_model=NoteOut, status_code=status.HTTP_201_CREATED,
             summary="Add a staff-only internal note")
def add_note(complaint_id: uuid.UUID, req: NoteCreate, principal: CurrentUser, db: DB) -> NoteOut:
    c = svc.get_visible(db, principal, complaint_id)
    return NoteOut.model_validate(svc.add_note(db, principal, c, req.body))


@router.get("/{complaint_id}/media", response_model=list[MediaOut])
def list_media(complaint_id: uuid.UUID, principal: CurrentUser, db: DB) -> list[MediaOut]:
    c = svc.get_visible(db, principal, complaint_id)
    return [MediaOut.model_validate(m) for m in media.list_for_complaint(db, principal, c)]


@router.get("/{complaint_id}/possible-duplicates", response_model=list[DuplicateCandidate],
            summary="Bounded duplicate candidates (same/related category, nearby, recent, open)")
def possible_duplicates(complaint_id: uuid.UUID, principal: CurrentUser, db: DB) -> list[DuplicateCandidate]:
    c = svc.get_visible(db, principal, complaint_id)
    return duplicates.find_candidates(db, principal, c)


@router.post("/{complaint_id}/merge", response_model=Detail,
             summary="Merge this complaint into a verified duplicate (staff, reason required)")
def merge(complaint_id: uuid.UUID, req: MergeRequest, response: Response, principal: CurrentUser,
          db: DB) -> Detail:
    principal.require(P.complaint_merge)
    c = svc.get_visible(db, principal, complaint_id)
    return _detail(db, principal, svc.merge(db, principal, c, req.target_id, req.reason), response)


@router.post("/{complaint_id}/feedback", response_model=FeedbackOut, status_code=status.HTTP_201_CREATED,
             summary="Reporter rates the outcome (1-5) once resolved; confirm_resolved closes the case")
def feedback(complaint_id: uuid.UUID, req: FeedbackCreate, principal: CurrentUser, db: DB) -> FeedbackOut:
    c = svc.get_visible(db, principal, complaint_id)
    return FeedbackOut.model_validate(svc.submit_feedback(db, principal, c, req))


@router.post("/{complaint_id}/support", response_model=SupportOut, status_code=status.HTTP_201_CREATED,
             summary="Add your support to a public open report (once per account; supporters stay private)")
def support(complaint_id: uuid.UUID, principal: CurrentUser, db: DB) -> SupportOut:
    return SupportOut(complaint_id=complaint_id, support_count=svc.add_support(db, principal, complaint_id),
                      supported=True)


@router.delete("/{complaint_id}/support", response_model=SupportOut)
def unsupport(complaint_id: uuid.UUID, principal: CurrentUser, db: DB) -> SupportOut:
    return SupportOut(complaint_id=complaint_id, support_count=svc.remove_support(db, principal, complaint_id),
                      supported=False)
