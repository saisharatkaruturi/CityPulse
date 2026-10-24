"""Upload validation and authorised retrieval.

* Type is detected from content (magic bytes), not the client's filename or Content-Type.
* Only JPEG, PNG and WebP images are accepted. Images are re-encoded with Pillow, which
  removes EXIF (including GPS) metadata and rejects malformed files.
* No malware scanner is configured; rows are marked `not_scanned` (documented limitation).
"""

from __future__ import annotations

import io
import re
import uuid
from datetime import timedelta

from PIL import Image, UnidentifiedImageError
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.adapters.storage import get_storage
from app.core.config import get_settings
from app.core.errors import AppError, Forbidden, NotFound, ValidationFailed
from app.core.permissions import Principal, can_read, can_staff_read, can_staff_work
from app.core.time import utcnow
from app.domain.enums import MediaKind, ScanState, Visibility
from app.models import Complaint, ComplaintMedia

_SIGNATURES = [
    (b"\xff\xd8\xff", "image/jpeg", "jpg", "JPEG"),
    (b"\x89PNG\r\n\x1a\n", "image/png", "png", "PNG"),
]
MAX_PIXELS = 40_000_000


def sniff(data: bytes) -> tuple[str, str, str] | None:
    for sig, ctype, ext, fmt in _SIGNATURES:
        if data.startswith(sig):
            return ctype, ext, fmt
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp", "webp", "WEBP"
    return None


def sanitize_filename(name: str | None) -> str:
    base = re.split(r"[\\/]", name or "upload")[-1]
    base = re.sub(r"[^A-Za-z0-9._-]", "_", base).strip("._") or "upload"
    return base[:100]


def _strip_metadata(data: bytes, fmt: str) -> bytes:
    Image.MAX_IMAGE_PIXELS = MAX_PIXELS
    try:
        with Image.open(io.BytesIO(data)) as img:
            img.verify()
        with Image.open(io.BytesIO(data)) as img:
            if img.format != fmt:
                raise ValidationFailed("File content does not match its detected type", code="unsupported_media")
            clean = Image.new(img.mode, img.size)
            clean.putdata(list(img.getdata()))
            out = io.BytesIO()
            if fmt == "JPEG" and clean.mode not in ("RGB", "L"):
                clean = clean.convert("RGB")
            clean.save(out, format=fmt)
            return out.getvalue()
    except (UnidentifiedImageError, OSError, Image.DecompressionBombError, SyntaxError):
        raise ValidationFailed("File is not a valid image", code="unsupported_media") from None


def upload(db: Session, principal: Principal, data: bytes, filename: str | None, kind: MediaKind,
           complaint_id: uuid.UUID | None) -> ComplaintMedia:
    settings = get_settings()
    if len(data) == 0:
        raise ValidationFailed("Empty file", code="empty_file")
    if len(data) > settings.max_upload_bytes:
        raise AppError("File too large", code="file_too_large", status_code=413)
    detected = sniff(data)
    if detected is None:
        raise ValidationFailed("Only JPEG, PNG or WebP images are accepted", code="unsupported_media")
    ctype, ext, fmt = detected
    complaint = None
    if kind == MediaKind.resolution_evidence:
        if complaint_id is None:
            raise ValidationFailed("Evidence must target a complaint", code="complaint_required")
        complaint = db.get(Complaint, complaint_id)
        if complaint is None or not can_staff_work(principal, complaint):
            raise NotFound("Complaint not found")
    elif complaint_id is not None:
        complaint = db.get(Complaint, complaint_id)
        if complaint is None or complaint.reporter_id != principal.id:
            raise NotFound("Complaint not found")
    clean = _strip_metadata(data, fmt)
    key = get_storage().put(clean, ext)
    now = utcnow()
    # Evidence is uploaded unattached and claimed by the resolve call; report photos may attach directly.
    media = ComplaintMedia(
        complaint_id=complaint.id if complaint and kind == MediaKind.report_photo else None,
        uploader_id=principal.id, storage_key=key, original_filename=sanitize_filename(filename),
        content_type=ctype, size_bytes=len(clean), kind=kind, visibility=Visibility.private,
        scan_state=ScanState.not_scanned, exif_stripped=True, created_at=now,
        attached_at=now if complaint and kind == MediaKind.report_photo else None)
    db.add(media)
    try:
        db.commit()
    except Exception:
        db.rollback()
        get_storage().delete(key)
        raise
    return media


def get_for_download(db: Session, principal: Principal, media_id: uuid.UUID) -> tuple[ComplaintMedia, bytes]:
    m = db.get(ComplaintMedia, media_id)
    if m is None:
        raise NotFound("File not found")
    if m.complaint_id is None:
        if m.uploader_id != principal.id:
            raise NotFound("File not found")
    else:
        c = db.get(Complaint, m.complaint_id)
        if c is None or not can_read(principal, c):
            raise NotFound("File not found")
        # Residents see their own photos and resolution evidence on their own report; staff see all in scope.
        if c.reporter_id != principal.id and not can_staff_read(principal, c):
            raise Forbidden("Not permitted")
    if m.scan_state == ScanState.infected:
        raise Forbidden("File is quarantined", code="quarantined")
    return m, get_storage().get(m.storage_key)


def list_for_complaint(db: Session, principal: Principal, c: Complaint) -> list[ComplaintMedia]:
    if not can_read(principal, c):
        raise NotFound("Complaint not found")
    return list(db.scalars(select(ComplaintMedia).where(ComplaintMedia.complaint_id == c.id)
                           .order_by(ComplaintMedia.created_at)).all())


def cleanup_orphans(db: Session) -> int:
    cutoff = utcnow() - timedelta(hours=get_settings().orphan_media_max_age_hours)
    rows = db.scalars(select(ComplaintMedia).where(ComplaintMedia.complaint_id.is_(None),
                                                   ComplaintMedia.created_at < cutoff)).all()
    storage = get_storage()
    for m in rows:
        storage.delete(m.storage_key)
        db.delete(m)
    db.commit()
    return len(rows)
