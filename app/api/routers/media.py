from __future__ import annotations

import uuid
from typing import Annotated

from fastapi import APIRouter, File, Form, Request, UploadFile, status
from fastapi.responses import Response

from app.api.deps import DB, CurrentUser
from app.core import ratelimit
from app.core.config import get_settings
from app.core.errors import AppError
from app.domain.enums import MediaKind
from app.schemas.common import ERROR_RESPONSES
from app.schemas.complaints import MediaOut
from app.services import media

router = APIRouter(prefix="/api/media", tags=["media"], responses=ERROR_RESPONSES)


@router.post("", response_model=MediaOut, status_code=status.HTTP_201_CREATED,
             summary="Upload a photo (JPEG/PNG/WebP). EXIF metadata is stripped; storage is private.",
             description="Upload first, then pass the returned id in `media_ids` when creating a complaint "
                         "(or `evidence_media_ids` when resolving). Unattached uploads expire.")
async def upload(request: Request, principal: CurrentUser, db: DB, file: Annotated[UploadFile, File()],
                 kind: Annotated[MediaKind, Form()] = MediaKind.report_photo,
                 complaint_id: Annotated[uuid.UUID | None, Form()] = None) -> MediaOut:
    ratelimit.enforce(ratelimit.UPLOAD, request, key=f"user:{principal.id}")
    limit = get_settings().max_upload_bytes
    data = await file.read(limit + 1)
    if len(data) > limit:
        raise AppError("File too large", code="file_too_large", status_code=413)
    return MediaOut.model_validate(media.upload(db, principal, data, file.filename, kind, complaint_id))


@router.get("/{media_id}/content", summary="Download a file you are authorised to see",
            responses={200: {"content": {"image/*": {}}}})
def content(media_id: uuid.UUID, principal: CurrentUser, db: DB) -> Response:
    m, data = media.get_for_download(db, principal, media_id)
    return Response(content=data, media_type=m.content_type, headers={
        "Content-Disposition": f'inline; filename="{m.original_filename}"',
        "X-Content-Type-Options": "nosniff", "Cache-Control": "private, no-store"})
