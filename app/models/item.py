from dataclasses import dataclass, field
from decimal import Decimal
from typing import Optional


@dataclass(slots=True)
class Item:
    # DB: INT AUTO_INCREMENT
    id: Optional[int] = None
    name: str = ""
    description: str = ""
    category: Optional[str] = None
    price: Decimal = field(default_factory=lambda: Decimal("0.00"))
    stock_quantity: int = 0
    like_count: int = 0

    def __post_init__(self) -> None:
        if not self.name.strip():
            raise ValueError("name must be non-empty")
        if isinstance(self.price, (int, float, str)):
            self.price = Decimal(str(self.price))
        if self.price < Decimal("0"):
            raise ValueError("price must be non-negative")
        if self.stock_quantity < 0:
            raise ValueError("stock_quantity must be >= 0")
        if self.like_count < 0:
            raise ValueError("like_count must be >= 0")

    def increase_stock(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("amount must be positive")
        self.stock_quantity += amount

    def decrease_stock(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("amount must be positive")
        if amount > self.stock_quantity:
            raise ValueError("cannot decrease stock below zero")
        self.stock_quantity -= amount

    def like(self) -> None:
        self.like_count += 1

    def unlike(self) -> None:
        if self.like_count == 0:
            return
        self.like_count -= 1


