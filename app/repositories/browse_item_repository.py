from __future__ import annotations

from typing import List

from app.models import Item
from . import base


def _row_to_item(row: dict) -> Item:
    return Item(
        id=row["id"],
        name=row.get("name"),
        description=row.get("description") or "",
        category=row.get("category"),
        price=row.get("price"),
        stock_quantity=row.get("stock_quantity"),
        like_count=row.get("like_count"),
    )


class BrowseItemRepository:
    @staticmethod
    def list_all_popular_first() -> list[Item]:
        rows = base.fetch_all(
            "SELECT * FROM item ORDER BY like_count DESC, id ASC",
            (),
        )
        return [_row_to_item(r) for r in rows]


