# Backend Unit Tests

Comprehensive unit test suite for the backend API with good test coverage.

## Test Structure

```
backend/tests/
├── __init__.py
├── conftest.py                 # Pytest configuration and fixtures
├── test_json_parser.py         # JSON parsing utility tests
├── test_error_handler.py       # Error handling tests
├── test_validators.py          # Request/response validation tests
├── test_content_generator.py   # Content generation service tests
├── test_auth.py                # Authentication tests
└── test_logger.py              # Logger utility tests
```

## Test Coverage

### 1. JSON Parser (`test_json_parser.py`)
- **Valid JSON parsing**: Objects, arrays, nested structures
- **Code fence handling**: ```json, ```python blocks
- **Malformed JSON recovery**: Single quotes, trailing commas, extraction from text
- **Error handling**: Invalid input, empty strings, non-string types
- **Model parsing**: Epic, story, QA models
- **List conversion**: Ensuring proper list formatting

**Coverage**: 13 test cases

### 2. Error Handler (`test_error_handler.py`)
- **APIError**: Base error class, status codes, detail handling
- **ValidationError**: Validation failures, proper HTTP 400 status
- **ResourceNotFoundError**: 404 errors with resource details
- **ProcessingError**: Processing/generation failures
- **Error inheritance**: Proper exception hierarchy
- **Error properties**: Message, status code, detail fields

**Coverage**: 16 test cases

### 3. Validators (`test_validators.py`)
- **PaginationParams**: Limit validation, default values, boundary checking
- **SortParams**: Valid sort orders, field names, default values
- **BaseResponse**: Success/error responses, timestamps, complex data
- **ErrorResponse**: Error codes, detail messages, timestamps
- **Request validation**: Required fields, None values, empty strings
- **Data validation**: Various input types and scenarios

**Coverage**: 24 test cases

### 4. Content Generator (`test_content_generator.py`)
- **Service initialization**: Proper setup with mocked dependencies
- **Epic generation**: Successful generation, error handling
- **Story generation**: Content creation and formatting
- **QA generation**: Question-answer pair generation
- **Test plan generation**: Test case and step generation
- **Error handling**: API failures, invalid responses
- **Upload validation**: Missing uploads, resource not found

**Coverage**: 13 test cases

### 5. Authentication (`test_auth.py`)
- **Password hashing**: Hash creation, verification, salt handling
- **Token generation**: JWT creation, custom expiration, payload structure
- **Token verification**: Valid/invalid/expired tokens
- **Auth configuration**: Secret keys, algorithm, expiration settings
- **Multiple tokens**: Different users, same user scenarios
- **Payload validation**: Subject, expiration, issued-at timestamps

**Coverage**: 19 test cases

### 6. Logger (`test_logger.py`)
- **Logger setup**: Creation, naming, handlers, levels
- **Logger retrieval**: Getting logger instances, consistency
- **Log functionality**: Debug, info, warning, error, exception levels
- **Context logging**: Extra context information, multiple messages
- **Logger configuration**: Format, propagation, consistency

**Coverage**: 17 test cases

## Total Test Count: 102 tests

## Running Tests

### Quick Start
```bash
cd backend
bash run_tests.sh
```

### Install Test Dependencies
```bash
pip install pytest pytest-cov pytest-mock
```

### Run All Tests
```bash
pytest tests/
```

### Run with Verbose Output
```bash
pytest tests/ -v
```

### Run Specific Test File
```bash
pytest tests/test_json_parser.py -v
```

### Run Specific Test Class
```bash
pytest tests/test_json_parser.py::TestExtractValidJson -v
```

### Run Specific Test
```bash
pytest tests/test_json_parser.py::TestExtractValidJson::test_valid_json_object -v
```

### Run Tests with Coverage Report
```bash
pytest tests/ \
  --cov=backend \
  --cov-report=html \
  --cov-report=term-missing
```

### Run Only Unit Tests
```bash
pytest tests/ -m unit -v
```

### Run Only Integration Tests
```bash
pytest tests/ -m integration -v
```

### Run Tests (excluding slow tests)
```bash
pytest tests/ -m "not slow" -v
```

## Coverage Report

After running tests with coverage, view the detailed HTML report:

```bash
# Generate coverage report
pytest tests/ \
  --cov=backend \
  --cov-report=html

# Open in browser (macOS)
open backend/htmlcov/index.html

# Or on Linux
firefox backend/htmlcov/index.html
```

## Test Features

### Fixtures
- `test_config`: Provides common test configuration
- `mock_session`: Mocked SQLAlchemy session
- `mock_request`: Mocked FastAPI request
- `mock_db`: Mocked database connection
- `content_service`: Mocked content generator service

### Markers
- `@pytest.mark.unit`: Unit test (default)
- `@pytest.mark.integration`: Integration test
- `@pytest.mark.slow`: Slow running test

### Mocking
- Uses `unittest.mock` for dependencies
- Patches external services (Gemini API, database, etc.)
- Isolates components for unit testing

## Test Quality Standards

✅ **Good test structure**: Descriptive names, clear assertions
✅ **Edge cases**: Boundary conditions, error scenarios, invalid inputs
✅ **Error handling**: Tests for exceptions and error paths
✅ **Fixtures**: Reusable test components
✅ **Markers**: Categorized tests for selective running
✅ **Documentation**: Docstrings for all test methods
✅ **Isolation**: Tests are independent and can run in any order
✅ **Coverage**: Comprehensive coverage of core functionality

## Key Testing Patterns

### 1. Parametrized Tests (when needed)
```python
@pytest.mark.parametrize("input,expected", [
    ("valid", True),
    ("invalid", False)
])
def test_validation(input, expected):
    assert validate(input) == expected
```

### 2. Fixture Usage
```python
def test_with_fixture(mock_db):
    # mock_db is automatically provided
    assert mock_db is not None
```

### 3. Mock Patching
```python
with patch('module.function') as mock_func:
    mock_func.return_value = "mocked"
    result = function_under_test()
```

### 4. Exception Testing
```python
with pytest.raises(ValueError):
    function_that_raises()
```

## Continuous Integration

These tests are designed to run in CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
- name: Run Backend Tests
  run: |
    cd backend
    pip install pytest pytest-cov
    pytest tests/ --cov=backend
```

## Maintenance

### Adding New Tests
1. Create test file in `tests/` directory
2. Name file as `test_*.py`
3. Follow naming convention: `Test*` for classes, `test_*` for functions
4. Add docstrings explaining what is tested
5. Use fixtures for common setup

### Updating Tests
1. Keep tests isolated and independent
2. Update fixtures when dependencies change
3. Maintain test documentation
4. Keep coverage above 80%

## Troubleshooting

### Import Errors
```bash
# Add backend to Python path
export PYTHONPATH="${PYTHONPATH}:$(pwd)/backend"
pytest tests/
```

### Module Not Found
```bash
# Install in development mode
pip install -e .
```

### Tests Fail with Database Error
- Tests use mocked database
- Ensure sqlalchemy is installed
- Check mock configuration in conftest.py

## Best Practices

1. **Test One Thing**: Each test should verify a single behavior
2. **Clear Names**: Test names should describe what is tested
3. **Arrange-Act-Assert**: Setup, execute, verify pattern
4. **No External Dependencies**: Use mocks for external services
5. **Fast Execution**: Unit tests should complete quickly
6. **Deterministic**: Tests should produce same result every run
7. **Independent**: Tests shouldn't depend on other tests
8. **Documented**: Include docstrings explaining the test

## Example Test Structure

```python
class TestFeature:
    """Tests for specific feature"""
    
    def test_successful_case(self):
        """Test successful scenario"""
        # Arrange: Setup test data
        input_data = {"key": "value"}
        
        # Act: Execute the code
        result = function(input_data)
        
        # Assert: Verify the result
        assert result is not None
    
    def test_error_case(self):
        """Test error scenario"""
        with pytest.raises(ValueError):
            function(invalid_data)
```

## Coverage Goals

| Module | Target | Status |
|--------|--------|--------|
| json_parser.py | 90%+ | ✅ |
| error_handler.py | 90%+ | ✅ |
| validators.py | 85%+ | ✅ |
| content_generator.py | 80%+ | ✅ |
| auth.py | 85%+ | ✅ |
| logger.py | 80%+ | ✅ |

## Support

For issues with tests:
1. Check test output for error messages
2. Review pytest documentation: https://pytest.org
3. Check mock documentation: https://docs.python.org/3/library/unittest.mock.html
4. Review test file comments for implementation details
