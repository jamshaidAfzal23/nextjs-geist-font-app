# Smart CRM SaaS Backend Tests

This directory contains comprehensive tests for the Smart CRM SaaS backend application.

## Test Structure

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test interactions between components
- **API Tests**: Test API endpoints

## Test Files

- `test_main.py`: Basic application tests
- `test_auth_endpoints.py`: Authentication endpoint tests
- `test_user_endpoints.py`: User management endpoint tests
- `test_client_endpoints.py`: Client management endpoint tests
- `test_client_history_endpoints.py`: Client history endpoint tests
- `test_client_note_endpoints.py`: Client notes endpoint tests
- `test_project_endpoints.py`: Project management endpoint tests
- `test_financial_endpoints.py`: Invoice and payment endpoint tests
- `test_report_endpoints.py`: Report generation endpoint tests
- `test_ai_endpoints.py`: AI analysis endpoint tests
- `test_integration.py`: End-to-end workflow tests

## Setup

### Install Test Dependencies

```bash
pip install -r tests/requirements-test.txt
python -m spacy download en_core_web_sm
```

## Running Tests

### Run All Tests

```bash
pytest
```

### Run Tests with Coverage Report

```bash
pytest --cov=app tests/
```

### Run Specific Test File

```bash
pytest tests/test_auth_endpoints.py
```

### Run Specific Test Function

```bash
pytest tests/test_auth_endpoints.py::test_login
```

### Run Tests with Verbose Output

```bash
pytest -v
```

## Test Database

Tests use an in-memory SQLite database that is created and populated with test data for each test session. The database is automatically cleaned up after tests complete.

## Authentication in Tests

The test suite includes fixtures for creating authentication tokens for both admin and regular users. These tokens can be used in test requests that require authentication.

Example:

```python
@pytest.mark.asyncio
async def test_protected_endpoint(admin_headers):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/protected-route", headers=admin_headers)
    assert response.status_code == 200
```

## Test Data

Test data is automatically seeded in the database for each test session through the `seed_database` fixture in `conftest.py`. This includes:

- Users (admin and regular)
- Clients
- Projects
- Invoices
- Payments
- Client notes
- Client history

## Continuous Integration

These tests are designed to be run in a CI/CD pipeline. They are fast, isolated, and do not require external services.