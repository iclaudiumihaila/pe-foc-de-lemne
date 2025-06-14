"""
Pytest configuration and fixtures for backend tests.

This module provides common test fixtures and configuration for all test modules
in the backend test suite.
"""

import pytest
import os
import sys
from unittest.mock import patch

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app import create_app
from app.config import TestingConfig


@pytest.fixture
def app():
    """Create Flask application for testing."""
    app = create_app(TestingConfig)
    
    # Push application context
    with app.app_context():
        yield app


@pytest.fixture
def client(app):
    """Create Flask test client."""
    return app.test_client()


@pytest.fixture
def runner(app):
    """Create Flask CLI runner."""
    return app.test_cli_runner()


@pytest.fixture
def mock_database():
    """Mock database connection for tests."""
    with patch('app.database.get_database') as mock_db:
        # Mock database collections
        mock_db.return_value = {
            'categories': MockCollection(),
            'products': MockCollection(),
            'users': MockCollection(),
            'orders': MockCollection()
        }
        yield mock_db


class MockCollection:
    """Mock MongoDB collection for testing."""
    
    def __init__(self):
        self.data = []
    
    def find(self, query=None, **kwargs):
        """Mock find operation."""
        return self.data
    
    def find_one(self, query=None, **kwargs):
        """Mock find_one operation."""
        return self.data[0] if self.data else None
    
    def insert_one(self, document):
        """Mock insert_one operation."""
        self.data.append(document)
        return MockInsertResult()
    
    def update_one(self, query, update, **kwargs):
        """Mock update_one operation."""
        return MockUpdateResult()
    
    def delete_one(self, query):
        """Mock delete_one operation."""
        return MockDeleteResult()
    
    def aggregate(self, pipeline):
        """Mock aggregate operation."""
        return [{'products': self.data, 'total_count': [{'count': len(self.data)}]}]


class MockInsertResult:
    """Mock MongoDB insert result."""
    
    def __init__(self):
        self.inserted_id = "507f1f77bcf86cd799439011"


class MockUpdateResult:
    """Mock MongoDB update result."""
    
    def __init__(self):
        self.modified_count = 1


class MockDeleteResult:
    """Mock MongoDB delete result."""
    
    def __init__(self):
        self.deleted_count = 1