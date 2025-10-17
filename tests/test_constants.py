"""
Test suite for constants and validation patterns.

This module tests all validation constants, enums, and validation functions
to ensure they work correctly and cover all expected use cases.
"""

import pytest
import re
from src.core.constants import (
    # Enums
    ProjectType, ProjectStatus, QuoteStatus, VendorQuoteStatus,
    CustomerStatus, FreightPriority,

    # Choice lists
    PROJECT_TYPE_CHOICES, PROJECT_STATUS_CHOICES, QUOTE_STATUS_CHOICES,
    VENDOR_QUOTE_STATUS_CHOICES, CUSTOMER_STATUS_CHOICES, FREIGHT_PRIORITY_CHOICES,

    # Validation functions
    get_valid_project_types, get_valid_project_statuses, get_valid_quote_statuses,
    get_valid_vendor_quote_statuses, get_valid_customer_statuses, get_valid_freight_priorities,

    # Validation patterns
    validate_email, validate_zip_code, validate_phone, validate_tracking_id,
    validate_name_length, validate_description_length,

    # Field constraints
    MAX_NAME_LENGTH, MAX_DESCRIPTION_LENGTH, MAX_EMAIL_LENGTH, MAX_PHONE_LENGTH,
    MAX_ZIP_LENGTH, MAX_ADDRESS_LENGTH, MAX_CITY_LENGTH, MAX_STATE_LENGTH,
    MAX_SPECIALTY_LENGTH, MAX_ITEMS_TEXT_LENGTH, MAX_DELIVERY_REQUIREMENTS_LENGTH,

    # Amount constraints
    MIN_BUDGET, MAX_BUDGET, MIN_AMOUNT, MAX_AMOUNT, MIN_WEIGHT, MAX_WEIGHT,
    MIN_QUOTED_AMOUNT, MAX_QUOTED_AMOUNT,

    # Tracking ID generation
    generate_tracking_id,

    # Error messages
    VALIDATION_ERROR_MESSAGES
)


class TestProjectTypeConstants:
    """Test project type constants and validation."""

    def test_project_type_enum_values(self):
        """Test that ProjectType enum has expected values."""
        expected_types = ["installation", "repair", "maintenance", "consulting", "other"]
        actual_types = [ptype.value for ptype in ProjectType]
        assert sorted(actual_types) == sorted(expected_types)

    def test_project_type_choices_format(self):
        """Test that PROJECT_TYPE_CHOICES has correct format."""
        assert isinstance(PROJECT_TYPE_CHOICES, list)
        assert len(PROJECT_TYPE_CHOICES) == 5

        for choice in PROJECT_TYPE_CHOICES:
            assert isinstance(choice, tuple)
            assert len(choice) == 2
            assert isinstance(choice[0], str)  # value
            assert isinstance(choice[1], str)  # display name
            assert choice[0] in [ptype.value for ptype in ProjectType]

    def test_get_valid_project_types(self):
        """Test get_valid_project_types returns all expected types."""
        types = get_valid_project_types()
        assert isinstance(types, list)
        assert len(types) == 5
        assert "installation" in types
        assert "repair" in types
        assert "maintenance" in types
        assert "consulting" in types
        assert "other" in types


class TestProjectStatusConstants:
    """Test project status constants and validation."""

    def test_project_status_enum_values(self):
        """Test that ProjectStatus enum has expected values."""
        expected_statuses = ["planning", "in_progress", "on_hold", "completed", "cancelled"]
        actual_statuses = [status.value for status in ProjectStatus]
        assert sorted(actual_statuses) == sorted(expected_statuses)

    def test_project_status_choices_format(self):
        """Test that PROJECT_STATUS_CHOICES has correct format."""
        assert isinstance(PROJECT_STATUS_CHOICES, list)
        assert len(PROJECT_STATUS_CHOICES) == 5

        for choice in PROJECT_STATUS_CHOICES:
            assert isinstance(choice, tuple)
            assert len(choice) == 2
            assert isinstance(choice[0], str)
            assert isinstance(choice[1], str)
            assert choice[0] in [status.value for status in ProjectStatus]

    def test_get_valid_project_statuses(self):
        """Test get_valid_project_statuses returns all expected statuses."""
        statuses = get_valid_project_statuses()
        assert isinstance(statuses, list)
        assert len(statuses) == 5
        assert "planning" in statuses
        assert "in_progress" in statuses
        assert "on_hold" in statuses
        assert "completed" in statuses
        assert "cancelled" in statuses


class TestQuoteStatusConstants:
    """Test quote status constants and validation."""

    def test_quote_status_enum_values(self):
        """Test that QuoteStatus enum has expected values."""
        expected_statuses = ["draft", "pending_freight", "ready", "sent", "approved", "declined"]
        actual_statuses = [status.value for status in QuoteStatus]
        assert sorted(actual_statuses) == sorted(expected_statuses)

    def test_quote_status_choices_format(self):
        """Test that QUOTE_STATUS_CHOICES has correct format."""
        assert isinstance(QUOTE_STATUS_CHOICES, list)
        assert len(QUOTE_STATUS_CHOICES) == 6

        for choice in QUOTE_STATUS_CHOICES:
            assert isinstance(choice, tuple)
            assert len(choice) == 2
            assert isinstance(choice[0], str)
            assert isinstance(choice[1], str)
            assert choice[0] in [status.value for status in QuoteStatus]

    def test_get_valid_quote_statuses(self):
        """Test get_valid_quote_statuses returns all expected statuses."""
        statuses = get_valid_quote_statuses()
        assert isinstance(statuses, list)
        assert len(statuses) == 6
        assert "draft" in statuses
        assert "pending_freight" in statuses
        assert "ready" in statuses
        assert "sent" in statuses
        assert "approved" in statuses
        assert "declined" in statuses


class TestVendorQuoteStatusConstants:
    """Test vendor quote status constants and validation."""

    def test_vendor_quote_status_enum_values(self):
        """Test that VendorQuoteStatus enum has expected values."""
        expected_statuses = ["pending", "quoted", "approved", "rejected", "completed"]
        actual_statuses = [status.value for status in VendorQuoteStatus]
        assert sorted(actual_statuses) == sorted(expected_statuses)

    def test_vendor_quote_status_choices_format(self):
        """Test that VENDOR_QUOTE_STATUS_CHOICES has correct format."""
        assert isinstance(VENDOR_QUOTE_STATUS_CHOICES, list)
        assert len(VENDOR_QUOTE_STATUS_CHOICES) == 5

        for choice in VENDOR_QUOTE_STATUS_CHOICES:
            assert isinstance(choice, tuple)
            assert len(choice) == 2
            assert isinstance(choice[0], str)
            assert isinstance(choice[1], str)
            assert choice[0] in [status.value for status in VendorQuoteStatus]

    def test_get_valid_vendor_quote_statuses(self):
        """Test get_valid_vendor_quote_statuses returns all expected statuses."""
        statuses = get_valid_vendor_quote_statuses()
        assert isinstance(statuses, list)
        assert len(statuses) == 5
        assert "pending" in statuses
        assert "quoted" in statuses
        assert "approved" in statuses
        assert "rejected" in statuses
        assert "completed" in statuses


class TestCustomerStatusConstants:
    """Test customer status constants and validation."""

    def test_customer_status_enum_values(self):
        """Test that CustomerStatus enum has expected values."""
        expected_statuses = ["active", "inactive", "prospect"]
        actual_statuses = [status.value for status in CustomerStatus]
        assert sorted(actual_statuses) == sorted(expected_statuses)

    def test_customer_status_choices_format(self):
        """Test that CUSTOMER_STATUS_CHOICES has correct format."""
        assert isinstance(CUSTOMER_STATUS_CHOICES, list)
        assert len(CUSTOMER_STATUS_CHOICES) == 3

        for choice in CUSTOMER_STATUS_CHOICES:
            assert isinstance(choice, tuple)
            assert len(choice) == 2
            assert isinstance(choice[0], str)
            assert isinstance(choice[1], str)
            assert choice[0] in [status.value for status in CustomerStatus]

    def test_get_valid_customer_statuses(self):
        """Test get_valid_customer_statuses returns all expected statuses."""
        statuses = get_valid_customer_statuses()
        assert isinstance(statuses, list)
        assert len(statuses) == 3
        assert "active" in statuses
        assert "inactive" in statuses
        assert "prospect" in statuses


class TestFreightPriorityConstants:
    """Test freight priority constants and validation."""

    def test_freight_priority_enum_values(self):
        """Test that FreightPriority enum has expected values."""
        expected_priorities = ["low", "medium", "high", "urgent"]
        actual_priorities = [priority.value for priority in FreightPriority]
        assert sorted(actual_priorities) == sorted(expected_priorities)

    def test_freight_priority_choices_format(self):
        """Test that FREIGHT_PRIORITY_CHOICES has correct format."""
        assert isinstance(FREIGHT_PRIORITY_CHOICES, list)
        assert len(FREIGHT_PRIORITY_CHOICES) == 4

        for choice in FREIGHT_PRIORITY_CHOICES:
            assert isinstance(choice, tuple)
            assert len(choice) == 2
            assert isinstance(choice[0], str)
            assert isinstance(choice[1], str)
            assert choice[0] in [priority.value for priority in FreightPriority]

    def test_get_valid_freight_priorities(self):
        """Test get_valid_freight_priorities returns all expected priorities."""
        priorities = get_valid_freight_priorities()
        assert isinstance(priorities, list)
        assert len(priorities) == 4
        assert "low" in priorities
        assert "medium" in priorities
        assert "high" in priorities
        assert "urgent" in priorities


class TestEmailValidation:
    """Test email validation function."""

    def test_valid_emails(self):
        """Test valid email addresses."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "user+tag@example.org",
            "user123@test-domain.com",
            "firstname.lastname@company.com",
            "a@b.co",
            "test.email.with+symbol@example.com"
        ]

        for email in valid_emails:
            assert validate_email(email), f"Should be valid: {email}"

    def test_invalid_emails(self):
        """Test invalid email addresses."""
        invalid_emails = [
            "",
            "invalid-email",
            "@example.com",
            "test@",
            "test..test@example.com",
            "test@example",
            "test space@example.com",
            "test@.com",
            "test@com.",
            "test@.example.com",
            "test@example..com"
        ]

        for email in invalid_emails:
            assert not validate_email(email), f"Should be invalid: {email}"

    def test_email_length_validation(self):
        """Test email length validation."""
        # Test maximum length (@example.com is 12 chars)
        max_length_email = "a" * (MAX_EMAIL_LENGTH - 12) + "@example.com"
        assert validate_email(max_length_email)

        # Test exceeding maximum length
        too_long_email = "a" * (MAX_EMAIL_LENGTH - 11) + "@example.com"
        assert not validate_email(too_long_email)


class TestZipCodeValidation:
    """Test ZIP code validation function."""

    def test_valid_zip_codes(self):
        """Test valid ZIP codes."""
        valid_zips = [
            "12345",
            "12345-6789",
            "90210",
            "10001-1234"
        ]

        for zip_code in valid_zips:
            assert validate_zip_code(zip_code), f"Should be valid: {zip_code}"

    def test_invalid_zip_codes(self):
        """Test invalid ZIP codes."""
        invalid_zips = [
            "",
            "1234",
            "123456",
            "12345-678",
            "12345-67890",
            "abcde",
            "12-345",
            "12345-67a9"
        ]

        for zip_code in invalid_zips:
            assert not validate_zip_code(zip_code), f"Should be invalid: {zip_code}"

    def test_zip_code_length_validation(self):
        """Test ZIP code length validation."""
        # Test maximum length
        max_length_zip = "12345-6789"
        assert len(max_length_zip) <= MAX_ZIP_LENGTH
        assert validate_zip_code(max_length_zip)

        # Test exceeding maximum length
        too_long_zip = "12345-67890"
        assert len(too_long_zip) > MAX_ZIP_LENGTH
        assert not validate_zip_code(too_long_zip)


class TestPhoneValidation:
    """Test phone validation function."""

    def test_valid_phone_numbers(self):
        """Test valid phone numbers."""
        valid_phones = [
            "(212) 555-1234",
            "212-555-1234",
            "212.555.1234",
            "+1 (212) 555-1234",
            "2125551234"
        ]

        for phone in valid_phones:
            assert validate_phone(phone), f"Should be valid: {phone}"

    def test_invalid_phone_numbers(self):
        """Test invalid phone numbers."""
        invalid_phones = [
            "",
            "123",
            "123-456",
            "(212) 555-123",
            "abc-def-ghij",
            "212 555 1234",
            "1-212-555-1234"
        ]

        for phone in invalid_phones:
            assert not validate_phone(phone), f"Should be invalid: {phone}"


class TestTrackingIdValidation:
    """Test tracking ID validation function."""

    def test_valid_tracking_ids(self):
        """Test valid tracking IDs."""
        valid_ids = [
            "VQ24-1",
            "VQ25-123",
            "VQ23-9999",
            "VQ20-100"
        ]

        for tracking_id in valid_ids:
            assert validate_tracking_id(tracking_id), f"Should be valid: {tracking_id}"

    def test_invalid_tracking_ids(self):
        """Test invalid tracking IDs."""
        invalid_ids = [
            "",
            "VQ24",
            "24-1",
            "VQ-1",
            "VQ24-",
            "VQ24-ABC",
            "VQ2A-1",
            "VQ24-1A"
        ]

        for tracking_id in invalid_ids:
            assert not validate_tracking_id(tracking_id), f"Should be invalid: {tracking_id}"


class TestTrackingIdGeneration:
    """Test tracking ID generation function."""

    def test_tracking_id_generation_format(self):
        """Test tracking ID generation produces correct format."""
        tracking_id = generate_tracking_id(2024, 1)
        assert tracking_id == "VQ24-1"

        tracking_id = generate_tracking_id(2025, 123)
        assert tracking_id == "VQ25-123"

        tracking_id = generate_tracking_id(1999, 9999)
        assert tracking_id == "VQ99-9999"

    def test_tracking_id_generation_edge_cases(self):
        """Test tracking ID generation edge cases."""
        # Year 2000
        tracking_id = generate_tracking_id(2000, 1)
        assert tracking_id == "VQ00-1"

        # Year 2099
        tracking_id = generate_tracking_id(2099, 1)
        assert tracking_id == "VQ99-1"

        # Large sequence number
        tracking_id = generate_tracking_id(2024, 999999)
        assert tracking_id == "VQ24-999999"


class TestNameLengthValidation:
    """Test name length validation function."""

    def test_valid_name_lengths(self):
        """Test valid name lengths."""
        valid_names = [
            "A",
            "Test Name",
            "A" * MAX_NAME_LENGTH
        ]

        for name in valid_names:
            assert validate_name_length(name), f"Should be valid: '{name}'"

    def test_invalid_name_lengths(self):
        """Test invalid name lengths."""
        invalid_names = [
            "",
            " " * 5,  # Empty with spaces
            "A" * (MAX_NAME_LENGTH + 1)
        ]

        for name in invalid_names:
            assert not validate_name_length(name), f"Should be invalid: '{name}'"


class TestDescriptionLengthValidation:
    """Test description length validation function."""

    def test_valid_description_lengths(self):
        """Test valid description lengths."""
        valid_descriptions = [
            "",
            "Short description",
            "A" * MAX_DESCRIPTION_LENGTH,
            None  # None should be valid
        ]

        for desc in valid_descriptions:
            assert validate_description_length(desc), f"Should be valid: '{desc}'"

    def test_invalid_description_lengths(self):
        """Test invalid description lengths."""
        invalid_desc = "A" * (MAX_DESCRIPTION_LENGTH + 1)
        assert not validate_description_length(invalid_desc)


class TestFieldConstraints:
    """Test field constraint constants."""

    def test_max_length_constants(self):
        """Test maximum length constants are reasonable."""
        assert MAX_NAME_LENGTH == 255
        assert MAX_DESCRIPTION_LENGTH == 1000
        assert MAX_EMAIL_LENGTH == 254
        assert MAX_PHONE_LENGTH == 20
        assert MAX_ZIP_LENGTH == 10
        assert MAX_ADDRESS_LENGTH == 255
        assert MAX_CITY_LENGTH == 100
        assert MAX_STATE_LENGTH == 50
        assert MAX_SPECIALTY_LENGTH == 100
        assert MAX_ITEMS_TEXT_LENGTH == 2000
        assert MAX_DELIVERY_REQUIREMENTS_LENGTH == 1000

    def test_amount_constraints(self):
        """Test amount constraint constants are reasonable."""
        assert MIN_BUDGET == 0.01
        assert MAX_BUDGET == 999999999.99
        assert MIN_AMOUNT == 0.01
        assert MAX_AMOUNT == 999999999.99
        assert MIN_WEIGHT == 0.01
        assert MAX_WEIGHT == 999999.99
        assert MIN_QUOTED_AMOUNT == 0.01
        assert MAX_QUOTED_AMOUNT == 999999999.99


class TestErrorMessages:
    """Test validation error messages."""

    def test_error_messages_exist(self):
        """Test that all expected error messages exist."""
        expected_keys = [
            "email_invalid",
            "zip_invalid",
            "phone_invalid",
            "tracking_id_invalid",
            "name_too_long",
            "name_too_short",
            "description_too_long",
            "budget_too_low",
            "budget_too_high",
            "amount_too_low",
            "amount_too_high",
            "weight_too_low",
            "weight_too_high",
            "quoted_amount_too_low",
            "quoted_amount_too_high",
            "project_type_invalid",
            "project_status_invalid",
            "quote_status_invalid",
            "vendor_quote_status_invalid",
            "customer_status_invalid",
            "freight_priority_invalid"
        ]

        for key in expected_keys:
            assert key in VALIDATION_ERROR_MESSAGES
            assert isinstance(VALIDATION_ERROR_MESSAGES[key], str)
            assert len(VALIDATION_ERROR_MESSAGES[key]) > 0


class TestChoiceValidationIntegration:
    """Test integration between different choice validation functions."""

    def test_no_duplicate_choices(self):
        """Test that no choice lists have duplicate values."""
        all_choices = [
            (get_valid_project_types(), "project_types"),
            (get_valid_project_statuses(), "project_statuses"),
            (get_valid_quote_statuses(), "quote_statuses"),
            (get_valid_vendor_quote_statuses(), "vendor_quote_statuses"),
            (get_valid_customer_statuses(), "customer_statuses"),
            (get_valid_freight_priorities(), "freight_priorities")
        ]

        for choices, name in all_choices:
            assert len(choices) == len(set(choices)), f"Duplicate values found in {name}"

    def test_choices_are_strings(self):
        """Test that all choice values are strings."""
        all_choices = [
            get_valid_project_types(),
            get_valid_project_statuses(),
            get_valid_quote_statuses(),
            get_valid_vendor_quote_statuses(),
            get_valid_customer_statuses(),
            get_valid_freight_priorities()
        ]

        for choices in all_choices:
            for choice in choices:
                assert isinstance(choice, str), f"Choice should be string: {choice}"
                assert len(choice.strip()) > 0, f"Choice should not be empty: '{choice}'"


class TestConstantConsistency:
    """Test consistency between constants and related functions."""

    def test_enum_values_match_choice_values(self):
        """Test that enum values match choice list values."""
        enum_choice_pairs = [
            (ProjectType, get_valid_project_types()),
            (ProjectStatus, get_valid_project_statuses()),
            (QuoteStatus, get_valid_quote_statuses()),
            (VendorQuoteStatus, get_valid_vendor_quote_statuses()),
            (CustomerStatus, get_valid_customer_statuses()),
            (FreightPriority, get_valid_freight_priorities())
        ]

        for enum_class, choice_values in enum_choice_pairs:
            enum_values = [member.value for member in enum_class]
            assert sorted(enum_values) == sorted(choice_values), \
                f"Mismatch between {enum_class.__name__} enum and choice values"

    def test_tracking_id_pattern_matches_validation(self):
        """Test that tracking ID pattern matches validation function."""
        from src.core.constants import TRACKING_ID_PATTERN

        # Test some valid IDs against both pattern and function
        valid_ids = ["VQ24-1", "VQ25-123", "VQ23-9999"]

        for tracking_id in valid_ids:
            # Test against regex pattern
            assert TRACKING_ID_PATTERN.match(tracking_id), f"Pattern should match: {tracking_id}"
            # Test against validation function
            assert validate_tracking_id(tracking_id), f"Function should accept: {tracking_id}"