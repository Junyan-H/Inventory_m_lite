"""
Item model for inventory database operations
"""

from database import execute_query, get_db_cursor


class Item:
    """Item model with CRUD operations"""

    @staticmethod
    def get_by_location(location):
        """
        Get all items for a specific location

        Args:
            location (str): Location name

        Returns:
            list: List of item records
        """
        query = """
            SELECT item_id, item_name, category, location,
                   quantity_total, quantity_available, quantity_checked_out,
                   purchase_price, restock_date, condition, status,
                   last_audit_date, notes, image_url,
                   created_at, updated_at
            FROM inventory.items
            WHERE location = %s
            ORDER BY item_name
        """
        return execute_query(query, (location,), fetch_all=True)

    @staticmethod
    def get_by_id(item_id):
        """
        Get item by ID

        Args:
            item_id (int): Item ID

        Returns:
            dict: Item record or None
        """
        query = """
            SELECT item_id, item_name, category, location,
                   quantity_total, quantity_available, quantity_checked_out,
                   purchase_price, restock_date, condition, status,
                   last_audit_date, notes, image_url,
                   created_at, updated_at
            FROM inventory.items
            WHERE item_id = %s
        """
        return execute_query(query, (item_id,), fetch_one=True)

    @staticmethod
    def get_available_items(location=None):
        """
        Get items that are available for checkout

        Args:
            location (str, optional): Filter by location

        Returns:
            list: List of available items
        """
        query = """
            SELECT item_id, item_name, category, location,
                   quantity_total, quantity_available, quantity_checked_out,
                   purchase_price, condition, status, notes, image_url
            FROM inventory.items
            WHERE quantity_available > 0 AND status = 'available'
        """
        params = ()

        if location:
            query += " AND location = %s"
            params = (location,)

        query += " ORDER BY item_name"

        return execute_query(query, params, fetch_all=True)

    @staticmethod
    def search(query_text, location=None):
        """
        Search items by name or category

        Args:
            query_text (str): Search query
            location (str, optional): Filter by location

        Returns:
            list: List of matching items
        """
        query = """
            SELECT item_id, item_name, category, location,
                   quantity_total, quantity_available, quantity_checked_out,
                   purchase_price, condition, status, notes, image_url
            FROM inventory.items
            WHERE (item_name ILIKE %s OR category ILIKE %s)
        """
        search_pattern = f"%{query_text}%"
        params = [search_pattern, search_pattern]

        if location:
            query += " AND location = %s"
            params.append(location)

        query += " ORDER BY item_name"

        return execute_query(query, tuple(params), fetch_all=True)

    @staticmethod
    def update_quantities(item_id, quantity_change, is_checkout=True):
        """
        Update item quantities when checking out or returning

        Args:
            item_id (int): Item ID
            quantity_change (int): Quantity to add/subtract
            is_checkout (bool): True for checkout (decrease available), False for checkin (increase available)

        Returns:
            dict: Updated item record or None

        Raises:
            ValueError: If insufficient quantity available
        """
        with get_db_cursor(commit=True) as cursor:
            # Lock row for update
            cursor.execute(
                "SELECT quantity_available, quantity_checked_out FROM inventory.items WHERE item_id = %s FOR UPDATE",
                (item_id,)
            )
            item = cursor.fetchone()

            if not item:
                raise ValueError(f"Item {item_id} not found")

            if is_checkout:
                # Checkout: decrease available, increase checked_out
                if item['quantity_available'] < quantity_change:
                    raise ValueError(
                        f"Insufficient quantity. Available: {item['quantity_available']}, Requested: {quantity_change}"
                    )

                cursor.execute("""
                    UPDATE inventory.items
                    SET quantity_available = quantity_available - %s,
                        quantity_checked_out = quantity_checked_out + %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE item_id = %s
                    RETURNING item_id, item_name, quantity_total, quantity_available, quantity_checked_out
                """, (quantity_change, quantity_change, item_id))
            else:
                # Check-in: increase available, decrease checked_out
                if item['quantity_checked_out'] < quantity_change:
                    raise ValueError(
                        f"Cannot check in {quantity_change} items. Only {item['quantity_checked_out']} currently checked out"
                    )

                cursor.execute("""
                    UPDATE inventory.items
                    SET quantity_available = quantity_available + %s,
                        quantity_checked_out = quantity_checked_out - %s,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE item_id = %s
                    RETURNING item_id, item_name, quantity_total, quantity_available, quantity_checked_out
                """, (quantity_change, quantity_change, item_id))

            return cursor.fetchone()

    @staticmethod
    def create(item_name, category, location, quantity_total, **kwargs):
        """
        Create a new item

        Args:
            item_name (str): Item name
            category (str): Item category
            location (str): Storage location
            quantity_total (int): Total quantity
            **kwargs: Optional fields (purchase_price, restock_date, condition, status, notes, image_url)

        Returns:
            dict: Created item record
        """
        query = """
            INSERT INTO inventory.items (
                item_name, category, location, quantity_total, quantity_available,
                purchase_price, restock_date, condition, status, notes, image_url
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING item_id, item_name, category, location,
                      quantity_total, quantity_available, quantity_checked_out,
                      purchase_price, restock_date, condition, status,
                      last_audit_date, notes, image_url, created_at, updated_at
        """

        params = (
            item_name,
            category,
            location,
            quantity_total,
            quantity_total,  # Initially all available
            kwargs.get('purchase_price'),
            kwargs.get('restock_date'),
            kwargs.get('condition', 'good'),
            kwargs.get('status', 'available'),
            kwargs.get('notes'),
            kwargs.get('image_url')
        )

        with get_db_cursor(commit=True) as cursor:
            cursor.execute(query, params)
            return cursor.fetchone()

    @staticmethod
    def update(item_id, **kwargs):
        """
        Update item fields

        Args:
            item_id (int): Item ID
            **kwargs: Fields to update

        Returns:
            dict: Updated item record or None
        """
        allowed_fields = [
            'item_name', 'category', 'purchase_price', 'restock_date',
            'condition', 'status', 'last_audit_date', 'notes', 'image_url'
        ]
        updates = {k: v for k, v in kwargs.items() if k in allowed_fields}

        if not updates:
            return None

        set_clause = ', '.join([f"{k} = %s" for k in updates.keys()])
        values = list(updates.values()) + [item_id]

        query = f"""
            UPDATE inventory.items
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP
            WHERE item_id = %s
            RETURNING item_id, item_name, category, location,
                      quantity_total, quantity_available, quantity_checked_out,
                      purchase_price, restock_date, condition, status,
                      last_audit_date, notes, image_url, created_at, updated_at
        """

        with get_db_cursor(commit=True) as cursor:
            cursor.execute(query, values)
            return cursor.fetchone()