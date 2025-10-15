# Testing Examples

This document provides quick examples of how to run and use the test suite for the Projects API.

## 🚀 Quick Start

### 1. Install Test Dependencies

```bash
pip install -r requirements-test.txt
```

### 2. Run All Projects Tests

```bash
python run_tests.py projects
```

### 3. Run with Coverage

```bash
python run_tests.py coverage
```

## 📋 Specific Test Examples

### Running Individual Test Classes

```bash
# Run main test class
pytest tests/api/test_projects.py::TestProjectsAPI -v

# Run edge cases
pytest tests/api/test_projects.py::TestProjectsAPIEdgeCases -v

# Run integration tests
pytest tests/api/test_projects.py::TestProjectsAPIIntegration -v
```

### Running Specific Test Methods

```bash
# Test project creation
pytest tests/api/test_projects.py::TestProjectsAPI::test_create_project_success -v

# Test error handling
pytest tests/api/test_projects.py::TestProjectsAPI::test_create_project_validation_errors -v

# Test edge cases
pytest tests/api/test_projects.py::TestProjectsAPIEdgeCases::test_create_project_maximum_budget -v
```

## 🔍 Debugging Tests

### Run with Detailed Output

```bash
pytest tests/api/test_projects.py -vv -s
```

### Run with Debugger

```bash
pytest tests/api/test_projects.py::test_create_project_success --pdb
```

### Run Specific Test Patterns

```bash
# Run all create tests
pytest tests/api/test_projects.py -k "create_project" -v

# Run all validation tests
pytest tests/api/test_projects.py -k "validation" -v

# Run all error tests
pytest tests/api/test_projects.py -k "error" -v
```

## 📊 Coverage Examples

### Generate Coverage Report

```bash
# HTML report (recommended)
pytest --cov=src --cov-report=html tests/api/test_projects.py

# Terminal report
pytest --cov=src --cov-report=term-missing tests/api/test_projects.py

# Both reports
pytest --cov=src --cov-report=html --cov-report=term-missing tests/api/test_projects.py
```

### View Coverage Report

After running HTML coverage:
```bash
# Open in browser
open htmlcov/index.html

# Or view specific file
open htmlcov/src_api_routes_projects_py.html
```

## 🧪 Test Categories

### Success Path Tests

```bash
# All successful operation tests
pytest tests/api/test_projects.py -k "success" -v
```

### Error Handling Tests

```bash
# All error scenarios
pytest tests/api/test_projects.py -k "error" -v
```

### Validation Tests

```bash
# Input validation tests
pytest tests/api/test_projects.py -k "validation" -v
```

### Edge Case Tests

```bash
# Boundary conditions
pytest tests/api/test_projects.py::TestProjectsAPIEdgeCases -v
```

## 🛠️ Test Development

### Create New Test

```python
def test_new_feature(self, client, test_db_manager):
    """Test new project feature."""
    # Arrange
    project_data = {
        "name": "New Feature Test",
        "budget": 100000,
        "status": "active",
        "start_date": "2024-01-01",
        "customer_id": 1
    }

    with patch('src.api.routes.projects.get_database_manager') as mock_get_db, \
         patch('src.api.routes.projects.validate_customer_exists') as mock_validate:

        mock_get_db.return_value = test_db_manager
        mock_validate.return_value = True

        # Act
        response = client.post("/api/projects/", json=project_data)

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "new feature test" in data["data"]["name"].lower()
```

### Test with Mock Data

```python
def test_with_custom_data(self, client):
    """Test with custom mock data."""
    # Create custom test data
    custom_projects = [
        {"id": 999, "customer_id": 1, "name": "Custom Project",
         "budget": 12345, "status": "active", "start_date": "2024-01-01"}
    ]

    with patch('src.api.routes.projects.get_database_manager') as mock_get_db:
        mock_db = Mock()
        mock_db.filter_by_field.return_value = custom_projects
        mock_get_db.return_value = mock_db

        response = client.get("/api/projects/1")
        assert response.status_code == 200
        assert len(response.json()) == 1
        assert response.json()[0]["name"] == "Custom Project"
```

## 📝 Test Results Examples

### Successful Test Output

```
==================================================== test session starts ====================================================
collected 31 items

tests/api/test_projects.py::TestProjectsAPI::test_get_projects_success PASSED                                           [ 3%]
tests/api/test_projects.py::TestProjectsAPI::test_create_project_success PASSED                                       [ 6%]
tests/api/test_projects.py::TestProjectsAPI::test_update_project_success PASSED                                       [ 9%]
tests/api/test_projects.py::TestProjectsAPI::test_delete_project_success PASSED                                       [12%]

=============================== 31 passed, 1 warning in 2.45s ================================
```

### Coverage Report Output

```
---------- coverage: platform linux, python 3.12.0 -----------
Name                                 Stmts   Miss  Cover   Missing
------------------------------------------------------------------
src/api/routes/projects.py            180     5    97%   25-30, 55-58
src/core/database.py                  372    12    97%   150-155, 300-305
------------------------------------------------------------------
TOTAL                                552     17    97%
```

### Failed Test Example

```
tests/api/test_projects.py::TestProjectsAPI::test_create_project_validation_errors FAILED

>       assert response.status_code == 400
E       assert 422 == 400
E        +  where 422 = <Response [422]>.status_code

E       Expected validation error but got FastAPI validation error
```

## 🎯 Best Practices

### 1. Test Naming

```python
# Good: descriptive and specific
def test_create_project_with_maximum_budget_should_succeed(self):
    # Bad: too generic
def test_project_creation(self):
```

### 2. Test Structure

```python
def test_example(self, client, test_db_manager):
    """Clear description of what is being tested."""
    # Arrange - Setup test data and mocks
    test_data = {...}

    # Act - Execute the operation
    with patch(...) as mock:
        mock.return_value = {...}
        response = client.post("/api/projects/", json=test_data)

    # Assert - Verify expected outcome
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
```

### 3. Error Testing

```python
def test_error_scenario(self, client):
    """Test how system handles errors gracefully."""
    # Test both the error and the error response
    response = client.post("/api/projects/", json=invalid_data)

    assert response.status_code == 400
    data = response.json()
    assert data["success"] is False
    assert "validation" in data["error"].lower() or "required" in data["error"].lower()
```

## 🔗 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing Guide](https://fastapi.tiangolo.com/tutorial/testing/)
- [Mock Documentation](https://docs.python.org/3/library/unittest.mock.html)
- [Coverage.py Documentation](https://coverage.readthedocs.io/)