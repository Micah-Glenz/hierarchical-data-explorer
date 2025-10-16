"""
Common dependencies for the Hierarchical Data Explorer API.

This module contains shared dependencies, utilities, and middleware
used across different API routes.
"""

from typing import List, Dict, Any, Optional

from ..core.database import get_database
from ..core.config import get_settings


def get_database_manager():
    """
    Dependency function to get the database manager.

    Returns:
        Database manager instance
    """
    return get_database()


def get_settings_manager():
    """
    Dependency function to get the settings manager.

    Returns:
        Settings manager instance
    """
    return get_settings()


async def validate_customer_exists(customer_id: int) -> bool:
    """
    Validate that a customer exists.

    Args:
        customer_id: ID of the customer to validate

    Returns:
        True if customer exists, False otherwise
    """
    db = get_database()
    customer = db.find_by_id("customers.json", customer_id)
    return customer is not None


async def validate_project_exists(project_id: int) -> bool:
    """
    Validate that a project exists.

    Args:
        project_id: ID of the project to validate

    Returns:
        True if project exists, False otherwise
    """
    db = get_database()
    project = db.find_by_id("projects.json", project_id)
    return project is not None


async def validate_quote_exists(quote_id: int) -> bool:
    """
    Validate that a quote exists.

    Args:
        quote_id: ID of the quote to validate

    Returns:
        True if quote exists, False otherwise
    """
    db = get_database()
    quote = db.find_by_id("quotes.json", quote_id)
    return quote is not None


async def validate_vendor_exists(vendor_id: int) -> bool:
    """
    Validate that a vendor exists.

    Args:
        vendor_id: ID of the vendor to validate

    Returns:
        True if vendor exists, False otherwise
    """
    db = get_database()
    vendor = db.find_by_id("vendors.json", vendor_id)
    return vendor is not None


def enrich_freight_requests(freight_requests: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Enrich freight requests with vendor names.

    Args:
        freight_requests: List of freight request dictionaries

    Returns:
        List of enriched freight requests with vendor names
    """
    db = get_database()
    vendors = db.find_all("vendors.json")
    vendor_map = {v["id"]: v["name"] for v in vendors}

    enriched_requests = []
    for fr in freight_requests:
        fr_copy = fr.copy()
        fr_copy["vendor_name"] = vendor_map.get(fr["vendor_id"], "Unknown Vendor")
        enriched_requests.append(fr_copy)

    return enriched_requests


def calculate_item_counts(entity_type: str, parent_id: Optional[int] = None) -> Dict[int, int]:
    """
    Calculate item counts for entities.

    Args:
        entity_type: Type of entity ('projects', 'quotes', 'freight_requests', 'customers')
        parent_id: Optional parent ID to filter entities. When provided, only counts
                 for entities belonging to this parent are calculated.
                 For 'projects': parent_id is customer_id to filter projects by customer
                 For 'quotes': parent_id is project_id to filter quotes by project
                 For 'customers': parent_id is ignored (customers have no parents)
                 For 'freight_requests': parent_id is ignored (no children)

    Returns:
        Dictionary mapping entity IDs to their child counts
    """
    db = get_database()
    counts = {}

    if entity_type == "projects":
        # Count quotes for each project
        if parent_id is not None:
            # Filter projects by customer_id first
            projects = db.filter_by_field("projects.json", "customer_id", parent_id)
        else:
            projects = db.find_all("projects.json")

        for project in projects:
            quote_count = len(db.filter_by_field("quotes.json", "project_id", project["id"]))
            counts[project["id"]] = quote_count

    elif entity_type == "quotes":
        # Count freight requests for each quote
        if parent_id is not None:
            # Filter quotes by project_id first
            quotes = db.filter_by_field("quotes.json", "project_id", parent_id)
        else:
            quotes = db.find_all("quotes.json")

        for quote in quotes:
            fr_count = len(db.filter_by_field("freight_requests.json", "quote_id", quote["id"]))
            counts[quote["id"]] = fr_count

    elif entity_type == "freight_requests":
        # Freight requests don't have children
        pass

    elif entity_type == "customers":
        # Count projects for each customer (parent_id is ignored for customers)
        customers = db.find_all("customers.json")
        for customer in customers:
            project_count = len(db.filter_by_field("projects.json", "customer_id", customer["id"]))
            counts[customer["id"]] = project_count

    return counts

def get_valid_industries() -> List[str]:
    """
    Get list of valid industries.

    Returns:
        List of valid industry names
    """
    return [
        "Technology",
        "Manufacturing",
        "Retail",
        "Healthcare",
        "Logistics",
        "Finance",
        "Construction",
        "Energy"
    ]


def get_valid_statuses() -> List[str]:
    """
    Get list of valid statuses.

    Returns:
        List of valid status values
    """
    return ["active", "planning", "in_progress", "on_hold", "completed"]


def get_valid_priorities() -> List[str]:
    """
    Get list of valid priorities.

    Returns:
        List of valid priority values
    """
    return ["low", "medium", "high", "critical"]


def validate_choice(value: str, choices: List[str], field_name: str) -> str:
    """
    Validate a choice field.

    Args:
        value: Value to validate
        choices: List of valid choices
        field_name: Name of the field for error messages

    Returns:
        Validated choice value

    Raises:
        ValueError: If validation fails
    """
    if value not in choices:
        raise ValueError(f"{field_name} must be one of: {', '.join(choices)}")
    return value


def format_error_response(message: str, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Format a standardized error response.

    Args:
        message: Error message
        details: Additional error details

    Returns:
        Formatted error response dictionary
    """
    return {
        "success": False,
        "error": message,
        "details": details or {}
    }


def format_success_response(message: str, data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Format a standardized success response.

    Args:
        message: Success message
        data: Response data

    Returns:
        Formatted success response dictionary
    """
    response = {
        "success": True,
        "message": message
    }
    if data:
        response["data"] = data
    return response


class ValidationHelper:
    """
    Helper class for common validation operations.
    """

    @staticmethod
    def validate_required_string(value: str, field_name: str) -> str:
        """
        Validate a required string field.

        Args:
            value: String value to validate
            field_name: Name of the field for error messages

        Returns:
            Validated string value

        Raises:
            ValueError: If validation fails
        """
        if not value or not value.strip():
            raise ValueError(f"{field_name} is required")
        return value.strip()

    @staticmethod
    def validate_positive_number(value: float, field_name: str, max_value: Optional[float] = None) -> float:
        """
        Validate a positive number field.

        Args:
            value: Number value to validate
            field_name: Name of the field for error messages
            max_value: Maximum allowed value (optional)

        Returns:
            Validated number value

        Raises:
            ValueError: If validation fails
        """
        if value <= 0:
            raise ValueError(f"{field_name} must be greater than 0")
        if max_value and value > max_value:
            raise ValueError(f"{field_name} cannot exceed {max_value}")
        return value

    @staticmethod
    def validate_date_string(date_str: str, field_name: str) -> str:
        """
        Validate a date string.

        Args:
            date_str: Date string to validate
            field_name: Name of the field for error messages

        Returns:
            Validated date string

        Raises:
            ValueError: If validation fails
        """
        if not date_str or not date_str.strip():
            raise ValueError(f"{field_name} cannot be empty")

        try:
            from datetime import datetime
            datetime.strptime(date_str.strip(), '%Y-%m-%d')
            return date_str.strip()
        except ValueError:
            raise ValueError(f"{field_name} must be in YYYY-MM-DD format")

    @staticmethod
    def validate_choice(value: str, choices: List[str], field_name: str) -> str:
        """
        Validate a choice field.

        Args:
            value: Value to validate
            choices: List of valid choices
            field_name: Name of the field for error messages

        Returns:
            Validated choice value

        Raises:
            ValueError: If validation fails
        """
        if value not in choices:
            raise ValueError(f"{field_name} must be one of: {', '.join(choices)}")
        return value