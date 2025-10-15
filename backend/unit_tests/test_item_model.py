"""
Unit tests for Item model
"""

import pytest
from unittest.mock import patch, MagicMock
from models.item import Item


class TestItemModel:
    """Test suite for Item model"""

    def test_get_by_location(self, sample_item):
        """Test getting items by location"""
        with patch('models.item.execute_query', return_value=[sample_item]) as mock_query:
            result = Item.get_by_location('san_jose')

            assert result == [sample_item]
            mock_query.assert_called_once()
            call_args = mock_query.call_args
            assert 'WHERE location = %s' in call_args[0][0]
            assert 'ORDER BY item_name' in call_args[0][0]
            assert call_args[0][1] == ('san_jose',)

    def test_get_by_location_empty(self):
        """Test getting items from location with no items"""
        with patch('models.item.execute_query', return_value=[]):
            result = Item.get_by_location('empty_location')
            assert result == []

    def test_get_by_id_success(self, sample_item):
        """Test successful item retrieval by ID"""
        with patch('models.item.execute_query', return_value=sample_item) as mock_query:
            result = Item.get_by_id(1)

            assert result == sample_item
            call_args = mock_query.call_args
            assert 'WHERE item_id = %s' in call_args[0][0]
            assert call_args[0][1] == (1,)

    def test_get_by_id_not_found(self):
        """Test item not found by ID"""
        with patch('models.item.execute_query', return_value=None):
            result = Item.get_by_id(999)
            assert result is None

    def test_get_available_items_no_location(self, sample_item):
        """Test getting all available items without location filter"""
        with patch('models.item.execute_query', return_value=[sample_item]) as mock_query:
            result = Item.get_available_items()

            assert result == [sample_item]
            call_args = mock_query.call_args
            assert 'quantity_available > 0' in call_args[0][0]
            assert "status = 'available'" in call_args[0][0]
            assert call_args[0][1] == ()

    def test_get_available_items_with_location(self, sample_item):
        """Test getting available items filtered by location"""
        with patch('models.item.execute_query', return_value=[sample_item]) as mock_query:
            result = Item.get_available_items(location='san_jose')

            assert result == [sample_item]
            call_args = mock_query.call_args
            assert 'AND location = %s' in call_args[0][0]
            assert call_args[0][1] == ('san_jose',)

    def test_search_by_name(self, sample_item):
        """Test searching items by name"""
        with patch('models.item.execute_query', return_value=[sample_item]) as mock_query:
            result = Item.search('drill')

            assert result == [sample_item]
            call_args = mock_query.call_args
            assert 'item_name ILIKE %s' in call_args[0][0]
            assert 'category ILIKE %s' in call_args[0][0]
            assert call_args[0][1] == ('%drill%', '%drill%')

    def test_search_with_location(self, sample_item):
        """Test searching items with location filter"""
        with patch('models.item.execute_query', return_value=[sample_item]) as mock_query:
            result = Item.search('drill', location='san_jose')

            assert result == [sample_item]
            call_args = mock_query.call_args
            assert 'AND location = %s' in call_args[0][0]
            assert call_args[0][1] == ('%drill%', '%drill%', 'san_jose')

    def test_search_no_results(self):
        """Test search with no matching results"""
        with patch('models.item.execute_query', return_value=[]):
            result = Item.search('nonexistent')
            assert result == []

    def test_update_quantities_checkout_success(self, mock_db_cursor, sample_item):
        """Test updating quantities for checkout"""
        # Mock the SELECT FOR UPDATE
        mock_db_cursor.fetchone.side_effect = [
            {'quantity_available': 10, 'quantity_checked_out': 0},
            {'item_id': 1, 'item_name': 'Test Drill', 'quantity_total': 10,
             'quantity_available': 8, 'quantity_checked_out': 2}
        ]

        result = Item.update_quantities(1, 2, is_checkout=True)

        assert result['quantity_available'] == 8
        assert result['quantity_checked_out'] == 2
        # Verify two execute calls: SELECT FOR UPDATE and UPDATE
        assert mock_db_cursor.execute.call_count == 2

    def test_update_quantities_checkout_insufficient(self, mock_db_cursor):
        """Test checkout with insufficient quantity"""
        mock_db_cursor.fetchone.return_value = {
            'quantity_available': 1,
            'quantity_checked_out': 9
        }

        with pytest.raises(ValueError, match="Insufficient quantity"):
            Item.update_quantities(1, 5, is_checkout=True)

    def test_update_quantities_checkin_success(self, mock_db_cursor):
        """Test updating quantities for check-in"""
        mock_db_cursor.fetchone.side_effect = [
            {'quantity_available': 8, 'quantity_checked_out': 2},
            {'item_id': 1, 'item_name': 'Test Drill', 'quantity_total': 10,
             'quantity_available': 10, 'quantity_checked_out': 0}
        ]

        result = Item.update_quantities(1, 2, is_checkout=False)

        assert result['quantity_available'] == 10
        assert result['quantity_checked_out'] == 0

    def test_update_quantities_item_not_found(self, mock_db_cursor):
        """Test updating quantities for non-existent item"""
        mock_db_cursor.fetchone.return_value = None

        with pytest.raises(ValueError, match="Item .* not found"):
            Item.update_quantities(999, 1, is_checkout=True)

    def test_create_item_minimal(self, mock_db_cursor, sample_item):
        """Test creating item with minimal required fields"""
        mock_db_cursor.fetchone.return_value = sample_item

        result = Item.create('Test Drill', 'tools', 'san_jose', 10)

        assert result == sample_item
        call_args = mock_db_cursor.execute.call_args
        assert 'INSERT INTO items' in call_args[0][0]
        assert call_args[0][1][0] == 'Test Drill'
        assert call_args[0][1][1] == 'tools'
        assert call_args[0][1][2] == 'san_jose'
        assert call_args[0][1][3] == 10  # quantity_total
        assert call_args[0][1][4] == 10  # quantity_available (same as total initially)

    def test_create_item_all_fields(self, mock_db_cursor, sample_item):
        """Test creating item with all optional fields"""
        mock_db_cursor.fetchone.return_value = sample_item

        result = Item.create(
            'Test Drill',
            'tools',
            'san_jose',
            10,
            purchase_price=150.00,
            restock_date='2024-01-01',
            condition='new',
            status='available',
            notes='Test notes',
            image_url='http://example.com/drill.jpg'
        )

        assert result == sample_item
        call_args = mock_db_cursor.execute.call_args
        params = call_args[0][1]
        assert params[5] == 150.00  # purchase_price
        assert params[6] == '2024-01-01'  # restock_date
        assert params[7] == 'new'  # condition
        assert params[8] == 'available'  # status
        assert params[9] == 'Test notes'  # notes
        assert params[10] == 'http://example.com/drill.jpg'  # image_url

    def test_create_item_default_values(self, mock_db_cursor, sample_item):
        """Test creating item uses default values for optional fields"""
        mock_db_cursor.fetchone.return_value = sample_item

        result = Item.create('Test Drill', 'tools', 'san_jose', 10)

        call_args = mock_db_cursor.execute.call_args
        params = call_args[0][1]
        assert params[7] == 'good'  # default condition
        assert params[8] == 'available'  # default status

    def test_update_item_single_field(self, mock_db_cursor, sample_item):
        """Test updating a single item field"""
        updated_item = sample_item.copy()
        updated_item['notes'] = 'Updated notes'
        mock_db_cursor.fetchone.return_value = updated_item

        result = Item.update(1, notes='Updated notes')

        assert result == updated_item
        call_args = mock_db_cursor.execute.call_args
        assert 'UPDATE items' in call_args[0][0]
        assert 'notes = %s' in call_args[0][0]
        assert 'updated_at = CURRENT_TIMESTAMP' in call_args[0][0]

    def test_update_item_multiple_fields(self, mock_db_cursor, sample_item):
        """Test updating multiple item fields"""
        updated_item = sample_item.copy()
        updated_item['condition'] = 'fair'
        updated_item['status'] = 'maintenance'
        mock_db_cursor.fetchone.return_value = updated_item

        result = Item.update(1, condition='fair', status='maintenance')

        assert result == updated_item
        call_args = mock_db_cursor.execute.call_args
        assert 'condition = %s' in call_args[0][0]
        assert 'status = %s' in call_args[0][0]

    def test_update_item_invalid_fields(self, mock_db_cursor):
        """Test updating with invalid fields returns None"""
        result = Item.update(1, invalid_field='value')

        assert result is None
        mock_db_cursor.execute.assert_not_called()

    def test_update_item_no_fields(self, mock_db_cursor):
        """Test updating with no fields returns None"""
        result = Item.update(1)

        assert result is None
        mock_db_cursor.execute.assert_not_called()

    def test_update_item_cannot_change_quantities_directly(self, mock_db_cursor, sample_item):
        """Test that quantities cannot be updated directly via update method"""
        mock_db_cursor.fetchone.return_value = sample_item

        # Try to update quantity fields - they should be ignored
        result = Item.update(1, quantity_total=20, quantity_available=15)

        # The update should not be called since these fields are not allowed
        assert result is None

    def test_allowed_update_fields(self, mock_db_cursor, sample_item):
        """Test that only allowed fields can be updated"""
        allowed_fields = [
            'item_name', 'category', 'purchase_price', 'restock_date',
            'condition', 'status', 'last_audit_date', 'notes', 'image_url'
        ]

        for field in allowed_fields:
            mock_db_cursor.reset_mock()
            mock_db_cursor.fetchone.return_value = sample_item

            Item.update(1, **{field: 'test_value'})

            assert mock_db_cursor.execute.called
            call_args = mock_db_cursor.execute.call_args
            assert f"{field} = %s" in call_args[0][0]