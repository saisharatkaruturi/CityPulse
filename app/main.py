"""Application factory."""

from __future__ import annotations

import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response
from starlette.types import ASGIApp

from app.api.routers import admin, auth, catalog, complaints, media, notifications
from app.core.config import Settings, get_settings
from app.core.errors import error_body, install_error_handlers
from app.core.logging import configure_logging, request_id_var
from app.db.session import session_factory

logger = logging.getLogger("app.http")


class RequestContextMiddleware(BaseHTTPMiddleware):
    """Correlation ID, request-size limit, security headers, and access logging."""

    def __init__(self, app: ASGIApp, settings: Settings) -> None:
        super().__init__(app)
        self.settings = settings

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        incoming = request.headers.get("X-Request-ID", "")
        rid = incoming if 8 <= len(incoming) <= 64 and incoming.replace("-", "").isalnum() else uuid.uuid4().hex
        request.state.request_id = rid
        token = request_id_var.set(rid)
        start = time.perf_counter()
        try:
            limit = self.settings.max_upload_bytes + 64_000 if request.url.path == "/api/media" \
                else self.settings.max_request_bytes
            length = request.headers.get("content-length")
            if length is not None and (not length.isdigit() or int(length) > limit):
                response: Response = JSONResponse(
                    error_body(request, "payload_too_large", "Request body too large"), status_code=413)
            else:
                response = await call_next(request)
            response.headers["X-Request-ID"] = rid
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["Referrer-Policy"] = "no-referrer"
            logger.info("request", extra={"method": request.method, "path": request.url.path,
                                          "status": response.status_code,
                                          "ms": round((time.perf_counter() - start) * 1000, 1),
                                          "user_id": getattr(request.state, "user_id", None)})
            return response
        finally:
            request_id_var.reset(token)


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or get_settings()
    configure_logging("DEBUG" if settings.debug else "INFO")
    app = FastAPI(
        title=f"{settings.app_name} API",
        version="0.1.0",
        description="Backend for reporting local civic issues, finding municipal services, routing reports "
                    "to departments, and tracking transparent status updates. All demo data is fictional; "
                    "external integrations are disabled or SIMULATED unless configured.",
        debug=settings.debug,
        docs_url=None if settings.is_production else "/docs",
        redoc_url=None if settings.is_production else "/redoc",
        openapi_url=None if settings.is_production else "/openapi.json",
    )
    install_error_handlers(app)
    app.add_middleware(RequestContextMiddleware, settings=settings)
    if settings.cors_origins:
        app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origins, allow_credentials=False,
                           allow_methods=["GET", "POST", "PATCH", "PUT", "DELETE"],
                           allow_headers=["Authorization", "Content-Type", "Idempotency-Key", "If-Match",
                                          "X-Request-ID", "Accept-Language"],
                           expose_headers=["ETag", "X-Request-ID", "Location", "Idempotent-Replay"])

    for r in (auth.router, complaints.router, catalog.router, notifications.router, media.router, admin.router):
        app.include_router(r)

    @app.get("/health", tags=["ops"], summary="Liveness: the process is up")
    def health() -> dict:
        return {"status": "ok"}

    @app.get("/ready", tags=["ops"], summary="Readiness: the database is reachable",
             responses={503: {"description": "Database unavailable"}})
    def ready() -> JSONResponse:
        try:
            with session_factory()() as db:
                db.execute(text("SELECT 1"))
        except Exception:
            logger.exception("readiness_failed")
            return JSONResponse({"status": "unavailable"}, status_code=503)
        return JSONResponse({"status": "ready"})

    return app


app = create_app()
