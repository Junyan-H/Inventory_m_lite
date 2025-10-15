"""
Unit tests for Flask app and routes
"""

import pytest
import json
from unittest.mock import patch
from datetime import datetime, timedelta


class TestAppBasics:
    """Test basic app functionality"""

    def test_app_creation(self, app):
        """Test that app is created successfully"""
        assert app is not None
        assert app.config['TESTING'] is True

    def test_root_endpoint(self, client):
        """Test root endpoint returns API info"""
        response = client.get('/')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['name'] == 'Inventory Management API'
        assert data['version'] == '1.0.0'
        assert 'endpoints' in data

    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/health')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['database'] == 'connected'


class TestInventoryRoutes:
    """Test inventory routes"""

    def test_get_inventory_success(self, client, sample_item):
        """Test getting inventory for a location"""
        with patch('models.item.Item.get_by_location', return_value=[sample_item]):
            response = client.get('/api/inventory?location=san_jose')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['location'] == 'san_jose'
            assert data['total_items'] == 1
            assert len(data['items']) == 1
            assert data['items'][0]['item_name'] == 'Test Drill'

    def test_get_inventory_with_user(self, client, sample_item, sample_user):
        """Test getting inventory with user LDAP"""
        with patch('models.item.Item.get_by_location', return_value=[sample_item]):
            with patch('models.user.User.get_by_ldap', return_value=sample_user):
                response = client.get('/api/inventory?location=san_jose&ldap=jdoe')

                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['success'] is True
                assert data['user'] is not None
                assert data['user']['ldap'] == 'jdoe'
                assert data['user']['full_name'] == 'John Doe'

    def test_get_inventory_missing_location(self, client):
        """Test getting inventory without location parameter"""
        response = client.get('/api/inventory')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'location' in data['error']

    def test_get_inventory_invalid_user(self, client):
        """Test getting inventory with invalid LDAP"""
        with patch('models.user.User.get_by_ldap', return_value=None):
            response = client.get('/api/inventory?location=san_jose&ldap=invalid')

            assert response.status_code == 401
            data = json.loads(response.data)
            assert 'error' in data
            assert 'LDAP' in data['error']

    def test_get_inventory_availability_status(self, client, sample_item):
        """Test availability status calculation"""
        # Test Out of Stock
        out_of_stock_item = sample_item.copy()
        out_of_stock_item['quantity_available'] = 0

        with patch('models.item.Item.get_by_location', return_value=[out_of_stock_item]):
            response = client.get('/api/inventory?location=san_jose')
            data = json.loads(response.data)
            assert data['items'][0]['availability_status'] == 'Out of Stock'

        # Test Low Stock
        low_stock_item = sample_item.copy()
        low_stock_item['quantity_available'] = 1
        low_stock_item['quantity_total'] = 10

        with patch('models.item.Item.get_by_location', return_value=[low_stock_item]):
            response = client.get('/api/inventory?location=san_jose')
            data = json.loads(response.data)
            assert data['items'][0]['availability_status'] == 'Low Stock'

        # Test Available
        available_item = sample_item.copy()
        available_item['quantity_available'] = 8
        available_item['quantity_total'] = 10

        with patch('models.item.Item.get_by_location', return_value=[available_item]):
            response = client.get('/api/inventory?location=san_jose')
            data = json.loads(response.data)
            assert data['items'][0]['availability_status'] == 'Available'

    def test_search_inventory_success(self, client, sample_item):
        """Test searching inventory"""
        with patch('models.item.Item.search', return_value=[sample_item]):
            response = client.get('/api/inventory/search?q=drill')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['query'] == 'drill'
            assert data['total_results'] == 1
            assert len(data['items']) == 1

    def test_search_inventory_with_location(self, client, sample_item):
        """Test searching inventory with location filter"""
        with patch('models.item.Item.search', return_value=[sample_item]):
            response = client.get('/api/inventory/search?q=drill&location=san_jose')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['location'] == 'san_jose'

    def test_search_inventory_missing_query(self, client):
        """Test searching without query parameter"""
        response = client.get('/api/inventory/search')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_get_item_details_success(self, client, sample_item):
        """Test getting item details by ID"""
        with patch('models.item.Item.get_by_id', return_value=sample_item):
            response = client.get('/api/inventory/1')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['item']['item_id'] == 1
            assert data['item']['item_name'] == 'Test Drill'

    def test_get_item_details_not_found(self, client):
        """Test getting non-existent item"""
        with patch('models.item.Item.get_by_id', return_value=None):
            response = client.get('/api/inventory/999')

            assert response.status_code == 404
            data = json.loads(response.data)
            assert 'error' in data
            assert 'not found' in data['error']


class TestCheckoutRoutes:
    """Test checkout routes"""

    def test_checkout_item_success_with_ldap(self, client, sample_user, sample_checkout):
        """Test successful checkout with user LDAP"""
        checkout_record = sample_checkout.copy()
        checkout_record['checkout_date'] = datetime.now()
        checkout_record['expected_return_datetime'] = datetime.now() + timedelta(days=7)

        with patch('models.user.User.get_by_ldap', return_value=sample_user):
            with patch('models.checkout.Checkout.checkout_item', return_value=checkout_record):
                response = client.post('/api/checkout', json={
                    'item_id': 1,
                    'user_ldap': 'jdoe',
                    'quantity': 2,
                    'notes': 'Test checkout'
                })

                assert response.status_code == 201
                data = json.loads(response.data)
                assert data['success'] is True
                assert data['message'] == 'Item checked out successfully'
                assert data['checkout']['checkout_id'] == 1

    def test_checkout_item_success_with_user_id(self, client, sample_checkout):
        """Test successful checkout with user ID"""
        checkout_record = sample_checkout.copy()
        checkout_record['checkout_date'] = datetime.now()
        checkout_record['expected_return_datetime'] = datetime.now() + timedelta(days=7)

        with patch('models.checkout.Checkout.checkout_item', return_value=checkout_record):
            response = client.post('/api/checkout', json={
                'item_id': 1,
                'user_id': 1,
                'quantity': 2
            })

            assert response.status_code == 201
            data = json.loads(response.data)
            assert data['success'] is True

    def test_checkout_item_missing_item_id(self, client):
        """Test checkout without item_id"""
        response = client.post('/api/checkout', json={
            'user_ldap': 'jdoe',
            'quantity': 1
        })

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'item_id' in data['error']

    def test_checkout_item_missing_user(self, client):
        """Test checkout without user identifier"""
        response = client.post('/api/checkout', json={
            'item_id': 1,
            'quantity': 1
        })

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'user' in data['error'].lower()

    def test_checkout_item_user_not_found(self, client):
        """Test checkout with non-existent user"""
        with patch('models.user.User.get_by_ldap', return_value=None):
            response = client.post('/api/checkout', json={
                'item_id': 1,
                'user_ldap': 'nonexistent',
                'quantity': 1
            })

            assert response.status_code == 404
            data = json.loads(response.data)
            assert 'error' in data

    def test_checkout_item_insufficient_quantity(self, client, sample_user):
        """Test checkout with insufficient quantity"""
        with patch('models.user.User.get_by_ldap', return_value=sample_user):
            with patch('models.checkout.Checkout.checkout_item',
                      side_effect=ValueError("Insufficient quantity")):
                response = client.post('/api/checkout', json={
                    'item_id': 1,
                    'user_ldap': 'jdoe',
                    'quantity': 100
                })

                assert response.status_code == 400
                data = json.loads(response.data)
                assert 'error' in data

    def test_checkin_item_success(self, client, sample_checkout_history):
        """Test successful check-in"""
        history_record = sample_checkout_history.copy()
        history_record['checkout_date'] = datetime.now() - timedelta(days=7)
        history_record['return_date'] = datetime.now()

        with patch('models.checkout.Checkout.checkin_item', return_value=history_record):
            response = client.post('/api/checkout/checkin', json={
                'checkout_id': 1,
                'return_condition': 'good',
                'return_notes': 'Returned on time'
            })

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['message'] == 'Item checked in successfully'
            assert data['history']['is_returned'] is True

    def test_checkin_item_missing_checkout_id(self, client):
        """Test check-in without checkout_id"""
        response = client.post('/api/checkout/checkin', json={
            'return_condition': 'good'
        })

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
        assert 'checkout_id' in data['error']

    def test_checkin_item_not_found(self, client):
        """Test check-in of non-existent checkout"""
        with patch('models.checkout.Checkout.checkin_item',
                  side_effect=ValueError("Checkout 999 not found")):
            response = client.post('/api/checkout/checkin', json={
                'checkout_id': 999
            })

            assert response.status_code == 400
            data = json.loads(response.data)
            assert 'error' in data

    def test_get_active_checkouts(self, client):
        """Test getting all active checkouts"""
        checkouts = [{
            'checkout_id': 1,
            'checkout_date': datetime.now(),
            'expected_return_datetime': datetime.now() + timedelta(days=7),
            'quantity': 2,
            'ldap': 'jdoe',
            'full_name': 'John Doe',
            'email': 'jdoe@company.com',
            'item_id': 1,
            'item_name': 'Test Drill',
            'category': 'tools',
            'location': 'san_jose',
            'is_overdue': False,
            'days_overdue': 0,
            'notes': 'Test'
        }]

        with patch('models.checkout.Checkout.get_active_checkouts', return_value=checkouts):
            response = client.get('/api/checkout/active')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['total_active_checkouts'] == 1
            assert len(data['checkouts']) == 1

    def test_get_active_checkouts_filtered_by_user(self, client):
        """Test getting active checkouts filtered by user"""
        with patch('models.checkout.Checkout.get_active_checkouts', return_value=[]):
            response = client.get('/api/checkout/active?user_id=1')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True

    def test_get_overdue_checkouts(self, client):
        """Test getting overdue checkouts"""
        checkouts = [{
            'checkout_id': 1,
            'checkout_date': datetime.now() - timedelta(days=10),
            'expected_return_datetime': datetime.now() - timedelta(days=2),
            'days_overdue': 2,
            'quantity': 2,
            'ldap': 'jdoe',
            'full_name': 'John Doe',
            'email': 'jdoe@company.com',
            'item_id': 1,
            'item_name': 'Test Drill',
            'location': 'san_jose'
        }]

        with patch('models.checkout.Checkout.get_overdue_checkouts', return_value=checkouts):
            response = client.get('/api/checkout/overdue')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['total_overdue'] == 1
            assert len(data['checkouts']) == 1

    def test_get_user_checkouts(self, client, sample_user):
        """Test getting user checkout history"""
        history = [{
            'history_id': 1,
            'checkout_date': datetime.now() - timedelta(days=30),
            'return_date': datetime.now() - timedelta(days=23),
            'expected_return_datetime': datetime.now() - timedelta(days=23),
            'quantity': 2,
            'is_returned': True,
            'late_return': False,
            'item_id': 1,
            'item_name': 'Test Drill',
            'category': 'tools',
            'location': 'san_jose',
            'checkout_condition': 'good',
            'return_condition': 'good'
        }]

        with patch('models.user.User.get_by_ldap', return_value=sample_user):
            with patch('models.checkout.Checkout.get_user_checkout_history', return_value=history):
                response = client.get('/api/checkout/user/jdoe')

                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['success'] is True
                assert data['user']['ldap'] == 'jdoe'
                assert data['total_records'] == 1

    def test_get_user_checkouts_not_found(self, client):
        """Test getting history for non-existent user"""
        with patch('models.user.User.get_by_ldap', return_value=None):
            response = client.get('/api/checkout/user/nonexistent')

            assert response.status_code == 404
            data = json.loads(response.data)
            assert 'error' in data

    def test_get_user_checkouts_custom_limit(self, client, sample_user):
        """Test getting user history with custom limit"""
        with patch('models.user.User.get_by_ldap', return_value=sample_user):
            with patch('models.checkout.Checkout.get_user_checkout_history', return_value=[]):
                response = client.get('/api/checkout/user/jdoe?limit=10')

                assert response.status_code == 200
                data = json.loads(response.data)
                assert data['success'] is True

    def test_get_item_history(self, client):
        """Test getting item checkout history"""
        history = [{
            'history_id': 1,
            'checkout_date': datetime.now() - timedelta(days=30),
            'return_date': datetime.now() - timedelta(days=23),
            'expected_return_datetime': datetime.now() - timedelta(days=23),
            'quantity': 2,
            'is_returned': True,
            'late_return': False,
            'ldap': 'jdoe',
            'full_name': 'John Doe',
            'checkout_condition': 'good',
            'return_condition': 'good',
            'checkout_notes': 'Test',
            'return_notes': 'Returned'
        }]

        with patch('models.checkout.Checkout.get_item_checkout_history', return_value=history):
            response = client.get('/api/checkout/item/1/history')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert data['item_id'] == 1
            assert data['total_records'] == 1

    def test_get_item_history_custom_limit(self, client):
        """Test getting item history with custom limit"""
        with patch('models.checkout.Checkout.get_item_checkout_history', return_value=[]):
            response = client.get('/api/checkout/item/1/history?limit=25')

            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True

    def test_checkout_no_data(self, client):
        """Test checkout endpoint with no JSON data"""
        response = client.post('/api/checkout', data='null', content_type='application/json')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data

    def test_checkin_no_data(self, client):
        """Test check-in endpoint with no JSON data"""
        response = client.post('/api/checkout/checkin', data='null', content_type='application/json')

        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data