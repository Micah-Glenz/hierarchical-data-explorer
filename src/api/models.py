"""
Pydantic models for the Hierarchical Data Explorer API.

This module defines all request and response models used by the API,
providing type safety and validation for all data operations.
"""

from datetime import date, datetime
from typing import List, Dict, Any, Optional

from pydantic import BaseModel, Field, validator


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
    industry: str = Field(..., min_length=1, max_length=100, description="Customer industry")
    status: str = Field(..., description="Customer status")

    @validator('status')
    def validate_status(cls, v):
        """Validate status field."""
        allowed_statuses = ['active', 'planning', 'in_progress', 'on_hold', 'completed']
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v

    @validator('industry')
    def validate_industry(cls, v):
        """Validate industry field."""
        allowed_industries = [
            'Technology', 'Manufacturing', 'Retail', 'Healthcare',
            'Logistics', 'Finance', 'Construction', 'Energy'
        ]
        if v not in allowed_industries:
            raise ValueError(f'Industry must be one of: {", ".join(allowed_industries)}')
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
            raise ValueError('Date must be in YYYY-MM-DD format')


class CustomerUpdate(BaseModel):
    """Model for updating an existing customer."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    industry: Optional[str] = None
    status: Optional[str] = None

    @validator('status')
    def validate_status(cls, v):
        """Validate status field if provided."""
        if v is not None:
            allowed_statuses = ['active', 'planning', 'in_progress', 'on_hold', 'completed']
            if v not in allowed_statuses:
                raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v

    @validator('industry')
    def validate_industry(cls, v):
        """Validate industry field if provided."""
        if v is not None:
            allowed_industries = [
                'Technology', 'Manufacturing', 'Retail', 'Healthcare',
                'Logistics', 'Finance', 'Construction', 'Energy'
            ]
            if v not in allowed_industries:
                raise ValueError(f'Industry must be one of: {", ".join(allowed_industries)}')
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
        allowed_statuses = ['active', 'planning', 'in_progress', 'on_hold', 'completed']
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
            raise ValueError('Date must be in YYYY-MM-DD format')


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
            allowed_statuses = ['active', 'planning', 'in_progress', 'on_hold', 'completed']
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
        allowed_statuses = ['active', 'planning', 'in_progress', 'on_hold', 'completed']
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
            allowed_statuses = ['active', 'planning', 'in_progress', 'on_hold', 'completed']
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
        allowed_statuses = ['active', 'planning', 'in_progress', 'on_hold', 'completed']
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v

    @validator('priority')
    def validate_priority(cls, v):
        """Validate priority field."""
        allowed_priorities = ['low', 'medium', 'high', 'critical']
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
            allowed_statuses = ['active', 'planning', 'in_progress', 'on_hold', 'completed']
            if v not in allowed_statuses:
                raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v

    @validator('priority')
    def validate_priority(cls, v):
        """Validate priority field if provided."""
        if v is not None:
            allowed_priorities = ['low', 'medium', 'high', 'critical']
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