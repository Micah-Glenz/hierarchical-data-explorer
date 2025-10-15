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

        # Collect quotes to delete before attempting cascade
        quotes = db.filter_by_field("quotes.json", "project_id", project_id)
        if not quotes:
            # No quotes to cascade, just delete project
            if db.soft_delete_by_id("projects.json", project_id):
                return format_success_response("Project deleted successfully", {"deleted_project_id": project_id})
            else:
                raise DatabaseOperationError("Failed to delete project", "delete", "projects.json")

        # Track failed deletions
        failed_quotes = []
        failed_frs = []
        deleted_quotes = 0
        deleted_frs = 0

        # First pass: Identify all dependent freight requests
        all_frs_to_delete = []
        for quote in quotes:
            frs = db.filter_by_field("freight_requests.json", "quote_id", quote["id"])
            all_frs_to_delete.extend(frs)

        # Attempt cascade deletion
        for quote in quotes:
            quote_id = quote["id"]
            # Delete dependent freight requests first
            frs = db.filter_by_field("freight_requests.json", "quote_id", quote_id)
            quote_failed = False

            for fr in frs:
                fr_id = fr["id"]
                if not db.soft_delete_by_id("freight_requests.json", fr_id):
                    failed_frs.append({
                        "id": fr_id,
                        "type": "freight_request",
                        "parent": f"quote_id={quote_id}"
                    })
                    quote_failed = True
                else:
                    deleted_frs += 1

            if not quote_failed:
                # Only delete quote if all freight requests were deleted successfully
                if not db.soft_delete_by_id("quotes.json", quote_id):
                    failed_quotes.append({
                        "id": quote_id,
                        "type": "quote",
                        "parent": f"project_id={project_id}"
                    })
                else:
                    deleted_quotes += 1

        # Check for failures and handle appropriately
        if failed_quotes or failed_frs:
            error_details = {
                "project_id": project_id,
                "failed_quotes": failed_quotes,
                "failed_freight_requests": failed_frs,
                "successful_deletions": {
                    "quotes": deleted_quotes,
                    "freight_requests": deleted_frs
                }
            }
            raise HTTPException(
                status_code=500,
                detail=format_error_response(
                    f"Cascade delete partially failed for project {project_id}. "
                    f"Failed to delete {len(failed_quotes)} quotes and {len(failed_frs)} freight requests.",
                    error_details
                )
            )

        # All cascade deletions successful - now delete the project
        if not db.soft_delete_by_id("projects.json", project_id):
            raise DatabaseOperationError("Failed to delete project", "delete", "projects.json")

        # Success - include counters in response
        total_items = deleted_quotes + deleted_frs
        message = (f"Project and {deleted_quotes} related quotes with {deleted_frs} freight requests "
                  f"deleted successfully ({total_items + 1} total items)")
        return format_success_response(
            message,
            {
                "deleted_project_id": project_id,
                "deletion_summary": {
                    "quotes": deleted_quotes,
                    "freight_requests": deleted_frs,
                    "total_items": total_items + 1  # +1 for the project
                }
            }
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=format_error_response("Failed to delete project", {"original_error": str(e)})
        )