"""
Database connection manager for PostgreSQL
Provides connection pooling and helper functions for database operations
"""

import psycopg2
from psycopg2 import pool, extras
from contextlib import contextmanager
from flask import current_app, g


class Database:
    """Database connection pool manager"""

    _connection_pool = None

    @classmethod
    def initialize(cls, database_url, min_conn=1, max_conn=10):
        """
        Initialize the connection pool

        Args:
            database_url (str): PostgreSQL connection string
            min_conn (int): Minimum number of connections
            max_conn (int): Maximum number of connections
        """
        try:
            cls._connection_pool = psycopg2.pool.SimpleConnectionPool(
                min_conn,
                max_conn,
                database_url
            )
            if cls._connection_pool:
                print("✓ Database connection pool created successfully")
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"✗ Error creating connection pool: {error}")
            raise

    @classmethod
    def get_connection(cls):
        """
        Get a connection from the pool

        Returns:
            connection: PostgreSQL connection object
        """
        if cls._connection_pool is None:
            raise Exception("Connection pool not initialized. Call initialize() first.")
        return cls._connection_pool.getconn()

    @classmethod
    def return_connection(cls, connection):
        """
        Return a connection to the pool

        Args:
            connection: PostgreSQL connection object
        """
        if cls._connection_pool:
            cls._connection_pool.putconn(connection)

    @classmethod
    def close_all_connections(cls):
        """Close all connections in the pool"""
        if cls._connection_pool:
            cls._connection_pool.closeall()
            print("✓ All database connections closed")


@contextmanager
def get_db_connection():
    """
    Context manager for database connections
    Automatically returns connection to pool

    Usage:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
    """
    connection = Database.get_connection()
    try:
        yield connection
    finally:
        Database.return_connection(connection)


@contextmanager
def get_db_cursor(commit=False):
    """
    Context manager for database cursor with automatic commit/rollback

    Args:
        commit (bool): Whether to commit transaction on success

    Usage:
        with get_db_cursor(commit=True) as cursor:
            cursor.execute("INSERT INTO users ...")
    """
    connection = Database.get_connection()
    cursor = connection.cursor(cursor_factory=extras.RealDictCursor)
    try:
        yield cursor
        if commit:
            connection.commit()
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        cursor.close()
        Database.return_connection(connection)


def execute_query(query, params=None, fetch_one=False, fetch_all=False, commit=False):
    """
    Execute a database query with automatic connection handling

    Args:
        query (str): SQL query to execute
        params (tuple/dict): Query parameters
        fetch_one (bool): Fetch single result
        fetch_all (bool): Fetch all results
        commit (bool): Commit transaction

    Returns:
        Result of query or None
    """
    with get_db_cursor(commit=commit) as cursor:
        cursor.execute(query, params or ())

        if fetch_one:
            return cursor.fetchone()
        elif fetch_all:
            return cursor.fetchall()
        elif not commit:
            return cursor.fetchall()

        return cursor.rowcount


def init_app(app):
    """
    Initialize database with Flask app

    Args:
        app: Flask application instance
    """
    database_url = app.config.get('DATABASE_URL')
    min_conn = 1
    max_conn = app.config.get('DB_POOL_SIZE', 5) + app.config.get('DB_MAX_OVERFLOW', 10)

    print(database_url)
    Database.initialize(database_url, min_conn, max_conn)

    @app.teardown_appcontext
    def shutdown_session(exception=None):
        """Close database connections on app context teardown"""
        pass  # Connections are returned to pool automatically via context managers