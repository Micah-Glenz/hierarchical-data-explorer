# Test Suite for Hierarchical Data Explorer

This directory contains comprehensive tests for the Hierarchical Data Explorer API.

## 📁 Test Structure

```
tests/
├── api/                          # API endpoint tests
│   ├── conftest.py              # Shared fixtures and utilities
│   └── test_projects.py         # Projects API tests
├── frontend/                    # Frontend tests (future)
├── integration/                 # Integration tests (future)
└── README.md                    # This file
```

## 🚀 Running Tests

### Using the Test Runner Script (Recommended)

```bash
# Run all tests
python run_tests.py all

# Run only projects API tests
python run_tests.py projects

# Run with coverage
python run_tests.py coverage

# Run with verbose output
python run_tests.py projects -v

# Run tests matching a keyword
python run_tests.py projects -k "test_create_project"

# Run without coverage
python run_tests.py projects --no-cov
```

### Using pytest directly

```bash
# Run all tests
pytest

# Run projects tests
pytest tests/api/test_projects.py

# Run with coverage
pytest --cov=src --cov-report=html

# Run with verbose output
pytest -v tests/api/test_projects.py

# Run specific test
pytest tests/api/test_projects.py::TestProjectsAPI::test_create_project_success
```

## 🧪 Test Categories

### API Tests (`tests/api/`)

Tests for all API endpoints including:

- **CRUD Operations**: Create, Read, Update, Delete
- **Validation**: Input validation and error handling
- **Business Logic**: Cascade deletion, relationship management
- **Edge Cases**: Boundary conditions and error scenarios
- **Integration**: End-to-end workflows

### Test Markers

Tests are organized using pytest markers:

- `@pytest.mark.unit`: Unit tests
- `@pytest.mark.integration`: Integration tests
- `@pytest.mark.api`: API tests
- `@pytest.mark.edge_case`: Edge case tests
- `@pytest.mark.validation`: Validation tests
- `@pytest.mark.error_handling`: Error handling tests

### Running by Markers

```bash
# Run only unit tests
pytest -m "unit"

# Run only API tests
pytest -m "api"

# Run tests excluding slow ones
pytest -m "not slow"
```

## 📊 Coverage

The test suite includes code coverage reporting:

```bash
# Generate coverage report
python run_tests.py coverage

# View HTML coverage report
open htmlcov/index.html
```

## 🔧 Test Data and Fixtures

### Mock Database

Tests use a mock database manager (`TestDatabaseManager`) that simulates:

- JSON file operations
- Data relationships
- Soft delete functionality
- Cascade deletion

### Test Fixtures

Key fixtures available in `conftest.py`:

- `client`: FastAPI test client
- `mock_db_manager`: Mock database manager
- `test_db_manager`: In-memory test database
- `temp_data_dir`: Temporary directory for test data
- Sample data fixtures for all entities

### Sample Data

Test data includes realistic scenarios:

- **Customers**: 2 customers with different industries
- **Projects**: Multiple projects with varying statuses and budgets
- **Quotes**: Quotes with different amounts and statuses
- **Freight Requests**: Requests with weights, priorities, and vendors
- **Vendors**: Sample vendor data for freight requests

## 📋 Test Cases

### Projects API Tests (`test_projects.py`)

#### CRUD Operations
- ✅ GET projects for customer
- ✅ POST create new project
- ✅ PUT update existing project
- ✅ DELETE soft delete with cascade

#### Validation Tests
- ✅ Required field validation
- ✅ Data type validation
- ✅ Business rule validation
- ✅ Boundary condition testing

#### Error Handling
- ✅ Not found scenarios
- ✅ Database errors
- ✅ Invalid input handling
- ✅ Permission/validation errors

#### Edge Cases
- ✅ Maximum/minimum budget values
- ✅ Long field values
- ✅ Special date handling
- ✅ Invalid ID formats

#### Integration Tests
- ✅ Complete CRUD lifecycle
- ✅ Cascade deletion verification
- ✅ Data relationship integrity

## 🛠️ Development Guidelines

### Writing New Tests

1. **Use descriptive test names** that explain what is being tested
2. **Follow the Arrange-Act-Assert pattern**:
   ```python
   def test_example():
       # Arrange - Setup test data and mocks
       # Act - Execute the code being tested
       # Assert - Verify the expected behavior
   ```
3. **Use appropriate fixtures** to avoid code duplication
4. **Test both happy path and error scenarios**
5. **Include business logic validation** (not just technical validation)

### Test Structure

```python
class TestFeature:
    """Test class for a specific feature."""

    def test_success_case(self, fixture1, fixture2):
        """Test successful operation."""
        # Arrange
        # Act
        # Assert

    def test_error_case(self, fixture1):
        """Test error handling."""
        # Arrange
        # Act
        # Assert
```

### Assertions

- Use specific assertions rather than generic ones
- Assert on the structure and content of responses
- Include meaningful error messages in assertions
- Test both the what and the why of behavior

## 🐛 Debugging Tests

### Running Individual Tests

```bash
# Run specific test with detailed output
pytest -v -s tests/api/test_projects.py::test_create_project_success

# Run with debugging
pytest --pdb tests/api/test_projects.py::test_create_project_success

# Run with logging
pytest -v -s --log-cli-level=DEBUG tests/api/test_projects.py
```

### Test Output

- Use `-v` for verbose output
- Use `-s` to see print statements
- Use `--tb=short` for concise tracebacks
- Use `--tb=long` for detailed tracebacks

## 📈 Continuous Integration

The test suite is designed for CI/CD integration:

```yaml
# Example GitHub Actions workflow
- name: Run Tests
  run: |
    python run_tests.py coverage
    python run_tests.py lint
```

## 🔍 Troubleshooting

### Common Issues

1. **Import errors**: Ensure PYTHONPATH includes the project root
2. **Database not found**: Check temp_data_dir fixture setup
3. **Mock not working**: Verify patch paths are correct
4. **Tests flaky**: Check for race conditions or external dependencies

### Debug Commands

```bash
# Check Python path
python -c "import sys; print(sys.path)"

# Check test discovery
pytest --collect-only

# Run with debugging
pytest --pdb
```

## 📝 Adding New Tests

When adding tests for new endpoints:

1. **Create test file** in appropriate directory (`tests/api/`)
2. **Add fixtures** if needed (in `conftest.py` or local file)
3. **Follow existing patterns** for test structure
4. **Include comprehensive test cases**:
   - Happy path scenarios
   - Error conditions
   - Edge cases
   - Validation errors
   - Business logic rules

5. **Update this README** with new test information

## 🎯 Best Practices

1. **Test behavior, not implementation**
2. **Keep tests independent and isolated**
3. **Use descriptive test names**
4. **Mock external dependencies**
5. **Test error conditions thoroughly**
6. **Maintain test data consistency**
7. **Run tests frequently during development**
8. **Keep test execution time reasonable**

## 📚 Resources

- [pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing Documentation](https://fastapi.tiangolo.com/tutorial/testing/)
- [Test-Driven Development with Python](https://testdriven.io/)
- [Effective Python Testing with Pytest](https://realpython.com/pytest-python-testing/)