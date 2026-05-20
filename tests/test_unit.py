"""Unit tests for CartService — pure business logic, no database."""

from foodwerk.services.cart_service import CartService


def test_subtotal_empty_cart():
    cart = CartService()
    assert cart.subtotal == 0.0


def test_subtotal_single_item():
    cart = CartService()
    cart.add_item(menu_item_id=1, name="Classic Burger", unit_price=12.90, quantity=1)
    assert cart.subtotal == 12.90


def test_total_equals_subtotal_above_50():
    """No discount applies — total always equals subtotal."""
    cart = CartService()
    cart.add_item(menu_item_id=1, name="Classic Burger", unit_price=30.00, quantity=1)
    cart.add_item(menu_item_id=2, name="Cheeseburger", unit_price=30.00, quantity=1)

    assert cart.subtotal == 60.0
    assert cart.total == 60.0


def test_total_equals_subtotal_exactly_50():
    cart = CartService()
    cart.add_item(menu_item_id=1, name="Classic Burger", unit_price=25.00, quantity=2)

    assert cart.subtotal == 50.0
    assert cart.total == 50.0


def test_total_equals_subtotal_below_50():
    cart = CartService()
    cart.add_item(menu_item_id=1, name="Classic Burger", unit_price=12.90, quantity=1)
    cart.add_item(menu_item_id=2, name="Cola", unit_price=3.90, quantity=1)

    assert cart.subtotal == 16.80
    assert cart.total == 16.80


def test_total_equals_subtotal_multiple_quantities():
    cart = CartService()
    cart.add_item(menu_item_id=1, name="Pizza Margherita", unit_price=14.90, quantity=4)

    assert cart.subtotal == round(14.90 * 4, 2)
    assert cart.total == cart.subtotal
