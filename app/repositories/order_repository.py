from __future__ import annotations

from decimal import Decimal
from typing import List, Optional

from app.models import OrderStatus, PaymentMethod
from app.models.order import Order
from . import base
from app.repositories.item_repository import ItemRepository


class OrderRepository:
    ORDER_TABLE = "`order`"
    ITEM_TABLE = "order_item"
    _has_item_name_col: Optional[bool] = None

    @staticmethod
    def _ensure_item_name_probe() -> bool:
        if OrderRepository._has_item_name_col is None:
            row = base.fetch_one(
                "SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS "
                "WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'order_item' "
                "AND COLUMN_NAME = 'item_name' LIMIT 1"
            )
            OrderRepository._has_item_name_col = bool(row)
        return bool(OrderRepository._has_item_name_col)

    @staticmethod
    def create_order(
        customer_id: str,
        to_state: Optional[str],
        to_city: Optional[str],
        to_address_line: Optional[str],
        payment_method: PaymentMethod,
        status: OrderStatus,
        total_amount: Decimal,
    ) -> int:
        sql = (
            f"INSERT INTO {OrderRepository.ORDER_TABLE} "
            "(customer_id, to_state, to_city, to_address_line, total_amount, status, payment_method) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )
        order_id = base.execute(
            sql,
            (
                customer_id,
                to_state,
                to_city,
                to_address_line,
                str(total_amount),
                status.value,
                payment_method.value,
            ),
        )
        return int(order_id)

    @staticmethod
    def add_order_item(order_id: int, item_id: int, quantity: int, unit_price: Decimal) -> int:
        sub_total = (unit_price * Decimal(quantity)).quantize(Decimal("0.01"))
        if OrderRepository._ensure_item_name_probe():
            # Include item_name column if it exists
            item = ItemRepository.get_by_id(item_id)
            item_name = item.name if item and item.name else None
            sql = (
                f"INSERT INTO {OrderRepository.ITEM_TABLE} "
                "(order_id, item_id, quantity, unit_price, sub_total, item_name) "
                "VALUES (%s, %s, %s, %s, %s, %s)"
            )
            return int(base.execute(sql, (order_id, item_id, quantity, str(unit_price), str(sub_total), item_name)))
        else:
            sql = (
                f"INSERT INTO {OrderRepository.ITEM_TABLE} "
                "(order_id, item_id, quantity, unit_price, sub_total) "
                "VALUES (%s, %s, %s, %s, %s)"
            )
            return int(base.execute(sql, (order_id, item_id, quantity, str(unit_price), str(sub_total))))

    @staticmethod
    def update_total(order_id: int) -> None:
        sql = (
            f"UPDATE {OrderRepository.ORDER_TABLE} o "
            "JOIN (SELECT order_id, SUM(sub_total) AS total FROM order_item WHERE order_id=%s) s "
            "ON s.order_id = o.id "
            "SET o.total_amount = s.total"
        )
        base.execute(sql, (order_id,))

    @staticmethod
    def decrement_stock_for_item(item_id: int, quantity: int = 1) -> None:
        base.execute("UPDATE item SET stock_quantity = stock_quantity - %s WHERE id=%s AND stock_quantity >= %s", (quantity, item_id, quantity))

    @staticmethod
    def list_orders_by_customer(customer_id: str) -> list[dict]:
        sql = (
            f"SELECT id, total_amount, status, payment_method, order_date "
            f"FROM {OrderRepository.ORDER_TABLE} WHERE customer_id=%s ORDER BY order_date DESC"
        )
        return base.fetch_all(sql, (customer_id,))

    @staticmethod
    def get_by_id(order_id: int) -> Optional[Order]:
        sql = (
            f"SELECT * FROM {OrderRepository.ORDER_TABLE} WHERE id={order_id}"
        )
        row = base.fetch_one(sql)
        return row if row else None
