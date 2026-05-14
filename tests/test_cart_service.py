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

    def test_update_quantity(self):
        cart = CartService()
        cart.add_item(menu_item_id=1, name="Burger", unit_price=12.90)
        cart.update_quantity(0, 5)
        assert cart.items[0].quantity == 5

    def test_total(self):
        cart = CartService()
        cart.add_item(menu_item_id=1, name="Burger", unit_price=12.90)
        cart.add_item(menu_item_id=2, name="Cola", unit_price=3.90)
        assert cart.total == 16.80

    def test_serialization_roundtrip(self):
        cart = CartService()
        cart.add_item(menu_item_id=1, name="Burger", unit_price=12.90, quantity=2, notes="No onions")
        cart.add_item(menu_item_id=2, name="Cola", unit_price=3.90)
        restored = CartService.from_dict_list(cart.to_dict_list())
        assert restored.item_count == cart.item_count
        assert restored.total == cart.total
        assert len(restored.items) == 2
