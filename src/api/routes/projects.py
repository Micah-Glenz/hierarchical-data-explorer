"""
Project API routes for the Hierarchical Data Explorer.

This module contains all API endpoints related to project operations.
"""

from typing import List

from fastapi import APIRouter, HTTPException, Depends

from ..models import (
    ProjectCreate, ProjectUpdate, ProjectResponse,
    CreateResponse, UpdateResponse, DeleteResponse
)
from ..dependencies import (
    get_database_manager, ValidationHelper, get_valid_statuses,
    format_error_response, format_success_response, validate_customer_exists,
    calculate_item_counts
)
from ...core.exceptions import DataNotFoundError, DatabaseOperationError


router = APIRouter(
    prefix="/api/projects",
    tags=["projects"]
)


@router.get("/{customer_id}", response_model=List[ProjectResponse])
async def get_projects(customer_id: int, db=Depends(get_database_manager)):
    """Get all projects for a specific customer."""
    try:
        # Validate customer exists
        if not await validate_customer_exists(customer_id):
            raise HTTPException(
                status_code=404,
                detail=format_error_response(f"Customer with ID {customer_id} not found")
            )

        projects = db.filter_by_field("projects.json", "customer_id", customer_id)
        quote_counts = calculate_item_counts("projects", parent_id=customer_id)

        # Enrich projects with quote counts
        enriched_projects = []
        for project in projects:
            project_copy = project.copy()
            project_copy["quote_count"] = quote_counts.get(project["id"], 0)
            enriched_projects.append(project_copy)

        return enriched_projects

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=format_error_response("Failed to load projects", {"original_error": str(e)})
        )


@router.post("/", response_model=CreateResponse)
async def create_project(project: ProjectCreate, db=Depends(get_database_manager)):
    """Create a new project."""
    try:
        # Validate customer exists
        if not await validate_customer_exists(project.customer_id):
            raise HTTPException(
                status_code=400,
                detail=format_error_response(f"Customer with ID {project.customer_id} not found")
            )

        # Validate fields
        validated_name = ValidationHelper.validate_required_string(project.name, "Project name")
        validated_budget = ValidationHelper.validate_positive_number(project.budget, "Budget", 999999999.99)
        validated_status = ValidationHelper.validate_required_string(project.status, "Status")
        validated_date = ValidationHelper.validate_date_string(project.start_date, "Start date")
        ValidationHelper.validate_choice(validated_status, get_valid_statuses(), "Status")

        new_project = {
            "id": db.get_next_id("projects.json"),
            "name": validated_name,
            "budget": validated_budget,
            "status": validated_status,
            "start_date": validated_date,
            "customer_id": project.customer_id,
            "quote_count": 0
        }

        if db.append_item("projects.json", new_project):
            return format_success_response("Project created successfully", {"data": new_project})
        else:
            raise DatabaseOperationError("Failed to save project", "create", "projects.json")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=format_error_response("Failed to create project", {"original_error": str(e)})
        )


@router.put("/{project_id}", response_model=UpdateResponse)
async def update_project(project_id: int, project_update: ProjectUpdate, db=Depends(get_database_manager)):
    """Update an existing project."""
    try:
        # Check if project exists
        existing_project = db.find_by_id("projects.json", project_id)
        if not existing_project:
            raise HTTPException(
                status_code=404,
                detail=format_error_response(f"Project with ID {project_id} not found", {"resource_id": project_id})
            )

        # Prepare updates
        updates = {}
        if project_update.name is not None:
            updates["name"] = ValidationHelper.validate_required_string(project_update.name, "Project name")
        if project_update.budget is not None:
            updates["budget"] = ValidationHelper.validate_positive_number(project_update.budget, "Budget", 999999999.99)
        if project_update.status is not None:
            updates["status"] = ValidationHelper.validate_required_string(project_update.status, "Status")
            ValidationHelper.validate_choice(updates["status"], get_valid_statuses(), "Status")
        if project_update.start_date is not None:
            updates["start_date"] = ValidationHelper.validate_date_string(project_update.start_date, "Start date")

        if db.update_by_id("projects.json", project_id, updates):
            updated_project = db.find_by_id("projects.json", project_id)
            # Use parent filtering for efficiency
            quote_counts = calculate_item_counts("projects", parent_id=updated_project.get("customer_id"))
            updated_project["quote_count"] = quote_counts.get(project_id, 0)

            return format_success_response("Project updated successfully", {"data": updated_project})
        else:
            raise DatabaseOperationError("Failed to update project", "update", "projects.json")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=format_error_response("Failed to update project", {"original_error": str(e)})
        )


@router.delete("/{project_id}", response_model=DeleteResponse)
async def delete_project(project_id: int, db=Depends(get_database_manager)):
    """Delete a project (soft delete with cascade)."""
    try:
        existing_project = db.find_by_id("projects.json", project_id)
        if not existing_project:
            raise HTTPException(
                status_code=404,
                detail=format_error_response(f"Project with ID {project_id} not found", {"resource_id": project_id})
            )

        # Soft delete project
        if db.soft_delete_by_id("projects.json", project_id):
            # Cascade delete to quotes
            quotes = db.filter_by_field("quotes.json", "project_id", project_id)
            deleted_quotes = 0
            for quote in quotes:
                if db.soft_delete_by_id("quotes.json", quote["id"]):
                    deleted_quotes += 1
                    # Cascade delete to freight requests
                    frs = db.filter_by_field("freight_requests.json", "quote_id", quote["id"])
                    deleted_frs = sum(1 for fr in frs if db.soft_delete_by_id("freight_requests.json", fr["id"]))

            message = f"Project and {deleted_quotes} related quotes deleted successfully"
            return format_success_response(message, {"deleted_project_id": project_id})
        else:
            raise DatabaseOperationError("Failed to delete project", "delete", "projects.json")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=format_error_response("Failed to delete project", {"original_error": str(e)})
        )