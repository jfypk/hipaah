# HIPAah Python SDK Tests

This directory contains unit tests for the HIPAah Python SDK.

## Running Tests

### Install test dependencies

```bash
pip install -e ".[test]"
```

### Run all tests

```bash
pytest
```

### Run with coverage report

```bash
pytest --cov=hipaah --cov-report=html
```

This will generate an HTML coverage report in the `htmlcov` directory.

## Test Structure

- `conftest.py` - Pytest fixtures shared across tests
- `test_client.py` - Tests for the HipaahClient class
- `test_utils.py` - Tests for utility functions

## Adding New Tests

When adding new tests, follow these naming conventions:
- Test files should be named `test_*.py`
- Test functions should be named `test_*`
- Test classes should be named `Test*`