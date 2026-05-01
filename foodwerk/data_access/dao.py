"""DAO classes — all database access is isolated here.

Services must never import Session or run queries directly.
Each DAO owns the SQL for one entity family.

Design pattern: DAO (Data Access Object) — wraps all persistence
operations behind class-based interfaces so services stay pure.
"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from sqlalchemy.engine import Engine
from sqlmodel import Session, select

from ..domain.models import (
    Address, Category, DeliveryInfo, Extra, Ingredient,
    MenuItem, MenuItemIngredient, Order, OrderItem, OrderItemExtra,
    Review, Special, User,
)


# ---------------------------------------------------------------------------
# Base DAO
# ---------------------------------------------------------------------------

class BaseDAO:
    """Holds the SQLAlchemy engine and provides session access."""

    def __init__(self, engine: Engine) -> None:
        self.engine = engine

    def session(self) -> Session:
        return Session(self.engine)


# ---------------------------------------------------------------------------
# UserDAO
# ---------------------------------------------------------------------------

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

    def get_all(self) -> List[User]:
        with self.session() as session:
            return list(session.exec(select(User)).all())


# ---------------------------------------------------------------------------
# CategoryDAO
# ---------------------------------------------------------------------------

class CategoryDAO(BaseDAO):

    def get_all(self) -> List[Category]:
        with self.session() as session:
            return list(session.exec(select(Category).order_by(Category.name)).all())

    def get_by_id(self, category_id: int) -> Optional[Category]:
        with self.session() as session:
            return session.get(Category, category_id)


# ---------------------------------------------------------------------------
# MenuItemDAO
# ---------------------------------------------------------------------------

class MenuItemDAO(BaseDAO):

    def get_by_id(self, item_id: int) -> Optional[MenuItem]:
        with self.session() as session:
            item = session.get(MenuItem, item_id)
            if item:
                _ = item.category
                _ = [mii.ingredient for mii in item.ingredients]
                _ = item.specials
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

    def set_availability(self, item_id: int, is_available: bool) -> Optional[MenuItem]:
        with self.session() as session:
            item = session.get(MenuItem, item_id)
            if not item:
                return None
            item.is_available = is_available
            session.commit()
            session.refresh(item)
            return item

    def create(self, item: MenuItem) -> MenuItem:
        with self.session() as session:
            session.add(item)
            session.commit()
            session.refresh(item)
            return item


# ---------------------------------------------------------------------------
# ExtraDAO
# ---------------------------------------------------------------------------

class ExtraDAO(BaseDAO):

    def get_all(self, available_only: bool = True) -> List[Extra]:
        with self.session() as session:
            stmt = select(Extra)
            if available_only:
                stmt = stmt.where(Extra.is_available == True)
            return list(session.exec(stmt).all())

    def get_by_category(self, category_id: int, available_only: bool = True) -> List[Extra]:
        with self.session() as session:
            stmt = select(Extra).where(Extra.category_id == category_id)
            if available_only:
                stmt = stmt.where(Extra.is_available == True)
            return list(session.exec(stmt).all())


# ---------------------------------------------------------------------------
# SpecialDAO
# ---------------------------------------------------------------------------

class SpecialDAO(BaseDAO):

    def get_by_id(self, special_id: int) -> Optional[Special]:
        with self.session() as session:
            special = session.get(Special, special_id)
            if special:
                _ = special.menu_item
            return special

    def get_all(self) -> List[Special]:
        with self.session() as session:
            specials = list(session.exec(select(Special).order_by(Special.end_date.desc())).all())
            for s in specials:
                _ = s.menu_item
            return specials

    def get_active(self) -> List[Special]:
        now = datetime.utcnow()
        with self.session() as session:
            stmt = (
                select(Special)
                .where(Special.is_active == True)
                .where(Special.start_date <= now)
                .where(Special.end_date >= now)
            )
            specials = list(session.exec(stmt).all())
            for s in specials:
                _ = s.menu_item
                if s.menu_item:
                    _ = [mii.ingredient for mii in s.menu_item.ingredients]
            return specials

    def get_active_for_item(self, menu_item_id: int) -> Optional[Special]:
        now = datetime.utcnow()
        with self.session() as session:
            return session.exec(
                select(Special)
                .where(Special.menu_item_id == menu_item_id)
                .where(Special.is_active == True)
                .where(Special.start_date <= now)
                .where(Special.end_date >= now)
            ).first()

    def create(self, special: Special) -> Special:
        with self.session() as session:
            session.add(special)
            session.commit()
            session.refresh(special)
            _ = session.get(MenuItem, special.menu_item_id)
            return special

    def update(self, special_id: int, **kwargs) -> Optional[Special]:
        with self.session() as session:
            special = session.get(Special, special_id)
            if not special:
                return None
            for key, value in kwargs.items():
                if hasattr(special, key):
                    setattr(special, key, value)
            session.commit()
            session.refresh(special)
            return special


# ---------------------------------------------------------------------------
# OrderDAO
# ---------------------------------------------------------------------------

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
                for oi in order.order_items:
                    _ = oi.menu_item
                    _ = oi.extras
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


# ---------------------------------------------------------------------------
# AddressDAO
# ---------------------------------------------------------------------------

class AddressDAO(BaseDAO):

    def create(self, address: Address) -> Address:
        with self.session() as session:
            session.add(address)
            session.commit()
            session.refresh(address)
            return address

    def get_by_user(self, user_id: int) -> List[Address]:
        with self.session() as session:
            return list(session.exec(select(Address).where(Address.user_id == user_id)).all())


# ---------------------------------------------------------------------------
# ReviewDAO
# ---------------------------------------------------------------------------

class ReviewDAO(BaseDAO):

    def get_by_id(self, review_id: int) -> Optional[Review]:
        with self.session() as session:
            return session.get(Review, review_id)

    def get_all(self) -> List[Review]:
        with self.session() as session:
            return list(session.exec(select(Review).order_by(Review.created_at.desc())).all())

    def get_by_menu_item(self, menu_item_id: int) -> List[Review]:
        with self.session() as session:
            return list(
                session.exec(
                    select(Review)
                    .where(Review.menu_item_id == menu_item_id)
                    .order_by(Review.created_at.desc())
                ).all()
            )

    def create(self, review: Review) -> Review:
        with self.session() as session:
            session.add(review)
            session.commit()
            session.refresh(review)
            return review
