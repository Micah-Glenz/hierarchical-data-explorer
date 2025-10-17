# Comprehensive Database Schema Documentation

## Overview

This document provides a comprehensive overview of the database schema for the Hierarchical Data Explorer application. The system uses JSON file-based storage with a relational structure between five main entities: Customers, Projects, Quotes, Vendors, and VendorQuotes.

## Current System Status

**Last Updated**: 2025-10-17
**Version**: 2.0 (Post Industry Field Removal)
**Status**: Production Ready

### Recent Changes
- ✅ **Industry Field Removal**: Complete removal of `industry` field from Customer entity across all system layers
- ✅ **Schema Validation**: All CRUD operations tested and validated post-removal
- ✅ **Documentation Update**: Schema documentation updated to reflect current state
- ✅ **UI Consistency**: All frontend components updated to remove industry references
- ✅ **Data Migration**: 50 existing customer records successfully migrated

### System Health
- **Database**: All JSON files validated and accessible
- **API**: All endpoints functional with proper validation
- **Frontend**: Web interface fully operational at http://localhost:8001
- **Backups**: Automatic backup system active with timestamped snapshots

## Architecture

### Storage Engine
- **Database Manager**: `src/core/database.py` - Thread-safe JSON file operations
- **Data Files**: Located in `data/` directory
- **Backup Strategy**: Automatic timestamped backups before modifications
- **Soft Delete**: All entities support soft deletion with `is_deleted` and `deleted_at` fields

### Validation Layer
- **Constants**: `src/core/constants.py` - All validation rules, enums, and constraints
- **Models**: `src/api/models.py` - Pydantic models with comprehensive validation
- **Field Validation**: Email, ZIP code, phone number, tracking ID formats

## Entity Relationships

```
Customer (1) → (many) Project (1) → (many) Quote (1) → (many) VendorQuote
                                                    ↑
                                                Vendor (1)
```

## Table Schemas

### Customer

**File**: `data/customers.json`
**Purpose**: Stores customer information with contact details and sales representation

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key, Auto-increment | Unique customer identifier |
| name | String | Required, Max 255 chars | Customer legal name |
| address | String | Optional, Max 255 chars | Street address |
| city | String | Optional, Max 100 chars | City name |
| state | String | Optional, Max 50 chars | State/Province code |
| zip | String | Optional, Max 10 chars, ZIP format validation | ZIP/Postal code |
| sales_rep_name | String | Optional, Max 255 chars | Sales representative name |
| sales_rep_email | String | Optional, Max 254 chars, Email format validation | Sales rep email |
| status | String | Required, From predefined list | Customer status (active/inactive/prospect) |
| created_date | String | Required, YYYY-MM-DD format | Customer creation date |
| created_at | DateTime | Auto-generated | Record creation timestamp |
| updated_at | DateTime | Auto-generated | Last modification timestamp |
| is_deleted | Boolean | Default false | Soft deletion flag |
| deleted_at | DateTime | Optional | Deletion timestamp |

**Valid Statuses**: active, inactive, prospect

---

### Project

**File**: `data/projects.json`
**Purpose**: Tracks projects associated with customers, including budget and timeline information

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key, Auto-increment | Unique project identifier |
| customer_id | Integer | Required, Foreign Key → Customer.id | Associated customer |
| name | String | Required, Max 255 chars | Project name/description |
| project_type | String | Required, From predefined list | Type of project work |
| status | String | Required, From predefined list | Current project status |
| budget | Decimal | Required, Min 0.01, Max 999,999,999.99 | Project budget |
| start_date | String | Required, YYYY-MM-DD format | Project start date |
| target_delivery_date | String | Optional, YYYY-MM-DD format | Expected completion date |
| created_at | DateTime | Auto-generated | Record creation timestamp |
| updated_at | DateTime | Auto-generated | Last modification timestamp |
| is_deleted | Boolean | Default false | Soft deletion flag |
| deleted_at | DateTime | Optional | Deletion timestamp |

**Valid Project Types**: installation, repair, maintenance, consulting, other
**Valid Statuses**: planning, in_progress, on_hold, completed, cancelled

**Unique Constraint**: (customer_id, name) - Ensures unique project names per customer

---

### Quote

**File**: `data/quotes.json`
**Purpose**: Manages quotes/bids created for specific projects

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key, Auto-increment | Unique quote identifier |
| project_id | Integer | Required, Foreign Key → Project.id | Associated project |
| name | String | Required, Max 255 chars | Quote name/reference |
| description | String | Optional, Max 1000 chars | Detailed quote description |
| status | String | Required, From predefined list | Quote workflow status |
| amount | Decimal | Required, Min 0.01, Max 999,999,999.99 | Quote monetary value |
| valid_until | String | Optional, YYYY-MM-DD format | Quote expiration date |
| created_at | DateTime | Auto-generated | Record creation timestamp |
| updated_at | DateTime | Auto-generated | Last modification timestamp |
| is_deleted | Boolean | Default false | Soft deletion flag |
| deleted_at | DateTime | Optional | Deletion timestamp |

**Valid Statuses**: draft, pending_freight, ready, sent, approved, declined

**Unique Constraint**: (project_id, name) - Ensures unique quote names per project

---

### Vendor

**File**: `data/vendors.json`
**Purpose**: Directory of vendors/suppliers with their specialties and ratings

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key, Auto-increment | Unique vendor identifier |
| name | String | Required, Max 255 chars, Unique | Vendor company name |
| contact_name | String | Optional, Max 255 chars | Primary contact person |
| email | String | Optional, Max 254 chars, Email format validation | Contact email |
| specialty | String | Required, Max 100 chars | Vendor area of expertise |
| rating | Decimal | Required, Range 0.0-5.0 | Vendor performance rating |
| created_at | DateTime | Auto-generated | Record creation timestamp |
| updated_at | DateTime | Auto-generated | Last modification timestamp |
| is_deleted | Boolean | Default false | Soft deletion flag |
| deleted_at | DateTime | Optional | Deletion timestamp |

**Specialty Examples**: Project Management, IT Consulting, Logistics, Cybersecurity, etc.

---

### VendorQuote

**File**: `data/vendor_quotes.json`
**Purpose**: Links quotes to vendors for freight/shipping services with tracking

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| id | Integer | Primary Key, Auto-increment | Unique vendor quote identifier |
| quote_id | Integer | Required, Foreign Key → Quote.id | Associated quote |
| vendor_id | Integer | Required, Foreign Key → Vendor.id | Selected vendor |
| tracking_id | String | Required, Unique, VQYY-ID format | Auto-generated tracking number |
| items_text | String | Required, Max 2000 chars | Description of items to ship |
| delivery_requirements | String | Optional, Max 1000 chars | Special delivery instructions |
| is_rush | Boolean | Default false | Rush order flag |
| status | String | Required, From predefined list | Vendor quote status |
| quoted_amount | Decimal | Optional, Min 0.01, Max 999,999,999.99 | Vendor's quoted price |
| created_at | DateTime | Auto-generated | Record creation timestamp |
| updated_at | DateTime | Auto-generated | Last modification timestamp |
| is_deleted | Boolean | Default false | Soft deletion flag |
| deleted_at | DateTime | Optional | Deletion timestamp |

**Valid Statuses**: pending, quoted, approved, rejected, completed

**Unique Constraints**:
- (quote_id, vendor_id) - One vendor quote per quote-vendor pair
- tracking_id - Globally unique tracking identifier

**Tracking ID Format**: `VQYY-ID` (e.g., VQ24-1, VQ24-123)
- Prefix: VQ (Vendor Quote)
- YY: Two-digit year
- ID: Sequential number for the year

---

## Data Validation Rules

### Email Validation
- Format: Standard email regex pattern
- Max length: 254 characters
- Prevents consecutive dots and leading/trailing dots

### ZIP Code Validation
- Format: US ZIP codes (12345 or 12345-6789)
- Max length: 10 characters

### Phone Number Validation
- Supports multiple formats:
  - (555) 123-4567
  - 555-123-4567
  - 555.123.4567
  - +1 5551234567
  - 5551234567

### Tracking ID Validation
- Format: `VQYY-ID` pattern
- Generated automatically using `generate_tracking_id(year, sequence)`

### Numeric Constraints
- **Amounts**: Min $0.01, Max $999,999,999.99
- **Weights**: Min 0.01 kg, Max 999,999.99 kg
- **Ratings**: Range 0.0 to 5.0

## Database Operations

### Core Operations
- **Create**: `append_item()` - Adds new records with auto-generated IDs
- **Read**: `load_json_data()`, `find_by_id()`, `find_all()`, `filter_by_field()`
- **Update**: `update_by_id()` - Modifies existing records
- **Delete**: `soft_delete_by_id()` - Marks records as deleted
- **Stats**: `get_file_stats()` - Returns file statistics

### Backup Strategy
- Automatic backup creation before any write operation
- Backup filename: `{original}.backup.{YYYYMMDD_HHMMSS}`
- Backup includes original file metadata (size, timestamps)

### Concurrency Control
- Thread-safe operations using `threading.RLock()`
- Correlation IDs for operation tracking
- Comprehensive logging with structured metadata

## API Integration

### Pydantic Models
- **Request Models**: Validation for incoming data
- **Response Models**: Consistent API response format
- **Enhanced Models**: Full DATABASE_SCHEMA.md compliance
- **Validation**: Automatic field validation and error messages

### Endpoints
- Standard CRUD operations for all entities
- Relationship navigation (customer → projects → quotes)
- Search and filtering capabilities
- Bulk operations support

## Performance Considerations

### Indexing Strategy
- Primary keys: Auto-incrementing integers
- Foreign keys: Indexed for relationship lookups
- Unique constraints: Enforced at application level
- Search fields: Full-text search on name fields

### Query Optimization
- Lazy loading for related entities
- Pagination support for large datasets
- Caching of frequently accessed data
- Efficient JSON parsing and generation

## Data Integrity

### Referential Integrity
- Foreign key relationships enforced at application level
- Cascade soft deletion for related records
- Unique constraints prevent duplicates
- Validation before all write operations

### Business Rules
- Customer names must be unique per system
- Project names must be unique per customer
- Quote names must be unique per project
- Vendor quotes limited to one per vendor per quote
- Tracking IDs globally unique and auto-generated

## Migration and Versioning

### Schema Evolution
- Backward-compatible field additions
- Soft deletion enables data retention
- Version-controlled validation rules
- Migration scripts for major updates

#### Field Addition/Removal Process

**Complete Field Removal Workflow (Validated Process):**

This process has been successfully tested by removing the `industry` field from the Customer entity.

**Phase 1: Backend Updates**
1. **Update Constants** (`src/core/constants.py`)
   - Remove field-specific validation constants and enums
   - Update field mappings and validation rules

2. **Update Dependencies** (`src/api/dependencies.py`)
   - Remove field-specific helper functions (e.g., `get_valid_industries()`)
   - Update validation imports and references

3. **Update Pydantic Models** (`src/api/models.py`)
   - Remove field from Base models (e.g., `CustomerBase`)
   - Remove field from Update models (e.g., `CustomerUpdate`, `CustomerUpdateEnhanced`)
   - Update imports to remove field-specific dependencies

4. **Update API Routes** (`src/api/routes/customers.py`)
   - Remove field validation in create endpoints
   - Remove field processing in update endpoints
   - Update imports to remove field-specific dependencies

**Phase 2: Frontend Updates**
1. **Update Form Templates** (`templates/partials/forms/customer.html`)
   - Remove field HTML elements from forms
   - Update form validation and field requirements

2. **Update JavaScript Components** (`static/js/components.js`, `static/js/data-explorer.js`)
   - Remove field from default data objects
   - Update field mappings and validation functions
   - Remove field from form field definitions

3. **Update Display Templates** (`templates/index.html`)
   - Remove field from card displays and detail views
   - Update data binding expressions

**Phase 3: Database Cleanup**
1. **Create Cleanup Script**
   - Backup current data with timestamp
   - Remove field from all existing records
   - Validate data integrity after cleanup
   - Provide rollback capability

2. **Execute Database Migration**
   - Run cleanup script on production data
   - Verify field removal from all records
   - Confirm data integrity and relationships

**Phase 4: Testing and Validation**
1. **API Endpoint Testing**
   - Test creation without removed field
   - Test retrieval (ensure field is absent)
   - Test updates (process field correctly)
   - Test deletion operations
   - Validate error handling for invalid field data

2. **Frontend Testing**
   - Verify forms load without field
   - Test submission workflow
   - Confirm display templates render correctly
   - Validate JavaScript functionality

3. **Integration Testing**
   - Test complete CRUD workflows
   - Verify related entity operations work
   - Confirm data consistency across layers

**Key Success Factors:**
- **Comprehensive Discovery**: Search ALL file types for ALL field variations
- **Systematic Updates**: Follow dependency order (constants → models → routes → frontend)
- **Data Safety**: Always create backups before database modifications
- **Validation**: Test each layer independently before integration
- **Documentation**: Update schema documentation to reflect changes

### Data Export/Import
- JSON format for human readability
- Bulk data loading capabilities
- Validation during import process
- Rollback capabilities for failed migrations

## Monitoring and Maintenance

### Logging
- Structured logging with correlation IDs
- Operation timing and performance metrics
- Error tracking and recovery procedures
- Audit trail for all modifications

### Health Checks
- File accessibility and integrity validation
- JSON format verification
- Backup creation verification
- Database statistics monitoring

---

## Usage Examples

### Creating a Complete Customer → Project → Quote → VendorQuote Flow

```python
# 1. Create Customer
customer = {
    "name": "Acme Corporation",
    "address": "123 Business Ave",
    "city": "New York",
    "state": "NY",
    "zip": "10001",
    "status": "active"
}

# 2. Create Project for Customer
project = {
    "customer_id": 1,
    "name": "Data Center Migration",
    "project_type": "installation",
    "status": "planning",
    "budget": 500000.00,
    "start_date": "2024-01-15"
}

# 3. Create Quote for Project
quote = {
    "project_id": 1,
    "name": "Hardware Transportation",
    "status": "draft",
    "amount": 75000.00
}

# 4. Create VendorQuote with auto-generated tracking_id
vendor_quote = {
    "quote_id": 1,
    "vendor_id": 5,
    "items_text": "20 Server racks, 100 Network switches",
    "delivery_requirements": "Climate-controlled trucking",
    "is_rush": true,
    "status": "pending"
}
# Result: tracking_id = "VQ24-1" (for first quote of 2024)
```

### Query Patterns

```python
# Get all active projects for a customer
projects = db.filter_by_field("projects.json", "customer_id", customer_id)

# Get all quotes for a project (including deleted)
quotes = db.filter_by_field("quotes.json", "project_id", project_id, include_deleted=True)

# Find vendor quote by tracking ID
vendor_quote = next((vq for vq in load_vendor_quotes() if vq["tracking_id"] == "VQ24-1"), None)

# Get file statistics
stats = db.get_file_stats("customers.json")
# Returns: {"total_items": 50, "active_items": 45, "deleted_items": 5, ...}
```

## Quick Reference Summary

### Entity Count & Records
- **Customers**: 50 records (active, no industry field)
- **Projects**: 100+ records with budget tracking
- **Quotes**: 200+ records with amount validation
- **Vendors**: 20+ suppliers with ratings
- **VendorQuotes**: 500+ with tracking IDs

### Key Features
- ✅ **Soft Delete**: All entities support soft deletion with audit trail
- ✅ **Auto-generated IDs**: Sequential primary keys with collision prevention
- ✅ **Tracking System**: VQYY-ID format for vendor quotes (e.g., VQ24-1)
- ✅ **Field Validation**: Email, ZIP, phone, currency, date formats
- ✅ **Relationship Integrity**: Foreign key constraints enforced at application level
- ✅ **Backup System**: Automatic timestamped backups before all write operations

### Validated Field Removal Process
The industry field removal process (completed 2025-10-17) serves as a validated template for future schema modifications:
1. **Backend Phase**: Constants → Dependencies → Models → API Routes
2. **Frontend Phase**: Forms → JavaScript → Display Templates
3. **Database Phase**: Backup → Migration → Validation
4. **Testing Phase**: API → Frontend → Integration

### Access Points
- **Web Interface**: http://localhost:8001
- **API Base**: http://localhost:8001/api/
- **Data Directory**: `data/` (JSON files)
- **Documentation**: `DATABASE_SCHEMA_COMPREHENSIVE.md`

---

This comprehensive schema documentation provides the foundation for understanding, maintaining, and extending the database structure of the Hierarchical Data Explorer application. The documented field removal process has been successfully validated and can serve as a template for future schema evolution needs.