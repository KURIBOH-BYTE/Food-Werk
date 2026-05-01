"""Menu service — menu items, categories, extras, specials."""

from __future__ import annotations

from typing import Optional

from .base_service import BaseService
from ..data_access.dao import CategoryDAO, ExtraDAO, MenuItemDAO, SpecialDAO
from ..domain.models import Category, Extra, MenuItem, Special


class MenuService(BaseService):

    def __init__(
        self,
        menu_item_dao: MenuItemDAO,
        category_dao: CategoryDAO,
        extra_dao: ExtraDAO,
        special_dao: SpecialDAO,
    ) -> None:
        self.menu_item_dao = menu_item_dao
        self.category_dao = category_dao
        self.extra_dao = extra_dao
        self.special_dao = special_dao

    def get_by_id(self, entity_id: int) -> Optional[MenuItem]:
        return self.menu_item_dao.get_by_id(entity_id)

    def get_all(self) -> list[MenuItem]:
        return self.menu_item_dao.get_all()

    # ------------------------------------------------------------------

    def get_categories(self) -> list[Category]:
        return self.category_dao.get_all()

    def get_menu_items(self, category_id: Optional[int] = None, available_only: bool = True) -> list[MenuItem]:
        if category_id:
            return self.menu_item_dao.get_by_category(category_id, available_only=available_only)
        return self.menu_item_dao.get_all(available_only=available_only)

    def get_extras(self, category_id: Optional[int] = None, available_only: bool = True) -> list[Extra]:
        if category_id:
            return self.extra_dao.get_by_category(category_id, available_only=available_only)
        return self.extra_dao.get_all(available_only=available_only)

    def set_availability(self, item_id: int, is_available: bool) -> MenuItem:
        item = self.menu_item_dao.set_availability(item_id, is_available)
        if not item:
            raise ValueError("Menu item not found.")
        return item

    def create_menu_item(
        self,
        category_id: int,
        name: str,
        description: Optional[str],
        price: float,
        image_url: Optional[str] = None,
    ) -> MenuItem:
        if price <= 0:
            raise ValueError("Price must be greater than 0.")
        item = MenuItem(
            category_id=category_id,
            name=name,
            description=description,
            price=price,
            image_url=image_url,
            is_available=True,
        )
        return self.menu_item_dao.create(item)

    def get_active_specials(self) -> list[Special]:
        return self.special_dao.get_active()

    def get_effective_price(self, item: MenuItem) -> float:
        """Return the special price if active, otherwise the regular price."""
        special = self.special_dao.get_active_for_item(item.id)
        return special.special_price if special else item.price
