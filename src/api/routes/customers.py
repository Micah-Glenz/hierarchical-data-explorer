"""
Customer API routes for the Hierarchical Data Explorer.

This module contains all API endpoints related to customer operations
including CRUD operations and business logic validation.
"""

from datetime import datetime
from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from ..models import (
    CustomerCreate, CustomerUpdate, CustomerResponse,
    CreateResponse, UpdateResponse, DeleteResponse
)
from ..dependencies import (
    get_database_manager, ValidationHelper,
    validate_choice, get_valid_industries, get_valid_statuses,
    format_error_response, format_success_response,
    calculate_item_counts
)
from ...core.exceptions import (
    DataValidationError, DataNotFoundError,
    DatabaseOperationError, BusinessRuleViolationError
)


router = APIRouter(
    prefix="/api/customers",
    tags=["customers"]
)


@router.get("/", response_model=List[CustomerResponse])
async def get_customers(db=Depends(get_database_manager)):
    """
    Get all customers.

    Returns a list of all active customers (excluding soft-deleted items).

    Args:
        db: Database manager dependency

    Returns:
        List of customer dictionaries

    Raises:
        DatabaseOperationError: If data cannot be loaded
    """
    try:
        customers = db.find_all("customers.json")
        project_counts = calculate_item_counts("customers")

        # Enrich customers with project counts
        enriched_customers = []
        for customer in customers:
            customer_copy = customer.copy()
            customer_copy["project_count"] = project_counts.get(customer["id"], 0)
            enriched_customers.append(customer_copy)

        return enriched_customers

    except DatabaseOperationError as e:
        raise HTTPException(
            status_code=500,
            detail=format_error_response("Failed to load customers", {"original_error": str(e)})
        )


@router.post("/", response_model=CreateResponse)
async def create_customer(
    customer: CustomerCreate,
    db=Depends(get_database_manager)
):
    """
    Create a new customer.

    Creates a new customer with validation and business logic checks.

    Args:
        customer: Customer creation data
        db: Database manager dependency

    Returns:
        Success response with created customer data

    Raises:
        HTTPException: If validation fails or creation error occurs
    """
    try:
        # Validate required fields
        validated_name = ValidationHelper.validate_required_string(customer.name, "Customer name")
        validated_industry = ValidationHelper.validate_required_string(customer.industry, "Industry")
        validated_status = ValidationHelper.validate_required_string(customer.status, "Status")
        validated_date = ValidationHelper.validate_date_string(customer.created_date, "Created date")

        # Validate choices
        validate_choice(validated_industry, get_valid_industries(), "Industry")
        validate_choice(validated_status, get_valid_statuses(), "Status")

        # Create new customer
        new_customer = {
            "id": db.get_next_id("customers.json"),
            "name": validated_name,
            "industry": validated_industry,
            "status": validated_status,
            "created_date": validated_date,
            "project_count": 0
        }

        if db.append_item("customers.json", new_customer):
            return format_success_response("Customer created successfully", {"data": new_customer})
        else:
            raise DatabaseOperationError("Failed to save customer", "create", "customers.json")

    except (DataValidationError, ValueError) as e:
        raise HTTPException(
            status_code=400,
            detail=format_error_response(str(e))
        )
    except DatabaseOperationError as e:
        raise HTTPException(
            status_code=500,
            detail=format_error_response("Failed to create customer", {"original_error": str(e)})
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=format_error_response("Internal server error", {"original_error": str(e)})
        )


@router.get("/{customer_id}", response_model=CustomerResponse)
async def get_customer(
    customer_id: int,
    db=Depends(get_database_manager)
):
    """
    Get a specific customer by ID.

    Args:
        customer_id: ID of the customer to retrieve
        db: Database manager dependency

    Returns:
        Customer data

    Raises:
        HTTPException: If customer is not found
    """
    try:
        customer = db.find_by_id("customers.json", customer_id)
        if not customer:
            raise DataNotFoundError(
                f"Customer with ID {customer_id} not found",
                "customer",
                customer_id
            )

        # Enrich with project count
        project_counts = calculate_item_counts("customers")
        customer["project_count"] = project_counts.get(customer["id"], 0)

        return customer

    except DataNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=format_error_response(str(e), {"resource_id": customer_id})
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=format_error_response("Failed to retrieve customer", {"original_error": str(e)})
        )


@router.put("/{customer_id}", response_model=UpdateResponse)
async def update_customer(
    customer_id: int,
    customer_update: CustomerUpdate,
    db=Depends(get_database_manager)
):
    """
    Update an existing customer.

    Updates customer data with validation for only the provided fields.

    Args:
        customer_id: ID of the customer to update
        customer_update: Customer update data
        db: Database manager dependency

    Returns:
        Success response with updated customer data

    Raises:
        HTTPException: If customer is not found or validation fails
    """
    try:
        # Check if customer exists
        existing_customer = db.find_by_id("customers.json", customer_id)
        if not existing_customer:
            raise DataNotFoundError(
                f"Customer with ID {customer_id} not found",
                "customer",
                customer_id
            )

        # Prepare updates with validation
        updates = {}
        if customer_update.name is not None:
            updates["name"] = ValidationHelper.validate_required_string(
                customer_update.name, "Customer name"
            )
        if customer_update.industry is not None:
            updates["industry"] = ValidationHelper.validate_required_string(
                customer_update.industry, "Industry"
            )
            validate_choice(updates["industry"], get_valid_industries(), "Industry")
        if customer_update.status is not None:
            updates["status"] = ValidationHelper.validate_required_string(
                customer_update.status, "Status"
            )
            validate_choice(updates["status"], get_valid_statuses(), "Status")

        # Update customer
        if db.update_by_id("customers.json", customer_id, updates):
            # Get updated customer
            updated_customer = db.find_by_id("customers.json", customer_id)
            project_counts = calculate_item_counts("customers")
            updated_customer["project_count"] = project_counts.get(customer_id, 0)

            return format_success_response("Customer updated successfully", {"data": updated_customer})
        else:
            raise DatabaseOperationError("Failed to update customer", "update", "customers.json")

    except DataNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=format_error_response(str(e), {"resource_id": customer_id})
        )
    except (DataValidationError, ValueError) as e:
        raise HTTPException(
            status_code=400,
            detail=format_error_response(str(e))
        )
    except DatabaseOperationError as e:
        raise HTTPException(
            status_code=500,
            detail=format_error_response("Failed to update customer", {"original_error": str(e)})
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=format_error_response("Internal server error", {"original_error": str(e)})
        )


@router.delete("/{customer_id}", response_model=DeleteResponse)
async def delete_customer(
    customer_id: int,
    db=Depends(get_database_manager)
):
    """
    Delete a customer (soft delete with cascade).

    Soft deletes a customer and cascades the deletion to all related
    projects, quotes, and freight requests.

    Args:
        customer_id: ID of the customer to delete
        db: Database manager dependency

    Returns:
        Success response with deletion details

    Raises:
        HTTPException: If customer is not found or deletion fails
    """
    try:
        # Check if customer exists
        existing_customer = db.find_by_id("customers.json", customer_id)
        if not existing_customer:
            raise DataNotFoundError(
                f"Customer with ID {customer_id} not found",
                "customer",
                customer_id
            )

        # Check for cascade implications
        projects = db.filter_by_field("projects.json", "customer_id", customer_id)

        if not projects:
            # No projects to cascade, just delete customer
            if db.soft_delete_by_id("customers.json", customer_id):
                return format_success_response("Customer deleted successfully", {
                    "deleted_customer_id": customer_id
                })
            else:
                raise DatabaseOperationError("Failed to delete customer", "delete", "customers.json")

        # Projects exist - perform cascade delete with proper error handling and counter tracking
        deleted_projects = 0
        deleted_quotes = 0
        deleted_freight_requests = 0
        failed_deletions = []

        # First pass: Identify all items to be deleted for verification
        projects_to_delete = projects
        total_projects = len(projects_to_delete)

        # Track all dependent items before deletion
        all_quotes_to_delete = []
        all_frs_to_delete = []

        for project in projects_to_delete:
            quotes = db.filter_by_field("quotes.json", "project_id", project["id"])
            all_quotes_to_delete.extend(quotes)
            for quote in quotes:
                frs = db.filter_by_field("freight_requests.json", "quote_id", quote["id"])
                all_frs_to_delete.extend(frs)

        # Mark customer as deleted first
        if not db.soft_delete_by_id("customers.json", customer_id):
            raise DatabaseOperationError("Failed to delete customer", "delete", "customers.json")

        # Attempt cascade deletion with rollback on failure
        try:
            # Delete projects and their dependents
            for project in projects_to_delete:
                project_id = project["id"]
                project_failed = False

                # Delete dependent quotes first
                quotes = db.filter_by_field("quotes.json", "project_id", project_id)
                for quote in quotes:
                    quote_id = quote["id"]
                    quote_failed = False

                    # Delete dependent freight requests
                    frs = db.filter_by_field("freight_requests.json", "quote_id", quote_id)
                    for fr in frs:
                        fr_id = fr["id"]
                        if not db.soft_delete_by_id("freight_requests.json", fr_id):
                            failed_deletions.append({
                                "type": "freight_request",
                                "id": fr_id,
                                "parent": f"quote_id={quote_id}",
                                "operation": "soft_delete_by_id",
                                "file": "freight_requests.json"
                            })
                            quote_failed = True
                            project_failed = True

                    if not quote_failed:
                        # Only increment counter if all freight requests were deleted successfully
                        deleted_freight_requests += len(frs)

                        # Delete the quote
                        if not db.soft_delete_by_id("quotes.json", quote_id):
                            failed_deletions.append({
                                "type": "quote",
                                "id": quote_id,
                                "parent": f"project_id={project_id}",
                                "operation": "soft_delete_by_id",
                                "file": "quotes.json"
                            })
                            project_failed = True
                        else:
                            deleted_quotes += 1

                if not project_failed:
                    # Only delete project if all dependents were deleted successfully
                    if not db.soft_delete_by_id("projects.json", project_id):
                        failed_deletions.append({
                            "type": "project",
                            "id": project_id,
                            "parent": f"customer_id={customer_id}",
                            "operation": "soft_delete_by_id",
                            "file": "projects.json"
                        })
                    else:
                        deleted_projects += 1

            # Check if any deletions failed and provide comprehensive error response
            if failed_deletions:
                error_details = {
                    "customer_id": customer_id,
                    "failed_deletions": failed_deletions,
                    "successful_deletions": {
                        "projects": deleted_projects,
                        "quotes": deleted_quotes,
                        "freight_requests": deleted_freight_requests
                    },
                    "total_items_before_deletion": {
                        "projects": total_projects,
                        "quotes": len(all_quotes_to_delete),
                        "freight_requests": len(all_frs_to_delete)
                    }
                }
                raise HTTPException(
                    status_code=500,
                    detail=format_error_response(
                        f"Cascade delete partially failed for customer {customer_id}. "
                        f"{len(failed_deletions)} items failed to delete out of "
                        f"{total_projects + len(all_quotes_to_delete) + len(all_frs_to_delete)} total items.",
                        error_details
                    )
                )

            # Success - include all counters in the message
            total_items = deleted_projects + deleted_quotes + deleted_freight_requests
            message = (f"Customer and {deleted_projects} projects, {deleted_quotes} quotes, "
                      f"and {deleted_freight_requests} freight requests deleted successfully "
                      f"({total_items} total items)")
            return format_success_response(
                message,
                {
                    "deleted_customer_id": customer_id,
                    "deletion_summary": {
                        "projects": deleted_projects,
                        "quotes": deleted_quotes,
                        "freight_requests": deleted_freight_requests,
                        "total_items": total_items
                    }
                }
            )

        except HTTPException:
            # Re-raise HTTP exceptions (like our error above)
            raise
        except Exception as e:
            # Handle any unexpected errors during cascade deletion
            raise HTTPException(
                status_code=500,
                detail=format_error_response(
                    f"Unexpected error during cascade delete for customer {customer_id}",
                    {
                        "customer_id": customer_id,
                        "original_error": str(e),
                        "partial_results": {
                            "projects": deleted_projects,
                            "quotes": deleted_quotes,
                            "freight_requests": deleted_freight_requests
                        }
                    }
                )
            ) from e

    except DataNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=format_error_response(str(e), {"resource_id": customer_id})
        )
    except DatabaseOperationError as e:
        raise HTTPException(
            status_code=500,
            detail=format_error_response("Failed to delete customer", {"original_error": str(e)})
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=format_error_response("Internal server error", {"original_error": str(e)})
        )


@router.get("/{customer_id}/stats")
async def get_customer_stats(
    customer_id: int,
    db=Depends(get_database_manager)
):
    """
    Get statistics for a specific customer.

    Returns detailed statistics about the customer including
    project counts, quote counts, and freight request counts.

    Args:
        customer_id: ID of the customer
        db: Database manager dependency

    Returns:
        Customer statistics

    Raises:
        HTTPException: If customer is not found
    """
    try:
        customer = db.find_by_id("customers.json", customer_id)
        if not customer:
            raise DataNotFoundError(
                f"Customer with ID {customer_id} not found",
                "customer",
                customer_id
            )

        # Get projects
        projects = db.filter_by_field("projects.json", "customer_id", customer_id)

        # Get quotes
        quote_count = 0
        for project in projects:
            quotes = db.filter_by_field("quotes.json", "project_id", project["id"])
            quote_count += len(quotes)

        # Get freight requests
        freight_request_count = 0
        for project in projects:
            quotes = db.filter_by_field("quotes.json", "project_id", project["id"])
            for quote in quotes:
                frs = db.filter_by_field("freight_requests.json", "quote_id", quote["id"])
                freight_request_count += len(frs)

        stats = {
            "customer": customer,
            "project_count": len(projects),
            "quote_count": quote_count,
            "freight_request_count": freight_request_count,
            "total_hierarchy_items": 1 + len(projects) + quote_count + freight_request_count
        }

        return stats

    except DataNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=format_error_response(str(e), {"resource_id": customer_id})
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=format_error_response("Failed to get customer statistics", {"original_error": str(e)})
        )