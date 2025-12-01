from __future__ import annotations

from typing import Iterable

from app.repositories.liked_item_repository import LikedItemRepository


class LikeService:
    def like_items(self, customer_id: str, item_ids: Iterable[int]) -> int:
        count = 0
        for iid in item_ids:
            try:
                LikedItemRepository.like(customer_id, iid)
                count += 1
            except Exception:
                # ignore duplicates or failures per-id
                pass
        return count

    def unlike_items(self, customer_id: str, item_ids: Iterable[int]) -> int:
        count = 0
        for iid in item_ids:
            try:
                LikedItemRepository.unlike(customer_id, iid)
                count += 1
            except Exception:
                pass
        return count

    def list_liked(self, customer_id: str) -> list[dict]:
        return LikedItemRepository.list_by_customer(customer_id)


