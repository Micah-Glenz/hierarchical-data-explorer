"""
Shared test fixtures and utilities for API tests.

This module provides common test fixtures, mock data, and utility functions
used across all API test modules.
"""

import json
import tempfile
from pathlib import Path
from typing import Dict, Any, List
from unittest.mock import Mock, AsyncMock, patch
import pytest
from fastapi.testclient import TestClient

from src.main import app
from src.core.database import DatabaseManager
from src.core.config import Settings


@pytest.fixture
def client():
    """Create a test client for the FastAPI application."""
    return TestClient(app)


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for test data files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_db_manager(temp_data_dir):
    """Create a mock database manager with temporary directory."""
    # Create mock settings
    mock_settings = Mock(spec=Settings)
    mock_settings.DATA_DIR = temp_data_dir

    # Create database manager with mocked settings
    db_manager = DatabaseManager()
    db_manager.settings = mock_settings

    # Create test data files
    test_data = {
        "customers.json": [
            {"id": 1, "name": "Test Customer", "industry": "Technology", "status": "active",
             "created_date": "2024-01-01", "project_count": 2, "is_deleted": False, "deleted_at": None},
            {"id": 2, "name": "Another Customer", "industry": "Manufacturing", "status": "active",
             "created_date": "2024-01-15", "project_count": 1, "is_deleted": False, "deleted_at": None}
        ],
        "projects.json": [
            {"id": 101, "customer_id": 1, "name": "Test Project 1", "status": "active",
             "budget": 100000, "start_date": "2024-02-01", "quote_count": 2, "is_deleted": False, "deleted_at": None},
            {"id": 102, "customer_id": 1, "name": "Test Project 2", "status": "planning",
             "budget": 50000, "start_date": "2024-03-01", "quote_count": 1, "is_deleted": False, "deleted_at": None},
            {"id": 201, "customer_id": 2, "name": "Another Project", "status": "completed",
             "budget": 75000, "start_date": "2024-01-20", "quote_count": 0, "is_deleted": False, "deleted_at": None}
        ],
        "quotes.json": [
            {"id": 1001, "project_id": 101, "name": "Test Quote 1", "status": "active",
             "amount": 25000, "valid_until": "2024-06-30", "freight_request_count": 1, "is_deleted": False, "deleted_at": None},
            {"id": 1002, "project_id": 101, "name": "Test Quote 2", "status": "planning",
             "amount": 15000, "valid_until": "2024-07-15", "freight_request_count": 0, "is_deleted": False, "deleted_at": None},
            {"id": 1003, "project_id": 102, "name": "Test Quote 3", "status": "active",
             "amount": 20000, "valid_until": "2024-08-31", "freight_request_count": 0, "is_deleted": False, "deleted_at": None}
        ],
        "freight_requests.json": [
            {"id": 10001, "quote_id": 1001, "name": "Test Freight Request 1", "vendor_id": 1,
             "status": "active", "weight": 100, "priority": "medium", "estimated_delivery": "2024-05-01",
             "is_deleted": False, "deleted_at": None}
        ],
        "vendors.json": [
            {"id": 1, "name": "Test Vendor", "specialty": "Electronics", "rating": 4.5},
            {"id": 2, "name": "Another Vendor", "specialty": "Logistics", "rating": 4.2}
        ]
    }

    # Write test data files
    for filename, data in test_data.items():
        file_path = temp_data_dir / filename
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)

    return db_manager


@pytest.fixture
def mock_settings():
    """Create a mock settings object."""
    settings = Mock(spec=Settings)
    settings.DATA_DIR = Path("test_data")
    settings.HOST = "0.0.0.0"
    settings.PORT = 8001
    settings.DEBUG = False
    return settings


@pytest.fixture
def sample_customer_data():
    """Sample customer data for testing."""
    return {
        "id": 1,
        "name": "Test Customer",
        "industry": "Technology",
        "status": "active",
        "created_date": "2024-01-01",
        "project_count": 2
    }


@pytest.fixture
def sample_project_data():
    """Sample project data for testing."""
    return {
        "id": 101,
        "customer_id": 1,
        "name": "Test Project",
        "budget": 100000,
        "status": "active",
        "start_date": "2024-02-01",
        "quote_count": 2
    }


@pytest.fixture
def sample_quote_data():
    """Sample quote data for testing."""
    return {
        "id": 1001,
        "project_id": 101,
        "name": "Test Quote",
        "amount": 25000,
        "status": "active",
        "valid_until": "2024-06-30",
        "freight_request_count": 1
    }


@pytest.fixture
def sample_freight_request_data():
    """Sample freight request data for testing."""
    return {
        "id": 10001,
        "quote_id": 1001,
        "name": "Test Freight Request",
        "vendor_id": 1,
        "status": "active",
        "weight": 100,
        "priority": "medium",
        "estimated_delivery": "2024-05-01"
    }


@pytest.fixture
def create_project_request():
    """Valid project creation request."""
    return {
        "name": "New Test Project",
        "budget": 150000,
        "status": "active",
        "start_date": "2024-03-01",
        "customer_id": 1
    }


@pytest.fixture
def update_project_request():
    """Valid project update request."""
    return {
        "name": "Updated Project Name",
        "budget": 175000,
        "status": "in_progress",
        "start_date": "2024-03-15"
    }


class TestDatabaseManager:
    """Mock database manager for testing."""

    def __init__(self, temp_data_dir: Path):
        self.temp_data_dir = temp_data_dir
        self.data = self._load_test_data()

    def _load_test_data(self) -> Dict[str, List[Dict]]:
        """Load test data into memory."""
        return {
            "customers.json": [
                {"id": 1, "name": "Test Customer", "industry": "Technology", "status": "active",
                 "created_date": "2024-01-01", "project_count": 2, "is_deleted": False, "deleted_at": None},
                {"id": 2, "name": "Another Customer", "industry": "Manufacturing", "status": "active",
                 "created_date": "2024-01-15", "project_count": 1, "is_deleted": False, "deleted_at": None}
            ],
            "projects.json": [
                {"id": 101, "customer_id": 1, "name": "Test Project 1", "status": "active",
                 "budget": 100000, "start_date": "2024-02-01", "quote_count": 2, "is_deleted": False, "deleted_at": None},
                {"id": 102, "customer_id": 1, "name": "Test Project 2", "status": "planning",
                 "budget": 50000, "start_date": "2024-03-01", "quote_count": 1, "is_deleted": False, "deleted_at": None},
                {"id": 201, "customer_id": 2, "name": "Another Project", "status": "completed",
                 "budget": 75000, "start_date": "2024-01-20", "quote_count": 0, "is_deleted": False, "deleted_at": None}
            ],
            "quotes.json": [
                {"id": 1001, "project_id": 101, "name": "Test Quote 1", "status": "active",
                 "amount": 25000, "valid_until": "2024-06-30", "freight_request_count": 1, "is_deleted": False, "deleted_at": None},
                {"id": 1002, "project_id": 101, "name": "Test Quote 2", "status": "planning",
                 "amount": 15000, "valid_until": "2024-07-15", "freight_request_count": 0, "is_deleted": False, "deleted_at": None},
                {"id": 1003, "project_id": 102, "name": "Test Quote 3", "status": "active",
                 "amount": 20000, "valid_until": "2024-08-31", "freight_request_count": 0, "is_deleted": False, "deleted_at": None}
            ],
            "freight_requests.json": [
                {"id": 10001, "quote_id": 1001, "name": "Test Freight Request 1", "vendor_id": 1,
                 "status": "active", "weight": 100, "priority": "medium", "estimated_delivery": "2024-05-01",
                 "is_deleted": False, "deleted_at": None}
            ],
            "vendors.json": [
                {"id": 1, "name": "Test Vendor", "specialty": "Electronics", "rating": 4.5},
                {"id": 2, "name": "Another Vendor", "specialty": "Logistics", "rating": 4.2}
            ]
        }

    def find_by_id(self, filename: str, item_id: int, include_deleted: bool = False) -> Dict[str, Any] | None:
        """Find item by ID."""
        items = self.data.get(filename, [])
        for item in items:
            if item.get("id") == item_id:
                if include_deleted or not item.get("is_deleted", False):
                    return item.copy()
        return None

    def filter_by_field(self, filename: str, field: str, value: Any, include_deleted: bool = False) -> List[Dict[str, Any]]:
        """Filter items by field value."""
        items = self.data.get(filename, [])
        filtered_items = []
        for item in items:
            if item.get(field) == value:
                if include_deleted or not item.get("is_deleted", False):
                    filtered_items.append(item.copy())
        return filtered_items

    def get_next_id(self, filename: str) -> int:
        """Get next available ID."""
        items = self.data.get(filename, [])
        if not items:
            return 1
        max_id = max(item.get("id", 0) for item in items)
        return max_id + 1

    def append_item(self, filename: str, item: Dict[str, Any]) -> bool:
        """Append new item."""
        if filename not in self.data:
            self.data[filename] = []
        self.data[filename].append(item)
        return True

    def update_by_id(self, filename: str, item_id: int, updates: Dict[str, Any]) -> bool:
        """Update item by ID."""
        items = self.data.get(filename, [])
        for i, item in enumerate(items):
            if item.get("id") == item_id and not item.get("is_deleted", False):
                for key, value in updates.items():
                    if value is not None:
                        items[i][key] = value
                return True
        return False

    def soft_delete_by_id(self, filename: str, item_id: int) -> bool:
        """Soft delete item by ID."""
        items = self.data.get(filename, [])
        for item in items:
            if item.get("id") == item_id and not item.get("is_deleted", False):
                item["is_deleted"] = True
                return True
        return False


@pytest.fixture
def test_db_manager(temp_data_dir):
    """Create test database manager."""
    return TestDatabaseManager(temp_data_dir)


# Utility functions for tests
def assert_project_response(actual: Dict, expected: Dict):
    """Assert project response structure."""
    assert actual["id"] == expected["id"]
    assert actual["customer_id"] == expected["customer_id"]
    assert actual["name"] == expected["name"]
    assert actual["budget"] == expected["budget"]
    assert actual["status"] == expected["status"]
    assert actual["start_date"] == expected["start_date"]
    assert "quote_count" in actual


def assert_error_response(response, expected_status_code: int, expected_error_msg: str):
    """Assert error response structure."""
    assert response.status_code == expected_status_code
    data = response.json()
    assert data["success"] is False
    assert expected_error_msg.lower() in data["error"].lower()