from __future__ import annotations

from contextlib import contextmanager
from dataclasses import asdict
from typing import Any, Callable, Dict, Iterable, Iterator, Optional, Sequence, Tuple, TypeVar

from app.db.connection import db_cursor

T = TypeVar("T")


@contextmanager
def transaction_cursor() -> Iterator[Tuple[Any, Any]]:
    # delegates to db_cursor which already wraps commit/rollback
    with db_cursor(dictionary=True) as ctx:
        yield ctx


def execute(query: str, params: Sequence[Any] | Dict[str, Any] | None = None) -> int:
    with transaction_cursor() as (conn, cur):
        cur.execute(query, params or ())
        # lastrowid is available for AUTO_INCREMENT tables
        return getattr(cur, "lastrowid", 0) or 0


def executemany(query: str, param_list: Iterable[Sequence[Any] | Dict[str, Any]]) -> None:
    with transaction_cursor() as (conn, cur):
        cur.executemany(query, list(param_list))


def fetch_one(query: str, params: Sequence[Any] | Dict[str, Any] | None = None) -> Optional[Dict[str, Any]]:
    with transaction_cursor() as (conn, cur):
        cur.execute(query, params or ())
        row = cur.fetchone()
        return dict(row) if row is not None else None


def fetch_all(query: str, params: Sequence[Any] | Dict[str, Any] | None = None) -> list[Dict[str, Any]]:
    with transaction_cursor() as (conn, cur):
        cur.execute(query, params or ())
        rows = cur.fetchall() or []
        return [dict(r) for r in rows]


def insert_from_dataclass(table: str, data: Any, include: Optional[set[str]] = None) -> None:
    """
    Convenience insert using a dataclass' fields mapped to column names.
    Use only when field names match column names exactly.
    """
    row = asdict(data)
    if include:
        row = {k: v for k, v in row.items() if k in include}
    columns = ", ".join(row.keys())
    placeholders = ", ".join(["%s"] * len(row))
    sql = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
    execute(sql, list(row.values()))


def update(table: str, id_value: int | str, data: dict, id_column: str = "id") -> None:
    """
    Generic partial-update helper.
    - Only non-None values in `data` are applied.
    - Column names are validated against a safe pattern to avoid SQL injection via column names.
    - Uses parameterized queries for values.
    """
    if not data:
        return
    # filter None values (only update provided fields)
    fields = {k: v for k, v in data.items() if v is not None}
    if not fields:
        return

    # very small safety check for column names: only allow alnum + underscore and must start with letter/_
    import re

    col_re = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
    for k in fields.keys():
        if not col_re.match(k):
            raise ValueError(f"Invalid column name: {k}")

    set_clause = ", ".join([f"{col}=%s" for col in fields.keys()])
    params = list(fields.values()) + [id_value]
    sql = f"UPDATE {table} SET {set_clause} WHERE {id_column}=%s"
    execute(sql, params)

def delete_from_dataclass(table: str, id: int | str) -> None:
    sql = f"DELETE FROM {table} WHERE id={id}"
    execute(sql)
