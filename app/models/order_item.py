from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional


@dataclass(slots=True)
class OrderItem:
    # DB: INT AUTO_INCREMENT
    id: Optional[int] = None
    order_id: int = 0    # order.id
    item_id: Optional[int] = None  # item.id (nullable when item was deleted)
    item_name: str = ""             # snapshot of item.name at purchase time
    item_description: Optional[str] = None  # snapshot of item.description
    item_category: Optional[str] = None     # snapshot of item.category
    quantity: int = 1
    unit_price: Decimal = field(default_factory=lambda: Decimal("0.00"))

    def __post_init__(self) -> None:
        if isinstance(self.unit_price, (int, float, str)):
            self.unit_price = Decimal(str(self.unit_price))
        if self.unit_price < Decimal("0"):
            raise ValueError("unit_price must be non-negative")
        if self.quantity <= 0:
            raise ValueError("quantity must be positive")
        if self.order_id <= 0:
            raise ValueError("order_id must be a positive integer")
        if self.item_id is not None and self.item_id <= 0:
            raise ValueError("item_id must be a positive integer when provided")
        if not self.item_name.strip():
            raise ValueError("item_name must be non-empty")

    @property
    def sub_total(self) -> Decimal:
        return (self.unit_price * Decimal(self.quantity)).quantize(Decimal("0.01"))


