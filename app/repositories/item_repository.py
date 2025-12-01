from __future__ import annotations

from typing import Optional
from app.models import Item
from . import base

def _row_to_item(row: dict) -> Item:
    return Item(
        id=row["id"],
        name=row.get("name"),
        description=row.get("description"),
        category=row.get("category"),
        price=row.get("price"),
        stock_quantity=row.get("stock_quantity"),
        like_count=row.get("like_count"),
    )

class ItemRepository:
    TABLE = "item"

    @staticmethod
    def list() -> Optional[list[Item]]:
        rows = base.fetch_all(
            f"SELECT * FROM {ItemRepository.TABLE}"
        )
        return [_row_to_item(row) for row in rows] if rows else None

    @staticmethod
    def get_by_id(id: int) -> Optional[Item]:
        row = base.fetch_one(
            f"SELECT * FROM {ItemRepository.TABLE} WHERE id={id}"
        )
        return _row_to_item(row) if row else None

    @staticmethod
    def create(item: Item) -> None:
        base.insert_from_dataclass(
            ItemRepository.TABLE,
            item,
            include={
                "name",
                "description",
                "category",
                "price",
                "stock_quantity",
                "like_count"
            }
        )

    @staticmethod
    def delete(id: int) -> None:
        base.delete_from_dataclass(ItemRepository.TABLE, id)

    @staticmethod
    def update(id: int, item: Item) -> None:
        # Use the new base.update helper to perform a parameterized, safe update
        data = {
            "name": item.name,
            "description": item.description,
            "category": item.category,
            "price": item.price,
            "stock_quantity": item.stock_quantity,
            "like_count": item.like_count,
        }
        base.update(ItemRepository.TABLE, id, data)

    @staticmethod
    def update_partial(id: int, data: dict) -> None:
        """Update only the provided non-None fields for an item record."""
        base.update(ItemRepository.TABLE, id, data)

    @staticmethod
    def list_all_popular_first(limit: int | None = None, offset: int | None = None) -> list[Item]:
        # Return items ordered by popularity (likes) then id. Supports optional pagination.
        sql = f"SELECT * FROM {ItemRepository.TABLE} ORDER BY like_count DESC, id ASC"
        params: tuple = ()
        if limit is not None:
            sql += " LIMIT %s"
            params = (limit,)
            if offset is not None:
                sql += " OFFSET %s"
                params = (limit, offset)
        rows = base.fetch_all(sql, params)
        return [_row_to_item(r) for r in rows]
