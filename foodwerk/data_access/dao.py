from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy.engine import Engine
from sqlalchemy import or_
from sqlmodel import Session, select

from ..domain.models import (
    Category, DeliveryAddress, MenuItem, MenuItemIngredient,
    Order, OrderItem, User,
)


class BaseDAO:
    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def session(self) -> Session:
        return Session(self.engine)


class UserDAO(BaseDAO):

    def get_by_id(self, user_id: int) -> Optional[User]:
        with self.session() as session:
            return session.get(User, user_id)

    def get_by_email(self, email: str) -> Optional[User]:
        with self.session() as session:
            return session.exec(select(User).where(User.email == email)).first()

    def create(self, user: User) -> User:
        with self.session() as session:
            session.add(user)
            session.commit()
            session.refresh(user)
            return user

    def update(self, user_id: int, **kwargs) -> Optional[User]:
        with self.session() as session:
            user = session.get(User, user_id)
            if not user:
                return None
            for key, value in kwargs.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            session.commit()
            session.refresh(user)
            return user

    def get_all(self) -> List[User]:
        with self.session() as session:
            return list(session.exec(select(User)).all())


class DeliveryAddressDAO(BaseDAO):

    def get_by_user(self, user_id: int) -> List[DeliveryAddress]:
        with self.session() as session:
            return list(session.exec(
                select(DeliveryAddress).where(DeliveryAddress.user_id == user_id)
            ).all())

    def get_by_id(self, address_id: int) -> Optional[DeliveryAddress]:
        with self.session() as session:
            return session.get(DeliveryAddress, address_id)

    def create(self, address: DeliveryAddress) -> DeliveryAddress:
        with self.session() as session:
            session.add(address)
            session.commit()
            session.refresh(address)
            return address

    def delete(self, address_id: int, user_id: int) -> bool:
        with self.session() as session:
            address = session.get(DeliveryAddress, address_id)
            if not address or address.user_id != user_id:
                return False
            session.delete(address)
            session.commit()
            return True


class CategoryDAO(BaseDAO):

    def get_all(self) -> List[Category]:
        with self.session() as session:
            return list(session.exec(select(Category).order_by(Category.name)).all())

    def get_by_id(self, category_id: int) -> Optional[Category]:
        with self.session() as session:
            return session.get(Category, category_id)


class MenuItemDAO(BaseDAO):

    def get_by_id(self, item_id: int) -> Optional[MenuItem]:
        with self.session() as session:
            item = session.get(MenuItem, item_id)
            if item:
                _ = item.category
                _ = [mii.ingredient for mii in item.ingredients]
            return item

    def get_all(self, available_only: bool = False) -> List[MenuItem]:
        with self.session() as session:
            stmt = select(MenuItem)
            if available_only:
                stmt = stmt.where(MenuItem.is_available == True)
            items = list(session.exec(stmt).all())
            for item in items:
                _ = item.category
                _ = [mii.ingredient for mii in item.ingredients]
            return items

    def get_by_category(self, category_id: int, available_only: bool = True) -> List[MenuItem]:
        with self.session() as session:
            stmt = select(MenuItem).where(MenuItem.category_id == category_id)
            if available_only:
                stmt = stmt.where(MenuItem.is_available == True)
            items = list(session.exec(stmt).all())
            for item in items:
                _ = [mii.ingredient for mii in item.ingredients]
            return items

    def get_specials(self) -> List[MenuItem]:
        with self.session() as session:
            stmt = select(MenuItem).where(
                MenuItem.is_special == True,
                MenuItem.is_available == True,
            )
            items = list(session.exec(stmt).all())
            for item in items:
                _ = item.category
                _ = [mii.ingredient for mii in item.ingredients]
            return items

    def set_availability(self, item_id: int, is_available: bool) -> Optional[MenuItem]:
        with self.session() as session:
            item = session.get(MenuItem, item_id)
            if not item:
                return None
            item.is_available = is_available
            session.commit()
            session.refresh(item)
            return item

    def set_special(self, item_id: int, is_special: bool) -> Optional[MenuItem]:
        with self.session() as session:
            item = session.get(MenuItem, item_id)
            if not item:
                return None
            item.is_special = is_special
            session.commit()
            session.refresh(item)
            return item

    def set_discount(self, item_id: int, discount_price: Optional[float], discount_until: Optional[datetime]) -> Optional[MenuItem]:
        with self.session() as session:
            item = session.get(MenuItem, item_id)
            if not item:
                return None
            item.discount_price = discount_price
            item.discount_until = discount_until
            session.commit()
            session.refresh(item)
            return item

    def update_image_url(self, item_id: int, image_url: str) -> Optional[MenuItem]:
        with self.session() as session:
            item = session.get(MenuItem, item_id)
            if not item:
                return None
            item.image_url = image_url
            session.commit()
            session.refresh(item)
            return item

    def create(self, item: MenuItem) -> MenuItem:
        with self.session() as session:
            session.add(item)
            session.commit()
            session.refresh(item)
            return item


class OrderDAO(BaseDAO):

    def create(self, order: Order) -> Order:
        with self.session() as session:
            session.add(order)
            session.commit()
            session.refresh(order)
            return order

    def get_by_id(self, order_id: int) -> Optional[Order]:
        with self.session() as session:
            order = session.get(Order, order_id)
            if order:
                _ = order.user
                _ = order.delivery_address
                for oi in order.order_items:
                    _ = oi.menu_item
            return order

    def get_by_user(self, user_id: int) -> List[Order]:
        with self.session() as session:
            orders = list(
                session.exec(
                    select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc())
                ).all()
            )
            for o in orders:
                for oi in o.order_items:
                    _ = oi.menu_item
            return orders

    def get_all(self, status: Optional[str] = None) -> List[Order]:
        with self.session() as session:
            stmt = select(Order).order_by(Order.created_at.desc())
            if status:
                stmt = stmt.where(Order.status == status)
            orders = list(session.exec(stmt).all())
            for o in orders:
                _ = o.user
                for oi in o.order_items:
                    _ = oi.menu_item
            return orders

    def update_status(self, order_id: int, new_status: str) -> Optional[Order]:
        with self.session() as session:
            order = session.get(Order, order_id)
            if not order:
                return None
            order.status = new_status
            session.commit()
            session.refresh(order)
            return order
