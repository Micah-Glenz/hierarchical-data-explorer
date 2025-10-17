"""
Hierarchical Data Explorer - Main Application Entry Point

This is the main FastAPI application that serves the hierarchical data
explorer interface. The application manages a 4-tier hierarchy:
Customers → Projects → Quotes → Freight Requests.

The application has been refactored into a modular structure with:
- Core services (config, database, exceptions)
- API routes organized by entity
- Modular frontend assets
- Comprehensive documentation
"""

import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from pathlib import Path

# Import core application components
from src.core.config import Settings, load_env_settings
from src.core.exceptions import (
    DataExplorerException,
    DataValidationError,
    DataNotFoundError,
    DatabaseOperationError,
    BusinessRuleViolationError
)

# Import API routes
from src.api.routes import (
    customers,
    projects,
    quotes,
    freight_requests,
    vendors,
    vendor_quotes
)

# Initialize configuration
settings = Settings()
load_env_settings()  # Load environment variables

# Create FastAPI application
app = FastAPI(
    title="Hierarchical Data Explorer API",
    description="API for managing hierarchical data: Customers → Projects → Quotes → Freight Requests",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure static files
static_dir = Path("static")
if static_dir.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")

# Configure templates
templates = Jinja2Templates(directory="templates")

# Include API routes
app.include_router(customers.router)
app.include_router(projects.router)
app.include_router(quotes.router)
app.include_router(freight_requests.router)
app.include_router(vendors.router)
app.include_router(vendor_quotes.router)


@app.get("/")
async def read_index(request: Request):
    """Serve the main HTML page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "application": "Hierarchical Data Explorer"
    }


# Global exception handlers
@app.exception_handler(DataExplorerException)
async def data_explorer_exception_handler(request, exc: DataExplorerException):
    """Handle custom data explorer exceptions."""
    from fastapi.responses import JSONResponse
    from src.api.dependencies import format_error_response

    return JSONResponse(
        status_code=400,
        content=format_error_response(str(exc))
    )


@app.exception_handler(DataValidationError)
async def data_validation_exception_handler(request, exc: DataValidationError):
    """Handle data validation errors."""
    from fastapi.responses import JSONResponse
    from src.api.dependencies import format_error_response

    return JSONResponse(
        status_code=400,
        content=format_error_response(str(exc))
    )


@app.exception_handler(DataNotFoundError)
async def data_not_found_exception_handler(request, exc: DataNotFoundError):
    """Handle data not found errors."""
    from fastapi.responses import JSONResponse
    from src.api.dependencies import format_error_response

    return JSONResponse(
        status_code=404,
        content=format_error_response(str(exc))
    )


@app.exception_handler(DatabaseOperationError)
async def database_operation_exception_handler(request, exc: DatabaseOperationError):
    """Handle database operation errors."""
    from fastapi.responses import JSONResponse
    from src.api.dependencies import format_error_response

    return JSONResponse(
        status_code=500,
        content=format_error_response("Database operation failed", {
            "operation": exc.operation,
            "resource": exc.resource
        })
    )


@app.exception_handler(BusinessRuleViolationError)
async def business_rule_violation_exception_handler(request, exc: BusinessRuleViolationError):
    """Handle business rule violations."""
    from fastapi.responses import JSONResponse
    from src.api.dependencies import format_error_response

    return JSONResponse(
        status_code=422,
        content=format_error_response(str(exc))
    )


@app.on_event("startup")
async def startup_event():
    """Application startup event handler."""
    # Ensure data directory exists
    settings.DATA_DIR.mkdir(exist_ok=True)

    # Ensure required data files exist
    required_files = [
        "customers.json",
        "projects.json",
        "quotes.json",
        "freight_requests.json",
        "vendors.json",
        "vendor_quotes.json"
    ]

    for file_name in required_files:
        file_path = settings.DATA_DIR / file_name
        if not file_path.exists():
            # Create empty JSON file
            import json
            with open(file_path, 'w') as f:
                json.dump([], f)

    print("🚀 Hierarchical Data Explorer started successfully")
    print(f"📁 Data directory: {settings.DATA_DIR}")
    print(f"🌐 Server running on http://{settings.HOST}:{settings.PORT}")


@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event handler."""
    print("🛑 Hierarchical Data Explorer shutting down...")


if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"
    )