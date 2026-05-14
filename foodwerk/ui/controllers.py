"""UI controllers — coordinate services and hold cart state.

Design pattern: MVC Controller layer (same as reference project).
Controllers sit between the UI layer and the service layer.
Pages never call DAOs or create sessions directly.

Controllers are instantiated once in application.py and shared across
all page requests via the Pages class.
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from nicegui import app

from ..domain.models import DeliveryAddress, MenuItem, Order, User
from ..services.auth_service import AuthService
from ..services.cart_service import CartService
from ..services.menu_service import MenuService
from ..services.order_service import OrderService
from ..services.payment_service import PaymentService


# ---------------------------------------------------------------------------
# Cart helpers — per-user storage in NiceGUI's server-side storage
# ---------------------------------------------------------------------------

def _get_cart() -> CartService:
    """Reconstruct CartService from server-side user storage."""
    return CartService.from_dict_list(app.storage.user.get("cart_items", []))


def _save_cart(cart: CartService) -> None:
    """Persist CartService back to server-side user storage."""
    app.storage.user["cart_items"] = cart.to_dict_list()


# ---------------------------------------------------------------------------
# AuthController
# ---------------------------------------------------------------------------

class AuthController:
    """Handles login and registration."""

    def __init__(self, auth_service: AuthService) -> None:
        self._auth = auth_service

    def login(self, email: str, password: str) -> Optional[User]:
        return self._auth.login(email, password)

    def register(
        self,
        first_name: str,
        last_name: str,
        email: str,
        password: str,
        phone: Optional[str] = None,
    ) -> User:
        return self._auth.register(first_name, last_name, email, password, phone)

    def get_delivery_addresses(self, user_id: int) -> list[DeliveryAddress]:
        return self._auth.get_delivery_addresses(user_id)

    def add_delivery_address(
        self,
        user_id: int,
        street: str,
        house_nr: str,
        city: str,
        postal_code: str,
        floor: Optional[str] = None,
        label: Optional[str] = None,
    ) -> DeliveryAddress:
        return self._auth.add_delivery_address(user_id, street, house_nr, city, postal_code, floor, label)

    def delete_delivery_address(self, address_id: int, user_id: int) -> bool:
        return self._auth.delete_delivery_address(address_id, user_id)

    def current_user(self) -> Optional[dict]:
        return app.storage.user.get("user")

    def store_user(self, user: User) -> None:
        app.storage.user["user"] = {
            "id": user.id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "email": user.email,
            "role": user.role,
        }

    def logout(self) -> None:
        app.storage.user.clear()


# ---------------------------------------------------------------------------
# ShoppingController
# ---------------------------------------------------------------------------

class ShoppingController:
    """Handles menu browsing, cart, and order checkout."""

    def __init__(
        self,
        menu_service: MenuService,
        order_service: OrderService,
    ) -> None:
        self._menu = menu_service
        self._order = order_service

    # Menu
    def get_categories(self):
        return self._menu.get_categories()

    def get_menu_items(self, category_id=None, available_only: bool = True):
        return self._menu.get_menu_items(category_id=category_id, available_only=available_only)

    def get_specials(self) -> list[MenuItem]:
        return self._menu.get_specials()

    # Cart
    def get_cart(self) -> CartService:
        return _get_cart()

    def add_to_cart(
        self,
        menu_item_id: int,
        name: str,
        unit_price: float,
        quantity: int = 1,
        notes: str | None = None,
    ) -> None:
        cart = _get_cart()
        cart.add_item(menu_item_id, name, unit_price, quantity, notes=notes)
        _save_cart(cart)

    def remove_from_cart(self, index: int) -> None:
        cart = _get_cart()
        cart.remove_item(index)
        _save_cart(cart)

    def update_cart_quantity(self, index: int, quantity: int) -> None:
        cart = _get_cart()
        cart.update_quantity(index, quantity)
        _save_cart(cart)

    def clear_cart(self) -> None:
        cart = _get_cart()
        cart.clear()
        _save_cart(cart)

    # Order
    def place_order(
        self,
        user_id: int,
        order_type: str,
        delivery_address_id: int | None = None,
        pickup_time=None,
        notes: str | None = None,
    ) -> Order:
        cart = _get_cart()
        order = self._order.create_order(
            user_id=user_id,
            cart=cart,
            order_type=order_type,
            delivery_address_id=delivery_address_id,
            pickup_time=pickup_time,
            notes=notes,
        )
        _save_cart(cart)
        return order

    def get_order(self, order_id: int) -> Optional[Order]:
        return self._order.get_by_id(order_id)

    def get_user_orders(self, user_id: int) -> list[Order]:
        return self._order.get_user_orders(user_id)


# ---------------------------------------------------------------------------
# AdminController
# ---------------------------------------------------------------------------

class AdminController:
    """Handles admin dashboard, menu management, order management, specials."""

    def __init__(
        self,
        menu_service: MenuService,
        order_service: OrderService,
    ) -> None:
        self._menu = menu_service
        self._order = order_service

    def get_all_orders(self, status: Optional[str] = None) -> list[Order]:
        return self._order.get_all(status=status)

    def update_order_status(self, order_id: int, new_status: str) -> Order:
        return self._order.update_status(order_id, new_status)

    def get_categories(self):
        return self._menu.get_categories()

    def get_all_menu_items(self):
        return self._menu.get_menu_items(available_only=False)

    def get_menu_items_by_category(self, category_id: int):
        return self._menu.get_menu_items(category_id=category_id, available_only=False)

    def set_item_availability(self, item_id: int, is_available: bool) -> MenuItem:
        return self._menu.set_availability(item_id, is_available)

    def set_item_special(self, item_id: int, is_special: bool) -> MenuItem:
        return self._menu.set_special(item_id, is_special)

    def set_item_discount(self, item_id: int, discount_price: Optional[float], discount_until: Optional[datetime]) -> MenuItem:
        return self._menu.set_discount(item_id, discount_price, discount_until)

    def create_menu_item(
        self,
        category_id: int,
        name: str,
        description,
        price: float,
        image_url=None,
        is_special: bool = False,
        discount_price: Optional[float] = None,
        discount_until: Optional[datetime] = None,
        created_by_user_id: Optional[int] = None,
    ) -> MenuItem:
        return self._menu.create_menu_item(
            category_id, name, description, price, image_url,
            is_special, discount_price, discount_until, created_by_user_id,
        )

    def delete_menu_item(self, item_id: int) -> bool:
        return self._menu.delete_menu_item(item_id)

    def update_item_image(self, item_id: int, image_url: str) -> MenuItem:
        return self._menu.update_image_url(item_id, image_url)

    def get_specials(self) -> list[MenuItem]:
        return self._menu.get_specials()


# ---------------------------------------------------------------------------
# PaymentController
# ---------------------------------------------------------------------------

class PaymentController:
    """Handles Stripe Checkout payment flow."""

    def __init__(
        self,
        payment_service: PaymentService,
        order_service: OrderService,
    ) -> None:
        self._payment = payment_service
        self._order = order_service

    @property
    def stripe_configured(self) -> bool:
        return self._payment.is_configured

    def create_stripe_session(self, base_url: str) -> str:
        """Create a Stripe Checkout Session and return the redirect URL.

        base_url: e.g. 'http://localhost:8080'
        Raises ValueError if Stripe is not configured or the API call fails.
        """
        cart = _get_cart()
        if cart.is_empty:
            raise ValueError("Warenkorb ist leer.")
        return self._payment.create_checkout_session(
            cart=cart,
            success_url=f"{base_url}/payment/success",
            cancel_url=f"{base_url}/payment/cancel",
        )

    def complete_order(self) -> Optional[Order]:
        """Create the order from the saved pending data and clear the cart.

        Called when Stripe redirects back to /payment/success.
        Returns the created Order on success, None if no pending data exists.
        """
        pending = app.storage.user.get("pending_order")
        if not pending:
            return None

        cart = _get_cart()
        if cart.is_empty:
            return None

        order = self._order.create_order(
            user_id=pending["user_id"],
            cart=cart,
            order_type=pending["order_type"],
            delivery_address_id=pending.get("delivery_address_id"),
            pickup_time=pending.get("pickup_time") or None,
            notes=pending.get("notes"),
        )
        _save_cart(cart)
        app.storage.user.pop("pending_order", None)
        app.storage.user["last_order_id"] = order.id
        return order

    def save_pending_order(self, **kwargs) -> None:
        """Save order intent before redirecting to Stripe."""
        app.storage.user["pending_order"] = kwargs
