"""Order service — creation and status management."""

from __future__ import annotations

from typing import Optional

from .base_service import BaseService
from .cart_service import CartService
from ..data_access.dao import OrderDAO
from ..domain.models import Order, OrderItem


VALID_STATUSES = ["pending", "preparing", "ready", "delivered", "collected"]


class OrderService(BaseService):

    def __init__(self, order_dao: OrderDAO) -> None:
        self.order_dao = order_dao

    def get_by_id(self, entity_id: int) -> Optional[Order]:
        return self.order_dao.get_by_id(entity_id)

    def get_all(self, status: Optional[str] = None) -> list[Order]:
        return self.order_dao.get_all(status=status)

    # ------------------------------------------------------------------

    def create_order(
        self,
        user_id: int,
        cart: CartService,
        order_type: str,
        delivery_address_id: Optional[int] = None,
        pickup_time=None,
        notes: Optional[str] = None,
    ) -> Order:
        if cart.is_empty:
            raise ValueError("Cart is empty.")
        if order_type not in ("delivery", "pickup"):
            raise ValueError("Order type must be 'delivery' or 'pickup'.")
        if order_type == "delivery" and not delivery_address_id:
            raise ValueError("Für Lieferungen muss eine Lieferadresse angegeben werden.")

        order = Order(
            user_id=user_id,
            order_type=order_type,
            delivery_address_id=delivery_address_id,
            total_price=cart.total,
            pickup_time=pickup_time,
            notes=notes,
        )

        order_items = []
        for cart_item in cart.items:
            oi = OrderItem(
                menu_item_id=cart_item.menu_item_id,
                quantity=cart_item.quantity,
                unit_price=cart_item.unit_price,
                notes=cart_item.notes,
            )
            order_items.append(oi)
        order.order_items = order_items

        saved_order = self.order_dao.create(order)
        cart.clear()
        return saved_order

    def get_user_orders(self, user_id: int) -> list[Order]:
        return self.order_dao.get_by_user(user_id)

    def update_status(self, order_id: int, new_status: str) -> Order:
        if new_status not in VALID_STATUSES:
            raise ValueError(f"Invalid status: {new_status}. Must be one of {VALID_STATUSES}.")
        order = self.order_dao.update_status(order_id, new_status)
        if not order:
            raise ValueError("Order not found.")
        return order
