"""
Freight Request API routes for the Hierarchical Data Explorer.

This module contains all API endpoints related to freight request operations.
"""

from typing import List

from fastapi import APIRouter, HTTPException, Depends

from ..models import (
    FreightRequestCreate, FreightRequestUpdate, FreightRequestResponse,
    CreateResponse, UpdateResponse, DeleteResponse
)
from ..dependencies import (
    get_database_manager, ValidationHelper, get_valid_statuses, get_valid_priorities,
    format_error_response, format_success_response, validate_quote_exists,
    validate_vendor_exists, enrich_freight_requests
)
from ...core.exceptions import DataNotFoundError, DatabaseOperationError


router = APIRouter(
    prefix="/api/freight-requests",
    tags=["freight_requests"]
)


@router.get("/{quote_id}", response_model=List[FreightRequestResponse])
async def get_freight_requests(quote_id: int, db=Depends(get_database_manager)):
    """Get all freight requests for a specific quote."""
    try:
        if not await validate_quote_exists(quote_id):
            raise HTTPException(
                status_code=404,
                detail=format_error_response(f"Quote with ID {quote_id} not found")
            )

        freight_requests = db.filter_by_field("freight_requests.json", "quote_id", quote_id)
        enriched_requests = enrich_freight_requests(freight_requests)

        return enriched_requests

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=format_error_response("Failed to load freight requests", {"original_error": str(e)})
        )


@router.post("/", response_model=CreateResponse)
async def create_freight_request(
    freight_request: FreightRequestCreate,
    db=Depends(get_database_manager)
):
    """Create a new freight request."""
    try:
        if not await validate_quote_exists(freight_request.quote_id):
            raise HTTPException(
                status_code=400,
                detail=format_error_response(f"Quote with ID {freight_request.quote_id} not found")
            )

        if not await validate_vendor_exists(freight_request.vendor_id):
            raise HTTPException(
                status_code=400,
                detail=format_error_response(f"Vendor with ID {freight_request.vendor_id} not found")
            )

        validated_name = ValidationHelper.validate_required_string(
            freight_request.name, "Freight request name"
        )
        validated_status = ValidationHelper.validate_required_string(
            freight_request.status, "Status"
        )
        ValidationHelper.validate_choice(validated_status, get_valid_statuses(), "Status")

        validated_priority = ValidationHelper.validate_required_string(
            freight_request.priority, "Priority"
        )
        ValidationHelper.validate_choice(validated_priority, get_valid_priorities(), "Priority")

        validated_weight = ValidationHelper.validate_positive_number(
            freight_request.weight, "Weight", 999999.99
        )

        validated_date = ValidationHelper.validate_date_string(
            freight_request.estimated_delivery, "Estimated delivery date"
        )

        new_freight_request = {
            "id": db.get_next_id("freight_requests.json"),
            "name": validated_name,
            "vendor_id": freight_request.vendor_id,
            "status": validated_status,
            "weight": validated_weight,
            "priority": validated_priority,
            "estimated_delivery": validated_date,
            "quote_id": freight_request.quote_id,
        }

        # Get vendor name for response
        vendor = db.find_by_id("vendors.json", freight_request.vendor_id)
        new_freight_request["vendor_name"] = vendor.get("name", "Unknown Vendor") if vendor else "Unknown Vendor"

        if db.append_item("freight_requests.json", new_freight_request):
            return format_success_response("Freight request created successfully", {"data": new_freight_request})
        else:
            raise DatabaseOperationError("Failed to save freight request", "create", "freight_requests.json")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=format_error_response("Failed to create freight request", {"original_error": str(e)})
        )


@router.put("/{freight_request_id}", response_model=UpdateResponse)
async def update_freight_request(
    freight_request_id: int,
    freight_request_update: FreightRequestUpdate,
    db=Depends(get_database_manager)
):
    """Update an existing freight request."""
    try:
        existing_fr = db.find_by_id("freight_requests.json", freight_request_id)
        if not existing_fr:
            raise HTTPException(
                status_code=404,
                detail=format_error_response(
                    f"Freight request with ID {freight_request_id} not found",
                    {"resource_id": freight_request_id}
                )
            )

        updates = {}
        if freight_request_update.name is not None:
            updates["name"] = ValidationHelper.validate_required_string(
                freight_request_update.name, "Freight request name"
            )
        if freight_request_update.vendor_id is not None:
            updates["vendor_id"] = freight_request_update.vendor_id
            # Validate new vendor exists
            if not await validate_vendor_exists(freight_request_update.vendor_id):
                raise HTTPException(
                    status_code=400,
                    detail=format_error_response(f"Vendor with ID {freight_request_update.vendor_id} not found")
                )
        if freight_request_update.status is not None:
            updates["status"] = ValidationHelper.validate_required_string(
                freight_request_update.status, "Status"
            )
            ValidationHelper.validate_choice(updates["status"], get_valid_statuses(), "Status")
        if freight_request_update.priority is not None:
            updates["priority"] = ValidationHelper.validate_required_string(
                freight_request_update.priority, "Priority"
            )
            ValidationHelper.validate_choice(updates["priority"], get_valid_priorities(), "Priority")
        if freight_request_update.weight is not None:
            updates["weight"] = ValidationHelper.validate_positive_number(
                freight_request_update.weight, "Weight", 999999.99
            )
        if freight_request_update.estimated_delivery is not None:
            updates["estimated_delivery"] = ValidationHelper.validate_date_string(
                freight_request_update.estimated_delivery, "Estimated delivery date"
            )

        if db.update_by_id("freight_requests.json", freight_request_id, updates):
            updated_fr = db.find_by_id("freight_requests.json", freight_request_id)
            # Enrich with vendor name
            vendor = db.find_by_id("vendors.json", updated_fr["vendor_id"])
            updated_fr["vendor_name"] = vendor.get("name", "Unknown Vendor") if vendor else "Unknown Vendor"

            return format_success_response("Freight request updated successfully", {"data": updated_fr})
        else:
            raise DatabaseOperationError("Failed to update freight request", "update", "freight_requests.json")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=format_error_response("Failed to update freight request", {"original_error": str(e)})
        )


@router.delete("/{freight_request_id}", response_model=DeleteResponse)
async def delete_freight_request(freight_request_id: int, db=Depends(get_database_manager)):
    """Delete a freight request (soft delete)."""
    try:
        existing_fr = db.find_by_id("freight_requests.json", freight_request_id)
        if not existing_fr:
            raise HTTPException(
                status_code=404,
                detail=format_error_response(
                    f"Freight request with ID {freight_request_id} not found",
                    {"resource_id": freight_request_id}
                )
            )

        if db.soft_delete_by_id("freight_requests.json", freight_request_id):
            return format_success_response(
                "Freight request deleted successfully",
                {"deleted_freight_request_id": freight_request_id}
            )
        else:
            raise DatabaseOperationError("Failed to delete freight request", "delete", "freight_requests.json")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=format_error_response("Failed to delete freight request", {"original_error": str(e)})
        )