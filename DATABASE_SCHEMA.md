# Database Schema Tables & Fields

## Customer
| Field | Type | Constraints |
|-------|------|-------------|
| id | AutoField | Primary Key |
| name | CharField(255) | Unique |
| address | CharField(255) |  |
| city | CharField(255) |  |
| state | CharField(255) |  |
| zip | CharField(10) |  |
| sales_rep_name | CharField(255) | Optional |
| sales_rep_email | EmailField | Optional |
| created_at | DateTimeField | auto_now_add=True |
| updated_at | DateTimeField | auto_now=True |

## Project
| Field | Type | Constraints |
|-------|------|-------------|
| id | AutoField | Primary Key |
| customer | ForeignKey → Customer |  |
| name | CharField(255) |  |
| project_type | CharField(50) | Choices: installation, repair, maintenance, consulting, other |
| target_delivery_date | DateField |  |
| status | CharField(50) | Choices: planning, in_progress, on_hold, completed, cancelled |
| created_at | DateTimeField | auto_now_add=True |
| updated_at | DateTimeField | auto_now=True |

**Unique Constraint:** (customer_id, name)

## Quote
| Field | Type | Constraints |
|-------|------|-------------|
| id | AutoField | Primary Key |
| project | ForeignKey → Project |  |
| name | CharField(255) |  |
| description | TextField | Optional |
| status | CharField(50) | Choices: draft, pending_freight, ready, sent, approved, declined |
| created_at | DateTimeField | auto_now_add=True |
| updated_at | DateTimeField | auto_now=True |

**Unique Constraint:** (project_id, name)

## Vendor
| Field | Type | Constraints |
|-------|------|-------------|
| id | AutoField | Primary Key |
| name | CharField(255) | Unique |
| contact_name | CharField(255) | Optional |
| email | EmailField | Optional |
| created_at | DateTimeField | auto_now_add=True |
| updated_at | DateTimeField | auto_now=True |

## VendorFreightRequest
| Field | Type | Constraints |
|-------|------|-------------|
| id | AutoField | Primary Key |
| quote | ForeignKey → Quote |  |
| vendor | ForeignKey → Vendor |  |
| tracking_id | CharField(20) | Unique, Auto-generated (VQYY-ID format) |
| items_text | TextField |  |
| delivery_requirements | TextField | Optional |
| is_rush | BooleanField | default=False |
| status | CharField(50) | Choices: pending, quoted, approved, rejected, completed |
| quoted_amount | DecimalField(10,2) | Optional |
| created_at | DateTimeField | auto_now_add=True |
| updated_at | DateTimeField | auto_now=True |

**Unique Constraint:** (quote_id, vendor_id), tracking_id

## Relationships
- Customer → Project (1:many)
- Project → Quote (1:many)
- Quote → VendorFreightRequest (1:many)
- Vendor → VendorFreightRequest (1:many)