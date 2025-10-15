"""
Vendor API routes for the Hierarchical Data Explorer.

This module contains all API endpoints related to vendor operations.
"""

import json
from fastapi import APIRouter, HTTPException, Depends

from ..models import VendorResponse
from ..dependencies import get_database_manager, format_error_response
from ...core.exceptions import DatabaseOperationError



router = APIRouter(
    prefix="/api/vendors",
    tags=["vendors"]
)


@router.get("/", response_model=list[VendorResponse])
async def get_vendors(db=Depends(get_database_manager)):
    """Get all vendors."""
    try:
        vendors = db.find_all("vendors.json")
        return vendors
    except (DatabaseOperationError, FileNotFoundError, PermissionError, json.JSONDecodeError) as e:
        raise HTTPException(
            status_code=500,
            detail=format_error_response("Failed to load vendors", {"original_error": str(e)})
        ) from e