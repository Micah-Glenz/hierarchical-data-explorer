API Reference
=============

This section provides comprehensive documentation for all REST API endpoints
in the Hierarchical Data Explorer.

Base URL
---------

```
http://localhost:8001/api
```

Authentication
--------------

Currently, the API does not require authentication. This may change in future
versions.

Response Format
---------------

All API responses follow a consistent format:

Success Response
~~~~~~~~~~~~~~~~

.. code-block:: json

   {
       "message": "Operation completed successfully",
       "data": { ... }
   }

Error Response
~~~~~~~~~~~~~~

.. code-block:: json

   {
       "detail": "Error description"
   }

HTTP Status Codes
-----------------

- ``200 OK``: Request successful
- ``201 Created``: Resource created successfully
- ``400 Bad Request``: Validation error or invalid data
- ``404 Not Found``: Resource not found
- ``500 Internal Server Error``: Server error

Endpoints
---------

Customers
~~~~~~~~~~

.. http:get:: /api/customers

   Get all customers

   **Response:**

   .. code-block:: json

      [
          {
              "id": 1,
              "name": "Acme Corporation",
              "industry": "Technology",
              "status": "active",
              "created_date": "2024-01-15",
              "project_count": 3
          }
      ]

   :statuscode 200: Success
   :statuscode 500: Server error

.. http:get:: /api/customers/{customer_id}

   Get a specific customer by ID

   :param customer_id: Customer ID
   :statuscode 200: Success
   :statuscode 404: Customer not found
   :statuscode 500: Server error

.. http:post:: /api/customers

   Create a new customer

   **Request:**

   .. code-block:: json

      {
          "name": "New Corporation",
          "industry": "Finance",
          "status": "active",
          "created_date": "2024-01-20"
      }

   :<json string name: Customer name (required, max 255 chars)
   :<json string industry: Customer industry (required, must be one of: Technology, Manufacturing, Retail, Healthcare, Logistics, Finance, Construction, Energy)
   :<json string status: Customer status (required, must be one of: active, planning, in_progress, on_hold, completed)
   :<json string created_date: Creation date in YYYY-MM-DD format (required)

   **Response:**

   .. code-block:: json

      {
          "message": "Customer created successfully",
          "data": {
              "id": 2,
              "name": "New Corporation",
              "industry": "Finance",
              "status": "active",
              "created_date": "2024-01-20",
              "project_count": 0
          }
      }

   :statuscode 201: Created
   :statuscode 400: Validation error
   :statuscode 500: Server error

.. http:put:: /api/customers/{customer_id}

   Update an existing customer

   :param customer_id: Customer ID
   :<json string name: Customer name (optional)
   :<json string industry: Customer industry (optional)
   :<json string status: Customer status (optional)

   **Response:**

   .. code-block:: json

      {
          "message": "Customer updated successfully",
          "data": {
              "id": 1,
              "name": "Updated Corporation",
              "industry": "Finance",
              "status": "active",
              "created_date": "2024-01-15",
              "project_count": 3
          }
      }

   :statuscode 200: Success
   :statuscode 400: Validation error
   :statuscode 404: Customer not found
   :statuscode 500: Server error

.. http:delete:: /api/customers/{customer_id}

   Delete a customer (soft delete with cascade)

   :param customer_id: Customer ID

   **Response:**

   .. code-block:: json

      {
          "message": "Customer and 3 related projects deleted successfully",
          "deleted_customer_id": 1,
          "deleted_projects": 3
      }

   :statuscode 200: Success
   :statuscode 404: Customer not found
   :statuscode 500: Server error

Projects
~~~~~~~~

.. http:get:: /api/projects/{customer_id}

   Get all projects for a specific customer

   :param customer_id: Customer ID

   **Response:**

   .. code-block:: json

      [
          {
              "id": 1,
              "name": "Website Redesign",
              "budget": 50000.00,
              "status": "active",
              "start_date": "2024-01-15",
              "customer_id": 1,
              "quote_count": 2
          }
      ]

   :statuscode 200: Success
   :statuscode 404: Customer not found
   :statuscode 500: Server error

.. http:post:: /api/projects

   Create a new project

   **Request:**

   .. code-block:: json

      {
          "name": "Mobile App Development",
          "budget": 75000.00,
          "status": "planning",
          "start_date": "2024-02-01",
          "customer_id": 1
      }

   :<json string name: Project name (required, max 255 chars)
   :<json number budget: Project budget (required, > 0, max 999999999.99)
   :<json string status: Project status (required, must be one of: active, planning, in_progress, on_hold, completed)
   :<json string start_date: Start date in YYYY-MM-DD format (required)
   :<json int customer_id: Customer ID (required)

   **Response:**

   .. code-block:: json

      {
          "message": "Project created successfully",
          "data": {
              "id": 2,
              "name": "Mobile App Development",
              "budget": 75000.00,
              "status": "planning",
              "start_date": "2024-02-01",
              "customer_id": 1,
              "quote_count": 0
          }
      }

   :statuscode 201: Created
   :statuscode 400: Validation error
   :statuscode 404: Customer not found
   :statuscode 500: Server error

.. http:put:: /api/projects/{project_id}

   Update an existing project

   :param project_id: Project ID
   :<json string name: Project name (optional)
   :<json number budget: Project budget (optional, > 0)
   :<json string status: Project status (optional)
   :<json string start_date: Start date (optional)

   :statuscode 200: Success
   :statuscode 400: Validation error
   :statuscode 404: Project not found
   :statuscode 500: Server error

.. http:delete:: /api/projects/{project_id}

   Delete a project (soft delete with cascade)

   :param project_id: Project ID

   **Response:**

   .. code-block:: json

      {
          "message": "Project and 2 related quotes deleted successfully",
          "deleted_project_id": 1,
          "deleted_quotes": 2
      }

   :statuscode 200: Success
   :statuscode 404: Project not found
   :statuscode 500: Server error

Quotes
~~~~~~

.. http:get:: /api/quotes/{project_id}

   Get all quotes for a specific project

   :param project_id: Project ID

   **Response:**

   .. code-block:: json

      [
          {
              "id": 1,
              "name": "Phase 1 Quote",
              "amount": 25000.00,
              "status": "active",
              "valid_until": "2024-03-15",
              "project_id": 1,
              "freight_request_count": 1
          }
      ]

   :statuscode 200: Success
   :statuscode 404: Project not found
   :statuscode 500: Server error

.. http:post:: /api/quotes

   Create a new quote

   **Request:**

   .. code-block:: json

      {
          "name": "Phase 2 Quote",
          "amount": 30000.00,
          "status": "planning",
          "valid_until": "2024-04-01",
          "project_id": 1
      }

   :<json string name: Quote name (required, max 255 chars)
   :<json number amount: Quote amount (required, > 0, max 999999999.99)
   :<json string status: Quote status (required, must be one of: active, planning, in_progress, on_hold, completed)
   :<json string valid_until: Valid until date in YYYY-MM-DD format (optional)
   :<json int project_id: Project ID (required)

   :statuscode 201: Created
   :statuscode 400: Validation error
   :statuscode 404: Project not found
   :statuscode 500: Server error

.. http:put:: /api/quotes/{quote_id}

   Update an existing quote

   :param quote_id: Quote ID
   :<json string name: Quote name (optional)
   :<json number amount: Quote amount (optional, > 0)
   :<json string status: Quote status (optional)
   :<json string valid_until: Valid until date (optional)

   :statuscode 200: Success
   :statuscode 400: Validation error
   :statuscode 404: Quote not found
   :statuscode 500: Server error

.. http:delete:: /api/quotes/{quote_id}

   Delete a quote (soft delete with cascade)

   :param quote_id: Quote ID

   **Response:**

   .. code-block:: json

      {
          "message": "Quote and 1 related freight requests deleted successfully",
          "deleted_quote_id": 1
      }

   :statuscode 200: Success
   :statuscode 404: Quote not found
   :statuscode 500: Server error

Freight Requests
~~~~~~~~~~~~~~~~

.. http:get:: /api/freight-requests/{quote_id}

   Get all freight requests for a specific quote

   :param quote_id: Quote ID

   **Response:**

   .. code-block:: json

      [
          {
              "id": 1,
              "name": "Equipment Shipping",
              "vendor_id": 1,
              "vendor_name": "Global Logistics",
              "status": "active",
              "weight": 150.5,
              "priority": "high",
              "estimated_delivery": "2024-02-15",
              "quote_id": 1
          }
      ]

   :statuscode 200: Success
   :statuscode 404: Quote not found
   :statuscode 500: Server error

.. http:post:: /api/freight-requests

   Create a new freight request

   **Request:**

   .. code-block:: json

      {
          "name": "Supply Chain Delivery",
          "vendor_id": 2,
          "status": "planning",
          "weight": 75.0,
          "priority": "medium",
          "estimated_delivery": "2024-03-01",
          "quote_id": 1
      }

   :<json string name: Freight request name (required, max 255 chars)
   :<json int vendor_id: Vendor ID (required)
   :<json string status: Freight request status (required, must be one of: active, planning, in_progress, on_hold, completed)
   :<json number weight: Weight in kg (required, > 0, max 999999.99)
   :<json string priority: Priority level (required, must be one of: low, medium, high, critical)
   :<json string estimated_delivery: Estimated delivery date in YYYY-MM-DD format (optional)
   :<json int quote_id: Quote ID (required)

   :statuscode 201: Created
   :statuscode 400: Validation error
   :statuscode 404: Quote or vendor not found
   :statuscode 500: Server error

.. http:put:: /api/freight-requests/{freight_request_id}

   Update an existing freight request

   :param freight_request_id: Freight request ID
   :<json string name: Freight request name (optional)
   :<json int vendor_id: Vendor ID (optional)
   :<json string status: Freight request status (optional)
   :<json number weight: Weight in kg (optional, > 0)
   :<json string priority: Priority level (optional)
   :<json string estimated_delivery: Estimated delivery date (optional)

   :statuscode 200: Success
   :statuscode 400: Validation error
   :statuscode 404: Freight request not found
   :statuscode 500: Server error

.. http:delete:: /api/freight-requests/{freight_request_id}

   Delete a freight request (soft delete)

   :param freight_request_id: Freight request ID

   **Response:**

   .. code-block:: json

      {
          "message": "Freight request deleted successfully",
          "deleted_freight_request_id": 1
      }

   :statuscode 200: Success
   :statuscode 404: Freight request not found
   :statuscode 500: Server error

Vendors
~~~~~~~

.. http:get:: /api/vendors

   Get all vendors

   **Response:**

   .. code-block:: json

      [
          {
              "id": 1,
              "name": "Global Logistics",
              "contact_email": "info@globallogistics.com",
              "phone": "+1-555-0123"
          }
      ]

   :statuscode 200: Success
   :statuscode 500: Server error

Error Handling
--------------

The API uses standard HTTP status codes and returns detailed error messages
in the response body.

Validation Errors
~~~~~~~~~~~~~~~~~

When validation fails, the API returns a 400 status with detailed error
information:

.. code-block:: json

   {
       "detail": {
           "name": "Name is required",
           "budget": "Budget must be greater than 0"
       }
   }

Not Found Errors
~~~~~~~~~~~~~~~~

When a requested resource is not found:

.. code-block:: json

   {
       "detail": "Customer with ID 999 not found"
   }

Server Errors
~~~~~~~~~~~~~

For unexpected server errors:

.. code-block:: json

   {
       "detail": "Internal server error"
   }

Data Models
-----------

Customer Model
~~~~~~~~~~~~~~

.. code-block:: json

   {
       "id": "integer (auto-generated)",
       "name": "string (required, max 255 chars)",
       "industry": "string (required, enum)",
       "status": "string (required, enum)",
       "created_date": "string (required, YYYY-MM-DD)",
       "project_count": "integer (calculated)"
   }

Project Model
~~~~~~~~~~~~~~

.. code-block:: json

   {
       "id": "integer (auto-generated)",
       "name": "string (required, max 255 chars)",
       "budget": "number (required, > 0, max 999999999.99)",
       "status": "string (required, enum)",
       "start_date": "string (required, YYYY-MM-DD)",
       "customer_id": "integer (required)",
       "quote_count": "integer (calculated)"
   }

Quote Model
~~~~~~~~~~~~

.. code-block:: json

   {
       "id": "integer (auto-generated)",
       "name": "string (required, max 255 chars)",
       "amount": "number (required, > 0, max 999999999.99)",
       "status": "string (required, enum)",
       "valid_until": "string (optional, YYYY-MM-DD)",
       "project_id": "integer (required)",
       "freight_request_count": "integer (calculated)"
   }

Freight Request Model
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: json

   {
       "id": "integer (auto-generated)",
       "name": "string (required, max 255 chars)",
       "vendor_id": "integer (required)",
       "vendor_name": "string (enriched)",
       "status": "string (required, enum)",
       "weight": "number (required, > 0, max 999999.99)",
       "priority": "string (required, enum)",
       "estimated_delivery": "string (optional, YYYY-MM-DD)",
       "quote_id": "integer (required)"
   }

Vendor Model
~~~~~~~~~~~~

.. code-block:: json

   {
       "id": "integer (auto-generated)",
       "name": "string (required, max 255 chars)",
       "contact_email": "string (optional, email format)",
       "phone": "string (optional)"
   }