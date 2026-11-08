"""Typed central configuration.

All settings come from environment variables (optionally a `.env` file). Startup validation
fails fast with a message that names the offending setting but never echoes secret values.
"""

from __future__ import annotations

from enum import StrEnum
from functools import lru_cache
from typing import Annotated, Literal

from pydantic import AliasChoices, Field, ValidationError, field_validator, model_validator
from pydantic_settings import BaseSettings, NoDecode, SettingsConfigDict

DEFAULT_DEV_SECRET = "dev-only-insecure-secret-change-me-0123456789"


class Environment(StrEnum):
    development = "development"
    test = "test"
    production = "production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Your City, Your Services"
    environment: Environment = Environment.development
    debug: bool = False

    # POSTGRES_URL is what the Vercel Supabase/Postgres integrations inject (pooled connection).
    database_url: str = Field(default="sqlite:///./var/ycys.db",
                              validation_alias=AliasChoices("DATABASE_URL", "POSTGRES_URL", "database_url"))
    sql_echo: bool = False

    # Auth
    jwt_secret: str = DEFAULT_DEV_SECRET
    jwt_issuer: str = "ycys-backend"
    jwt_audience: str = "ycys-clients"
    access_token_ttl_minutes: int = Field(default=60, ge=5, le=24 * 60)
    allow_self_registration: bool = True

    # HTTP limits
    cors_origins: Annotated[list[str], NoDecode] = Field(default_factory=list)
    max_request_bytes: int = 1_000_000
    max_upload_bytes: int = 4_000_000  # under Vercel's 4.5 MB request cap
    default_page_size: int = 20
    max_page_size: int = 100
    rate_limit_enabled: bool = True

    # Built web UI (web/dist). Served at / when the folder exists; the API never depends on it.
    web_dist_dir: str = "./web/dist"

    # Media
    media_root: str = "./var/media"
    # "auto" picks Vercel Blob when BLOB_READ_WRITE_TOKEN is set, otherwise the local filesystem.
    storage_backend: Literal["auto", "local", "vercel_blob"] = "auto"
    blob_read_write_token: str = ""
    blob_access: Literal["private", "public"] = "private"  # must match the Blob store's access level
    orphan_media_max_age_hours: int = 24

    # Workflow policy (illustrative defaults, not official municipal policy)
    reopen_window_days: int = 14
    auto_close_resolved_after_days: int = 7
    require_resolution_notes: bool = True
    sla_reminder_lead_fraction: float = Field(default=0.2, gt=0, lt=1)
    escalation_max_level: int = 2

    # Duplicate detection
    duplicate_radius_m: int = Field(default=150, ge=10, le=2000)
    duplicate_window_days: int = Field(default=30, ge=1, le=365)
    duplicate_max_results: int = Field(default=10, ge=1, le=50)
    nearby_max_radius_m: int = 2000
    public_coordinate_decimals: int = Field(default=3, ge=2, le=4)

    # Optional integrations; all default to disabled
    ai_provider: Literal["keyword", "mock", "disabled"] = "keyword"
    ai_confidence_threshold: float = Field(default=0.6, ge=0, le=1)
    ai_timeout_seconds: float = 5.0
    email_provider: Literal["disabled", "mock"] = "disabled"
    sms_provider: Literal["disabled", "mock"] = "disabled"
    municipal_integration: Literal["disabled", "mock"] = "disabled"
    geocoding_provider: Literal["disabled", "mock"] = "disabled"
    external_call_timeout_seconds: float = 5.0

    # Background jobs
    outbox_max_attempts: int = Field(default=5, ge=1, le=20)
    outbox_base_backoff_seconds: int = 30
    worker_interval_seconds: int = 30
    # Shared secret for the scheduled worker endpoint (Vercel Cron sends it as a Bearer token).
    cron_secret: str = ""

    # Demo
    demo_password: str = "demo-password-123"
    # Demo mode shows the DEMO badge and offers the fictional seed accounts on the sign-in page.
    # Unset means: on outside production, off in production. Set DEMO_MODE=true to run a public demo.
    demo_mode: bool | None = None

    @field_validator("cors_origins", mode="before")
    @classmethod
    def _split_origins(cls, v: object) -> object:
        if isinstance(v, str):
            return [o.strip() for o in v.split(",") if o.strip()]
        return v

    @field_validator("database_url", mode="after")
    @classmethod
    def _normalise_db_url(cls, v: str) -> str:
        # Hosted Postgres providers (Neon, Vercel) hand out postgres:// URLs; use the psycopg 3 driver.
        for prefix in ("postgres://", "postgresql://"):
            if v.startswith(prefix):
                v = "postgresql+psycopg://" + v[len(prefix):]
                break
        if v.startswith("postgresql") and "?" in v:
            # Supabase adds a non-libpq "supa=" marker that psycopg rejects.
            from urllib.parse import parse_qsl, urlencode

            base, query = v.split("?", 1)
            kept = [(k, val) for k, val in parse_qsl(query, keep_blank_values=True) if k != "supa"]
            v = base + ("?" + urlencode(kept) if kept else "")
        return v

    @model_validator(mode="after")
    def _validate_for_environment(self) -> Settings:
        if self.environment == Environment.production:
            problems = []
            if self.jwt_secret == DEFAULT_DEV_SECRET or len(self.jwt_secret) < 32:
                problems.append("JWT_SECRET must be set to a random value of at least 32 characters")
            if self.debug:
                problems.append("DEBUG must be false in production")
            if self.storage_backend == "vercel_blob" and not self.blob_read_write_token:
                problems.append("BLOB_READ_WRITE_TOKEN must be set when STORAGE_BACKEND=vercel_blob")
            if "*" in self.cors_origins:
                problems.append("CORS_ORIGINS must list explicit origins in production")
            if problems:
                raise ValueError("Invalid production configuration: " + "; ".join(problems))
        return self

    @property
    def is_production(self) -> bool:
        return self.environment == Environment.production

    @property
    def effective_storage_backend(self) -> str:
        if self.storage_backend == "auto":
            return "vercel_blob" if self.blob_read_write_token else "local"
        return self.storage_backend

    @property
    def demo_mode_enabled(self) -> bool:
        return self.demo_mode if self.demo_mode is not None else not self.is_production


class ConfigurationError(RuntimeError):
    """Startup configuration error whose message never includes setting values."""


def load_settings(**overrides: object) -> Settings:
    try:
        return Settings(**overrides)  # type: ignore[arg-type]
    except ValidationError as exc:
        problems = []
        for err in exc.errors(include_input=False, include_url=False):
            field = ".".join(str(p) for p in err.get("loc", ())) or "settings"
            problems.append(f"{field}: {err.get('msg', 'invalid')}")
        raise ConfigurationError("Invalid configuration: " + "; ".join(problems)) from None


@lru_cache
def get_settings() -> Settings:
    return load_settings()
