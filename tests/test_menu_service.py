from foodwerk.data_access.dao import CategoryDAO, ExtraDAO, MenuItemDAO, SpecialDAO
from foodwerk.services.menu_service import MenuService


def _make_service(engine) -> MenuService:
    return MenuService(
        menu_item_dao=MenuItemDAO(engine),
        category_dao=CategoryDAO(engine),
        extra_dao=ExtraDAO(engine),
        special_dao=SpecialDAO(engine),
    )


class TestMenuService:
    def test_get_categories(self, seeded_engine):
        svc = _make_service(seeded_engine)
        cats = svc.get_categories()
        assert len(cats) >= 2
        assert any(c.name == "Burgers" for c in cats)

    def test_get_menu_items_available_only(self, seeded_engine):
        svc = _make_service(seeded_engine)
        items = svc.get_menu_items(available_only=True)
        assert all(i.is_available for i in items)
        assert not any(i.name == "Sold Out Burger" for i in items)
