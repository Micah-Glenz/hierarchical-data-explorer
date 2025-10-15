"""
Tests for Projects API routes.

This module contains comprehensive tests for all project-related endpoints,
including CRUD operations, validation, error handling, and business logic.
"""

import json
from unittest.mock import patch, AsyncMock
import pytest
from fastapi.testclient import TestClient

from src.api.routes.projects import router
from src.core.exceptions import DatabaseOperationError, DataNotFoundError


class TestProjectsAPI:
    """Test class for Projects API endpoints."""

    def test_get_projects_success(self, client, test_db_manager):
        """Test successful retrieval of projects for a customer."""
        # Mock the dependencies
        with patch('src.api.routes.projects.get_database_manager') as mock_get_db, \
             patch('src.api.routes.projects.validate_customer_exists') as mock_validate, \
             patch('src.api.routes.projects.calculate_item_counts') as mock_counts:

            # Setup mocks
            mock_get_db.return_value = test_db_manager
            mock_validate.return_value = True
            mock_counts.return_value = {101: 2, 102: 1}

            # Make request
            response = client.get("/api/projects/1")

            # Assertions
            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 2

            # Check first project
            project = data[0]
            assert project["id"] == 101
            assert project["customer_id"] == 1
            assert project["name"] == "Test Project 1"
            assert project["budget"] == 100000
            assert project["status"] == "active"
            assert project["quote_count"] == 2

            # Check second project
            project = data[1]
            assert project["id"] == 102
            assert project["quote_count"] == 1

    def test_get_projects_customer_not_found(self, client, test_db_manager):
        """Test GET projects when customer doesn't exist."""
        with patch('src.api.routes.projects.get_database_manager') as mock_get_db, \
             patch('src.api.routes.projects.validate_customer_exists') as mock_validate, \
             patch('src.api.routes.projects.calculate_item_counts') as mock_counts:

            mock_get_db.return_value = test_db_manager
            mock_validate.return_value = False

            response = client.get("/api/projects/999")

            assert response.status_code == 404
            data = response.json()
            assert data["success"] is False
            assert "not found" in data["error"].lower()

    def test_get_projects_database_error(self, client, test_db_manager):
        """Test GET projects with database error."""
        with patch('src.api.routes.projects.get_database_manager') as mock_get_db, \
             patch('src.api.routes.projects.validate_customer_exists') as mock_validate:

            mock_get_db.side_effect = Exception("Database connection failed")
            mock_validate.return_value = True

            response = client.get("/api/projects/1")

            assert response.status_code == 500
            data = response.json()
            assert data["success"] is False
            assert "failed to load projects" in data["error"].lower()

    def test_get_projects_empty_list(self, client, test_db_manager):
        """Test GET projects when customer has no projects."""
        # Create a customer with no projects
        test_db_manager.data["projects.json"] = []

        with patch('src.api.routes.projects.get_database_manager') as mock_get_db, \
             patch('src.api.routes.projects.validate_customer_exists') as mock_validate, \
             patch('src.api.routes.projects.calculate_item_counts') as mock_counts:

            mock_get_db.return_value = test_db_manager
            mock_validate.return_value = True
            mock_counts.return_value = {}

            response = client.get("/api/projects/1")

            assert response.status_code == 200
            data = response.json()
            assert isinstance(data, list)
            assert len(data) == 0

    def test_create_project_success(self, client, test_db_manager, create_project_request):
        """Test successful project creation."""
        with patch('src.api.routes.projects.get_database_manager') as mock_get_db, \
             patch('src.api.routes.projects.validate_customer_exists') as mock_validate:

            mock_get_db.return_value = test_db_manager
            mock_validate.return_value = True

            response = client.post("/api/projects/", json=create_project_request)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "project created successfully" in data["message"].lower()
            assert "data" in data

            project_data = data["data"]
            assert "id" in project_data
            assert project_data["name"] == create_project_request["name"]
            assert project_data["budget"] == create_project_request["budget"]
            assert project_data["customer_id"] == create_project_request["customer_id"]

    def test_create_project_customer_not_found(self, client, test_db_manager, create_project_request):
        """Test project creation when customer doesn't exist."""
        with patch('src.api.routes.projects.get_database_manager') as mock_get_db, \
             patch('src.api.routes.projects.validate_customer_exists') as mock_validate:

            mock_get_db.return_value = test_db_manager
            mock_validate.return_value = False

            response = client.post("/api/projects/", json=create_project_request)

            assert response.status_code == 400
            data = response.json()
            assert data["success"] is False
            assert "not found" in data["error"].lower()

    def test_create_project_validation_errors(self, client, test_db_manager):
        """Test project creation with various validation errors."""
        test_cases = [
            # Empty name
            {
                "name": "",
                "budget": 100000,
                "status": "active",
                "start_date": "2024-03-01",
                "customer_id": 1
            },
            # Negative budget
            {
                "name": "Test Project",
                "budget": -1000,
                "status": "active",
                "start_date": "2024-03-01",
                "customer_id": 1
            },
            # Invalid status
            {
                "name": "Test Project",
                "budget": 100000,
                "status": "invalid_status",
                "start_date": "2024-03-01",
                "customer_id": 1
            },
            # Invalid date format
            {
                "name": "Test Project",
                "budget": 100000,
                "status": "active",
                "start_date": "invalid-date",
                "customer_id": 1
            },
            # Missing required fields
            {
                "name": "Test Project"
                # Missing budget, status, start_date, customer_id
            }
        ]

        with patch('src.api.routes.projects.get_database_manager') as mock_get_db, \
             patch('src.api.routes.projects.validate_customer_exists') as mock_validate:

            mock_get_db.return_value = test_db_manager
            mock_validate.return_value = True

            for test_case in test_cases:
                response = client.post("/api/projects/", json=test_case)
                assert response.status_code in [400, 422], f"Failed for test case: {test_case}"
                data = response.json()
                assert data["success"] is False

    def test_create_project_database_error(self, client, test_db_manager, create_project_request):
        """Test project creation with database error."""
        with patch('src.api.routes.projects.get_database_manager') as mock_get_db, \
             patch('src.api.routes.projects.validate_customer_exists') as mock_validate:

            mock_db_instance = Mock()
            mock_db_instance.get_next_id.return_value = 999
            mock_db_instance.append_item.return_value = False
            mock_get_db.return_value = mock_db_instance
            mock_validate.return_value = True

            response = client.post("/api/projects/", json=create_project_request)

            assert response.status_code == 500
            data = response.json()
            assert data["success"] is False
            assert "failed to create project" in data["error"].lower()

    def test_update_project_success(self, client, test_db_manager, update_project_request):
        """Test successful project update."""
        with patch('src.api.routes.projects.get_database_manager') as mock_get_db:
            mock_get_db.return_value = test_db_manager

            response = client.put("/api/projects/101", json=update_project_request)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "project updated successfully" in data["message"].lower()
            assert "data" in data

            project_data = data["data"]
            assert project_data["id"] == 101
            assert project_data["name"] == update_project_request["name"]
            assert project_data["budget"] == update_project_request["budget"]
            assert project_data["status"] == update_project_request["status"]

    def test_update_project_not_found(self, client, test_db_manager, update_project_request):
        """Test update when project doesn't exist."""
        with patch('src.api.routes.projects.get_database_manager') as mock_get_db:
            mock_get_db.return_value = test_db_manager

            response = client.put("/api/projects/999", json=update_project_request)

            assert response.status_code == 404
            data = response.json()
            assert data["success"] is False
            assert "not found" in data["error"].lower()

    def test_update_project_partial_update(self, client, test_db_manager):
        """Test partial project update (only some fields)."""
        partial_update = {
            "name": "Partially Updated Project"
        }

        with patch('src.api.routes.projects.get_database_manager') as mock_get_db:
            mock_get_db.return_value = test_db_manager

            response = client.put("/api/projects/101", json=partial_update)

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True

            project_data = data["data"]
            assert project_data["name"] == "Partially Updated Project"
            # Other fields should remain unchanged
            assert project_data["budget"] == 100000  # Original value
            assert project_data["status"] == "active"  # Original value

    def test_update_project_validation_errors(self, client, test_db_manager):
        """Test project update with validation errors."""
        test_cases = [
            # Empty name
            {"name": ""},
            # Negative budget
            {"budget": -1000},
            # Invalid status
            {"status": "invalid_status"},
            # Invalid date
            {"start_date": "invalid-date"}
        ]

        with patch('src.api.routes.projects.get_database_manager') as mock_get_db:
            mock_get_db.return_value = test_db_manager

            for test_case in test_cases:
                response = client.put("/api/projects/101", json=test_case)
                assert response.status_code == 400, f"Failed for test case: {test_case}"
                data = response.json()
                assert data["success"] is False

    def test_update_project_database_error(self, client, test_db_manager, update_project_request):
        """Test project update with database error."""
        with patch('src.api.routes.projects.get_database_manager') as mock_get_db:
            mock_db_instance = Mock()
            mock_db_instance.find_by_id.return_value = {"id": 101, "name": "Test"}
            mock_db_instance.update_by_id.return_value = False
            mock_get_db.return_value = mock_db_instance

            response = client.put("/api/projects/101", json=update_project_request)

            assert response.status_code == 500
            data = response.json()
            assert data["success"] is False

    def test_delete_project_success(self, client, test_db_manager):
        """Test successful project deletion."""
        with patch('src.api.routes.projects.get_database_manager') as mock_get_db:
            mock_get_db.return_value = test_db_manager

            response = client.delete("/api/projects/101")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            assert "deleted successfully" in data["message"].lower()
            assert "deleted_project_id" in data

    def test_delete_project_not_found(self, client, test_db_manager):
        """Test delete when project doesn't exist."""
        with patch('src.api.routes.projects.get_database_manager') as mock_get_db:
            mock_get_db.return_value = test_db_manager

            response = client.delete("/api/projects/999")

            assert response.status_code == 404
            data = response.json()
            assert data["success"] is False
            assert "not found" in data["error"].lower()

    def test_delete_project_with_cascade(self, client, test_db_manager):
        """Test project deletion cascades to quotes and freight requests."""
        with patch('src.api.routes.projects.get_database_manager') as mock_get_db:
            mock_get_db.return_value = test_db_manager

            response = client.delete("/api/projects/101")

            assert response.status_code == 200
            data = response.json()
            assert data["success"] is True
            # Should mention cascade deletion
            assert "2 related quotes" in data["message"]

    def test_delete_project_database_error(self, client, test_db_manager):
        """Test project deletion with database error."""
        with patch('src.api.routes.projects.get_database_manager') as mock_get_db:
            mock_db_instance = Mock()
            mock_db_instance.find_by_id.return_value = {"id": 101}
            mock_db_instance.soft_delete_by_id.return_value = False
            mock_get_db.return_value = mock_db_instance

            response = client.delete("/api/projects/101")

            assert response.status_code == 500
            data = response.json()
            assert data["success"] is False


class TestProjectsAPIEdgeCases:
    """Test edge cases and boundary conditions for Projects API."""

    def test_create_project_maximum_budget(self, client, test_db_manager):
        """Test creating project with maximum allowed budget."""
        max_budget_project = {
            "name": "Maximum Budget Project",
            "budget": 999999999.99,
            "status": "active",
            "start_date": "2024-03-01",
            "customer_id": 1
        }

        with patch('src.api.routes.projects.get_database_manager') as mock_get_db, \
             patch('src.api.routes.projects.validate_customer_exists') as mock_validate:

            mock_get_db.return_value = test_db_manager
            mock_validate.return_value = True

            response = client.post("/api/projects/", json=max_budget_project)
            assert response.status_code == 200

    def test_create_project_budget_exceeds_limit(self, client, test_db_manager):
        """Test creating project with budget exceeding limit."""
        over_budget_project = {
            "name": "Over Budget Project",
            "budget": 1000000000.00,  # Exceeds limit
            "status": "active",
            "start_date": "2024-03-01",
            "customer_id": 1
        }

        with patch('src.api.routes.projects.get_database_manager') as mock_get_db, \
             patch('src.api.routes.projects.validate_customer_exists') as mock_validate:

            mock_get_db.return_value = test_db_manager
            mock_validate.return_value = True

            response = client.post("/api/projects/", json=over_budget_project)
            assert response.status_code == 400

    def test_create_project_minimum_budget(self, client, test_db_manager):
        """Test creating project with minimum positive budget."""
        min_budget_project = {
            "name": "Minimum Budget Project",
            "budget": 0.01,
            "status": "active",
            "start_date": "2024-03-01",
            "customer_id": 1
        }

        with patch('src.api.routes.projects.get_database_manager') as mock_get_db, \
             patch('src.api.routes.projects.validate_customer_exists') as mock_validate:

            mock_get_db.return_value = test_db_manager
            mock_validate.return_value = True

            response = client.post("/api/projects/", json=min_budget_project)
            assert response.status_code == 200

    def test_create_project_zero_budget(self, client, test_db_manager):
        """Test creating project with zero budget should fail."""
        zero_budget_project = {
            "name": "Zero Budget Project",
            "budget": 0,
            "status": "active",
            "start_date": "2024-03-01",
            "customer_id": 1
        }

        with patch('src.api.routes.projects.get_database_manager') as mock_get_db, \
             patch('src.api.routes.projects.validate_customer_exists') as mock_validate:

            mock_get_db.return_value = test_db_manager
            mock_validate.return_value = True

            response = client.post("/api/projects/", json=zero_budget_project)
            assert response.status_code == 400

    def test_create_project_invalid_customer_id(self, client, test_db_manager):
        """Test creating project with invalid customer ID."""
        invalid_project = {
            "name": "Invalid Customer Project",
            "budget": 100000,
            "status": "active",
            "start_date": "2024-03-01",
            "customer_id": 0  # Invalid ID
        }

        with patch('src.api.routes.projects.get_database_manager') as mock_get_db, \
             patch('src.api.routes.projects.validate_customer_exists') as mock_validate:

            mock_get_db.return_value = test_db_manager
            mock_validate.return_value = True

            response = client.post("/api/projects/", json=invalid_project)
            # This should be handled by Pydantic validation
            assert response.status_code == 422

    def test_update_non_existent_project(self, client, test_db_manager):
        """Test updating a project that doesn't exist."""
        update_data = {
            "name": "Updated Name"
        }

        with patch('src.api.routes.projects.get_database_manager') as mock_get_db:
            mock_get_db.return_value = test_db_manager

            response = client.put("/api/projects/99999", json=update_data)
            assert response.status_code == 404

    def test_get_projects_invalid_customer_id_format(self, client):
        """Test getting projects with invalid customer ID format."""
        response = client.get("/api/projects/invalid")
        # FastAPI should handle this as a validation error
        assert response.status_code == 422

    def test_update_project_invalid_id_format(self, client):
        """Test updating project with invalid ID format."""
        update_data = {"name": "Updated"}
        response = client.put("/api/projects/invalid", json=update_data)
        assert response.status_code == 422

    def test_delete_project_invalid_id_format(self, client):
        """Test deleting project with invalid ID format."""
        response = client.delete("/api/projects/invalid")
        assert response.status_code == 422

    def test_project_name_length_validation(self, client, test_db_manager):
        """Test project name length validation."""
        # Very long name (should fail)
        long_name = "a" * 256  # Exceeds typical length limits

        long_name_project = {
            "name": long_name,
            "budget": 100000,
            "status": "active",
            "start_date": "2024-03-01",
            "customer_id": 1
        }

        with patch('src.api.routes.projects.get_database_manager') as mock_get_db, \
             patch('src.api.routes.projects.validate_customer_exists') as mock_validate:

            mock_get_db.return_value = test_db_manager
            mock_validate.return_value = True

            response = client.post("/api/projects/", json=long_name_project)
            assert response.status_code == 400

    def test_project_edge_case_dates(self, client, test_db_manager):
        """Test project with edge case dates."""
        edge_case_project = {
            "name": "Edge Case Date Project",
            "budget": 100000,
            "status": "active",
            "start_date": "2024-02-29",  # Leap day (2024 is leap year)
            "customer_id": 1
        }

        with patch('src.api.routes.projects.get_database_manager') as mock_get_db, \
             patch('src.api.routes.projects.validate_customer_exists') as mock_validate:

            mock_get_db.return_value = test_db_manager
            mock_validate.return_value = True

            response = client.post("/api/projects/", json=edge_case_project)
            assert response.status_code == 200

    def test_project_status_valid_values(self, client, test_db_manager):
        """Test all valid status values."""
        valid_statuses = ['active', 'planning', 'in_progress', 'on_hold', 'completed']

        with patch('src.api.routes.projects.get_database_manager') as mock_get_db, \
             patch('src.api.routes.projects.validate_customer_exists') as mock_validate:

            mock_get_db.return_value = test_db_manager
            mock_validate.return_value = True

            for status in valid_statuses:
                project_data = {
                    "name": f"Test Project - {status}",
                    "budget": 100000,
                    "status": status,
                    "start_date": "2024-03-01",
                    "customer_id": 1
                }

                response = client.post("/api/projects/", json=project_data)
                assert response.status_code == 200, f"Failed for status: {status}"


class TestProjectsAPIIntegration:
    """Integration tests for Projects API."""

    def test_project_crud_lifecycle(self, client, test_db_manager):
        """Test complete CRUD lifecycle for a project."""
        project_data = {
            "name": "Lifecycle Test Project",
            "budget": 150000,
            "status": "planning",
            "start_date": "2024-04-01",
            "customer_id": 1
        }

        with patch('src.api.routes.projects.get_database_manager') as mock_get_db, \
             patch('src.api.routes.projects.validate_customer_exists') as mock_validate:

            mock_get_db.return_value = test_db_manager
            mock_validate.return_value = True

            # Create project
            create_response = client.post("/api/projects/", json=project_data)
            assert create_response.status_code == 200
            created_project = create_response.json()["data"]
            project_id = created_project["id"]

            # Read projects
            with patch('src.api.routes.projects.calculate_item_counts') as mock_counts:
                mock_counts.return_value = {project_id: 0}
                read_response = client.get(f"/api/projects/{project_data['customer_id']}")
                assert read_response.status_code == 200

                projects = read_response.json()
                created = next((p for p in projects if p["id"] == project_id), None)
                assert created is not None

            # Update project
            update_data = {"name": "Updated Lifecycle Project", "status": "active"}
            update_response = client.put(f"/api/projects/{project_id}", json=update_data)
            assert update_response.status_code == 200

            # Delete project
            delete_response = client.delete(f"/api/projects/{project_id}")
            assert delete_response.status_code == 200
            assert delete_response.json()["success"] is True

    def test_project_with_quotes_deletion_cascade(self, client, test_db_manager):
        """Test that project deletion cascades to related quotes and freight requests."""
        with patch('src.api.routes.projects.get_database_manager') as mock_get_db:
            mock_get_db.return_value = test_db_manager

            # Project 101 has 2 quotes, one of which has a freight request
            delete_response = client.delete("/api/projects/101")
            assert delete_response.status_code == 200

            data = delete_response.json()
            assert data["success"] is True
            # Should mention cascade deletion of quotes
            assert "2 related quotes" in data["message"]