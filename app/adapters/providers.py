"""Optional external providers: email/SMS delivery, municipal case system, geocoding.

Every provider here is either disabled or a clearly SIMULATED mock. No real message is sent and
no real municipality is contacted by this codebase. Real adapters implement the same Protocols.
"""

from __future__ import annotations

import secrets
from dataclasses import dataclass
from typing import Protocol


class ProviderUnavailable(Exception):
    """Transient failure (timeout, 5xx). Safe to retry."""


class ProviderRejected(Exception):
    """Permanent rejection. Do not retry."""


# --- Message delivery -------------------------------------------------------------------------

@dataclass(frozen=True)
class DeliveryReceipt:
    provider_reference: str
    simulated: bool


class MessageProvider(Protocol):
    name: str

    def send(self, to: str, subject: str, body: str) -> DeliveryReceipt: ...


class MockMessageProvider:
    """SIMULATED: records the call in memory; nothing leaves the process."""

    def __init__(self, name: str) -> None:
        self.name = name
        self.sent: list[tuple[str, str, str]] = []
        self.fail_next: int = 0

    def send(self, to: str, subject: str, body: str) -> DeliveryReceipt:
        if self.fail_next > 0:
            self.fail_next -= 1
            raise ProviderUnavailable("simulated provider outage")
        self.sent.append((to, subject, body))
        return DeliveryReceipt(f"SIMULATED-{self.name}-{secrets.token_hex(6)}", simulated=True)


# --- External municipal case management ----------------------------------------------------------

@dataclass(frozen=True)
class ExternalCaseAck:
    external_case_id: str
    simulated: bool


class MunicipalCaseProvider(Protocol):
    name: str

    def submit_case(self, reference: str, category_code: str | None, department_code: str | None,
                    summary: str) -> ExternalCaseAck: ...


class MockMunicipalProvider:
    """SIMULATED municipal system. IDs are prefixed SIMULATED- and flagged as such in the DB."""

    name = "mock-municipal"

    def __init__(self) -> None:
        self.mode: str = "ok"  # ok | timeout | reject

    def submit_case(self, reference: str, category_code: str | None, department_code: str | None,
                    summary: str) -> ExternalCaseAck:
        if self.mode == "timeout":
            raise ProviderUnavailable("simulated timeout")
        if self.mode == "reject":
            raise ProviderRejected("simulated rejection: unsupported category")
        return ExternalCaseAck(f"SIMULATED-{reference}", simulated=True)


# --- Geocoding --------------------------------------------------------------------------------

class GeocodingProvider(Protocol):
    name: str

    def reverse(self, lat: float, lng: float) -> str | None: ...


class MockGeocoder:
    """SIMULATED reverse geocoder. Output is a display hint only, never proof of jurisdiction."""

    name = "mock-geocoder"

    def __init__(self) -> None:
        self.mode = "ok"

    def reverse(self, lat: float, lng: float) -> str | None:
        if self.mode == "timeout":
            raise ProviderUnavailable("simulated timeout")
        if self.mode == "empty":
            return None
        return f"Simulated address near ({lat:.3f}, {lng:.3f})"


@dataclass
class ProviderRegistry:
    email: MessageProvider | None
    sms: MessageProvider | None
    municipal: MunicipalCaseProvider | None
    geocoder: GeocodingProvider | None


_registry: ProviderRegistry | None = None


def get_providers() -> ProviderRegistry:
    global _registry
    if _registry is None:
        from app.core.config import get_settings

        s = get_settings()
        _registry = ProviderRegistry(
            email=MockMessageProvider("email") if s.email_provider == "mock" else None,
            sms=MockMessageProvider("sms") if s.sms_provider == "mock" else None,
            municipal=MockMunicipalProvider() if s.municipal_integration == "mock" else None,
            geocoder=MockGeocoder() if s.geocoding_provider == "mock" else None,
        )
    return _registry


def set_providers(registry: ProviderRegistry | None) -> None:
    global _registry
    _registry = registry
