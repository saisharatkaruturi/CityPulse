"""Controlled vocabularies shared by the database, API, tests, and seed data."""

from enum import StrEnum


class Role(StrEnum):
    resident = "resident"
    field_officer = "field_officer"
    supervisor = "supervisor"
    municipal_admin = "municipal_admin"
    system_admin = "system_admin"
    auditor = "auditor"


STAFF_ROLES = frozenset({Role.field_officer, Role.supervisor, Role.municipal_admin, Role.system_admin,
                         Role.auditor})


class ComplaintStatus(StrEnum):
    submitted = "submitted"
    under_review = "under_review"
    assigned = "assigned"
    in_progress = "in_progress"
    awaiting_resident = "awaiting_resident"
    on_hold = "on_hold"
    resolved = "resolved"
    closed = "closed"
    rejected = "rejected"
    withdrawn = "withdrawn"
    reopened = "reopened"


OPEN_STATUSES = frozenset({
    ComplaintStatus.submitted, ComplaintStatus.under_review, ComplaintStatus.assigned,
    ComplaintStatus.in_progress, ComplaintStatus.awaiting_resident, ComplaintStatus.on_hold,
    ComplaintStatus.reopened,
})
TERMINAL_STATUSES = frozenset({ComplaintStatus.closed, ComplaintStatus.rejected, ComplaintStatus.withdrawn})
SLA_PAUSED_STATUSES = frozenset({ComplaintStatus.on_hold, ComplaintStatus.awaiting_resident})


class Priority(StrEnum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


PRIORITY_ORDER = {Priority.low: 0, Priority.medium: 1, Priority.high: 2, Priority.critical: 3}


class Visibility(StrEnum):
    private = "private"
    public = "public"


class SourceChannel(StrEnum):
    api = "api"
    web = "web"
    mobile = "mobile"
    staff_entry = "staff_entry"
    seed = "seed"


class LocationSource(StrEnum):
    gps = "gps"
    manual_pin = "manual_pin"
    ward_selection = "ward_selection"
    address = "address"
    none = "none"


class RoutingOutcome(StrEnum):
    routed = "routed"
    fallback = "fallback"


class ServiceType(StrEnum):
    information = "information"
    complaint = "complaint"


class PublicationState(StrEnum):
    draft = "draft"
    published = "published"
    unavailable = "unavailable"
    unpublished = "unpublished"


class MediaKind(StrEnum):
    report_photo = "report_photo"
    resolution_evidence = "resolution_evidence"


class ScanState(StrEnum):
    not_scanned = "not_scanned"
    clean = "clean"
    infected = "infected"


class NotificationChannel(StrEnum):
    in_app = "in_app"
    email = "email"
    sms = "sms"


class DeliveryState(StrEnum):
    pending = "pending"
    sent = "sent"
    failed = "failed"
    skipped = "skipped"


class OutboxState(StrEnum):
    pending = "pending"
    processing = "processing"
    done = "done"
    failed = "failed"


class LinkType(StrEnum):
    duplicate_of = "duplicate_of"
    related = "related"


class AnnouncementState(StrEnum):
    draft = "draft"
    published = "published"
    expired = "expired"


class ExternalSyncState(StrEnum):
    not_configured = "not_configured"
    pending = "pending"
    confirmed = "confirmed"
    rejected = "rejected"
    failed = "failed"


class ActorKind(StrEnum):
    human = "human"
    system = "system"
