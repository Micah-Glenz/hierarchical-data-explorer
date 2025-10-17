"""
Pydantic models for the Hierarchical Data Explorer API.

This module defines all request and response models used by the API,
providing type safety and validation for all data operations.
"""

from datetime import date, datetime
from typing import List, Dict, Any, Optional

from pydantic import BaseModel, Field, validator
from .dependencies import get_valid_statuses, get_valid_priorities
from ..core.constants import (
    get_valid_project_types,
    get_valid_project_statuses,
    get_valid_quote_statuses,
    get_valid_vendor_quote_statuses,
    get_valid_customer_statuses,
    get_valid_freight_priorities,
    validate_email,
    validate_zip_code,
    validate_phone,
    validate_tracking_id,
    MAX_NAME_LENGTH,
    MAX_DESCRIPTION_LENGTH,
    MAX_EMAIL_LENGTH,
    MAX_PHONE_LENGTH,
    MAX_ZIP_LENGTH,
    MAX_ADDRESS_LENGTH,
    MAX_CITY_LENGTH,
    MAX_STATE_LENGTH,
    MAX_SPECIALTY_LENGTH,
    MAX_ITEMS_TEXT_LENGTH,
    MAX_DELIVERY_REQUIREMENTS_LENGTH,
    MIN_BUDGET,
    MAX_BUDGET,
    MIN_AMOUNT,
    MAX_AMOUNT,
    MIN_WEIGHT,
    MAX_WEIGHT,
    MIN_QUOTED_AMOUNT,
    MAX_QUOTED_AMOUNT,
    generate_tracking_id,
    VALIDATION_ERROR_MESSAGES
)


class BaseResponse(BaseModel):
    """Base response model for all API responses."""

    success: bool = True
    message: Optional[str] = None


class ErrorResponse(BaseResponse):
    """Error response model."""

    success: bool = False
    error: str
    details: Optional[Dict[str, Any]] = None


# Customer Models
class CustomerBase(BaseModel):
    """Base customer model with common fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Customer name")
    status: str = Field(..., description="Customer status")

    @validator('status')
    def validate_status(cls, v):
        """Validate status field."""
        allowed_statuses = get_valid_statuses()
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v


class CustomerCreate(CustomerBase):
    """Model for creating a new customer."""

    created_date: str = Field(..., description="Customer creation date in YYYY-MM-DD format")

    @validator('created_date')
    def validate_created_date(cls, v):
        """Validate created_date format."""
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format') from None


class CustomerUpdate(BaseModel):
    """Model for updating an existing customer."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    status: Optional[str] = None

    @validator('status')
    def validate_status(cls, v):
        """Validate status field if provided."""
        if v is not None:
            allowed_statuses = get_valid_statuses()
            if v not in allowed_statuses:
                raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v


class CustomerResponse(CustomerBase):
    """Customer response model."""

    id: int
    created_date: str
    project_count: int = 0

    class Config:
        """Pydantic configuration."""

        from_attributes = True


# Project Models
class ProjectBase(BaseModel):
    """Base project model with common fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Project name")
    budget: float = Field(..., gt=0, le=999999999.99, description="Project budget")
    status: str = Field(..., description="Project status")
    start_date: str = Field(..., description="Project start date in YYYY-MM-DD format")

    @validator('status')
    def validate_status(cls, v):
        """Validate status field."""
        allowed_statuses = get_valid_statuses()
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v

    @validator('start_date')
    def validate_start_date(cls, v):
        """Validate start_date format."""
        try:
            datetime.strptime(v, '%Y-%m-%d')
            return v
        except ValueError:
            raise ValueError('Date must be in YYYY-MM-DD format') from None


class ProjectCreate(ProjectBase):
    """Model for creating a new project."""

    customer_id: int = Field(..., gt=0, description="ID of the customer")


class ProjectUpdate(BaseModel):
    """Model for updating an existing project."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    budget: Optional[float] = Field(None, gt=0, le=999999999.99)
    status: Optional[str] = None
    start_date: Optional[str] = None

    @validator('status')
    def validate_status(cls, v):
        """Validate status field if provided."""
        if v is not None:
            allowed_statuses = get_valid_statuses()
            if v not in allowed_statuses:
                raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v

    @validator('start_date')
    def validate_start_date(cls, v):
        """Validate start_date format if provided."""
        if v is not None:
            try:
                datetime.strptime(v, '%Y-%m-%d')
                return v
            except ValueError:
                raise ValueError('Date must be in YYYY-MM-DD format')
        return v


class ProjectResponse(ProjectBase):
    """Project response model."""

    id: int
    customer_id: int
    quote_count: int = 0

    class Config:
        """Pydantic configuration."""

        from_attributes = True


# Quote Models
class QuoteBase(BaseModel):
    """Base quote model with common fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Quote name")
    amount: float = Field(..., gt=0, le=999999999.99, description="Quote amount")
    status: str = Field(..., description="Quote status")
    valid_until: Optional[str] = Field(None, description="Quote expiration date in YYYY-MM-DD format")

    @validator('status')
    def validate_status(cls, v):
        """Validate status field."""
        allowed_statuses = get_valid_statuses()
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v

    @validator('valid_until')
    def validate_valid_until(cls, v):
        """Validate valid_until format if provided."""
        if v is not None:
            try:
                datetime.strptime(v, '%Y-%m-%d')
                return v
            except ValueError:
                raise ValueError('Date must be in YYYY-MM-DD format')
        return v


class QuoteCreate(QuoteBase):
    """Model for creating a new quote."""

    project_id: int = Field(..., gt=0, description="ID of the project")


class QuoteUpdate(BaseModel):
    """Model for updating an existing quote."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    amount: Optional[float] = Field(None, gt=0, le=999999999.99)
    status: Optional[str] = None
    valid_until: Optional[str] = None

    @validator('status')
    def validate_status(cls, v):
        """Validate status field if provided."""
        if v is not None:
            allowed_statuses = get_valid_statuses()
            if v not in allowed_statuses:
                raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v

    @validator('valid_until')
    def validate_valid_until(cls, v):
        """Validate valid_until format if provided."""
        if v is not None:
            try:
                datetime.strptime(v, '%Y-%m-%d')
                return v
            except ValueError:
                raise ValueError('Date must be in YYYY-MM-DD format')
        return v


class QuoteResponse(QuoteBase):
    """Quote response model."""

    id: int
    project_id: int
    freight_request_count: int = 0

    class Config:
        """Pydantic configuration."""

        from_attributes = True


# Freight Request Models
class FreightRequestBase(BaseModel):
    """Base freight request model with common fields."""

    name: str = Field(..., min_length=1, max_length=255, description="Freight request name")
    vendor_id: int = Field(..., gt=0, description="ID of the vendor")
    status: str = Field(..., description="Freight request status")
    weight: float = Field(..., gt=0, le=999999.99, description="Weight in kilograms")
    priority: str = Field(..., description="Freight priority")
    estimated_delivery: Optional[str] = Field(None, description="Estimated delivery date in YYYY-MM-DD format")

    @validator('status')
    def validate_status(cls, v):
        """Validate status field."""
        allowed_statuses = get_valid_statuses()
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v

    @validator('priority')
    def validate_priority(cls, v):
        """Validate priority field."""
        allowed_priorities = get_valid_priorities()
        if v not in allowed_priorities:
            raise ValueError(f'Priority must be one of: {", ".join(allowed_priorities)}')
        return v

    @validator('estimated_delivery')
    def validate_estimated_delivery(cls, v):
        """Validate estimated_delivery format if provided."""
        if v is not None:
            try:
                datetime.strptime(v, '%Y-%m-%d')
                return v
            except ValueError:
                raise ValueError('Date must be in YYYY-MM-DD format')
        return v


class FreightRequestCreate(FreightRequestBase):
    """Model for creating a new freight request."""

    quote_id: int = Field(..., gt=0, description="ID of the quote")


class FreightRequestUpdate(BaseModel):
    """Model for updating an existing freight request."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    vendor_id: Optional[int] = Field(None, gt=0)
    status: Optional[str] = None
    weight: Optional[float] = Field(None, gt=0, le=999999.99)
    priority: Optional[str] = None
    estimated_delivery: Optional[str] = None

    @validator('status')
    def validate_status(cls, v):
        """Validate status field if provided."""
        if v is not None:
            allowed_statuses = get_valid_statuses()
            if v not in allowed_statuses:
                raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v

    @validator('priority')
    def validate_priority(cls, v):
        """Validate priority field if provided."""
        if v is not None:
            allowed_priorities = get_valid_priorities()
            if v not in allowed_priorities:
                raise ValueError(f'Priority must be one of: {", ".join(allowed_priorities)}')
        return v

    @validator('estimated_delivery')
    def validate_estimated_delivery(cls, v):
        """Validate estimated_delivery format if provided."""
        if v is not None:
            try:
                datetime.strptime(v, '%Y-%m-%d')
                return v
            except ValueError:
                raise ValueError('Date must be in YYYY-MM-DD format')
        return v


class FreightRequestResponse(FreightRequestBase):
    """Freight request response model."""

    id: int
    quote_id: int
    vendor_name: str = Field(..., description="Name of the vendor")

    class Config:
        """Pydantic configuration."""

        from_attributes = True


# Vendor Models
class VendorResponse(BaseModel):
    """Vendor response model."""

    id: int
    name: str
    specialty: str
    rating: float

    class Config:
        """Pydantic configuration."""

        from_attributes = True


# Success Response Models
class CreateResponse(BaseResponse):
    """Response model for create operations."""

    data: Dict[str, Any]


class UpdateResponse(BaseResponse):
    """Response model for update operations."""

    data: Dict[str, Any]


class DeleteResponse(BaseResponse):
    """Response model for delete operations."""


# VendorQuote Models
class VendorQuoteBase(BaseModel):
    """Base vendor quote model with common fields."""

    quote_id: int = Field(..., gt=0, description="ID of the associated quote")
    vendor_id: int = Field(..., gt=0, description="ID of the vendor")
    tracking_id: str = Field(..., description="Unique tracking identifier (VQYY-ID format)")
    items_text: str = Field(..., min_length=1, max_length=MAX_ITEMS_TEXT_LENGTH, description="Description of items")
    delivery_requirements: Optional[str] = Field(None, max_length=MAX_DELIVERY_REQUIREMENTS_LENGTH, description="Special delivery requirements")
    is_rush: bool = Field(False, description="Whether this is a rush order")
    status: str = Field(..., description="Vendor quote status")
    quoted_amount: Optional[float] = Field(None, ge=MIN_QUOTED_AMOUNT, le=MAX_QUOTED_AMOUNT, description="Quoted amount from vendor")

    @validator('tracking_id')
    def validate_tracking_id_format(cls, v):
        """Validate tracking ID format."""
        if not validate_tracking_id(v):
            raise ValueError(VALIDATION_ERROR_MESSAGES["tracking_id_invalid"])
        return v

    @validator('status')
    def validate_status(cls, v):
        """Validate status field."""
        allowed_statuses = get_valid_vendor_quote_statuses()
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v

    @validator('items_text')
    def validate_items_text(cls, v):
        """Validate items text is not empty."""
        if not v or not v.strip():
            raise ValueError("Items text cannot be empty")
        return v.strip()


class VendorQuoteCreate(VendorQuoteBase):
    """Model for creating a new vendor quote."""

    # Auto-generated fields that don't need to be provided during creation
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class VendorQuoteUpdate(BaseModel):
    """Model for updating an existing vendor quote."""

    quote_id: Optional[int] = Field(None, gt=0)
    vendor_id: Optional[int] = Field(None, gt=0)
    tracking_id: Optional[str] = Field(None, min_length=1, max_length=20, description="Unique tracking identifier (VQYY-ID format)")
    items_text: Optional[str] = Field(None, min_length=1, max_length=MAX_ITEMS_TEXT_LENGTH)
    delivery_requirements: Optional[str] = Field(None, max_length=MAX_DELIVERY_REQUIREMENTS_LENGTH)
    is_rush: Optional[bool] = None
    status: Optional[str] = None
    quoted_amount: Optional[float] = Field(None, ge=MIN_QUOTED_AMOUNT, le=MAX_QUOTED_AMOUNT)

    @validator('tracking_id')
    def validate_tracking_id(cls, v):
        """Validate tracking ID if provided."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Tracking ID cannot be empty")
            if not validate_tracking_id(v.strip()):
                raise ValueError("Tracking ID must be in VQYY-ID format (e.g., VQ24-1)")
            return v.strip()
        return v

    @validator('items_text')
    def validate_items_text(cls, v):
        """Validate items text if provided."""
        if v is not None:
            if not v or not v.strip():
                raise ValueError("Items text cannot be empty")
            return v.strip()
        return v

    @validator('status')
    def validate_status(cls, v):
        """Validate status field if provided."""
        if v is not None:
            allowed_statuses = get_valid_vendor_quote_statuses()
            if v not in allowed_statuses:
                raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v


class VendorQuoteResponse(VendorQuoteBase):
    """Vendor quote response model."""

    id: int
    created_at: str
    updated_at: str
    vendor_name: str = Field(..., description="Name of the vendor")
    quote_name: str = Field(..., description="Name of the associated quote")

    class Config:
        """Pydantic configuration."""

        from_attributes = True


# Enhanced Customer Models with DATABASE_SCHEMA.md fields
class CustomerBaseEnhanced(CustomerBase):
    """Enhanced customer model with DATABASE_SCHEMA.md fields."""

    address: Optional[str] = Field(None, max_length=MAX_ADDRESS_LENGTH, description="Street address")
    city: Optional[str] = Field(None, max_length=MAX_CITY_LENGTH, description="City")
    state: Optional[str] = Field(None, max_length=MAX_STATE_LENGTH, description="State")
    zip: Optional[str] = Field(None, max_length=MAX_ZIP_LENGTH, description="ZIP code")
    sales_rep_name: Optional[str] = Field(None, max_length=MAX_NAME_LENGTH, description="Sales representative name")
    sales_rep_email: Optional[str] = Field(None, max_length=MAX_EMAIL_LENGTH, description="Sales representative email")

    @validator('zip')
    def validate_zip_code(cls, v):
        """Validate ZIP code format if provided."""
        if v is not None and v.strip():
            if not validate_zip_code(v.strip()):
                raise ValueError(VALIDATION_ERROR_MESSAGES["zip_invalid"])
            return v.strip()
        return v

    @validator('sales_rep_email')
    def validate_sales_rep_email(cls, v):
        """Validate sales rep email format if provided."""
        if v is not None and v.strip():
            if not validate_email(v.strip()):
                raise ValueError(VALIDATION_ERROR_MESSAGES["email_invalid"])
            return v.strip()
        return v

    @validator('address', 'city', 'state', 'sales_rep_name')
    def validate_optional_strings(cls, v):
        """Validate optional string fields."""
        if v is not None:
            return v.strip() if v.strip() else None
        return v


class CustomerCreateEnhanced(CustomerBaseEnhanced):
    """Enhanced customer creation model."""

    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class CustomerUpdateEnhanced(BaseModel):
    """Enhanced customer update model."""

    name: Optional[str] = Field(None, min_length=1, max_length=MAX_NAME_LENGTH)
    status: Optional[str] = None
    address: Optional[str] = Field(None, max_length=MAX_ADDRESS_LENGTH)
    city: Optional[str] = Field(None, max_length=MAX_CITY_LENGTH)
    state: Optional[str] = Field(None, max_length=MAX_STATE_LENGTH)
    zip: Optional[str] = Field(None, max_length=MAX_ZIP_LENGTH)
    sales_rep_name: Optional[str] = Field(None, max_length=MAX_NAME_LENGTH)
    sales_rep_email: Optional[str] = Field(None, max_length=MAX_EMAIL_LENGTH)

    @validator('status')
    def validate_status(cls, v):
        """Validate status field if provided."""
        if v is not None:
            allowed_statuses = get_valid_customer_statuses()
            if v not in allowed_statuses:
                raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v

    @validator('zip')
    def validate_zip_code(cls, v):
        """Validate ZIP code format if provided."""
        if v is not None and v.strip():
            if not validate_zip_code(v.strip()):
                raise ValueError(VALIDATION_ERROR_MESSAGES["zip_invalid"])
            return v.strip()
        return v

    @validator('sales_rep_email')
    def validate_sales_rep_email(cls, v):
        """Validate sales rep email format if provided."""
        # First handle empty string case
        if v is not None and not v.strip():
            return None
        # Then validate email format
        if v is not None and v.strip():
            if not validate_email(v.strip()):
                raise ValueError(VALIDATION_ERROR_MESSAGES["email_invalid"])
            return v.strip()
        return v

    @validator('name', 'address', 'city', 'state', 'sales_rep_name')
    def validate_optional_strings(cls, v):
        """Validate optional string fields."""
        if v is not None:
            if not v.strip():
                return None
            return v.strip()
        return v


class CustomerResponseEnhanced(CustomerBaseEnhanced):
    """Enhanced customer response model."""

    id: int
    created_at: str
    updated_at: str
    project_count: int = 0

    class Config:
        """Pydantic configuration."""

        from_attributes = True


# Enhanced Project Models with DATABASE_SCHEMA.md fields
class ProjectBaseEnhanced(ProjectBase):
    """Enhanced project model with DATABASE_SCHEMA.md fields."""

    project_type: str = Field(..., description="Type of project")
    target_delivery_date: Optional[str] = Field(None, description="Target delivery date in YYYY-MM-DD format")

    @validator('project_type')
    def validate_project_type(cls, v):
        """Validate project type field."""
        allowed_types = get_valid_project_types()
        if v not in allowed_types:
            raise ValueError(f'Project type must be one of: {", ".join(allowed_types)}')
        return v

    @validator('target_delivery_date')
    def validate_target_delivery_date(cls, v):
        """Validate target delivery date format if provided."""
        if v is not None:
            try:
                datetime.strptime(v, '%Y-%m-%d')
                return v
            except ValueError:
                raise ValueError('Target delivery date must be in YYYY-MM-DD format')
        return v


class ProjectCreateEnhanced(ProjectBaseEnhanced):
    """Enhanced project creation model."""

    customer_id: int = Field(..., gt=0, description="ID of the customer")
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class ProjectUpdateEnhanced(BaseModel):
    """Enhanced project update model."""

    name: Optional[str] = Field(None, min_length=1, max_length=MAX_NAME_LENGTH)
    budget: Optional[float] = Field(None, gt=0, le=MAX_BUDGET)
    status: Optional[str] = None
    start_date: Optional[str] = None
    project_type: Optional[str] = None
    target_delivery_date: Optional[str] = None

    @validator('status')
    def validate_status(cls, v):
        """Validate status field if provided."""
        if v is not None:
            allowed_statuses = get_valid_project_statuses()
            if v not in allowed_statuses:
                raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v

    @validator('project_type')
    def validate_project_type(cls, v):
        """Validate project type field if provided."""
        if v is not None:
            allowed_types = get_valid_project_types()
            if v not in allowed_types:
                raise ValueError(f'Project type must be one of: {", ".join(allowed_types)}')
        return v

    @validator('start_date', 'target_delivery_date')
    def validate_date_formats(cls, v):
        """Validate date formats if provided."""
        if v is not None:
            try:
                datetime.strptime(v, '%Y-%m-%d')
                return v
            except ValueError:
                raise ValueError('Date must be in YYYY-MM-DD format')
        return v


class ProjectResponseEnhanced(ProjectBaseEnhanced):
    """Enhanced project response model."""

    id: int
    customer_id: int
    created_at: str
    updated_at: str
    quote_count: int = 0

    class Config:
        """Pydantic configuration."""

        from_attributes = True


# Enhanced Vendor Models with DATABASE_SCHEMA.md fields
class VendorBaseEnhanced(BaseModel):
    """Enhanced vendor model with DATABASE_SCHEMA.md fields."""

    name: str = Field(..., min_length=1, max_length=MAX_NAME_LENGTH, description="Vendor name")
    contact_name: Optional[str] = Field(None, max_length=MAX_NAME_LENGTH, description="Contact person name")
    email: Optional[str] = Field(None, max_length=MAX_EMAIL_LENGTH, description="Contact email address")
    specialty: str = Field(..., max_length=MAX_SPECIALTY_LENGTH, description="Vendor specialty")
    rating: float = Field(..., ge=0, le=5, description="Vendor rating (0-5)")

    @validator('email')
    def validate_email(cls, v):
        """Validate email format if provided."""
        if v is not None and v.strip():
            if not validate_email(v.strip()):
                raise ValueError(VALIDATION_ERROR_MESSAGES["email_invalid"])
            return v.strip()
        return v

    @validator('contact_name')
    def validate_contact_name(cls, v):
        """Validate contact name if provided."""
        if v is not None:
            return v.strip() if v.strip() else None
        return v


class VendorCreateEnhanced(VendorBaseEnhanced):
    """Enhanced vendor creation model."""

    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class VendorUpdateEnhanced(BaseModel):
    """Enhanced vendor update model."""

    name: Optional[str] = Field(None, min_length=1, max_length=MAX_NAME_LENGTH)
    contact_name: Optional[str] = Field(None, max_length=MAX_NAME_LENGTH)
    email: Optional[str] = Field(None, max_length=MAX_EMAIL_LENGTH)
    specialty: Optional[str] = Field(None, max_length=MAX_SPECIALTY_LENGTH)
    rating: Optional[float] = Field(None, ge=0, le=5)

    @validator('email')
    def validate_email(cls, v):
        """Validate email format if provided."""
        if v is not None and v.strip():
            if not validate_email(v.strip()):
                raise ValueError(VALIDATION_ERROR_MESSAGES["email_invalid"])
            return v.strip()
        return v

    @validator('name', 'contact_name', 'specialty')
    def validate_optional_strings(cls, v):
        """Validate optional string fields."""
        if v is not None:
            if not v.strip():
                return None
            return v.strip()
        return v


class VendorResponseEnhanced(VendorBaseEnhanced):
    """Enhanced vendor response model."""

    id: int
    created_at: str
    updated_at: str

    class Config:
        """Pydantic configuration."""

        from_attributes = True


# Enhanced Quote Models with DATABASE_SCHEMA.md fields
class QuoteBaseEnhanced(QuoteBase):
    """Enhanced quote model with DATABASE_SCHEMA.md fields."""

    description: Optional[str] = Field(None, max_length=MAX_DESCRIPTION_LENGTH, description="Quote description")

    @validator('description')
    def validate_description(cls, v):
        """Validate description if provided."""
        if v is not None:
            return v.strip() if v.strip() else None
        return v


class QuoteCreateEnhanced(QuoteBaseEnhanced):
    """Enhanced quote creation model."""

    project_id: int = Field(..., gt=0, description="ID of the project")
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class QuoteUpdateEnhanced(BaseModel):
    """Enhanced quote update model."""

    name: Optional[str] = Field(None, min_length=1, max_length=MAX_NAME_LENGTH)
    amount: Optional[float] = Field(None, gt=0, le=MAX_AMOUNT)
    status: Optional[str] = None
    valid_until: Optional[str] = None
    description: Optional[str] = Field(None, max_length=MAX_DESCRIPTION_LENGTH)

    @validator('status')
    def validate_status(cls, v):
        """Validate status field if provided."""
        if v is not None:
            allowed_statuses = get_valid_quote_statuses()
            if v not in allowed_statuses:
                raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v

    @validator('valid_until')
    def validate_valid_until(cls, v):
        """Validate valid_until format if provided."""
        if v is not None:
            try:
                datetime.strptime(v, '%Y-%m-%d')
                return v
            except ValueError:
                raise ValueError('Date must be in YYYY-MM-DD format')
        return v

    @validator('name', 'description')
    def validate_optional_strings(cls, v):
        """Validate optional string fields."""
        if v is not None:
            if not v.strip():
                return None
            return v.strip()
        return v


class QuoteResponseEnhanced(QuoteBaseEnhanced):
    """Enhanced quote response model."""

    id: int
    project_id: int
    created_at: str
    updated_at: str
    freight_request_count: int = 0

    class Config:
        """Pydantic configuration."""

        from_attributes = True