"""Menu service — menu items, categories, specials."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from .base_service import BaseService
from ..data_access.dao import CategoryDAO, MenuItemDAO
from ..domain.models import Category, MenuItem


class MenuService(BaseService):

    def __init__(
        self,
        menu_item_dao: MenuItemDAO,
        category_dao: CategoryDAO,
    ) -> None:
        self.menu_item_dao = menu_item_dao
        self.category_dao = category_dao

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

    def get_specials(self) -> list[MenuItem]:
        return self.menu_item_dao.get_specials()

    def delete_menu_item(self, item_id: int) -> bool:
        return self.menu_item_dao.delete(item_id)

    def update_image_url(self, item_id: int, image_url: str) -> MenuItem:
        item = self.menu_item_dao.update_image_url(item_id, image_url)
        if not item:
            raise ValueError("Menu item not found.")
        return item

    def set_availability(self, item_id: int, is_available: bool) -> MenuItem:
        item = self.menu_item_dao.set_availability(item_id, is_available)
        if not item:
            raise ValueError("Menu item not found.")
        return item

    def set_special(self, item_id: int, is_special: bool) -> MenuItem:
        item = self.menu_item_dao.set_special(item_id, is_special)
        if not item:
            raise ValueError("Menu item not found.")
        return item

    def set_discount(self, item_id: int, discount_price: Optional[float], discount_until: Optional[datetime]) -> MenuItem:
        if discount_price is not None and discount_price <= 0:
            raise ValueError("Discount price must be greater than 0.")
        item = self.menu_item_dao.set_discount(item_id, discount_price, discount_until)
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
        is_special: bool = False,
        discount_price: Optional[float] = None,
        discount_until: Optional[datetime] = None,
        created_by_user_id: Optional[int] = None,
    ) -> MenuItem:
        if price <= 0:
            raise ValueError("Price must be greater than 0.")
        if discount_price is not None and discount_price <= 0:
            raise ValueError("Discount price must be greater than 0.")
        item = MenuItem(
            category_id=category_id,
            name=name,
            description=description,
            price=price,
            image_url=image_url,
            is_available=True,
            is_special=is_special,
            discount_price=discount_price,
            discount_until=discount_until,
            created_by_user_id=created_by_user_id,
        )
        return self.menu_item_dao.create(item)
