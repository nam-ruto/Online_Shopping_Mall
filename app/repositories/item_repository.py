from typing import Optional
from app.models import Item
from app.repositories.account_repository import AccountRepository
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
