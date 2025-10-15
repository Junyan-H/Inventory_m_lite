"""
User model for database operations
"""

from database import execute_query, get_db_cursor


class User:
    """User model with CRUD operations"""

    @staticmethod
    def get_by_ldap(ldap):
        """
        Get user by LDAP username

        Args:
            ldap (str): LDAP username

        Returns:
            dict: User record or None
        """
        query = """
            SELECT user_id, ldap, full_name, email, role, department, active,
                   created_at, updated_at
            FROM inventory.users
            WHERE ldap = %s AND active = TRUE
        """
        return execute_query(query, (ldap,), fetch_one=True)

    @staticmethod
    def get_by_id(user_id):
        """
        Get user by ID

        Args:
            user_id (int): User ID

        Returns:
            dict: User record or None
        """
        query = """
            SELECT user_id, ldap, full_name, email, role, department, active,
                   created_at, updated_at
            FROM inventory.users
            WHERE user_id = %s
        """
        return execute_query(query, (user_id,), fetch_one=True)

    @staticmethod
    def create(ldap, full_name, email=None, role='employee', department=None):
        """
        Create a new user

        Args:
            ldap (str): LDAP username
            full_name (str): Full name
            email (str): Email address
            role (str): User role
            department (str): Department name

        Returns:
            dict: Created user record
        """
        query = """
            INSERT INTO inventory.users (ldap, full_name, email, role, department)
            VALUES (%s, %s, %s, %s, %s)
            RETURNING user_id, ldap, full_name, email, role, department, active,
                      created_at, updated_at
        """
        with get_db_cursor(commit=True) as cursor:
            cursor.execute(query, (ldap, full_name, email, role, department))
            return cursor.fetchone()

    @staticmethod
    def get_all(active_only=True):
        """
        Get all users

        Args:
            active_only (bool): Only return active users

        Returns:
            list: List of user records
        """
        query = """
            SELECT user_id, ldap, full_name, email, role, department, active,
                   created_at, updated_at
            FROM inventory.users
        """
        if active_only:
            query += " WHERE active = TRUE"

        query += " ORDER BY full_name"

        return execute_query(query, fetch_all=True)

    @staticmethod
    def update(user_id, **kwargs):
        """
        Update user fields

        Args:
            user_id (int): User ID
            **kwargs: Fields to update (full_name, email, role, department, active)

        Returns:
            dict: Updated user record or None
        """
        allowed_fields = ['full_name', 'email', 'role', 'department', 'active']
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not updates:
            return None

        set_clause = ', '.join([f"{k} = %s" for k in updates.keys()])
        values = list(updates.values()) + [user_id]

        query = f"""
            UPDATE inventory.users
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP
            WHERE user_id = %s
            RETURNING user_id, ldap, full_name, email, role, department, active,
                      created_at, updated_at
        """

        with get_db_cursor(commit=True) as cursor:
            cursor.execute(query, values)
            return cursor.fetchone()

    @staticmethod
    def deactivate(user_id):
        """
        Deactivate a user

        Args:
            user_id (int): User ID

        Returns:
            bool: Success status
        """
        return User.update(user_id, active=False) is not None