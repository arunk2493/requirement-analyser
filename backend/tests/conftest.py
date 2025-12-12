"""Pytest configuration and fixtures"""
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import pytest
from unittest.mock import MagicMock


@pytest.fixture(scope="session")
def test_config():
    """Provide test configuration"""
    return {
        "test_user_id": 1,
        "test_email": "test@example.com",
        "test_username": "testuser"
    }


@pytest.fixture
def mock_session():
    """Provide mock database session for all tests"""
    from sqlalchemy.orm import Session
    session = MagicMock(spec=Session)
    return session


@pytest.fixture
def mock_request():
    """Provide mock FastAPI request"""
    from fastapi import Request
    request = MagicMock(spec=Request)
    request.headers = {}
    return request


@pytest.fixture(autouse=True)
def clear_imports():
    """Clear module cache between tests to avoid import issues"""
    yield
    # Cleanup after each test if needed


def pytest_configure(config):
    """Configure pytest with custom settings"""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow"
    )


def pytest_collection_modifyitems(config, items):
    """Automatically add markers to tests"""
    for item in items:
        # Mark all tests as unit by default
        if "integration" not in item.keywords:
            item.add_marker(pytest.mark.unit)
