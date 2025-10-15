Hierarchical Data Explorer Documentation
==========================================

Welcome to the Hierarchical Data Explorer documentation! This application
provides a web-based interface for managing hierarchical data with
a 4-tier structure: Customers → Projects → Quotes → Freight Requests.

.. image:: https://img.shields.io/badge/Version-1.0.0-blue.svg
   :target: https://github.com/Micah-Glenz/hierarchical-data-explorer
   :alt: Version

.. image:: https://img.shields.io/badge/License-MIT-green.svg
   :target: LICENSE
   :alt: License

.. contents::
   :local:
   :depth: 2

Features
--------

* **Hierarchical Data Management**: Navigate through 4-tier hierarchy
* **Real-time Updates**: Live data updates with HTMX and Alpine.js
* **Responsive Design**: Mobile-friendly interface using IBM Carbon Design
* **RESTful API**: Complete CRUD operations for all data entities
* **Soft Delete**: Safe deletion with cascade management
* **Search & Filter**: Advanced sorting and filtering capabilities
* **Modern Stack**: FastAPI backend with Alpine.js frontend

Quick Start
-----------

.. note:: This section covers getting the application running. For detailed
   development setup, see :doc:`development/index`.

Prerequisites
~~~~~~~~~~~~~

* Python 3.8+
* Modern web browser with JavaScript enabled

Installation
~~~~~~~~~~~~

1. Clone the repository::

   git clone https://github.com/Micah-Glenz/hierarchical-data-explorer.git
   cd hierarchical-data-explorer

2. Install dependencies::

   pip install -r requirements.txt

3. Run the application::

   python main.py

4. Open your browser to ``http://localhost:8001``

User Guide
----------

Core Concepts
~~~~~~~~~~~~~

The application manages data in a hierarchical structure:

.. graphviz::

    digraph hierarchy {
        rankdir=LR;
        node [shape=record, style=filled, fillcolor=lightblue];

        customer [label="{Customer|• Name\l• Industry\l• Status\l• Created Date\l}"];
        project [label="{Project|• Name\l• Budget\l• Status\l• Start Date\l}"];
        quote [label="{Quote|• Name\l• Amount\l• Status\l• Valid Until\l}"];
        freight [label="{Freight Request|• Name\l• Vendor\l• Weight\l• Priority\l}"];

        customer -> project [label="1:N"];
        project -> quote [label="1:N"];
        quote -> freight [label="1:N"];
    }

Navigating the Interface
~~~~~~~~~~~~~~~~~~~~~~~~~

The main interface consists of four columns representing each hierarchy level:

.. figure:: _images/interface-overview.png
   :alt: Main Interface Overview
   :align: center

   Main interface showing the 4-column layout

* **Customers Column**: Shows all customers in the system
* **Projects Column**: Shows projects for the selected customer
* **Quotes Column**: Shows quotes for the selected project
* **Freight Requests Column**: Shows freight requests for the selected quote

Managing Data
~~~~~~~~~~~~~

Creating Items
++++++++++++++

1. Select the parent item (if required)
2. Click the ``+`` button in the appropriate column
3. Fill in the required fields
4. Click ``Create``

Editing Items
+++++++++++++

1. Select an item to view its details in the details pane
2. Click the ``Edit`` button in the details pane
3. Modify the desired fields
4. Click ``Update``

Deleting Items
++++++++++++++

.. warning:: Deleting an item will also delete all child items
   (cascade delete). This action cannot be undone.

1. Select an item to view its details
2. Click the ``Delete`` button in the details pane
3. Confirm the deletion in the dialog

Sorting and Filtering
~~~~~~~~~~~~~~~~~~~~~

Each column provides sorting options:

* **Name**: Alphabetical sorting
* **Status**: Group by status (Active, Planning, etc.)
* **ID**: Numerical sorting
* **Other fields**: Entity-specific fields (Budget, Amount, Priority, etc.)

Keyboard Shortcuts
~~~~~~~~~~~~~~~~~~

* ``Ctrl+K``: Clear all selections
* ``Escape``: Close modal dialogs
* ``Tab``: Navigate between form fields
* ``Enter``: Submit forms in modals

API Reference
-------------

The application provides a RESTful API for all data operations. See
:doc:`api/index` for complete API documentation.

Core Endpoints
~~~~~~~~~~~~~~

Customers
+++++++++

.. http:get:: /api/customers

   Get all customers

   :query page: Page number (default: 1)
   :query limit: Items per page (default: 50)
   :statuscode 200: Success
   :statuscode 500: Server error

.. http:post:: /api/customers

   Create a new customer

   :<json string name: Customer name (required)
   :<json string industry: Customer industry (required)
   :<json string status: Customer status (required)
   :<json string created_date: Creation date (required)
   :statuscode 201: Created
   :statuscode 400: Validation error
   :statuscode 500: Server error

Projects
++++++++

.. http:get:: /api/projects/{customer_id}

   Get all projects for a customer

   :param customer_id: Customer ID
   :statuscode 200: Success
   :statuscode 404: Customer not found
   :statuscode 500: Server error

Quotes
++++++

.. http:get:: /api/quotes/{project_id}

   Get all quotes for a project

   :param project_id: Project ID
   :statuscode 200: Success
   :statuscode 404: Project not found
   :statuscode 500: Server error

Freight Requests
++++++++++++++++

.. http:get:: /api/freight-requests/{quote_id}

   Get all freight requests for a quote

   :param quote_id: Quote ID
   :statuscode 200: Success
   :statuscode 404: Quote not found
   :statuscode 500: Server error

Development
-----------

For development setup, architecture, and contribution guidelines,
see :doc:`development/index`.

Architecture Overview
~~~~~~~~~~~~~~~~~~~~

.. graphviz::

    digraph architecture {
        rankdir=TB;

        frontend [label="Frontend\n• Alpine.js\n• HTMX\n• IBM Carbon CSS", shape=box, style=filled, fillcolor=lightgreen];
        api [label="API Layer\n• FastAPI\n• Pydantic Models\n• Validation", shape=box, style=filled, fillcolor=lightblue];
        core [label="Core Services\n• Database Manager\n• Configuration\n• Exception Handling", shape=box, style=filled, fillcolor=lightyellow];
        data [label="Data Layer\n• JSON Files\n• Soft Delete\n• Cascade Operations", shape=box, style=filled, fillcolor=lightcoral];

        frontend -> api;
        api -> core;
        core -> data;
    }

Technology Stack
~~~~~~~~~~~~~~~~

**Backend**
- FastAPI - Modern Python web framework
- Pydantic - Data validation and serialization
- Uvicorn - ASGI server

**Frontend**
- Alpine.js - Reactive JavaScript framework
- HTMX - AJAX-based interactions
- IBM Carbon Design System - UI components and styling

**Data Storage**
- JSON files for simplicity and portability
- Soft delete implementation
- Hierarchical data relationships

Troubleshooting
---------------

Common Issues
~~~~~~~~~~~~~

Application Won't Start
++++++++++++++++++++++++

1. Check Python version (requires 3.8+)
2. Install required dependencies: ``pip install -r requirements.txt``
3. Check if port 8001 is available
4. Verify data directory exists and is writable

Data Not Loading
++++++++++++++++

1. Check browser console for JavaScript errors
2. Verify API endpoints are accessible
3. Check data files exist in ``data/`` directory
4. Review server logs for error messages

Modal Dialogs Not Working
++++++++++++++++++++++++++

1. Ensure JavaScript is enabled in browser
2. Check for Alpine.js initialization errors
3. Verify HTMX is loaded correctly
4. Check CSS styles for modal display

Getting Help
~~~~~~~~~~~~~

* **Documentation**: Check the relevant sections in this guide
* **Issues**: Report bugs on `GitHub Issues <https://github.com/Micah-Glenz/hierarchical-data-explorer/issues>`_
* **Discussions**: Ask questions on `GitHub Discussions <https://github.com/Micah-Glenz/hierarchical-data-explorer/discussions>`_

License
-------

This project is licensed under the MIT License - see the
:doc:`license` file for details.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`