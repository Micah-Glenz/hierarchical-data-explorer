Development Guide
=================

This guide covers development setup, architecture, and contribution guidelines
for the Hierarchical Data Explorer.

.. contents::
   :local:
   :depth: 2

Development Setup
------------------

Prerequisites
~~~~~~~~~~~~~

* Python 3.8+
* Git
* Modern web browser
* Code editor (VS Code recommended)

Local Development
~~~~~~~~~~~~~~~~~

1. **Clone the repository**::

   git clone https://github.com/Micah-Glenz/hierarchical-data-explorer.git
   cd hierarchical-data-explorer

2. **Create virtual environment**::

   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS/Linux
   source venv/bin/activate

3. **Install dependencies**::

   pip install -r requirements.txt

4. **Install development dependencies**::

   pip install -r requirements-dev.txt

5. **Set up pre-commit hooks**::

   pre-commit install

6. **Run the application**::

   python main.py

7. **Access the application**:

   Open ``http://localhost:8001`` in your browser.

Development Dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~

Development dependencies are listed in ``requirements-dev.txt``:

- **pytest**: Testing framework
- **black**: Code formatting
- **flake8**: Linting
- **mypy**: Type checking
- **pre-commit**: Git hooks

Running Tests
~~~~~~~~~~~~~

Run all tests::

   pytest

Run with coverage::

   pytest --cov=src --cov-report=html

Run specific test file::

   pytest tests/test_api.py

Code Quality
~~~~~~~~~~~~

Format code::

   black src/ tests/

Lint code::

   flake8 src/ tests/

Type check::

   mypy src/

Project Structure
-----------------

.. graphviz::

    digraph project_structure {
        rankdir=TB;

        root [label="hierarchical-data-explorer/"];
        src [label="src/"];
        static [label="static/"];
        templates [label="templates/"];
        docs [label="docs/"];
        tests [label="tests/"];
        data [label="data/"];

        root -> src;
        root -> static;
        root -> templates;
        root -> docs;
        root -> tests;
        root -> data;

        src -> core [label="core/"];
        src -> api [label="api/"];
        core -> config [label="config.py"];
        core -> database [label="database.py"];
        core -> exceptions [label="exceptions.py"];
        api -> models [label="models.py"];
        api -> routes [label="routes/"];
        api -> dependencies [label="dependencies.py"];

        static -> css [label="css/"];
        static -> js [label="js/"];
        css -> base [label="base.css"];
        css -> layout [label="layout.css"];
        css -> components [label="components.css"];
        css -> utilities [label="utilities.css"];
        js -> utils [label="utils.js"];
        js -> api [label="api.js"];
        js -> components [label="components.js"];
        js -> data_explorer [label="data-explorer.js"];

        templates -> partials [label="partials/"];
        partials -> forms [label="forms/"];
    }

Directory Layout
~~~~~~~~~~~~~~~~

```
hierarchical-data-explorer/
├── src/                          # Python source code
│   ├── core/                     # Core application services
│   │   ├── config.py            # Configuration management
│   │   ├── database.py          # Database operations
│   │   └── exceptions.py        # Custom exceptions
│   └── api/                      # API layer
│       ├── models.py            # Pydantic models
│       ├── dependencies.py      # FastAPI dependencies
│       └── routes/              # API route handlers
│           ├── customers.py
│           ├── projects.py
│           ├── quotes.py
│           ├── freight_requests.py
│           └── vendors.py
├── static/                       # Static frontend assets
│   ├── css/                     # Stylesheets
│   │   ├── base.css             # Base styles and variables
│   │   ├── layout.css           # Layout components
│   │   ├── components.css       # UI components
│   │   └── utilities.css        # Utility classes
│   └── js/                      # JavaScript modules
│       ├── utils.js             # Utility functions
│       ├── api.js               # API service layer
│       ├── components.js        # Reusable components
│       └── data-explorer.js     # Main application logic
├── templates/                    # HTML templates
│   └── partials/               # Reusable HTML components
│       ├── header.html
│       ├── column.html
│       ├── modal.html
│       ├── details-pane.html
│       └── forms/              # Form templates
├── docs/                        # Documentation
├── tests/                       # Test files
├── data/                        # JSON data files
├── main.py                      # Application entry point
├── requirements.txt             # Production dependencies
└── requirements-dev.txt         # Development dependencies
```

Architecture
------------

The application follows a layered architecture with clear separation of concerns.

Backend Architecture
~~~~~~~~~~~~~~~~~~~~

.. graphviz::

    digraph backend_arch {
        rankdir=TB;

        main [label="main.py\nApplication Entry"];
        fastapi [label="FastAPI\nWeb Framework"];
        routes [label="API Routes\nHTTP Handlers"];
        core [label="Core Services\nBusiness Logic"];
        database [label="JSON Database\nData Storage"];

        main -> fastapi;
        fastapi -> routes;
        routes -> core;
        core -> database;
    }

**Core Services**

- **Config**: Centralized configuration management with environment variables
- **Database**: JSON file operations with soft delete and cascade handling
- **Exceptions**: Custom exception hierarchy for error handling

**API Layer**

- **Models**: Pydantic models for request/response validation
- **Routes**: HTTP endpoint handlers organized by entity
- **Dependencies**: FastAPI dependency injection for shared services

Frontend Architecture
~~~~~~~~~~~~~~~~~~~~~

.. graphviz::

    digraph frontend_arch {
        rankdir=TB;

        html [label="HTML\nTemplates"];
        alpine [label="Alpine.js\nReactive Components"];
        htmx [label="HTMX\nAJAX Interactions"];
        css [label="CSS\nComponents & Utilities"];
        js [label="JavaScript\nModules"];

        html -> alpine;
        html -> htmx;
        html -> css;
        alpine -> js;
        htmx -> js;
    }

**Component System**

- **Base**: CSS variables, typography, and base styles
- **Layout**: Grid system, responsive design
- **Components**: UI components (cards, modals, forms)
- **Utilities**: Helper classes and responsive utilities

**JavaScript Modules**

- **utils**: Common utility functions and helpers
- **api**: HTTP service layer with error handling
- **components**: Reusable Alpine.js components
- **data-explorer**: Main application state management

Data Flow
~~~~~~~~~~

1. **User Interaction** → Alpine.js component
2. **State Update** → HTTP request via HTMX/fetch
3. **API Request** → FastAPI route handler
4. **Business Logic** → Core service method
5. **Data Operation** → JSON file system
6. **Response** → API response with data
7. **UI Update** → Alpine.js reactive update

Coding Standards
----------------

Python Guidelines
~~~~~~~~~~~~~~~~

- Follow `PEP 8 <https://www.python.org/dev/peps/pep-0008/>`_ style guide
- Use type hints for all function signatures
- Write docstrings in Google format
- Keep functions small and focused
- Use meaningful variable and function names

**Example:**

.. code-block:: python

   def create_customer(customer_data: CustomerCreate) -> CustomerResponse:
       """Create a new customer in the system.

       Args:
           customer_data: The customer creation data with validation

       Returns:
           The created customer with generated ID and metadata

       Raises:
           DataValidationError: If validation fails
           DatabaseOperationError: If database operation fails
       """
       # Implementation here
       pass

JavaScript Guidelines
~~~~~~~~~~~~~~~~~~~~~

- Use modern ES6+ syntax
- Prefer arrow functions for callbacks
- Use JSDoc comments for functions
- Handle errors gracefully
- Keep modules focused and small

**Example:**

.. code-block:: javascript

   /**
    * Format currency values using USD formatting
    * @param {number} amount - The amount to format
    * @returns {string} The formatted currency string
    */
   const formatCurrency = (amount) => {
       return new Intl.NumberFormat('en-US', {
           style: 'currency',
           currency: 'USD'
       }).format(amount || 0);
   };

CSS Guidelines
~~~~~~~~~~~~~~

- Use BEM methodology for class naming
- Organize styles into logical modules
- Use CSS custom properties for theming
- Write mobile-first responsive design
- Comment complex or non-obvious styles

**Example:**

.. code-block:: css

   /* Card component */
   .card {
       background-color: var(--color-background);
       border: 1px solid var(--color-border);
       border-radius: var(--border-radius);
       transition: all 0.15s ease-in-out;
   }

   .card--selected {
       border-color: var(--color-primary);
       box-shadow: var(--shadow-md);
   }

   .card__header {
       padding: var(--spacing-md);
       border-bottom: 1px solid var(--color-border);
   }

Testing Strategy
----------------

Test Coverage
~~~~~~~~~~~~~

Aim for 80%+ test coverage across all modules:

- **Unit Tests**: Test individual functions and classes
- **Integration Tests**: Test API endpoints and data flow
- **Frontend Tests**: Test JavaScript components and interactions
- **End-to-End Tests**: Test complete user workflows

Test Structure
~~~~~~~~~~~~~~

```
tests/
├── unit/                    # Unit tests
│   ├── test_config.py
│   ├── test_database.py
│   └── test_models.py
├── integration/             # Integration tests
│   ├── test_api.py
│   └── test_data_flow.py
├── frontend/               # Frontend tests
│   ├── test_components.js
│   └── test_utils.js
└── e2e/                    # End-to-end tests
    └── test_workflows.py
```

Writing Tests
~~~~~~~~~~~~~~

**Unit Tests Example:**

.. code-block:: python

   import pytest
   from src.core.config import Settings

   def test_settings_initialization():
       """Test that Settings initializes with default values."""
       settings = Settings()
       assert settings.HOST == "0.0.0.0"
       assert settings.PORT == 8001

   def test_data_directory_validation():
       """Test data directory validation."""
       settings = Settings()
       assert settings.DATA_DIR.exists()

**API Tests Example:**

.. code-block:: python

   import pytest
   from fastapi.testclient import TestClient
   from main import app

   client = TestClient(app)

   def test_get_customers():
       """Test getting all customers."""
       response = client.get("/api/customers")
       assert response.status_code == 200
       assert isinstance(response.json(), list)

   def test_create_customer():
       """Test creating a new customer."""
       customer_data = {
           "name": "Test Customer",
           "industry": "Technology",
           "status": "active",
           "created_date": "2024-01-15"
       }
       response = client.post("/api/customers", json=customer_data)
       assert response.status_code == 201
       assert response.json()["data"]["name"] == "Test Customer"

Debugging
---------

Development Server
~~~~~~~~~~~~~~~~~~

Run the development server with auto-reload::

   python main.py

The server will reload automatically when code changes are detected.

Logging
~~~~~~

Check application logs in the console. For production, configure
structured logging with appropriate log levels.

Browser Developer Tools
~~~~~~~~~~~~~~~~~~~~~~~

Use browser developer tools for frontend debugging:

- **Console**: JavaScript errors and Alpine.js logs
- **Network**: HTTP requests and responses
- **Elements**: DOM inspection and CSS debugging
- **Application**: Local storage and session data

Common Issues
~~~~~~~~~~~~

**CORS Issues**: Ensure proper CORS configuration for development

**Import Errors**: Check Python path and module structure

**JavaScript Errors**: Verify script loading order and dependencies

**Data Loading Issues**: Check API endpoints and data file permissions

Deployment
----------

Production Setup
~~~~~~~~~~~~~~~~

1. **Install production dependencies**::

   pip install -r requirements.txt

2. **Set environment variables**::

   export HOST=0.0.0.0
   export PORT=8001

3. **Run with production server**::

   uvicorn main:app --host 0.0.0.0 --port 8001 --workers 4

Docker Deployment
~~~~~~~~~~~~~~~~~~

.. code-block:: dockerfile

   FROM python:3.9-slim

   WORKDIR /app

   COPY requirements.txt .
   RUN pip install --no-cache-dir -r requirements.txt

   COPY . .

   EXPOSE 8001

   CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]

Build and run::

   docker build -t hierarchical-data-explorer .
   docker run -p 8001:8001 hierarchical-data-explorer

Performance Considerations
--------------------------

Frontend Optimization
~~~~~~~~~~~~~~~~~~~~~

- Use Alpine.js reactivity efficiently
- Minimize DOM manipulations
- Optimize bundle sizes
- Implement lazy loading for large datasets

Backend Optimization
~~~~~~~~~~~~~~~~~~~~

- Implement database indexing for JSON queries
- Use pagination for large result sets
- Cache frequently accessed data
- Optimize JSON file operations

Contributing
------------

Pull Request Process
~~~~~~~~~~~~~~~~~~~~~

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Update documentation
7. Submit a pull request

Code Review Checklist
~~~~~~~~~~~~~~~~~~~~~

- Code follows style guidelines
- Tests are included and passing
- Documentation is updated
- No breaking changes without discussion
- Security implications considered
- Performance impact assessed

Release Process
~~~~~~~~~~~~~~

1. Update version number in ``main.py``
2. Update ``CHANGELOG.md``
3. Create Git tag
4. Update documentation
5. Deploy to production

Getting Help
------------

For development questions or issues:

- **Documentation**: Check this guide and API reference
- **Issues**: Report bugs on GitHub Issues
- **Discussions**: Ask questions on GitHub Discussions
- **Code Review**: Request help via pull request reviews