"""
Constants and validation patterns for the Hierarchical Data Explorer.

This module contains all the choice constants, validation patterns,
and enums used throughout the application for data validation.
"""

import re
from typing import List, Dict, Any
from enum import Enum


class ProjectType(str, Enum):
    """Project type choices."""
    INSTALLATION = "installation"
    REPAIR = "repair"
    MAINTENANCE = "maintenance"
    CONSULTING = "consulting"
    OTHER = "other"


class ProjectStatus(str, Enum):
    """Project status choices."""
    PLANNING = "planning"
    IN_PROGRESS = "in_progress"
    ON_HOLD = "on_hold"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class QuoteStatus(str, Enum):
    """Quote status choices."""
    DRAFT = "draft"
    PENDING_FREIGHT = "pending_freight"
    READY = "ready"
    SENT = "sent"
    APPROVED = "approved"
    DECLINED = "declined"


class VendorQuoteStatus(str, Enum):
    """Vendor quote status choices."""
    PENDING = "pending"
    QUOTED = "quoted"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"


class CustomerStatus(str, Enum):
    """Customer status choices."""
    ACTIVE = "active"
    INACTIVE = "inactive"
    PROSPECT = "prospect"


class FreightPriority(str, Enum):
    """Freight priority choices."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


# Choice lists for backward compatibility and dropdown menus
PROJECT_TYPE_CHOICES = [
    (ProjectType.INSTALLATION.value, "Installation"),
    (ProjectType.REPAIR.value, "Repair"),
    (ProjectType.MAINTENANCE.value, "Maintenance"),
    (ProjectType.CONSULTING.value, "Consulting"),
    (ProjectType.OTHER.value, "Other")
]

PROJECT_STATUS_CHOICES = [
    (ProjectStatus.PLANNING.value, "Planning"),
    (ProjectStatus.IN_PROGRESS.value, "In Progress"),
    (ProjectStatus.ON_HOLD.value, "On Hold"),
    (ProjectStatus.COMPLETED.value, "Completed"),
    (ProjectStatus.CANCELLED.value, "Cancelled")
]

QUOTE_STATUS_CHOICES = [
    (QuoteStatus.DRAFT.value, "Draft"),
    (QuoteStatus.PENDING_FREIGHT.value, "Pending Freight"),
    (QuoteStatus.READY.value, "Ready"),
    (QuoteStatus.SENT.value, "Sent"),
    (QuoteStatus.APPROVED.value, "Approved"),
    (QuoteStatus.DECLINED.value, "Declined")
]

VENDOR_QUOTE_STATUS_CHOICES = [
    (VendorQuoteStatus.PENDING.value, "Pending"),
    (VendorQuoteStatus.QUOTED.value, "Quoted"),
    (VendorQuoteStatus.APPROVED.value, "Approved"),
    (VendorQuoteStatus.REJECTED.value, "Rejected"),
    (VendorQuoteStatus.COMPLETED.value, "Completed")
]

CUSTOMER_STATUS_CHOICES = [
    (CustomerStatus.ACTIVE.value, "Active"),
    (CustomerStatus.INACTIVE.value, "Inactive"),
    (CustomerStatus.PROSPECT.value, "Prospect")
]

FREIGHT_PRIORITY_CHOICES = [
    (FreightPriority.LOW.value, "Low"),
    (FreightPriority.MEDIUM.value, "Medium"),
    (FreightPriority.HIGH.value, "High"),
    (FreightPriority.URGENT.value, "Urgent")
]

# Validation patterns
EMAIL_PATTERN = re.compile(
    r'^[a-zA-Z0-9](?:[a-zA-Z0-9._%+-]*[a-zA-Z0-9])?@[a-zA-Z0-9](?:[a-zA-Z0-9.-]*[a-zA-Z0-9])?\.[a-zA-Z]{2,}$'
)

ZIP_CODE_PATTERN = re.compile(
    r'^\d{5}(-\d{4})?$'  # US ZIP code format: 12345 or 12345-6789
)

PHONE_PATTERN = re.compile(
    r'^(?:\+1\s)?(?:\(\d{3}\)\s|\d{3}[-.])\d{3}[-.]?\d{4}$|^\+1\s?\d{10}$|^\d{10}$'
)

TRACKING_ID_PATTERN = re.compile(
    r'^VQ\d{2}-\d+$'  # VQYY-ID format
)

# Field validation constants
MAX_NAME_LENGTH = 255
MAX_DESCRIPTION_LENGTH = 1000
MAX_EMAIL_LENGTH = 254
MAX_PHONE_LENGTH = 20
MAX_ZIP_LENGTH = 10
MAX_ADDRESS_LENGTH = 255
MAX_CITY_LENGTH = 100
MAX_STATE_LENGTH = 50
MAX_SPECIALTY_LENGTH = 100
MAX_ITEMS_TEXT_LENGTH = 2000
MAX_DELIVERY_REQUIREMENTS_LENGTH = 1000

# Decimal field constraints
MIN_BUDGET = 0.01
MAX_BUDGET = 999999999.99
MIN_AMOUNT = 0.01
MAX_AMOUNT = 999999999.99
MIN_WEIGHT = 0.01
MAX_WEIGHT = 999999.99
MIN_QUOTED_AMOUNT = 0.01
MAX_QUOTED_AMOUNT = 999999999.99

# Validation functions
def validate_email(email: str) -> bool:
    """Validate email format."""
    if not email or not email.strip():
        return False
    email = email.strip()
    # Check length before other validation
    if len(email) > MAX_EMAIL_LENGTH:
        return False
    # Additional validation to prevent consecutive dots
    if '..' in email or email.startswith('.') or email.endswith('.'):
        return False
    return bool(EMAIL_PATTERN.match(email))


def validate_zip_code(zip_code: str) -> bool:
    """Validate US ZIP code format."""
    if not zip_code or len(zip_code) > MAX_ZIP_LENGTH:
        return False
    return bool(ZIP_CODE_PATTERN.match(zip_code))


def validate_phone(phone: str) -> bool:
    """Validate phone number format."""
    if not phone or len(phone) > MAX_PHONE_LENGTH:
        return False
    phone = phone.strip()
    return bool(PHONE_PATTERN.match(phone))


def validate_tracking_id(tracking_id: str) -> bool:
    """Validate vendor quote tracking ID format."""
    if not tracking_id:
        return False
    return bool(TRACKING_ID_PATTERN.match(tracking_id))


def validate_name_length(name: str) -> bool:
    """Validate name field length."""
    return bool(name and name.strip() and 1 <= len(name.strip()) <= MAX_NAME_LENGTH)


def validate_description_length(description: str) -> bool:
    """Validate description field length."""
    return description is None or len(description) <= MAX_DESCRIPTION_LENGTH


# Choice validation functions
def get_valid_project_types() -> List[str]:
    """Get list of valid project type values."""
    return [choice[0] for choice in PROJECT_TYPE_CHOICES]


def get_valid_project_statuses() -> List[str]:
    """Get list of valid project status values."""
    return [choice[0] for choice in PROJECT_STATUS_CHOICES]


def get_valid_quote_statuses() -> List[str]:
    """Get list of valid quote status values."""
    return [choice[0] for choice in QUOTE_STATUS_CHOICES]


def get_valid_vendor_quote_statuses() -> List[str]:
    """Get list of valid vendor quote status values."""
    return [choice[0] for choice in VENDOR_QUOTE_STATUS_CHOICES]


def get_valid_customer_statuses() -> List[str]:
    """Get list of valid customer status values."""
    return [choice[0] for choice in CUSTOMER_STATUS_CHOICES]


def get_valid_freight_priorities() -> List[str]:
    """Get list of valid freight priority values."""
    return [choice[0] for choice in FREIGHT_PRIORITY_CHOICES]


# Default values for data generation
DEFAULT_CUSTOMER_STATUSES = [CustomerStatus.ACTIVE.value, CustomerStatus.INACTIVE.value]
DEFAULT_PROJECT_TYPES = [
    ProjectType.INSTALLATION.value,
    ProjectType.REPAIR.value,
    ProjectType.MAINTENANCE.value
]
DEFAULT_PROJECT_STATUSES = [
    ProjectStatus.PLANNING.value,
    ProjectStatus.IN_PROGRESS.value,
    ProjectStatus.COMPLETED.value
]
DEFAULT_QUOTE_STATUSES = [
    QuoteStatus.DRAFT.value,
    QuoteStatus.READY.value,
    QuoteStatus.APPROVED.value
]
DEFAULT_VENDOR_QUOTE_STATUSES = [
    VendorQuoteStatus.PENDING.value,
    VendorQuoteStatus.QUOTED.value,
    VendorQuoteStatus.APPROVED.value
]
DEFAULT_FREIGHT_PRIORITIES = [
    FreightPriority.LOW.value,
    FreightPriority.MEDIUM.value,
    FreightPriority.HIGH.value
]

# Constants for tracking ID generation
TRACKING_ID_PREFIX = "VQ"
TRACKING_ID_YEAR_FORMAT = "%y"  # Two-digit year


def generate_tracking_id(year: int, sequence: int) -> str:
    """Generate a vendor quote tracking ID in VQYY-ID format.

    Args:
        year: Calendar year (e.g., 2024)
        sequence: Sequential number for the year

    Returns:
        Tracking ID string in format "VQYY-ID"

    Example:
        generate_tracking_id(2024, 1) -> "VQ24-1"
        generate_tracking_id(2024, 123) -> "VQ24-123"
    """
    year_suffix = year % 100  # Get last two digits of year
    return f"{TRACKING_ID_PREFIX}{year_suffix:02d}-{sequence}"


# Field mapping for DATABASE_SCHEMA.md compliance
SCHEMA_FIELD_MAPPINGS = {
    "customer": {
        "id": "id",
        "name": "name",
        "address": "address",
        "city": "city",
        "state": "state",
        "zip": "zip",
        "sales_rep_name": "sales_rep_name",
        "sales_rep_email": "sales_rep_email",
        "created_at": "created_at",
        "updated_at": "updated_at"
    },
    "project": {
        "id": "id",
        "customer": "customer_id",
        "name": "name",
        "project_type": "project_type",
        "target_delivery_date": "target_delivery_date",
        "status": "status",
        "created_at": "created_at",
        "updated_at": "updated_at"
    },
    "quote": {
        "id": "id",
        "project": "project_id",
        "name": "name",
        "description": "description",
        "status": "status",
        "created_at": "created_at",
        "updated_at": "updated_at"
    },
    "vendor": {
        "id": "id",
        "name": "name",
        "contact_name": "contact_name",
        "email": "email",
        "created_at": "created_at",
        "updated_at": "updated_at"
    },
    "vendor_quote": {
        "id": "id",
        "quote": "quote_id",
        "vendor": "vendor_id",
        "tracking_id": "tracking_id",
        "items_text": "items_text",
        "delivery_requirements": "delivery_requirements",
        "is_rush": "is_rush",
        "status": "status",
        "quoted_amount": "quoted_amount",
        "created_at": "created_at",
        "updated_at": "updated_at"
    }
}


# Validation error messages
VALIDATION_ERROR_MESSAGES = {
    "email_invalid": "Invalid email format",
    "zip_invalid": "Invalid ZIP code format (use 12345 or 12345-6789)",
    "phone_invalid": "Invalid phone number format",
    "tracking_id_invalid": "Invalid tracking ID format (use VQYY-ID)",
    "name_too_long": f"Name must be {MAX_NAME_LENGTH} characters or less",
    "name_too_short": "Name must be at least 1 character",
    "description_too_long": f"Description must be {MAX_DESCRIPTION_LENGTH} characters or less",
    "budget_too_low": f"Budget must be at least ${MIN_BUDGET:.2f}",
    "budget_too_high": f"Budget must be ${MAX_BUDGET:.2f} or less",
    "amount_too_low": f"Amount must be at least ${MIN_AMOUNT:.2f}",
    "amount_too_high": f"Amount must be ${MAX_AMOUNT:.2f} or less",
    "weight_too_low": f"Weight must be at least {MIN_WEIGHT}",
    "weight_too_high": f"Weight must be {MAX_WEIGHT} or less",
    "quoted_amount_too_low": f"Quoted amount must be at least ${MIN_QUOTED_AMOUNT:.2f}",
    "quoted_amount_too_high": f"Quoted amount must be ${MAX_QUOTED_AMOUNT:.2f} or less",
    "project_type_invalid": f"Project type must be one of: {', '.join(get_valid_project_types())}",
    "project_status_invalid": f"Project status must be one of: {', '.join(get_valid_project_statuses())}",
    "quote_status_invalid": f"Quote status must be one of: {', '.join(get_valid_quote_statuses())}",
    "vendor_quote_status_invalid": f"Vendor quote status must be one of: {', '.join(get_valid_vendor_quote_statuses())}",
    "customer_status_invalid": f"Customer status must be one of: {', '.join(get_valid_customer_statuses())}",
    "freight_priority_invalid": f"Freight priority must be one of: {', '.join(get_valid_freight_priorities())}"
}