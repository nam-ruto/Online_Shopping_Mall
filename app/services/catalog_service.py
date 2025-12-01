from __future__ import annotations

from typing import Optional, List

from app.models import Item
from app.repositories.item_repository import ItemRepository


class CatalogService:
    """High-level API for catalog/browsing functionality.

    Keeps UI/CLI code away from repository details and offers higher-level
    features like pagination and filters.
    """

    def list_popular_first(self, page: int = 1, page_size: int = 25) -> List[Item]:
        if page <= 0:
            page = 1
        if page_size <= 0:
            page_size = 25
        offset = (page - 1) * page_size
        return ItemRepository.list_all_popular_first(limit=page_size, offset=offset)

    # Future helpers: search_by_name, filter_by_category, etc.
