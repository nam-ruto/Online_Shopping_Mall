from __future__ import annotations

from typing import List

from . import base


class LikedItemRepository:
    TABLE = "liked_item"

    @staticmethod
    def like(customer_id: str, item_id: int) -> None:
        # Insert ignore-like behavior by checking uniqueness before insert
        sql = (
            f"INSERT INTO {LikedItemRepository.TABLE} (customer_id, item_id) "
            "VALUES (%s, %s)"
        )
        base.execute(sql, (customer_id, item_id))
        # Update item's like_count
        base.execute("UPDATE item SET like_count = like_count + 1 WHERE id=%s", (item_id,))

    @staticmethod
    def unlike(customer_id: str, item_id: int) -> None:
        base.execute(
            f"DELETE FROM {LikedItemRepository.TABLE} WHERE customer_id=%s AND item_id=%s",
            (customer_id, item_id),
        )
        base.execute("UPDATE item SET like_count = GREATEST(like_count - 1, 0) WHERE id=%s", (item_id,))

    @staticmethod
    def list_by_customer(customer_id: str) -> list[dict]:
        sql = (
            f"SELECT li.item_id, i.name, i.price, i.category "
            f"FROM {LikedItemRepository.TABLE} li "
            "JOIN item i ON i.id = li.item_id "
            "WHERE li.customer_id=%s "
            "ORDER BY i.like_count DESC, i.id ASC"
        )
        return base.fetch_all(sql, (customer_id,))


