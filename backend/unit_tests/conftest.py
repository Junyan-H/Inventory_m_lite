"""
Pytest configuration and fixtures for unit tests
"""

import pytest
import os
import sys
from unittest.mock import Mock, MagicMock, patch



# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from database import Database


@pytest.fixture
def app():
    """Create and configure a test Flask application"""
    # Set test configuration
    os.environ['FLASK_ENV'] = 'test'
    os.environ['DATABASE_URL'] = 'postgresql://test:test@localhost/test_inventory_db'

    app = create_app('test')
    app.config['TESTING'] = True
    app.config['DEBUG'] = True

    yield app


@pytest.fixture
def client(app):
    """Create a test client for the Flask application"""
    return app.test_client()


@pytest.fixture
def mock_db_cursor():
    """Mock database cursor for testing without actual database"""
    mock_cursor = MagicMock()
    mock_cursor.fetchone.return_value = None
    mock_cursor.fetchall.return_value = []
    mock_cursor.rowcount = 0

    # Need to patch in all modules that use it
    with patch('models.user.get_db_cursor') as mock_user:
        with patch('models.item.get_db_cursor') as mock_item:
            with patch('models.checkout.get_db_cursor') as mock_checkout:
                mock_user.return_value.__enter__.return_value = mock_cursor
                mock_item.return_value.__enter__.return_value = mock_cursor
                mock_checkout.return_value.__enter__.return_value = mock_cursor
                yield mock_cursor


@pytest.fixture
def mock_execute_query():
    """Mock execute_query function"""
    # Need to patch in all modules that use it
    with patch('models.user.execute_query') as mock_user:
        with patch('models.item.execute_query') as mock_item:
            with patch('models.checkout.execute_query') as mock_checkout:
                mock_user.return_value = []
                mock_item.return_value = []
                mock_checkout.return_value = []
                yield mock_user  # Return one of them for setting return values in tests


@pytest.fixture
def sample_user():
    """Sample user data for testing"""
    return {
        'user_id': 1,
        'ldap': 'jdoe',
        'full_name': 'John Doe',
        'email': 'jdoe@company.com',
        'role': 'employee',
        'department': 'Operations',
        'active': True,
        'created_at': '2024-01-01 00:00:00',
        'updated_at': '2024-01-01 00:00:00'
    }


@pytest.fixture
def sample_item():
    """Sample item data for testing"""
    from datetime import date, datetime
    return {
        'item_id': 1,
        'item_name': 'Test Drill',
        'category': 'tools',
        'location': 'san_jose',
        'quantity_total': 10,
        'quantity_available': 8,
        'quantity_checked_out': 2,
        'purchase_price': 150.00,
        'restock_date': date(2024, 1, 1),
        'condition': 'good',
        'status': 'available',
        'last_audit_date': date(2024, 1, 1),
        'notes': 'Test item',
        'image_url': 'http://example.com/drill.jpg',
        'created_at': datetime(2024, 1, 1, 0, 0, 0),
        'updated_at': datetime(2024, 1, 1, 0, 0, 0)
    }


@pytest.fixture
def sample_checkout():
    """Sample checkout data for testing"""
    return {
        'checkout_id': 1,
        'item_id': 1,
        'user_id': 1,
        'quantity': 2,
        'checkout_date': '2024-01-01 00:00:00',
        'expected_return_datetime': '2024-01-08 00:00:00',
        'checkout_condition': 'good',
        'notes': 'Test checkout',
        'created_at': '2024-01-01 00:00:00'
    }


@pytest.fixture
def sample_checkout_history():
    """Sample checkout history data for testing"""
    return {
        'history_id': 1,
        'item_id': 1,
        'user_id': 1,
        'quantity': 2,
        'checkout_date': '2024-01-01 00:00:00',
        'return_date': '2024-01-07 00:00:00',
        'expected_return_datetime': '2024-01-08 00:00:00',
        'checkout_condition': 'good',
        'return_condition': 'good',
        'is_returned': True,
        'late_return': False,
        'checkout_notes': 'Test checkout',
        'return_notes': 'Returned on time',
        'created_at': '2024-01-01 00:00:00',
        'updated_at': '2024-01-07 00:00:00'
    }


@pytest.fixture(autouse=True)
def mock_database_init():
    """Mock database initialization for all tests"""
    with patch.object(Database, 'initialize'):
        with patch.object(Database, 'get_connection'):
            yield