"""
Quote API routes for the Hierarchical Data Explorer.

This module contains all API endpoints related to quote operations.
"""

from typing import List

from fastapi import APIRouter, HTTPException, Depends

from ..models import (
    QuoteCreate, QuoteUpdate, QuoteResponse,
    CreateResponse, UpdateResponse, DeleteResponse
)
from ..dependencies import (
    get_database_manager, ValidationHelper, get_valid_statuses,
    format_error_response, format_success_response, validate_project_exists,
    calculate_item_counts
)
from ...core.exceptions import DataNotFoundError, DatabaseOperationError


router = APIRouter(
    prefix="/api/quotes",
    tags=["quotes"]
)


@router.get("/{project_id}", response_model=List[QuoteResponse])
async def get_quotes(project_id: int, db=Depends(get_database_manager)):
    """Get all quotes for a specific project."""
    try:
        if not await validate_project_exists(project_id):
            raise HTTPException(
                status_code=404,
                detail=format_error_response(f"Project with ID {project_id} not found")
            )

        quotes = db.filter_by_field("quotes.json", "project_id", project_id)
        fr_counts = calculate_item_counts("quotes", parent_id=project_id)

        enriched_quotes = []
        for quote in quotes:
            quote_copy = quote.copy()
            quote_copy["freight_request_count"] = fr_counts.get(quote["id"], 0)
            enriched_quotes.append(quote_copy)

        return enriched_quotes

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=format_error_response("Failed to load quotes", {"original_error": str(e)})
        )


@router.post("/", response_model=CreateResponse)
async def create_quote(quote: QuoteCreate, db=Depends(get_database_manager)):
    """Create a new quote."""
    try:
        if not await validate_project_exists(quote.project_id):
            raise HTTPException(
                status_code=400,
                detail=format_error_response(f"Project with ID {quote.project_id} not found")
            )

        validated_name = ValidationHelper.validate_required_string(quote.name, "Quote name")
        validated_amount = ValidationHelper.validate_positive_number(quote.amount, "Amount", 999999999.99)
        validated_status = ValidationHelper.validate_required_string(quote.status, "Status")
        ValidationHelper.validate_choice(validated_status, get_valid_statuses(), "Status")

        validated_date = ValidationHelper.validate_date_string(quote.valid_until, "Valid until date")

        new_quote = {
            "id": db.get_next_id("quotes.json"),
            "name": validated_name,
            "amount": validated_amount,
            "status": validated_status,
            "valid_until": validated_date,
            "project_id": quote.project_id,
            "freight_request_count": 0
        }

        if db.append_item("quotes.json", new_quote):
            return format_success_response("Quote created successfully", {"data": new_quote})
        else:
            raise DatabaseOperationError("Failed to save quote", "create", "quotes.json")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=format_error_response("Failed to create quote", {"original_error": str(e)})
        )


@router.put("/{quote_id}", response_model=UpdateResponse)
async def update_quote(quote_id: int, quote_update: QuoteUpdate, db=Depends(get_database_manager)):
    """Update an existing quote."""
    try:
        existing_quote = db.find_by_id("quotes.json", quote_id)
        if not existing_quote:
            raise HTTPException(
                status_code=404,
                detail=format_error_response(f"Quote with ID {quote_id} not found", {"resource_id": quote_id})
            )

        updates = {}
        if quote_update.name is not None:
            updates["name"] = ValidationHelper.validate_required_string(quote_update.name, "Quote name")
        if quote_update.amount is not None:
            updates["amount"] = ValidationHelper.validate_positive_number(quote_update.amount, "Amount", 999999999.99)
        if quote_update.status is not None:
            updates["status"] = ValidationHelper.validate_required_string(quote_update.status, "Status")
            ValidationHelper.validate_choice(updates["status"], get_valid_statuses(), "Status")
        if quote_update.valid_until is not None:
            updates["valid_until"] = ValidationHelper.validate_date_string(quote_update.valid_until, "Valid until date")

        if db.update_by_id("quotes.json", quote_id, updates):
            updated_quote = db.find_by_id("quotes.json", quote_id)
            # Use parent filtering for efficiency
            fr_counts = calculate_item_counts("quotes", parent_id=updated_quote.get("project_id"))
            updated_quote["freight_request_count"] = fr_counts.get(quote_id, 0)

            return format_success_response("Quote updated successfully", {"data": updated_quote})
        else:
            raise DatabaseOperationError("Failed to update quote", "update", "quotes.json")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=format_error_response("Failed to update quote", {"original_error": str(e)})
        )


@router.delete("/{quote_id}", response_model=DeleteResponse)
async def delete_quote(quote_id: int, db=Depends(get_database_manager)):
    """Delete a quote (soft delete with cascade)."""
    try:
        existing_quote = db.find_by_id("quotes.json", quote_id)
        if not existing_quote:
            raise HTTPException(
                status_code=404,
                detail=format_error_response(f"Quote with ID {quote_id} not found", {"resource_id": quote_id})
            )

        if db.soft_delete_by_id("quotes.json", quote_id):
            # Cascade delete to freight requests
            frs = db.filter_by_field("freight_requests.json", "quote_id", quote_id)
            deleted_frs = sum(1 for fr in frs if db.soft_delete_by_id("freight_requests.json", fr["id"]))

            message = f"Quote and {deleted_frs} related freight requests deleted successfully"
            return format_success_response(message, {"deleted_quote_id": quote_id})
        else:
            raise DatabaseOperationError("Failed to delete quote", "delete", "quotes.json")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=format_error_response("Failed to delete quote", {"original_error": str(e)})
        )