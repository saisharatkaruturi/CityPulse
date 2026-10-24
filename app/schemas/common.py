from __future__ import annotations

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints


class Schema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class StrictInput(BaseModel):
    """Request bodies reject unknown fields, which blocks mass assignment of protected fields."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class Page[T](Schema):
    items: list[T]
    total: int
    page: int
    page_size: int


class ErrorDetail(BaseModel):
    field: str | None = None
    issue: str | None = None
    message: str | None = None


class ErrorBody(BaseModel):
    code: str
    message: str
    details: list[ErrorDetail] = Field(default_factory=list)
    request_id: str | None = None


class ErrorResponse(BaseModel):
    error: ErrorBody


Reason = Annotated[str, StringConstraints(strip_whitespace=True, min_length=3, max_length=1000)]
OptionalReason = Annotated[str, StringConstraints(strip_whitespace=True, max_length=1000)] | None

ERROR_RESPONSES: dict[int | str, dict] = {
    401: {"model": ErrorResponse, "description": "Missing, invalid, expired or revoked credentials"},
    403: {"model": ErrorResponse, "description": "Authenticated but not permitted"},
    404: {"model": ErrorResponse, "description": "Not found or not visible to the caller"},
    409: {"model": ErrorResponse, "description": "Conflict (invalid state, stale version, duplicate)"},
    422: {"model": ErrorResponse, "description": "Validation error with field-level details"},
    429: {"model": ErrorResponse, "description": "Rate limited"},
}
