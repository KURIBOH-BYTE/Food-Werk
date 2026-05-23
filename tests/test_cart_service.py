from foodwerk.services.cart_service import CartService


class TestCartService:
    def test_add_item(self):
        cart = CartService()
        cart.add_item(menu_item_id=1, name="Burger", unit_price=12.90)
        assert cart.item_count == 1

    def test_remove_item(self):
        cart = CartService()
        cart.add_item(menu_item_id=1, name="Burger", unit_price=12.90)
        cart.remove_item(0)
        assert cart.is_empty

    def test_total(self):
        cart = CartService()
        cart.add_item(menu_item_id=1, name="Burger", unit_price=12.90)
        cart.add_item(menu_item_id=2, name="Cola", unit_price=3.90)
        assert cart.total == 16.80
