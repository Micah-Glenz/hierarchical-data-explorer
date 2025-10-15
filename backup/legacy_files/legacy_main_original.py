"""
ORIGINAL MONOLITHIC MAIN.PY - BACKUP COPY

This file contains the original 666-line monolithic main.py before refactoring.
It has been moved to backup/legacy_files/ for reference.

Original structure had:
- All API routes in one file (customers, projects, quotes, freight_requests)
- All Pydantic models mixed with route handlers
- Inline validation logic
- No separation of concerns
- All 666 lines in a single file

This has been replaced with the modular structure in src/ directory.
"""

# This is a placeholder file documenting the original structure
# The actual original code was moved during refactoring

ORIGINAL_FILE_STRUCTURE = """
main.py (666 lines) contained:
├── All API endpoints (GET, POST, PUT, DELETE for all entities)
├── All Pydantic models (CustomerCreate, ProjectCreate, etc.)
├── All validation logic
├── Database operations (load_json_file, save_json_file, etc.)
├── Error handling
└── FastAPI application setup

REFACTORED_TO:
├── src/core/ (config.py, database.py, exceptions.py)
├── src/api/ (models.py, dependencies.py, routes/)
├── static/ (css/, js/)
├── templates/ (partials/)
└── main.py (clean 187-line entry point)
"""