from foodwerk.data_access.dao import CategoryDAO, MenuItemDAO, OrderDAO
from foodwerk.services.cart_service import CartService
from foodwerk.services.menu_service import MenuService
from foodwerk.services.order_service import OrderService


def _make_order_service(engine) -> OrderService:
    return OrderService(order_dao=OrderDAO(engine))


def _make_auth_service(engine):
    from foodwerk.data_access.dao import DeliveryAddressDAO, UserDAO
    from foodwerk.services.auth_service import AuthService
    return AuthService(user_dao=UserDAO(engine), address_dao=DeliveryAddressDAO(engine))


def _make_menu_service(engine) -> MenuService:
    return MenuService(
        menu_item_dao=MenuItemDAO(engine),
        category_dao=CategoryDAO(engine),
    )


class TestOrderService:
    def test_create_pickup_order(self, seeded_engine):
        items = _make_menu_service(seeded_engine).get_menu_items(available_only=True)
        cart = CartService()
        cart.add_item(items[0].id, items[0].name, items[0].price)
        order = _make_order_service(seeded_engine).create_order(
            user_id=1, cart=cart, order_type="pickup"
        )
        assert order.id is not None
        assert order.status == "pending"
        assert cart.is_empty

    def test_create_delivery_order(self, seeded_engine):
        auth = _make_auth_service(seeded_engine)
        addr = auth.add_delivery_address(
            user_id=1, street="Bahnhofstrasse", house_nr="1",
            city="Zürich", postal_code="8001",
        )
        items = _make_menu_service(seeded_engine).get_menu_items(available_only=True)
        cart = CartService()
        cart.add_item(items[0].id, items[0].name, items[0].price)
        order = _make_order_service(seeded_engine).create_order(
            user_id=1, cart=cart, order_type="delivery",
            delivery_address_id=addr.id,
        )
        assert order.id is not None
        assert order.order_type == "delivery"
        assert order.delivery_address_id == addr.id

    def test_update_order_status(self, seeded_engine):
        items = _make_menu_service(seeded_engine).get_menu_items(available_only=True)
        cart = CartService()
        cart.add_item(items[0].id, items[0].name, items[0].price)
        order_svc = _make_order_service(seeded_engine)
        order = order_svc.create_order(user_id=1, cart=cart, order_type="pickup")
        updated = order_svc.update_status(order.id, "preparing")
        assert updated.status == "preparing"
