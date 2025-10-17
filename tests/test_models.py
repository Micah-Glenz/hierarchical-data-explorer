"""
Test suite for Pydantic models.

This module tests all Pydantic models including validation,
creation, serialization, and edge cases for all entities.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from src.api.models import (
    # VendorQuote Models
    VendorQuoteBase, VendorQuoteCreate, VendorQuoteUpdate, VendorQuoteResponse,

    # Enhanced Customer Models
    CustomerBaseEnhanced, CustomerCreateEnhanced, CustomerUpdateEnhanced, CustomerResponseEnhanced,

    # Enhanced Project Models
    ProjectBaseEnhanced, ProjectCreateEnhanced, ProjectUpdateEnhanced, ProjectResponseEnhanced,

    # Enhanced Vendor Models
    VendorBaseEnhanced, VendorCreateEnhanced, VendorUpdateEnhanced, VendorResponseEnhanced,

    # Enhanced Quote Models
    QuoteBaseEnhanced, QuoteCreateEnhanced, QuoteUpdateEnhanced, QuoteResponseEnhanced,

    # Base Models
    BaseResponse, ErrorResponse, CreateResponse, UpdateResponse, DeleteResponse
)

from src.core.constants import (
    get_valid_project_types, get_valid_project_statuses, get_valid_quote_statuses,
    get_valid_vendor_quote_statuses, get_valid_customer_statuses,
    MAX_ITEMS_TEXT_LENGTH, MAX_DELIVERY_REQUIREMENTS_LENGTH,
    MAX_NAME_LENGTH, MAX_ADDRESS_LENGTH, MAX_CITY_LENGTH, MAX_STATE_LENGTH,
    MAX_SPECIALTY_LENGTH, MAX_EMAIL_LENGTH, MAX_ZIP_LENGTH,
    MIN_BUDGET, MAX_BUDGET, MIN_AMOUNT, MAX_AMOUNT, MIN_QUOTED_AMOUNT, MAX_QUOTED_AMOUNT
)


class TestVendorQuoteModels:
    """Test VendorQuote Pydantic models."""

    def test_vendor_quote_base_valid_data(self):
        """Test VendorQuoteBase with valid data."""
        data = {
            "quote_id": 1,
            "vendor_id": 2,
            "tracking_id": "VQ24-123",
            "items_text": "Test items for quote",
            "delivery_requirements": "Special delivery needed",
            "is_rush": True,
            "status": "pending",
            "quoted_amount": 15000.50
        }

        vendor_quote = VendorQuoteBase(**data)
        assert vendor_quote.quote_id == 1
        assert vendor_quote.vendor_id == 2
        assert vendor_quote.tracking_id == "VQ24-123"
        assert vendor_quote.items_text == "Test items for quote"
        assert vendor_quote.delivery_requirements == "Special delivery needed"
        assert vendor_quote.is_rush is True
        assert vendor_quote.status == "pending"
        assert vendor_quote.quoted_amount == 15000.50

    def test_vendor_quote_base_optional_fields(self):
        """Test VendorQuoteBase with optional fields."""
        data = {
            "quote_id": 1,
            "vendor_id": 2,
            "tracking_id": "VQ24-123",
            "items_text": "Test items",
            "status": "approved"
        }

        vendor_quote = VendorQuoteBase(**data)
        assert vendor_quote.delivery_requirements is None
        assert vendor_quote.is_rush is False  # Default value
        assert vendor_quote.quoted_amount is None

    def test_vendor_quote_base_invalid_tracking_id(self):
        """Test VendorQuoteBase with invalid tracking ID."""
        data = {
            "quote_id": 1,
            "vendor_id": 2,
            "tracking_id": "INVALID-123",  # Invalid format
            "items_text": "Test items",
            "status": "pending"
        }

        with pytest.raises(ValidationError) as exc_info:
            VendorQuoteBase(**data)
        assert "tracking_id" in str(exc_info.value)

    def test_vendor_quote_base_invalid_status(self):
        """Test VendorQuoteBase with invalid status."""
        data = {
            "quote_id": 1,
            "vendor_id": 2,
            "tracking_id": "VQ24-123",
            "items_text": "Test items",
            "status": "invalid_status"
        }

        with pytest.raises(ValidationError) as exc_info:
            VendorQuoteBase(**data)
        assert "status" in str(exc_info.value)

    def test_vendor_quote_base_empty_items_text(self):
        """Test VendorQuoteBase with empty items text."""
        data = {
            "quote_id": 1,
            "vendor_id": 2,
            "tracking_id": "VQ24-123",
            "items_text": "   ",  # Empty with spaces
            "status": "pending"
        }

        with pytest.raises(ValidationError) as exc_info:
            VendorQuoteBase(**data)
        assert "items_text" in str(exc_info.value)

    def test_vendor_quote_base_items_text_too_long(self):
        """Test VendorQuoteBase with items text that's too long."""
        data = {
            "quote_id": 1,
            "vendor_id": 2,
            "tracking_id": "VQ24-123",
            "items_text": "A" * (MAX_ITEMS_TEXT_LENGTH + 1),
            "status": "pending"
        }

        with pytest.raises(ValidationError) as exc_info:
            VendorQuoteBase(**data)
        assert "items_text" in str(exc_info.value)

    def test_vendor_quote_create_model(self):
        """Test VendorQuoteCreate model."""
        data = {
            "quote_id": 1,
            "vendor_id": 2,
            "tracking_id": "VQ24-123",
            "items_text": "Test items",
            "status": "quoted"
        }

        vendor_quote = VendorQuoteCreate(**data)
        assert vendor_quote.quote_id == 1
        assert vendor_quote.created_at is None
        assert vendor_quote.updated_at is None

    def test_vendor_quote_update_valid_data(self):
        """Test VendorQuoteUpdate with valid data."""
        data = {
            "items_text": "Updated items",
            "status": "approved",
            "quoted_amount": 20000.00
        }

        update = VendorQuoteUpdate(**data)
        assert update.items_text == "Updated items"
        assert update.status == "approved"
        assert update.quoted_amount == 20000.00

    def test_vendor_quote_update_empty_optional_fields(self):
        """Test VendorQuoteUpdate with empty optional fields."""
        data = {
            "items_text": "   ",  # Should be rejected as empty
            "status": None
        }

        with pytest.raises(ValidationError) as exc_info:
            VendorQuoteUpdate(**data)
        assert "items_text" in str(exc_info.value)

    def test_vendor_quote_response_model(self):
        """Test VendorQuoteResponse model."""
        data = {
            "id": 1001,
            "quote_id": 1,
            "vendor_id": 2,
            "tracking_id": "VQ24-123",
            "items_text": "Test items",
            "delivery_requirements": None,
            "is_rush": False,
            "status": "approved",
            "quoted_amount": 15000.50,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-02T00:00:00",
            "vendor_name": "Test Vendor",
            "quote_name": "Test Quote"
        }

        response = VendorQuoteResponse(**data)
        assert response.id == 1001
        assert response.vendor_name == "Test Vendor"
        assert response.quote_name == "Test Quote"


class TestCustomerEnhancedModels:
    """Test enhanced customer Pydantic models."""

    def test_customer_base_enhanced_valid_data(self):
        """Test CustomerBaseEnhanced with valid data."""
        data = {
            "name": "Test Customer",
            "industry": "Technology",
            "status": "active",
            "address": "123 Main St",
            "city": "Test City",
            "state": "CA",
            "zip": "12345",
            "sales_rep_name": "John Doe",
            "sales_rep_email": "john.doe@example.com"
        }

        customer = CustomerBaseEnhanced(**data)
        assert customer.name == "Test Customer"
        assert customer.address == "123 Main St"
        assert customer.city == "Test City"
        assert customer.state == "CA"
        assert customer.zip == "12345"
        assert customer.sales_rep_name == "John Doe"
        assert customer.sales_rep_email == "john.doe@example.com"

    def test_customer_base_enhanced_optional_fields(self):
        """Test CustomerBaseEnhanced with optional fields."""
        data = {
            "name": "Test Customer",
            "industry": "Technology",
            "status": "active"
        }

        customer = CustomerBaseEnhanced(**data)
        assert customer.address is None
        assert customer.city is None
        assert customer.state is None
        assert customer.zip is None
        assert customer.sales_rep_name is None
        assert customer.sales_rep_email is None

    def test_customer_base_enhanced_invalid_zip(self):
        """Test CustomerBaseEnhanced with invalid ZIP code."""
        data = {
            "name": "Test Customer",
            "industry": "Technology",
            "status": "active",
            "zip": "invalid-zip"
        }

        with pytest.raises(ValidationError) as exc_info:
            CustomerBaseEnhanced(**data)
        assert "zip" in str(exc_info.value)

    def test_customer_base_enhanced_invalid_email(self):
        """Test CustomerBaseEnhanced with invalid email."""
        data = {
            "name": "Test Customer",
            "industry": "Technology",
            "status": "active",
            "sales_rep_email": "invalid-email"
        }

        with pytest.raises(ValidationError) as exc_info:
            CustomerBaseEnhanced(**data)
        assert "sales_rep_email" in str(exc_info.value)

    def test_customer_base_enhanced_whitespace_handling(self):
        """Test CustomerBaseEnhanced whitespace handling."""
        data = {
            "name": "Test Customer",
            "industry": "Technology",
            "status": "active",
            "address": "  123 Main St  ",
            "city": "  Test City  ",
            "state": "  CA  ",
            "zip": "  12345  ",
            "sales_rep_name": "  John Doe  ",
            "sales_rep_email": "  john.doe@example.com  "
        }

        customer = CustomerBaseEnhanced(**data)
        assert customer.address == "123 Main St"
        assert customer.city == "Test City"
        assert customer.state == "CA"
        assert customer.zip == "12345"
        assert customer.sales_rep_name == "John Doe"
        assert customer.sales_rep_email == "john.doe@example.com"

    def test_customer_create_enhanced_model(self):
        """Test CustomerCreateEnhanced model."""
        data = {
            "name": "Test Customer",
            "industry": "Technology",
            "status": "active",
            "created_date": "2024-01-01"
        }

        customer = CustomerCreateEnhanced(**data)
        assert customer.name == "Test Customer"
        assert customer.created_at is None
        assert customer.updated_at is None

    def test_customer_update_enhanced_model(self):
        """Test CustomerUpdateEnhanced model."""
        data = {
            "name": "Updated Customer",
            "address": "456 Oak Ave",
            "sales_rep_email": "updated@example.com"
        }

        update = CustomerUpdateEnhanced(**data)
        assert update.name == "Updated Customer"
        assert update.address == "456 Oak Ave"
        assert update.sales_rep_email == "updated@example.com"

    def test_customer_update_enhanced_empty_fields(self):
        """Test CustomerUpdateEnhanced with empty string fields."""
        data = {
            "name": "  ",  # Should be set to None
            "address": "  ",  # Should be set to None
            "sales_rep_email": "  "  # Should be set to None
        }

        update = CustomerUpdateEnhanced(**data)
        assert update.name is None
        assert update.address is None
        assert update.sales_rep_email is None

    def test_customer_response_enhanced_model(self):
        """Test CustomerResponseEnhanced model."""
        data = {
            "id": 1,
            "name": "Test Customer",
            "industry": "Technology",
            "status": "active",
            "address": "123 Main St",
            "city": "Test City",
            "state": "CA",
            "zip": "12345",
            "created_date": "2024-01-01",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-02T00:00:00",
            "project_count": 5
        }

        response = CustomerResponseEnhanced(**data)
        assert response.id == 1
        assert response.project_count == 5


class TestProjectEnhancedModels:
    """Test enhanced project Pydantic models."""

    def test_project_base_enhanced_valid_data(self):
        """Test ProjectBaseEnhanced with valid data."""
        data = {
            "name": "Test Project",
            "budget": 100000.00,
            "status": "in_progress",
            "start_date": "2024-01-01",
            "project_type": "installation",
            "target_delivery_date": "2024-06-30"
        }

        project = ProjectBaseEnhanced(**data)
        assert project.name == "Test Project"
        assert project.budget == 100000.00
        assert project.status == "in_progress"
        assert project.start_date == "2024-01-01"
        assert project.project_type == "installation"
        assert project.target_delivery_date == "2024-06-30"

    def test_project_base_enhanced_invalid_project_type(self):
        """Test ProjectBaseEnhanced with invalid project type."""
        data = {
            "name": "Test Project",
            "budget": 100000.00,
            "status": "in_progress",
            "start_date": "2024-01-01",
            "project_type": "invalid_type"
        }

        with pytest.raises(ValidationError) as exc_info:
            ProjectBaseEnhanced(**data)
        assert "project_type" in str(exc_info.value)

    def test_project_base_enhanced_invalid_date_format(self):
        """Test ProjectBaseEnhanced with invalid date format."""
        data = {
            "name": "Test Project",
            "budget": 100000.00,
            "status": "in_progress",
            "start_date": "2024/01/01",  # Invalid format
            "project_type": "installation"
        }

        with pytest.raises(ValidationError) as exc_info:
            ProjectBaseEnhanced(**data)
        assert "start_date" in str(exc_info.value)

    def test_project_create_enhanced_model(self):
        """Test ProjectCreateEnhanced model."""
        data = {
            "name": "Test Project",
            "budget": 100000.00,
            "status": "planning",
            "start_date": "2024-01-01",
            "project_type": "repair",
            "customer_id": 1
        }

        project = ProjectCreateEnhanced(**data)
        assert project.customer_id == 1
        assert project.created_at is None
        assert project.updated_at is None

    def test_project_update_enhanced_model(self):
        """Test ProjectUpdateEnhanced model."""
        data = {
            "name": "Updated Project",
            "budget": 150000.00,
            "project_type": "maintenance"
        }

        update = ProjectUpdateEnhanced(**data)
        assert update.name == "Updated Project"
        assert update.budget == 150000.00
        assert update.project_type == "maintenance"

    def test_project_response_enhanced_model(self):
        """Test ProjectResponseEnhanced model."""
        data = {
            "id": 101,
            "customer_id": 1,
            "name": "Test Project",
            "budget": 100000.00,
            "status": "completed",
            "start_date": "2024-01-01",
            "project_type": "installation",
            "target_delivery_date": "2024-06-30",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-02T00:00:00",
            "quote_count": 3
        }

        response = ProjectResponseEnhanced(**data)
        assert response.id == 101
        assert response.customer_id == 1
        assert response.quote_count == 3


class TestVendorEnhancedModels:
    """Test enhanced vendor Pydantic models."""

    def test_vendor_base_enhanced_valid_data(self):
        """Test VendorBaseEnhanced with valid data."""
        data = {
            "name": "Test Vendor",
            "contact_name": "John Doe",
            "email": "john.doe@vendor.com",
            "specialty": "Electronics",
            "rating": 4.5
        }

        vendor = VendorBaseEnhanced(**data)
        assert vendor.name == "Test Vendor"
        assert vendor.contact_name == "John Doe"
        assert vendor.email == "john.doe@vendor.com"
        assert vendor.specialty == "Electronics"
        assert vendor.rating == 4.5

    def test_vendor_base_enhanced_invalid_rating(self):
        """Test VendorBaseEnhanced with invalid rating."""
        data = {
            "name": "Test Vendor",
            "specialty": "Electronics",
            "rating": 6.0  # Invalid rating (> 5.0)
        }

        with pytest.raises(ValidationError) as exc_info:
            VendorBaseEnhanced(**data)
        assert "rating" in str(exc_info.value)

    def test_vendor_base_enhanced_invalid_email(self):
        """Test VendorBaseEnhanced with invalid email."""
        data = {
            "name": "Test Vendor",
            "specialty": "Electronics",
            "rating": 4.5,
            "email": "invalid-email"
        }

        with pytest.raises(ValidationError) as exc_info:
            VendorBaseEnhanced(**data)
        assert "email" in str(exc_info.value)

    def test_vendor_create_enhanced_model(self):
        """Test VendorCreateEnhanced model."""
        data = {
            "name": "Test Vendor",
            "specialty": "Electronics",
            "rating": 4.5
        }

        vendor = VendorCreateEnhanced(**data)
        assert vendor.created_at is None
        assert vendor.updated_at is None

    def test_vendor_update_enhanced_model(self):
        """Test VendorUpdateEnhanced model."""
        data = {
            "contact_name": "Updated Contact",
            "email": "updated@vendor.com",
            "rating": 4.8
        }

        update = VendorUpdateEnhanced(**data)
        assert update.contact_name == "Updated Contact"
        assert update.email == "updated@vendor.com"
        assert update.rating == 4.8

    def test_vendor_response_enhanced_model(self):
        """Test VendorResponseEnhanced model."""
        data = {
            "id": 1,
            "name": "Test Vendor",
            "contact_name": "John Doe",
            "email": "john.doe@vendor.com",
            "specialty": "Electronics",
            "rating": 4.5,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-02T00:00:00"
        }

        response = VendorResponseEnhanced(**data)
        assert response.id == 1
        assert response.name == "Test Vendor"


class TestQuoteEnhancedModels:
    """Test enhanced quote Pydantic models."""

    def test_quote_base_enhanced_valid_data(self):
        """Test QuoteBaseEnhanced with valid data."""
        data = {
            "name": "Test Quote",
            "amount": 50000.00,
            "status": "approved",
            "valid_until": "2024-12-31",
            "description": "Test quote description"
        }

        quote = QuoteBaseEnhanced(**data)
        assert quote.name == "Test Quote"
        assert quote.amount == 50000.00
        assert quote.status == "approved"
        assert quote.valid_until == "2024-12-31"
        assert quote.description == "Test quote description"

    def test_quote_base_enhanced_optional_description(self):
        """Test QuoteBaseEnhanced with optional description."""
        data = {
            "name": "Test Quote",
            "amount": 50000.00,
            "status": "approved",
            "valid_until": "2024-12-31"
        }

        quote = QuoteBaseEnhanced(**data)
        assert quote.description is None

    def test_quote_base_enhanced_description_whitespace(self):
        """Test QuoteBaseEnhanced description whitespace handling."""
        data = {
            "name": "Test Quote",
            "amount": 50000.00,
            "status": "approved",
            "valid_until": "2024-12-31",
            "description": "  Test description  "
        }

        quote = QuoteBaseEnhanced(**data)
        assert quote.description == "Test description"

    def test_quote_create_enhanced_model(self):
        """Test QuoteCreateEnhanced model."""
        data = {
            "name": "Test Quote",
            "amount": 50000.00,
            "status": "draft",
            "valid_until": "2024-12-31",
            "project_id": 1
        }

        quote = QuoteCreateEnhanced(**data)
        assert quote.project_id == 1
        assert quote.created_at is None
        assert quote.updated_at is None

    def test_quote_update_enhanced_model(self):
        """Test QuoteUpdateEnhanced model."""
        data = {
            "amount": 60000.00,
            "status": "approved",
            "description": "Updated description"
        }

        update = QuoteUpdateEnhanced(**data)
        assert update.amount == 60000.00
        assert update.status == "approved"
        assert update.description == "Updated description"

    def test_quote_response_enhanced_model(self):
        """Test QuoteResponseEnhanced model."""
        data = {
            "id": 1001,
            "project_id": 1,
            "name": "Test Quote",
            "amount": 50000.00,
            "status": "approved",
            "valid_until": "2024-12-31",
            "description": "Test description",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-02T00:00:00",
            "freight_request_count": 2
        }

        response = QuoteResponseEnhanced(**data)
        assert response.id == 1001
        assert response.project_id == 1
        assert response.freight_request_count == 2


class TestBaseResponseModels:
    """Test base response models."""

    def test_base_response_model(self):
        """Test BaseResponse model."""
        response = BaseResponse()
        assert response.success is True
        assert response.message is None

    def test_base_response_with_data(self):
        """Test BaseResponse with data."""
        response = BaseResponse(message="Success message")
        assert response.success is True
        assert response.message == "Success message"

    def test_error_response_model(self):
        """Test ErrorResponse model."""
        response = ErrorResponse(error="Test error", details={"field": "value"})
        assert response.success is False
        assert response.error == "Test error"
        assert response.details == {"field": "value"}

    def test_create_response_model(self):
        """Test CreateResponse model."""
        response = CreateResponse(message="Created successfully", data={"id": 1})
        assert response.success is True
        assert response.message == "Created successfully"
        assert response.data == {"id": 1}

    def test_update_response_model(self):
        """Test UpdateResponse model."""
        response = UpdateResponse(message="Updated successfully", data={"id": 1})
        assert response.success is True
        assert response.message == "Updated successfully"
        assert response.data == {"id": 1}

    def test_delete_response_model(self):
        """Test DeleteResponse model."""
        response = DeleteResponse(message="Deleted successfully")
        assert response.success is True
        assert response.message == "Deleted successfully"


class TestModelValidationEdgeCases:
    """Test edge cases and boundary conditions for model validation."""

    def test_maximum_amount_values(self):
        """Test maximum amount values."""
        # Test vendor quote with maximum amount
        vendor_quote_data = {
            "quote_id": 1,
            "vendor_id": 2,
            "tracking_id": "VQ24-123",
            "items_text": "Test items",
            "status": "approved",
            "quoted_amount": MAX_QUOTED_AMOUNT
        }
        vendor_quote = VendorQuoteBase(**vendor_quote_data)
        assert vendor_quote.quoted_amount == MAX_QUOTED_AMOUNT

        # Test project with maximum budget
        project_data = {
            "name": "Test Project",
            "budget": MAX_BUDGET,
            "status": "planning",
            "start_date": "2024-01-01",
            "project_type": "installation"
        }
        project = ProjectBaseEnhanced(**project_data)
        assert project.budget == MAX_BUDGET

    def test_minimum_amount_values(self):
        """Test minimum amount values."""
        # Test vendor quote with minimum amount
        vendor_quote_data = {
            "quote_id": 1,
            "vendor_id": 2,
            "tracking_id": "VQ24-123",
            "items_text": "Test items",
            "status": "approved",
            "quoted_amount": MIN_QUOTED_AMOUNT
        }
        vendor_quote = VendorQuoteBase(**vendor_quote_data)
        assert vendor_quote.quoted_amount == MIN_QUOTED_AMOUNT

    def test_maximum_string_lengths(self):
        """Test maximum string lengths."""
        # Test customer name at maximum length
        customer_data = {
            "name": "A" * MAX_NAME_LENGTH,
            "industry": "Technology",
            "status": "active"
        }
        customer = CustomerBaseEnhanced(**customer_data)
        assert len(customer.name) == MAX_NAME_LENGTH

        # Test vendor specialty at maximum length
        vendor_data = {
            "name": "Test Vendor",
            "specialty": "A" * MAX_SPECIALTY_LENGTH,
            "rating": 4.5
        }
        vendor = VendorBaseEnhanced(**vendor_data)
        assert len(vendor.specialty) == MAX_SPECIALTY_LENGTH

    def test_leap_year_dates(self):
        """Test leap year date validation."""
        # Valid leap year date
        project_data = {
            "name": "Test Project",
            "budget": 100000.00,
            "status": "planning",
            "start_date": "2024-02-29",  # Leap day
            "project_type": "installation"
        }
        project = ProjectBaseEnhanced(**project_data)
        assert project.start_date == "2024-02-29"

        # Invalid leap year date
        invalid_project_data = {
            "name": "Test Project",
            "budget": 100000.00,
            "status": "planning",
            "start_date": "2023-02-29",  # Not a leap year
            "project_type": "installation"
        }
        with pytest.raises(ValidationError) as exc_info:
            ProjectBaseEnhanced(**invalid_project_data)
        assert "start_date" in str(exc_info.value)

    def test_negative_ids(self):
        """Test validation of negative IDs."""
        vendor_quote_data = {
            "quote_id": -1,  # Invalid negative ID
            "vendor_id": 2,
            "tracking_id": "VQ24-123",
            "items_text": "Test items",
            "status": "pending"
        }
        with pytest.raises(ValidationError) as exc_info:
            VendorQuoteBase(**vendor_quote_data)
        assert "quote_id" in str(exc_info.value)

    def test_zero_ids(self):
        """Test validation of zero IDs."""
        vendor_quote_data = {
            "quote_id": 0,  # Invalid zero ID
            "vendor_id": 2,
            "tracking_id": "VQ24-123",
            "items_text": "Test items",
            "status": "pending"
        }
        with pytest.raises(ValidationError) as exc_info:
            VendorQuoteBase(**vendor_quote_data)
        assert "quote_id" in str(exc_info.value)


class TestModelSerialization:
    """Test model serialization and deserialization."""

    def test_vendor_quote_serialization(self):
        """Test VendorQuote model serialization."""
        data = {
            "id": 1001,
            "quote_id": 1,
            "vendor_id": 2,
            "tracking_id": "VQ24-123",
            "items_text": "Test items",
            "delivery_requirements": None,
            "is_rush": False,
            "status": "approved",
            "quoted_amount": 15000.50,
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-02T00:00:00",
            "vendor_name": "Test Vendor",
            "quote_name": "Test Quote"
        }

        vendor_quote = VendorQuoteResponse(**data)
        serialized = vendor_quote.model_dump()

        assert serialized["id"] == 1001
        assert serialized["tracking_id"] == "VQ24-123"
        assert serialized["is_rush"] is False
        assert serialized["quoted_amount"] == 15000.50

        # Test deserialization back to model
        deserialized = VendorQuoteResponse(**serialized)
        assert deserialized.id == vendor_quote.id
        assert deserialized.tracking_id == vendor_quote.tracking_id

    def test_enhanced_customer_serialization(self):
        """Test enhanced customer model serialization."""
        data = {
            "id": 1,
            "name": "Test Customer",
            "industry": "Technology",
            "status": "active",
            "address": "123 Main St",
            "city": "Test City",
            "state": "CA",
            "zip": "12345",
            "sales_rep_name": "John Doe",
            "sales_rep_email": "john.doe@example.com",
            "created_date": "2024-01-01",
            "created_at": "2024-01-01T00:00:00",
            "updated_at": "2024-01-02T00:00:00",
            "project_count": 5
        }

        customer = CustomerResponseEnhanced(**data)
        serialized = customer.model_dump()

        assert serialized["id"] == 1
        assert serialized["address"] == "123 Main St"
        assert serialized["sales_rep_email"] == "john.doe@example.com"
        assert serialized["project_count"] == 5

        # Test deserialization
        deserialized = CustomerResponseEnhanced(**serialized)
        assert deserialized.id == customer.id
        assert deserialized.address == customer.address