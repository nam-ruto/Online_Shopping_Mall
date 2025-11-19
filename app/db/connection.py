from contextlib import contextmanager
from typing import Iterator, Optional, Tuple

import mysql.connector
from mysql.connector import pooling, Error, MySQLConnection

from app.config.settings import settings

_pool: Optional[pooling.MySQLConnectionPool] = None


def _init_pool() -> pooling.MySQLConnectionPool:
    global _pool
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            pool_name="shopping_mall_pool",
            pool_size=5,
            **settings.mysql_connector_config(),
        )
    return _pool


def get_connection() -> MySQLConnection:
    """
    Get a pooled MySQL connection. Assumes schema already exists.
    """
    return _init_pool().get_connection()


@contextmanager
def db_cursor(dictionary: bool = True) -> Iterator[Tuple[MySQLConnection, mysql.connector.cursor.MySQLCursor]]:
    """
    Context manager yielding (connection, cursor) with commit/rollback handling.
    Usage:
        with db_cursor() as (conn, cur):
            cur.execute("SELECT 1")
            row = cur.fetchone()
    """
    conn: Optional[MySQLConnection] = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor(dictionary=dictionary)
        yield conn, cur
        conn.commit()
    except Error as exc:
        if conn is not None:
            try:
                conn.rollback()
            except Exception:
                pass
        raise exc
    finally:
        if cur is not None:
            try:
                cur.close()
            except Exception:
                pass
        if conn is not None:
            try:
                conn.close()
            except Exception:
                pass


def ping() -> bool:
    """
    Simple connectivity check to the configured database.
    """
    try:
        with get_connection() as conn:
            conn.ping(reconnect=True, attempts=1, delay=0)
        return True
    except Exception:
        return False


