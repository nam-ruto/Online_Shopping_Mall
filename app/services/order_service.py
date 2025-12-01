from __future__ import annotations

from decimal import Decimal
from typing import Dict, Iterable, List, Optional

from app.models import PaymentMethod, OrderStatus
from app.repositories.item_repository import ItemRepository
from app.repositories.order_repository import OrderRepository


class OrderService:
    def place_order(
        self,
        customer_id: str,
        item_id_to_quantity: Dict[int, int],
        to_state: Optional[str],
        to_city: Optional[str],
        to_address_line: Optional[str],
        payment_method: PaymentMethod,
    ) -> int:
        # Calculate total and validate stock
        total = Decimal("0.00")
        selected: List[tuple[int, int, Decimal]] = []
        for iid, qty in item_id_to_quantity.items():
            it = ItemRepository.get_by_id(iid)
            if it is None:
                raise ValueError(f"Item {iid} not found")
            if qty <= 0:
                continue
            if it.stock_quantity < qty:
                raise ValueError(f"Item {iid} does not have enough stock")
            price = Decimal(str(it.price))
            total += (price * Decimal(qty))
            selected.append((iid, qty, price))
        total = total.quantize(Decimal("0.01"))

        # Create order
        order_id = OrderRepository.create_order(
            customer_id=customer_id,
            to_state=to_state,
            to_city=to_city,
            to_address_line=to_address_line,
            payment_method=payment_method,
            status=OrderStatus.PROCESSING,
            total_amount=total,
        )

        # Add items and decrement stock
        for iid, qty, price in selected:
            OrderRepository.add_order_item(order_id, iid, qty, price)
            OrderRepository.decrement_stock_for_item(iid, qty)

        # Ensure total matches
        OrderRepository.update_total(order_id)
        return order_id

    def list_orders(self, customer_id: str) -> list[dict]:
        return OrderRepository.list_orders_by_customer(customer_id)


