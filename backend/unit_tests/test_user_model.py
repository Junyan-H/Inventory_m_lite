"""
Unit tests for User model
"""

import pytest
from unittest.mock import patch, MagicMock
from models.user import User


class TestUserModel:
    """Test suite for User model"""

    def test_get_by_ldap_success(self, mock_execute_query, sample_user):
        """Test successful user retrieval by LDAP"""
        mock_execute_query.return_value = sample_user

        result = User.get_by_ldap('jdoe')

        assert result == sample_user
        mock_execute_query.assert_called_once()
        # Check that the query includes LDAP and active filters
        call_args = mock_execute_query.call_args
        assert 'ldap = %s' in call_args[0][0]
        assert 'active = TRUE' in call_args[0][0]
        assert call_args[0][1] == ('jdoe',)

    def test_get_by_ldap_not_found(self, mock_execute_query):
        """Test user not found by LDAP"""
        mock_execute_query.return_value = None

        result = User.get_by_ldap('nonexistent')

        assert result is None

    def test_get_by_id_success(self, mock_execute_query, sample_user):
        """Test successful user retrieval by ID"""
        mock_execute_query.return_value = sample_user

        result = User.get_by_id(1)

        assert result == sample_user
        mock_execute_query.assert_called_once()
        call_args = mock_execute_query.call_args
        assert 'user_id = %s' in call_args[0][0]
        assert call_args[0][1] == (1,)

    def test_get_by_id_not_found(self, mock_execute_query):
        """Test user not found by ID"""
        mock_execute_query.return_value = None

        result = User.get_by_id(999)

        assert result is None

    def test_create_user_minimal(self, mock_db_cursor, sample_user):
        """Test creating user with minimal required fields"""
        mock_db_cursor.fetchone.return_value = sample_user

        result = User.create('jdoe', 'John Doe')

        assert result == sample_user
        mock_db_cursor.execute.assert_called_once()
        # Verify INSERT query
        call_args = mock_db_cursor.execute.call_args
        assert 'INSERT INTO users' in call_args[0][0]
        assert call_args[0][1][0] == 'jdoe'
        assert call_args[0][1][1] == 'John Doe'

    def test_create_user_all_fields(self, mock_db_cursor, sample_user):
        """Test creating user with all fields"""
        mock_db_cursor.fetchone.return_value = sample_user

        result = User.create(
            'jdoe',
            'John Doe',
            email='jdoe@company.com',
            role='manager',
            department='Operations'
        )

        assert result == sample_user
        call_args = mock_db_cursor.execute.call_args
        assert call_args[0][1] == ('jdoe', 'John Doe', 'jdoe@company.com', 'manager', 'Operations')

    def test_get_all_active_only(self, mock_execute_query, sample_user):
        """Test getting all active users"""
        mock_execute_query.return_value = [sample_user]

        result = User.get_all(active_only=True)

        assert result == [sample_user]
        call_args = mock_execute_query.call_args
        assert 'WHERE active = TRUE' in call_args[0][0]
        assert 'ORDER BY full_name' in call_args[0][0]

    def test_get_all_including_inactive(self, mock_execute_query, sample_user):
        """Test getting all users including inactive"""
        inactive_user = sample_user.copy()
        inactive_user['active'] = False
        mock_execute_query.return_value = [sample_user, inactive_user]

        result = User.get_all(active_only=False)

        assert len(result) == 2
        call_args = mock_execute_query.call_args
        assert 'WHERE active = TRUE' not in call_args[0][0]

    def test_update_user_single_field(self, mock_db_cursor, sample_user):
        """Test updating a single user field"""
        updated_user = sample_user.copy()
        updated_user['email'] = 'newemail@company.com'
        mock_db_cursor.fetchone.return_value = updated_user

        result = User.update(1, email='newemail@company.com')

        assert result == updated_user
        call_args = mock_db_cursor.execute.call_args
        assert 'UPDATE users' in call_args[0][0]
        assert 'email = %s' in call_args[0][0]
        assert 'updated_at = CURRENT_TIMESTAMP' in call_args[0][0]

    def test_update_user_multiple_fields(self, mock_db_cursor, sample_user):
        """Test updating multiple user fields"""
        updated_user = sample_user.copy()
        updated_user['email'] = 'newemail@company.com'
        updated_user['role'] = 'manager'
        mock_db_cursor.fetchone.return_value = updated_user

        result = User.update(1, email='newemail@company.com', role='manager')

        assert result == updated_user
        call_args = mock_db_cursor.execute.call_args
        assert 'email = %s' in call_args[0][0]
        assert 'role = %s' in call_args[0][0]

    def test_update_user_invalid_fields(self, mock_db_cursor):
        """Test updating with invalid fields returns None"""
        result = User.update(1, invalid_field='value')

        assert result is None
        mock_db_cursor.execute.assert_not_called()

    def test_update_user_no_fields(self, mock_db_cursor):
        """Test updating with no fields returns None"""
        result = User.update(1)

        assert result is None
        mock_db_cursor.execute.assert_not_called()

    def test_deactivate_user(self, mock_db_cursor, sample_user):
        """Test deactivating a user"""
        deactivated_user = sample_user.copy()
        deactivated_user['active'] = False
        mock_db_cursor.fetchone.return_value = deactivated_user

        result = User.deactivate(1)

        assert result is True
        mock_db_cursor.execute.assert_called_once()
        call_args = mock_db_cursor.execute.call_args
        assert 'UPDATE users' in call_args[0][0]
        # Check that active = False is in the values
        assert False in call_args[0][1]

    def test_deactivate_user_not_found(self, mock_db_cursor):
        """Test deactivating non-existent user"""
        mock_db_cursor.fetchone.return_value = None

        result = User.deactivate(999)

        assert result is False

    def test_allowed_update_fields(self, mock_db_cursor, sample_user):
        """Test that only allowed fields can be updated"""
        allowed_fields = ['full_name', 'email', 'role', 'department', 'active']

        for field in allowed_fields:
            mock_db_cursor.reset_mock()
            mock_db_cursor.fetchone.return_value = sample_user

            User.update(1, **{field: 'test_value'})

            assert mock_db_cursor.execute.called
            call_args = mock_db_cursor.execute.call_args
            assert f"{field} = %s" in call_args[0][0]