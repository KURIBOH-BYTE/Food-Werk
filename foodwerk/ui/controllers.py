"""UI controllers — coordinate services and hold cart state.

Design pattern: MVC Controller layer (same as reference project).
Controllers sit between the UI layer and the service layer.
Pages never call DAOs or create sessions directly.

Controllers are instantiated once in application.py and shared across
all page requests via the Pages class.
"""

from __future__ import annotations

from typing import Optional

from nicegui import app

from ..domain.models import MenuItem, Order, Special, User
from ..services.auth_service import AuthService
from ..services.cart_service import CartService
from ..services.menu_service import MenuService
from ..services.order_service import OrderService
from ..services.payment_service import PaymentService
from ..services.review_service import ReviewService
from ..services.special_service import SpecialService


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

    def get_active_specials(self):
        return self._menu.get_active_specials()

    def get_effective_price(self, item: MenuItem) -> float:
        return self._menu.get_effective_price(item)

    # Cart
    def get_cart(self) -> CartService:
        return _get_cart()

    def add_to_cart(
        self,
        menu_item_id: int,
        name: str,
        unit_price: float,
        quantity: int = 1,
        extras: list[dict] | None = None,
        notes: str | None = None,
    ) -> None:
        cart = _get_cart()
        cart.add_item(menu_item_id, name, unit_price, quantity, extras, notes)
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
        street: str | None = None,
        house_nr: str | None = None,
        city: str | None = None,
        postal_code: str | None = None,
        pickup_time=None,
        notes: str | None = None,
    ) -> Order:
        cart = _get_cart()
        order = self._order.create_order(
            user_id=user_id,
            cart=cart,
            order_type=order_type,
            street=street,
            house_nr=house_nr,
            city=city,
            postal_code=postal_code,
            pickup_time=pickup_time,
            notes=notes,
        )
        _save_cart(cart)  # cart was cleared in create_order
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
        special_service: SpecialService,
    ) -> None:
        self._menu = menu_service
        self._order = order_service
        self._special = special_service

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

    def create_menu_item(self, category_id: int, name: str, description, price: float, image_url=None) -> MenuItem:
        return self._menu.create_menu_item(category_id, name, description, price, image_url)

    def get_all_specials(self) -> list[Special]:
        return self._special.get_all()

    def create_special(self, menu_item_id, created_by, special_price, start_date, end_date, description=None) -> Special:
        return self._special.create_special(menu_item_id, created_by, special_price, start_date, end_date, description)

    def toggle_special(self, special_id: int, is_active: bool) -> Special:
        return self._special.update_special(special_id, is_active=is_active)


# ---------------------------------------------------------------------------
# PaymentController
# ---------------------------------------------------------------------------

class PaymentController:
    """Handles internal card payment flow (test cards, no Stripe API)."""

    def __init__(
        self,
        payment_service: PaymentService,
        order_service: OrderService,
    ) -> None:
        self._payment = payment_service
        self._order = order_service

    def validate_card(
        self,
        card_number: str,
        expiry: str,
        cvv: str,
        name: str,
    ) -> tuple[bool, str]:
        """Validate card fields. Returns (success, error_message)."""
        return self._payment.validate_card(card_number, expiry, cvv, name)

    def complete_order(self) -> Optional[Order]:
        """Create the order from the saved pending data and clear the cart.

        Returns the created Order on success, None if no pending order exists.
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
            street=pending.get("street"),
            house_nr=pending.get("house_nr"),
            city=pending.get("city"),
            postal_code=pending.get("postal_code"),
            pickup_time=pending.get("pickup_time"),
            notes=pending.get("notes"),
        )
        _save_cart(cart)
        app.storage.user.pop("pending_order", None)
        app.storage.user["last_order_id"] = order.id
        return order

    def save_pending_order(self, **kwargs) -> None:
        """Save order intent before navigating to the payment page."""
        app.storage.user["pending_order"] = kwargs

    def get_test_cards(self) -> list[dict]:
        """Return test card data for display in the payment UI."""
        return self._payment.get_test_cards()
