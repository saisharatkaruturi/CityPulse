"""Import every model so metadata is complete for Alembic and table creation."""

from app.models.catalog import (
    Announcement,
    Category,
    RoutingRule,
    Service,
    SlaPolicy,
    service_categories,
    service_departments,
)
from app.models.complaints import (
    AiClassification,
    Complaint,
    ComplaintAssignment,
    ComplaintCategoryChange,
    ComplaintComment,
    ComplaintInternalNote,
    ComplaintLink,
    ComplaintMedia,
    ComplaintPriorityChange,
    ComplaintStatusHistory,
    ComplaintSupporter,
    EscalationHistory,
    Feedback,
)
from app.models.identity import (
    AuthSession,
    Department,
    DepartmentWardCoverage,
    Officer,
    Team,
    User,
    UserRole,
    Ward,
)
from app.models.platform import (
    AuditLog,
    IdempotencyRecord,
    Notification,
    NotificationPreference,
    OutboxEvent,
)

__all__ = [
    "AiClassification", "Announcement", "AuditLog", "AuthSession", "Category", "Complaint",
    "ComplaintAssignment", "ComplaintCategoryChange", "ComplaintComment", "ComplaintInternalNote",
    "ComplaintLink", "ComplaintMedia", "ComplaintPriorityChange", "ComplaintStatusHistory",
    "ComplaintSupporter", "Department", "DepartmentWardCoverage", "EscalationHistory", "Feedback",
    "IdempotencyRecord", "Notification", "NotificationPreference", "Officer", "OutboxEvent",
    "RoutingRule", "Service", "SlaPolicy", "Team", "User", "UserRole", "Ward",
    "service_categories", "service_departments",
]
