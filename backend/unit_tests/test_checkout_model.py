"""
Unit tests for Checkout model
"""

import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta
from models.checkout import Checkout


class TestCheckoutModel:
    """Test suite for Checkout model"""

    def test_checkout_item_success(self, mock_db_cursor, sample_user, sample_item):
        """Test successful item checkout"""
        expected_return = datetime.now() + timedelta(days=7)

        # Mock User.get_by_id
        with patch('models.user.User.get_by_id', return_value=sample_user):
            # Mock Item.update_quantities
            with patch('models.item.Item.update_quantities', return_value=sample_item):
                mock_db_cursor.fetchone.return_value = {
                    'checkout_id': 1,
                    'item_id': 1,
                    'user_id': 1,
                    'quantity': 2,
                    'checkout_date': datetime.now(),
                    'expected_return_datetime': expected_return,
                    'checkout_condition': 'good',
                    'notes': 'Test checkout',
                    'created_at': datetime.now()
                }

                result = Checkout.checkout_item(
                    item_id=1,
                    user_id=1,
                    quantity=2,
                    expected_return_datetime=expected_return,
                    checkout_condition='good',
                    notes='Test checkout'
                )

                assert result['checkout_id'] == 1
                assert result['quantity'] == 2
                # Verify two INSERT queries: checkout and history
                assert mock_db_cursor.execute.call_count == 2

    def test_checkout_item_default_return_date(self, mock_db_cursor, sample_user, sample_item):
        """Test checkout with default return date (7 days)"""
        with patch('models.user.User.get_by_id', return_value=sample_user):
            with patch('models.item.Item.update_quantities', return_value=sample_item):
                mock_db_cursor.fetchone.return_value = {
                    'checkout_id': 1,
                    'item_id': 1,
                    'user_id': 1,
                    'quantity': 1,
                    'checkout_date': datetime.now(),
                    'expected_return_datetime': datetime.now() + timedelta(days=7),
                    'checkout_condition': 'good',
                    'notes': None,
                    'created_at': datetime.now()
                }

                result = Checkout.checkout_item(item_id=1, user_id=1, quantity=1)

                assert result is not None
                # Check that expected_return_datetime is set
                assert result['expected_return_datetime'] is not None

    def test_checkout_item_user_not_found(self, mock_db_cursor):
        """Test checkout fails when user not found"""
        with patch('models.user.User.get_by_id', return_value=None):
            with pytest.raises(ValueError, match="User .* not found"):
                Checkout.checkout_item(item_id=1, user_id=999, quantity=1)

    def test_checkout_item_insufficient_quantity(self, mock_db_cursor, sample_user):
        """Test checkout fails with insufficient quantity"""
        with patch('models.user.User.get_by_id', return_value=sample_user):
            with patch('models.item.Item.update_quantities', side_effect=ValueError("Insufficient quantity")):
                with pytest.raises(ValueError, match="Insufficient quantity"):
                    Checkout.checkout_item(item_id=1, user_id=1, quantity=100)

    def test_checkin_item_success(self, mock_db_cursor, sample_checkout):
        """Test successful item check-in"""
        # Mock the checkout record with future return date (not overdue)
        checkout_record = sample_checkout.copy()
        checkout_record['expected_return_datetime'] = datetime.now() + timedelta(days=1)
        checkout_record['checkout_date'] = datetime.now() - timedelta(days=6)

        mock_db_cursor.fetchone.side_effect = [
            checkout_record,  # SELECT from checkout
            {  # UPDATE checkout_history
                'history_id': 1,
                'item_id': 1,
                'user_id': 1,
                'quantity': 2,
                'checkout_date': checkout_record['checkout_date'],
                'return_date': datetime.now(),
                'expected_return_datetime': checkout_record['expected_return_datetime'],
                'is_returned': True,
                'late_return': False,
                'checkout_condition': 'good',
                'return_condition': 'good',
                'checkout_notes': 'Test checkout',
                'return_notes': 'Returned on time'
            }
        ]

        with patch('models.item.Item.update_quantities'):
            result = Checkout.checkin_item(1, return_condition='good', return_notes='Returned on time')

            assert result['is_returned'] is True
            assert result['late_return'] is False
            # Verify Item.update_quantities called for check-in
            # Verify DELETE from checkout and UPDATE history
            assert mock_db_cursor.execute.call_count == 3

    def test_checkin_item_overdue(self, mock_db_cursor, sample_checkout):
        """Test check-in of overdue item"""
        # Mock overdue checkout
        checkout_record = sample_checkout.copy()
        checkout_record['expected_return_datetime'] = datetime.now() - timedelta(days=2)
        checkout_record['checkout_date'] = datetime.now() - timedelta(days=9)

        mock_db_cursor.fetchone.side_effect = [
            checkout_record,
            {
                'history_id': 1,
                'item_id': 1,
                'user_id': 1,
                'quantity': 2,
                'checkout_date': checkout_record['checkout_date'],
                'return_date': datetime.now(),
                'expected_return_datetime': checkout_record['expected_return_datetime'],
                'is_returned': True,
                'late_return': True,
                'checkout_condition': 'good',
                'return_condition': 'good',
                'checkout_notes': 'Test checkout',
                'return_notes': 'Returned late'
            }
        ]

        with patch('models.item.Item.update_quantities'):
            result = Checkout.checkin_item(1, return_condition='good', return_notes='Returned late')

            assert result['is_returned'] is True
            assert result['late_return'] is True

    def test_checkin_item_not_found(self, mock_db_cursor):
        """Test check-in fails when checkout not found"""
        mock_db_cursor.fetchone.return_value = None

        with pytest.raises(ValueError, match="Checkout .* not found"):
            Checkout.checkin_item(999)

    def test_get_active_checkouts_all(self):
        """Test getting all active checkouts"""
        checkouts = [
            {'checkout_id': 1, 'item_id': 1, 'user_id': 1},
            {'checkout_id': 2, 'item_id': 2, 'user_id': 2}
        ]

        with patch('models.checkout.execute_query', return_value=checkouts) as mock_query:
            result = Checkout.get_active_checkouts()

            assert len(result) == 2
            call_args = mock_query.call_args
            assert 'FROM v_active_checkouts' in call_args[0][0]
            assert 'ORDER BY checkout_date DESC' in call_args[0][0]

    def test_get_active_checkouts_by_user(self):
        """Test getting active checkouts filtered by user"""
        checkouts = [{'checkout_id': 1, 'item_id': 1, 'user_id': 1}]

        with patch('models.checkout.execute_query', return_value=checkouts) as mock_query:
            result = Checkout.get_active_checkouts(user_id=1)

            assert len(result) == 1
            call_args = mock_query.call_args
            assert 'AND user_id = %s' in call_args[0][0]
            assert 1 in call_args[0][1]

    def test_get_active_checkouts_by_item(self):
        """Test getting active checkouts filtered by item"""
        checkouts = [{'checkout_id': 1, 'item_id': 1, 'user_id': 1}]

        with patch('models.checkout.execute_query', return_value=checkouts) as mock_query:
            result = Checkout.get_active_checkouts(item_id=1)

            assert len(result) == 1
            call_args = mock_query.call_args
            assert 'AND item_id = %s' in call_args[0][0]
            assert 1 in call_args[0][1]

    def test_get_active_checkouts_by_user_and_item(self):
        """Test getting active checkouts filtered by both user and item"""
        checkouts = [{'checkout_id': 1, 'item_id': 1, 'user_id': 1}]

        with patch('models.checkout.execute_query', return_value=checkouts) as mock_query:
            result = Checkout.get_active_checkouts(user_id=1, item_id=1)

            assert len(result) == 1
            call_args = mock_query.call_args
            assert 'AND user_id = %s' in call_args[0][0]
            assert 'AND item_id = %s' in call_args[0][0]
            assert call_args[0][1] == (1, 1)

    def test_get_overdue_checkouts(self):
        """Test getting overdue checkouts"""
        overdue_checkouts = [
            {'checkout_id': 1, 'is_overdue': True, 'days_overdue': 5},
            {'checkout_id': 2, 'is_overdue': True, 'days_overdue': 2}
        ]

        with patch('models.checkout.execute_query', return_value=overdue_checkouts) as mock_query:
            result = Checkout.get_overdue_checkouts()

            assert len(result) == 2
            call_args = mock_query.call_args
            assert 'WHERE is_overdue = TRUE' in call_args[0][0]
            assert 'ORDER BY days_overdue DESC' in call_args[0][0]

    def test_get_user_checkout_history(self, sample_user):
        """Test getting checkout history for a user"""
        history = [
            {'history_id': 1, 'ldap': 'jdoe', 'is_returned': True},
            {'history_id': 2, 'ldap': 'jdoe', 'is_returned': True}
        ]

        with patch('models.checkout.execute_query', return_value=history) as mock_query:
            with patch('models.user.User.get_by_id', return_value=sample_user):
                result = Checkout.get_user_checkout_history(1)

                assert len(result) == 2
                call_args = mock_query.call_args
                assert 'FROM v_checkout_history' in call_args[0][0]
                assert 'WHERE ldap = %s' in call_args[0][0]
                assert 'ORDER BY checkout_date DESC' in call_args[0][0]
                assert 'LIMIT %s' in call_args[0][0]

    def test_get_user_checkout_history_user_not_found(self):
        """Test getting history for non-existent user"""
        with patch('models.user.User.get_by_id', return_value=None):
            result = Checkout.get_user_checkout_history(999)

            assert result == []

    def test_get_user_checkout_history_custom_limit(self, sample_user):
        """Test getting checkout history with custom limit"""
        with patch('models.checkout.execute_query', return_value=[]) as mock_query:
            with patch('models.user.User.get_by_id', return_value=sample_user):
                result = Checkout.get_user_checkout_history(1, limit=10)

                call_args = mock_query.call_args
                assert call_args[0][1] == ('jdoe', 10)

    def test_get_item_checkout_history(self):
        """Test getting checkout history for an item"""
        history = [
            {'history_id': 1, 'item_id': 1, 'is_returned': True},
            {'history_id': 2, 'item_id': 1, 'is_returned': True}
        ]

        with patch('models.checkout.execute_query', return_value=history) as mock_query:
            result = Checkout.get_item_checkout_history(1)

            assert len(result) == 2
            call_args = mock_query.call_args
            assert 'FROM v_checkout_history' in call_args[0][0]
            assert 'WHERE item_id = %s' in call_args[0][0]
            assert 'ORDER BY checkout_date DESC' in call_args[0][0]
            assert 'LIMIT %s' in call_args[0][0]

    def test_get_item_checkout_history_custom_limit(self):
        """Test getting item history with custom limit"""
        with patch('models.checkout.execute_query', return_value=[]) as mock_query:
            result = Checkout.get_item_checkout_history(1, limit=25)

            call_args = mock_query.call_args
            assert call_args[0][1] == (1, 25)

    def test_get_checkout_by_id(self):
        """Test getting a specific checkout by ID"""
        checkout = {'checkout_id': 1, 'item_id': 1, 'user_id': 1}

        with patch('models.checkout.execute_query', return_value=checkout) as mock_query:
            result = Checkout.get_checkout_by_id(1)

            assert result == checkout
            call_args = mock_query.call_args
            assert 'FROM v_active_checkouts' in call_args[0][0]
            assert 'WHERE checkout_id = %s' in call_args[0][0]
            assert call_args[0][1] == (1,)

    def test_get_checkout_by_id_not_found(self):
        """Test getting non-existent checkout by ID"""
        with patch('models.checkout.execute_query', return_value=None):
            result = Checkout.get_checkout_by_id(999)

            assert result is None