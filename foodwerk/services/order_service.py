"""Order service — creation and status management."""

from __future__ import annotations

from typing import Optional

from .base_service import BaseService
from .cart_service import CartService
from ..data_access.dao import AddressDAO, OrderDAO
from ..domain.models import Address, DeliveryInfo, Order, OrderItem, OrderItemExtra


VALID_STATUSES = ["pending", "preparing", "ready", "delivered", "collected"]


class OrderService(BaseService):

    def __init__(self, order_dao: OrderDAO, address_dao: AddressDAO) -> None:
        self.order_dao = order_dao
        self.address_dao = address_dao

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
        street: Optional[str] = None,
        house_nr: Optional[str] = None,
        city: Optional[str] = None,
        postal_code: Optional[str] = None,
        pickup_time=None,
        notes: Optional[str] = None,
    ) -> Order:
        if cart.is_empty:
            raise ValueError("Cart is empty.")
        if order_type not in ("delivery", "pickup"):
            raise ValueError("Order type must be 'delivery' or 'pickup'.")
        if order_type == "delivery" and not all([street, house_nr, city, postal_code]):
            raise ValueError("All address fields are required for delivery orders.")

        order = Order(
            user_id=user_id,
            order_type=order_type,
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
            oi.extras = [
                OrderItemExtra(
                    extra_id=e["id"],
                    quantity=e.get("quantity", 1),
                    unit_price=e["price"],
                )
                for e in cart_item.extras
            ]
            order_items.append(oi)
        order.order_items = order_items

        if order_type == "delivery":
            address = Address(
                user_id=user_id,
                street=street,
                house_nr=house_nr,
                city=city,
                postal_code=postal_code,
            )
            saved_address = self.address_dao.create(address)
            order.delivery_info = DeliveryInfo(address_id=saved_address.id)

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
