from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
from app.models.item import Item
from app.repositories.item_repository import ItemRepository
from app.utils.validators import *


@dataclass
class ItemResult:
    success: bool
    message: str
    item: Optional[Item] = None

class ItemService:
    def create_item(
        self,
        name: str,
        price: Decimal,
        stock_quantity: int,
        description: Optional[str] = None,
        category: Optional[str] = None,
    ) -> ItemResult:
        # Validate inputs
        name = ensure_length_max(ensure_non_empty(name, "name"), "name", 100)
        if description:
            description = ensure_length_max(description, "description", 250)
        if category:
            category = ensure_length_max(category, "category", 100)

        if price <= 0.00:
            return ItemResult(False, "Price is invalid")

        # TODO: Maybe reject the new item if another has the same name as the new item.

        item = Item(
            name=name,
            description=description,
            category=category,
            price=price,
            stock_quantity=stock_quantity
        )
        ItemRepository.create(item)
        return ItemResult(True, "Item creation successful", item)

    def delete_item(self, id: int) -> ItemResult:
        ItemRepository.delete(id)
        return ItemResult(True, "Item deletion successful")

    def update_item(self, id: int, item: Item) -> ItemResult:
        ItemRepository.update(id, item)
        return ItemResult(True, "Item update successful")

    def get_by_id(self, id: int) -> Optional[Item]:
        return ItemRepository.get_by_id(id)

    def list_items(self) -> Optional[list[Item]]:
        return ItemRepository.list()
