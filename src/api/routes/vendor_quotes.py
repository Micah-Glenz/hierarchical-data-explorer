"""
Vendor Quote API routes for the Hierarchical Data Explorer.

This module contains all API endpoints related to vendor quote operations
including CRUD operations and business logic validation.
"""

from datetime import datetime
from typing import List, Dict, Any

from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import JSONResponse

from ..models import (
    VendorQuoteCreate, VendorQuoteUpdate, VendorQuoteResponse,
    CreateResponse, UpdateResponse, DeleteResponse
)
from ..dependencies import (
    get_database_manager, ValidationHelper,
    validate_choice, get_valid_vendor_quote_statuses, get_valid_freight_priorities,
    format_error_response, format_success_response,
    validate_tracking_id, validate_positive_amount
)
from ...core.exceptions import (
    DataValidationError, DataNotFoundError,
    DatabaseOperationError, BusinessRuleViolationError
)
from ...core.constants import (
    validate_tracking_id as validate_tracking_id_format,
    MAX_ITEMS_TEXT_LENGTH, MAX_DELIVERY_REQUIREMENTS_LENGTH
)


router = APIRouter(
    prefix="/api/vendor-quotes",
    tags=["vendor-quotes"]
)


@router.get("/", response_model=List[VendorQuoteResponse])
async def get_vendor_quotes(db=Depends(get_database_manager)):
    """
    Get all vendor quotes.

    Returns a list of all active vendor quotes (excluding soft-deleted items).

    Args:
        db: Database manager dependency

    Returns:
        List of vendor quote dictionaries

    Raises:
        DatabaseOperationError: If data cannot be loaded
    """
    try:
        vendor_quotes = db.find_all("vendor_quotes.json")

        # Enrich each vendor quote with vendor and quote names
        enriched_vendor_quotes = []
        for vq in vendor_quotes:
            # Get vendor name
            vendor = db.find_by_id("vendors.json", vq["vendor_id"])
            vendor_name = vendor["name"] if vendor else "Unknown Vendor"

            # Get quote name
            quote = db.find_by_id("quotes.json", vq["quote_id"])
            quote_name = quote["name"] if quote else "Unknown Quote"

            # Create enriched copy
            enriched_vq = vq.copy()
            enriched_vq["vendor_name"] = vendor_name
            enriched_vq["quote_name"] = quote_name
            enriched_vendor_quotes.append(enriched_vq)

        return enriched_vendor_quotes

    except DatabaseOperationError as e:
        raise HTTPException(
            status_code=500,
            detail=format_error_response("Failed to load vendor quotes", {"original_error": str(e)})
        )


@router.post("/", response_model=CreateResponse)
async def create_vendor_quote(
    vendor_quote: VendorQuoteCreate,
    db=Depends(get_database_manager)
):
    """
    Create a new vendor quote.

    Creates a new vendor quote with validation and business logic checks.

    Args:
        vendor_quote: Vendor quote creation data
        db: Database manager dependency

    Returns:
        Success response with created vendor quote data

    Raises:
        HTTPException: If validation fails or creation error occurs
    """
    try:
        # Validate related entities exist
        quote = db.find_by_id("quotes.json", vendor_quote.quote_id)
        if not quote:
            raise DataNotFoundError(
                f"Quote with ID {vendor_quote.quote_id} not found",
                "quote",
                vendor_quote.quote_id
            )

        vendor = db.find_by_id("vendors.json", vendor_quote.vendor_id)
        if not vendor:
            raise DataNotFoundError(
                f"Vendor with ID {vendor_quote.vendor_id} not found",
                "vendor",
                vendor_quote.vendor_id
            )

        # Validate required fields
        validated_tracking_id = ValidationHelper.validate_required_string(
            vendor_quote.tracking_id, "Tracking ID"
        )
        validated_items_text = ValidationHelper.validate_required_string(
            vendor_quote.items_text, "Items text"
        )
        validated_status = ValidationHelper.validate_required_string(
            vendor_quote.status, "Status"
        )

        # Validate tracking ID format
        if not validate_tracking_id_format(validated_tracking_id):
            raise DataValidationError(
                f"Invalid tracking ID format: {validated_tracking_id}. "
                "Expected format: VQYY-ID (e.g., VQ24-1)"
            )

        # Validate choices
        validate_choice(validated_status, get_valid_vendor_quote_statuses(), "Status")

        if vendor_quote.priority:
            validate_choice(vendor_quote.priority, get_valid_freight_priorities(), "Priority")

        # Validate field lengths
        if len(validated_items_text) > MAX_ITEMS_TEXT_LENGTH:
            raise DataValidationError(
                f"Items text exceeds maximum length of {MAX_ITEMS_TEXT_LENGTH} characters"
            )

        if vendor_quote.delivery_requirements and len(vendor_quote.delivery_requirements) > MAX_DELIVERY_REQUIREMENTS_LENGTH:
            raise DataValidationError(
                f"Delivery requirements exceed maximum length of {MAX_DELIVERY_REQUIREMENTS_LENGTH} characters"
            )

        # Validate amounts
        if vendor_quote.quoted_amount is not None:
            validate_positive_amount(vendor_quote.quoted_amount, "Quoted amount")

        # Check for duplicate tracking ID
        existing_quotes = db.filter_by_field("vendor_quotes.json", "tracking_id", validated_tracking_id)
        if existing_quotes:
            raise BusinessRuleViolationError(
                f"Tracking ID '{validated_tracking_id}' already exists",
                "tracking_id",
                validated_tracking_id
            )

        # Create new vendor quote
        new_vendor_quote = {
            "id": db.get_next_id("vendor_quotes.json"),
            "quote_id": vendor_quote.quote_id,
            "vendor_id": vendor_quote.vendor_id,
            "tracking_id": validated_tracking_id,
            "items_text": validated_items_text,
            "delivery_requirements": vendor_quote.delivery_requirements or "",
            "is_rush": vendor_quote.is_rush or False,
            "status": validated_status,
            "priority": vendor_quote.priority or "medium",
            "quoted_amount": vendor_quote.quoted_amount,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "is_deleted": False,
            "deleted_at": None
        }

        if db.append_item("vendor_quotes.json", new_vendor_quote):
            return format_success_response("Vendor quote created successfully", {"data": new_vendor_quote})
        else:
            raise DatabaseOperationError("Failed to save vendor quote", "create", "vendor_quotes.json")

    except (DataValidationError, BusinessRuleViolationError, ValueError) as e:
        raise HTTPException(
            status_code=400,
            detail=format_error_response(str(e))
        )
    except DataNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=format_error_response(str(e))
        )
    except DatabaseOperationError as e:
        raise HTTPException(
            status_code=500,
            detail=format_error_response("Failed to create vendor quote", {"original_error": str(e)})
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=format_error_response("Internal server error", {"original_error": str(e)})
        )


@router.get("/{vendor_quote_id}", response_model=VendorQuoteResponse)
async def get_vendor_quote(
    vendor_quote_id: int,
    db=Depends(get_database_manager)
):
    """
    Get a specific vendor quote by ID.

    Args:
        vendor_quote_id: ID of the vendor quote to retrieve
        db: Database manager dependency

    Returns:
        Vendor quote data

    Raises:
        HTTPException: If vendor quote is not found
    """
    try:
        vendor_quote = db.find_by_id("vendor_quotes.json", vendor_quote_id)
        if not vendor_quote:
            raise DataNotFoundError(
                f"Vendor quote with ID {vendor_quote_id} not found",
                "vendor_quote",
                vendor_quote_id
            )

        # Enrich with vendor and quote names
        vendor = db.find_by_id("vendors.json", vendor_quote["vendor_id"])
        vendor_name = vendor["name"] if vendor else "Unknown Vendor"

        quote = db.find_by_id("quotes.json", vendor_quote["quote_id"])
        quote_name = quote["name"] if quote else "Unknown Quote"

        # Create enriched copy
        enriched_vendor_quote = vendor_quote.copy()
        enriched_vendor_quote["vendor_name"] = vendor_name
        enriched_vendor_quote["quote_name"] = quote_name

        return enriched_vendor_quote

    except DataNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=format_error_response(str(e), {"resource_id": vendor_quote_id})
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=format_error_response("Failed to retrieve vendor quote", {"original_error": str(e)})
        )


@router.put("/{vendor_quote_id}", response_model=UpdateResponse)
async def update_vendor_quote(
    vendor_quote_id: int,
    vendor_quote_update: VendorQuoteUpdate,
    db=Depends(get_database_manager)
):
    """
    Update an existing vendor quote.

    Updates vendor quote data with validation for only the provided fields.

    Args:
        vendor_quote_id: ID of the vendor quote to update
        vendor_quote_update: Vendor quote update data
        db: Database manager dependency

    Returns:
        Success response with updated vendor quote data

    Raises:
        HTTPException: If vendor quote is not found or validation fails
    """
    try:
        # Check if vendor quote exists
        existing_vendor_quote = db.find_by_id("vendor_quotes.json", vendor_quote_id)
        if not existing_vendor_quote:
            raise DataNotFoundError(
                f"Vendor quote with ID {vendor_quote_id} not found",
                "vendor_quote",
                vendor_quote_id
            )

        # Prepare updates with validation
        updates = {}

        if vendor_quote_update.tracking_id is not None:
            validated_tracking_id = ValidationHelper.validate_required_string(
                vendor_quote_update.tracking_id, "Tracking ID"
            )
            if not validate_tracking_id_format(validated_tracking_id):
                raise DataValidationError(
                    f"Invalid tracking ID format: {validated_tracking_id}. "
                    "Expected format: VQYY-ID (e.g., VQ24-1)"
                )

            # Check for duplicate tracking ID (excluding current record)
            existing_quotes = db.filter_by_field("vendor_quotes.json", "tracking_id", validated_tracking_id)
            if any(quote["id"] != vendor_quote_id for quote in existing_quotes):
                raise BusinessRuleViolationError(
                    f"Tracking ID '{validated_tracking_id}' already exists",
                    "tracking_id",
                    validated_tracking_id
                )

            updates["tracking_id"] = validated_tracking_id

        if vendor_quote_update.items_text is not None:
            validated_items_text = ValidationHelper.validate_required_string(
                vendor_quote_update.items_text, "Items text"
            )
            if len(validated_items_text) > MAX_ITEMS_TEXT_LENGTH:
                raise DataValidationError(
                    f"Items text exceeds maximum length of {MAX_ITEMS_TEXT_LENGTH} characters"
                )
            updates["items_text"] = validated_items_text

        if vendor_quote_update.delivery_requirements is not None:
            if len(vendor_quote_update.delivery_requirements) > MAX_DELIVERY_REQUIREMENTS_LENGTH:
                raise DataValidationError(
                    f"Delivery requirements exceed maximum length of {MAX_DELIVERY_REQUIREMENTS_LENGTH} characters"
                )
            updates["delivery_requirements"] = vendor_quote_update.delivery_requirements

        if vendor_quote_update.is_rush is not None:
            updates["is_rush"] = vendor_quote_update.is_rush

        if vendor_quote_update.status is not None:
            validated_status = ValidationHelper.validate_required_string(
                vendor_quote_update.status, "Status"
            )
            validate_choice(validated_status, get_valid_vendor_quote_statuses(), "Status")
            updates["status"] = validated_status

        if vendor_quote_update.priority is not None:
            validate_choice(vendor_quote_update.priority, get_valid_freight_priorities(), "Priority")
            updates["priority"] = vendor_quote_update.priority

        if vendor_quote_update.quoted_amount is not None:
            validate_positive_amount(vendor_quote_update.quoted_amount, "Quoted amount")
            updates["quoted_amount"] = vendor_quote_update.quoted_amount

        # Add updated timestamp
        updates["updated_at"] = datetime.now().isoformat()

        # Update vendor quote
        if db.update_by_id("vendor_quotes.json", vendor_quote_id, updates):
            # Get updated vendor quote
            updated_vendor_quote = db.find_by_id("vendor_quotes.json", vendor_quote_id)

            return format_success_response("Vendor quote updated successfully", {"data": updated_vendor_quote})
        else:
            raise DatabaseOperationError("Failed to update vendor quote", "update", "vendor_quotes.json")

    except DataNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=format_error_response(str(e), {"resource_id": vendor_quote_id})
        )
    except (DataValidationError, BusinessRuleViolationError, ValueError) as e:
        raise HTTPException(
            status_code=400,
            detail=format_error_response(str(e))
        )
    except DatabaseOperationError as e:
        raise HTTPException(
            status_code=500,
            detail=format_error_response("Failed to update vendor quote", {"original_error": str(e)})
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=format_error_response("Internal server error", {"original_error": str(e)})
        )


@router.delete("/{vendor_quote_id}", response_model=DeleteResponse)
async def delete_vendor_quote(
    vendor_quote_id: int,
    db=Depends(get_database_manager)
):
    """
    Delete a vendor quote (soft delete).

    Soft deletes a vendor quote, making it inactive but preserving
    the data for audit purposes.

    Args:
        vendor_quote_id: ID of the vendor quote to delete
        db: Database manager dependency

    Returns:
        Success response with deletion details

    Raises:
        HTTPException: If vendor quote is not found or deletion fails
    """
    try:
        # Check if vendor quote exists
        existing_vendor_quote = db.find_by_id("vendor_quotes.json", vendor_quote_id)
        if not existing_vendor_quote:
            raise DataNotFoundError(
                f"Vendor quote with ID {vendor_quote_id} not found",
                "vendor_quote",
                vendor_quote_id
            )

        # Perform soft delete
        if db.soft_delete_by_id("vendor_quotes.json", vendor_quote_id):
            return format_success_response("Vendor quote deleted successfully", {
                "deleted_vendor_quote_id": vendor_quote_id,
                "tracking_id": existing_vendor_quote.get("tracking_id")
            })
        else:
            raise DatabaseOperationError("Failed to delete vendor quote", "delete", "vendor_quotes.json")

    except DataNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=format_error_response(str(e), {"resource_id": vendor_quote_id})
        )
    except DatabaseOperationError as e:
        raise HTTPException(
            status_code=500,
            detail=format_error_response("Failed to delete vendor quote", {"original_error": str(e)})
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=format_error_response("Internal server error", {"original_error": str(e)})
        )


@router.get("/by-quote/{quote_id}", response_model=List[VendorQuoteResponse])
async def get_vendor_quotes_by_quote(
    quote_id: int,
    db=Depends(get_database_manager)
):
    """
    Get all vendor quotes for a specific quote.

    Args:
        quote_id: ID of the quote to get vendor quotes for
        db: Database manager dependency

    Returns:
        List of vendor quote dictionaries

    Raises:
        HTTPException: If quote is not found
    """
    try:
        # Check if quote exists
        quote = db.find_by_id("quotes.json", quote_id)
        if not quote:
            raise DataNotFoundError(
                f"Quote with ID {quote_id} not found",
                "quote",
                quote_id
            )

        # Get vendor quotes for this quote and enrich with related data
        vendor_quotes = db.filter_by_field("vendor_quotes.json", "quote_id", quote_id)

        # Enrich each vendor quote with vendor and quote names
        enriched_vendor_quotes = []
        for vq in vendor_quotes:
            # Get vendor name
            vendor = db.find_by_id("vendors.json", vq["vendor_id"])
            vendor_name = vendor["name"] if vendor else "Unknown Vendor"

            # Get quote name
            quote = db.find_by_id("quotes.json", vq["quote_id"])
            quote_name = quote["name"] if quote else "Unknown Quote"

            # Create enriched copy
            enriched_vq = vq.copy()
            enriched_vq["vendor_name"] = vendor_name
            enriched_vq["quote_name"] = quote_name
            enriched_vendor_quotes.append(enriched_vq)

        return enriched_vendor_quotes

    except DataNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=format_error_response(str(e), {"quote_id": quote_id})
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=format_error_response("Failed to retrieve vendor quotes for quote", {"original_error": str(e)})
        )


@router.get("/by-vendor/{vendor_id}", response_model=List[VendorQuoteResponse])
async def get_vendor_quotes_by_vendor(
    vendor_id: int,
    db=Depends(get_database_manager)
):
    """
    Get all vendor quotes for a specific vendor.

    Args:
        vendor_id: ID of the vendor to get vendor quotes for
        db: Database manager dependency

    Returns:
        List of vendor quote dictionaries

    Raises:
        HTTPException: If vendor is not found
    """
    try:
        # Check if vendor exists
        vendor = db.find_by_id("vendors.json", vendor_id)
        if not vendor:
            raise DataNotFoundError(
                f"Vendor with ID {vendor_id} not found",
                "vendor",
                vendor_id
            )

        # Get vendor quotes for this vendor and enrich with related data
        vendor_quotes = db.filter_by_field("vendor_quotes.json", "vendor_id", vendor_id)

        # Enrich each vendor quote with vendor and quote names
        enriched_vendor_quotes = []
        for vq in vendor_quotes:
            # Get vendor name (we already have the vendor)
            vendor_name = vendor["name"] if vendor else "Unknown Vendor"

            # Get quote name
            quote = db.find_by_id("quotes.json", vq["quote_id"])
            quote_name = quote["name"] if quote else "Unknown Quote"

            # Create enriched copy
            enriched_vq = vq.copy()
            enriched_vq["vendor_name"] = vendor_name
            enriched_vq["quote_name"] = quote_name
            enriched_vendor_quotes.append(enriched_vq)

        return enriched_vendor_quotes

    except DataNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=format_error_response(str(e), {"vendor_id": vendor_id})
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=format_error_response("Failed to retrieve vendor quotes for vendor", {"original_error": str(e)})
        )


@router.get("/tracking/{tracking_id}", response_model=VendorQuoteResponse)
async def get_vendor_quote_by_tracking_id(
    tracking_id: str,
    db=Depends(get_database_manager)
):
    """
    Get a vendor quote by tracking ID.

    Args:
        tracking_id: Tracking ID of the vendor quote to retrieve
        db: Database manager dependency

    Returns:
        Vendor quote data

    Raises:
        HTTPException: If vendor quote is not found
    """
    try:
        # Validate tracking ID format
        if not validate_tracking_id_format(tracking_id):
            raise DataValidationError(
                f"Invalid tracking ID format: {tracking_id}. "
                "Expected format: VQYY-ID (e.g., VQ24-1)"
            )

        # Find vendor quote by tracking ID
        vendor_quotes = db.filter_by_field("vendor_quotes.json", "tracking_id", tracking_id)
        if not vendor_quotes:
            raise DataNotFoundError(
                f"Vendor quote with tracking ID '{tracking_id}' not found",
                "vendor_quote",
                tracking_id
            )

        # Enrich with vendor and quote names
        vendor_quote = vendor_quotes[0]  # Get the first (and only) match

        vendor = db.find_by_id("vendors.json", vendor_quote["vendor_id"])
        vendor_name = vendor["name"] if vendor else "Unknown Vendor"

        quote = db.find_by_id("quotes.json", vendor_quote["quote_id"])
        quote_name = quote["name"] if quote else "Unknown Quote"

        # Create enriched copy
        enriched_vendor_quote = vendor_quote.copy()
        enriched_vendor_quote["vendor_name"] = vendor_name
        enriched_vendor_quote["quote_name"] = quote_name

        return enriched_vendor_quote

    except DataValidationError as e:
        raise HTTPException(
            status_code=400,
            detail=format_error_response(str(e))
        )
    except DataNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=format_error_response(str(e), {"tracking_id": tracking_id})
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=format_error_response("Failed to retrieve vendor quote by tracking ID", {"original_error": str(e)})
        )