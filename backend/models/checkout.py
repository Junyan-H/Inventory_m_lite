"""
Checkout model for checkout/check-in operations
"""

from database import execute_query, get_db_cursor
from models.item import Item
from models.user import User
from datetime import datetime, timedelta


class Checkout:
    """Checkout model with business logic for checking out/in items"""

    @staticmethod
    def checkout_item(item_id, user_id, quantity, expected_return_datetime=None,
                     checkout_condition='good', notes=None):
        """
        Check out an item to a user

        Args:
            item_id (int): Item ID
            user_id (int): User ID
            quantity (int): Quantity to checkout
            expected_return_datetime (datetime): Expected return date/time
            checkout_condition (str): Condition of item at checkout
            notes (str): Checkout notes

        Returns:
            dict: Checkout record

        Raises:
            ValueError: If item not available or user not found
        """
        # Validate user exists
        user = User.get_by_id(user_id)
        if not user:
            raise ValueError(f"User {user_id} not found")

        # Set default return datetime (7 days from now)
        if expected_return_datetime is None:
            expected_return_datetime = datetime.now() + timedelta(days=7)

        with get_db_cursor(commit=True) as cursor:
            # Update item quantities (with row locking)
            item = Item.update_quantities(item_id, quantity, is_checkout=True)

            # Create checkout record
            cursor.execute("""
                INSERT INTO inventory.checkout (
                    item_id, user_id, quantity, checkout_date,
                    expected_return_datetime, checkout_condition, notes
                )
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP, %s, %s, %s)
                RETURNING checkout_id, item_id, user_id, quantity, checkout_date,
                          expected_return_datetime, checkout_condition, notes, created_at
            """, (item_id, user_id, quantity, expected_return_datetime, checkout_condition, notes))
            checkout_record = cursor.fetchone()

            # Add to history
            cursor.execute("""
                INSERT INTO inventory.checkout_history (
                    item_id, user_id, quantity, checkout_date,
                    expected_return_datetime, checkout_condition,
                    checkout_notes, is_returned
                )
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP, %s, %s, %s, FALSE)
            """, (item_id, user_id, quantity, expected_return_datetime, checkout_condition, notes))

            return checkout_record

    @staticmethod
    def checkin_item(checkout_id, return_condition='good', return_notes=None):
        """
        Check in an item (return it)

        Args:
            checkout_id (int): Checkout ID
            return_condition (str): Condition of item at return
            return_notes (str): Return notes

        Returns:
            dict: Updated history record

        Raises:
            ValueError: If checkout not found
        """
        with get_db_cursor(commit=True) as cursor:
            # Get checkout details
            cursor.execute("""
                SELECT checkout_id, item_id, user_id, quantity,
                       checkout_date, expected_return_datetime, checkout_condition
                FROM inventory.checkout
                WHERE checkout_id = %s
            """, (checkout_id,))
            checkout = cursor.fetchone()

            if not checkout:
                raise ValueError(f"Checkout {checkout_id} not found")

            # Update item quantities (return to inventory)
            Item.update_quantities(checkout['item_id'], checkout['quantity'], is_checkout=False)

            # Remove from active checkouts
            cursor.execute("DELETE FROM inventory.checkout WHERE checkout_id = %s", (checkout_id,))

            # Update history
            is_late = datetime.now() > checkout['expected_return_datetime']

            cursor.execute("""
                UPDATE inventory.checkout_history
                SET return_date = CURRENT_TIMESTAMP,
                    return_condition = %s,
                    return_notes = %s,
                    is_returned = TRUE,
                    late_return = %s,
                    updated_at = CURRENT_TIMESTAMP
                WHERE item_id = %s
                  AND user_id = %s
                  AND is_returned = FALSE
                  AND ABS(EXTRACT(EPOCH FROM (checkout_date - %s))) < 1
                RETURNING history_id, item_id, user_id, quantity, checkout_date,
                          return_date, expected_return_datetime, is_returned, late_return,
                          checkout_condition, return_condition, checkout_notes, return_notes
            """, (return_condition, return_notes, is_late,
                  checkout['item_id'], checkout['user_id'], checkout['checkout_date']))

            result = cursor.fetchone()

            if not result:
                raise ValueError(
                    f"Failed to update checkout history. No matching unreturned checkout found for "
                    f"item_id={checkout['item_id']}, user_id={checkout['user_id']}, "
                    f"checkout_date={checkout['checkout_date']}"
                )

            return result

    @staticmethod
    def get_active_checkouts(user_id=None, item_id=None):
        """
        Get active checkouts

        Args:
            user_id (int, optional): Filter by user
            item_id (int, optional): Filter by item

        Returns:
            list: List of active checkouts
        """
        query = "SELECT * FROM inventory.v_active_checkouts WHERE 1=1"
        params = []

        if user_id:
            query += " AND user_id = %s"
            params.append(user_id)

        if item_id:
            query += " AND item_id = %s"
            params.append(item_id)

        query += " ORDER BY checkout_date DESC"

        return execute_query(query, tuple(params) if params else None, fetch_all=True)

    @staticmethod
    def get_overdue_checkouts():
        """
        Get all overdue checkouts

        Returns:
            list: List of overdue checkouts
        """
        query = """
            SELECT * FROM inventory.v_active_checkouts
            WHERE is_overdue = TRUE
            ORDER BY days_overdue DESC
        """
        return execute_query(query, fetch_all=True)

    @staticmethod
    def get_user_checkout_history(user_id, limit=50):
        """
        Get checkout history for a specific user

        Args:
            user_id (int): User ID
            limit (int): Max results

        Returns:
            list: List of checkout history records
        """
        # First get user's ldap
        user = User.get_by_id(user_id)
        if not user:
            return []

        query = """
            SELECT * FROM inventory.v_checkout_history
            WHERE ldap = %s
            ORDER BY checkout_date DESC
            LIMIT %s
        """
        return execute_query(query, (user['ldap'], limit), fetch_all=True)

    @staticmethod
    def get_item_checkout_history(item_id, limit=50):
        """
        Get checkout history for a specific item

        Args:
            item_id (int): Item ID
            limit (int): Max results

        Returns:
            list: List of checkout history records
        """
        query = """
            SELECT * FROM inventory.v_checkout_history
            WHERE item_id = %s
            ORDER BY checkout_date DESC
            LIMIT %s
        """
        return execute_query(query, (item_id, limit), fetch_all=True)

    @staticmethod
    def get_checkout_by_id(checkout_id):
        """
        Get a specific checkout by ID

        Args:
            checkout_id (int): Checkout ID

        Returns:
            dict: Checkout record or None
        """
        query = """
            SELECT * FROM inventory.v_active_checkouts
            WHERE checkout_id = %s
        """
        return execute_query(query, (checkout_id,), fetch_one=True)