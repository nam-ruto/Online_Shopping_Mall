from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from .enums import OrderStatus, PaymentMethod
from .order_item import OrderItem


@dataclass(slots=True)
class Order:
    # DB: INT AUTO_INCREMENT
    id: Optional[int] = None
    customer_id: str = ""  # UUID
    transaction_id: Optional[int] = None
    to_state: Optional[str] = None
    to_city: Optional[str] = None
    to_address_line: Optional[str] = None
    total_amount: Decimal = field(default_factory=lambda: Decimal("0.00"))
    order_date: datetime = field(default_factory=datetime.utcnow)
    status: OrderStatus = OrderStatus.IN_CART
    payment_method: PaymentMethod = PaymentMethod.CREDIT
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    # Domain convenience (not a DB column)
    items: List[OrderItem] = field(default_factory=list)

    def __post_init__(self) -> None:
        if not self.customer_id:
            raise ValueError("customer_id must be provided")
        if not isinstance(self.status, OrderStatus):
            raise ValueError("status must be an instance of OrderStatus enum")
        if not isinstance(self.payment_method, PaymentMethod):
            raise ValueError("payment_method must be an instance of PaymentMethod enum")
        if isinstance(self.total_amount, (int, float, str)):
            self.total_amount = Decimal(str(self.total_amount))
        if self.total_amount < Decimal("0"):
            raise ValueError("total_amount must be non-negative")

    def add_item(self, order_item: OrderItem) -> None:
        if self.id is not None and order_item.order_id not in (0, self.id):
            raise ValueError("order_item belongs to a different order")
        if self.id is not None:
            order_item.order_id = self.id
        self.items.append(order_item)
        self.recalculate_total()

    def remove_item(self, order_item_id: int) -> None:
        self.items = [oi for oi in self.items if oi.id != order_item_id]
        self.recalculate_total()

    def recalculate_total(self) -> None:
        total = sum((oi.sub_total for oi in self.items), start=Decimal("0.00"))
        self.total_amount = total.quantize(Decimal("0.01"))


