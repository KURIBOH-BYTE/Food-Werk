"""Integration tests — full checkout flow wiring services together."""

from foodwerk.data_access.dao import CategoryDAO, MenuItemDAO, OrderDAO, UserDAO  # noqa: F401
from foodwerk.services.cart_service import CartService
from foodwerk.services.menu_service import MenuService
from foodwerk.services.order_service import OrderService


def _make_services(engine):
    menu_service = MenuService(MenuItemDAO(engine), CategoryDAO(engine))
    order_service = OrderService(OrderDAO(engine))
    return menu_service, order_service


def _get_user_id(engine) -> int:
    return UserDAO(engine).get_all()[0].id


def test_checkout_single_item_creates_order(seeded_engine):
    menu_service, order_service = _make_services(seeded_engine)
    user_id = _get_user_id(seeded_engine)

    items = menu_service.get_menu_items()
    item = next(i for i in items if i.name == "Classic Burger")

    cart = CartService()
    cart.add_item(item.id, item.name, item.price, quantity=1)

    order = order_service.create_order(user_id=user_id, cart=cart, order_type="pickup")
    loaded = OrderDAO(seeded_engine).get_by_id(order.id)

    assert loaded.id is not None
    assert loaded.total_price == item.price
    assert len(loaded.order_items) == 1


def test_checkout_multiple_items_total_equals_subtotal(seeded_engine):
    """Total is always the sum of item prices — no discount applied."""
    menu_service, order_service = _make_services(seeded_engine)
    user_id = _get_user_id(seeded_engine)

    items = menu_service.get_menu_items()
    burger = next(i for i in items if i.name == "Classic Burger")   # 12.90
    cheese = next(i for i in items if i.name == "Cheeseburger")     # 14.50

    cart = CartService()
    cart.add_item(burger.id, burger.name, burger.price, quantity=3)  # 3 x 12.90 = 38.70
    cart.add_item(cheese.id, cheese.name, cheese.price, quantity=1)  # 1 x 14.50 = 14.50
    # subtotal = 53.20

    expected_subtotal = round(3 * 12.90 + 14.50, 2)
    assert cart.subtotal == expected_subtotal
    assert cart.total == expected_subtotal  # no discount

    order = order_service.create_order(user_id=user_id, cart=cart, order_type="pickup")

    assert order.id is not None
    assert order.total_price == expected_subtotal


def test_checkout_total_matches_cart(seeded_engine):
    """Order total always matches the cart total exactly."""
    menu_service, order_service = _make_services(seeded_engine)
    user_id = _get_user_id(seeded_engine)

    items = menu_service.get_menu_items()
    item = items[0]
    cart = CartService()
    cart.add_item(item.id, item.name, 25.00, quantity=2)

    assert cart.subtotal == 50.0
    assert cart.total == 50.0

    order = order_service.create_order(user_id=user_id, cart=cart, order_type="pickup")

    assert order.total_price == 50.0
