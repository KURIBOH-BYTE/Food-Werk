from foodwerk.data_access.dao import CategoryDAO, MenuItemDAO
from foodwerk.services.menu_service import MenuService


def _make_service(engine) -> MenuService:
    return MenuService(
        menu_item_dao=MenuItemDAO(engine),
        category_dao=CategoryDAO(engine),
    )


class TestMenuService:
    def test_get_menu_items_available_only(self, seeded_engine):
        svc = _make_service(seeded_engine)
        items = svc.get_menu_items(available_only=True)
        assert all(i.is_available for i in items)
        assert not any(i.name == "Sold Out Burger" for i in items)

    def test_get_menu_items_by_category(self, seeded_engine):
        svc = _make_service(seeded_engine)
        cats = svc.get_categories()
        burgers_cat = next(c for c in cats if c.name == "Burgers")
        items = svc.get_menu_items(category_id=burgers_cat.id, available_only=True)
        assert len(items) >= 1
        assert all(i.category_id == burgers_cat.id for i in items)
