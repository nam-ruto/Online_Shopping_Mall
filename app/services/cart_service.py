from __future__ import annotations

from typing import Dict, Iterable, List, Tuple

from app.models import Item
from app.services.catalog_service import CatalogService
from app.services.item_service import ItemService


class CartService:
    def __init__(self) -> None:
        # session-local in-memory map: customer_id -> item_id -> quantity
        self._cart: Dict[str, Dict[int, int]] = {}
        # service helpers (kept small and local to the instance)
        self._items = ItemService()
        self._catalog = CatalogService()

    def add_item(self, customer_id: str, item_id: int, quantity: int) -> None:
        if quantity <= 0:
            return
        bag = self._cart.setdefault(customer_id, {})
        bag[item_id] = bag.get(item_id, 0) + quantity

    def remove_items(self, customer_id: str, item_ids: Iterable[int]) -> int:
        bag = self._cart.setdefault(customer_id, {})
        removed = 0
        for iid in item_ids:
            if iid in bag:
                del bag[iid]
                removed += 1
        return removed

    def list_items(self, customer_id: str) -> List[Tuple[Item, int]]:
        bag = self._cart.get(customer_id, {})
        out: List[Tuple[Item, int]] = []
        for iid, qty in sorted(bag.items()):
            it = self._items.get_by_id(iid)
            if it:
                out.append((it, qty))
        return out

    def has_items(self, customer_id: str) -> bool:
        return bool(self._cart.get(customer_id, {}))

    def clear_selected(self, customer_id: str, item_ids: Iterable[int]) -> None:
        bag = self._cart.setdefault(customer_id, {})
        for iid in item_ids:
            if iid in bag:
                del bag[iid]

    def get_quantities(self, customer_id: str) -> Dict[int, int]:
        return dict(self._cart.get(customer_id, {}))

    def set_quantity(self, customer_id: str, item_id: int, quantity: int) -> None:
        bag = self._cart.setdefault(customer_id, {})
        if quantity <= 0:
            if item_id in bag:
                del bag[item_id]
            return
        bag[item_id] = quantity


