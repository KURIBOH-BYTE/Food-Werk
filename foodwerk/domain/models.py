"""Domain models (SQLModel = SQLAlchemy + Pydantic combined).

All tables are defined here in one place. SQLModel maps Python classes
directly to database tables without a separate ORM Base class.

Note: from __future__ import annotations is intentionally omitted.
SQLModel's Relationship() resolver needs real type objects at definition
time — lazy string evaluation breaks forward-reference resolution.

Tables:
    User, Category, MenuItem, Ingredient, MenuItemIngredient,
    Extra, Address, Order, OrderItem, OrderItemExtra, DeliveryInfo,
    Special, Review
"""

from datetime import datetime
from typing import List, Optional

from sqlmodel import SQLModel, Field, Relationship


# ---------------------------------------------------------------------------
# User
# ---------------------------------------------------------------------------

class User(SQLModel, table=True):
    __tablename__ = "users"

    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    email: str = Field(max_length=100, index=True)
    password_hash: str = Field(max_length=255)
    phone: Optional[str] = Field(default=None, max_length=20)
    role: str = Field(default="customer", max_length=20)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    orders: List["Order"] = Relationship(back_populates="user")
    addresses: List["Address"] = Relationship(back_populates="user")
    reviews: List["Review"] = Relationship(back_populates="user")
    created_specials: List["Special"] = Relationship(back_populates="created_by_user")


# ---------------------------------------------------------------------------
# Category
# ---------------------------------------------------------------------------

class Category(SQLModel, table=True):
    __tablename__ = "categories"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=50, index=True)
    description: Optional[str] = Field(default=None, max_length=200)

    menu_items: List["MenuItem"] = Relationship(back_populates="category")
    extras: List["Extra"] = Relationship(back_populates="category")


# ---------------------------------------------------------------------------
# Ingredient
# ---------------------------------------------------------------------------

class Ingredient(SQLModel, table=True):
    __tablename__ = "ingredients"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)

    menu_items: List["MenuItemIngredient"] = Relationship(back_populates="ingredient")


class MenuItemIngredient(SQLModel, table=True):
    __tablename__ = "menu_item_ingredients"

    id: Optional[int] = Field(default=None, primary_key=True)
    menu_item_id: int = Field(foreign_key="menu_items.id")
    ingredient_id: int = Field(foreign_key="ingredients.id")

    menu_item: Optional["MenuItem"] = Relationship(back_populates="ingredients")
    ingredient: Optional["Ingredient"] = Relationship(back_populates="menu_items")


# ---------------------------------------------------------------------------
# Extra
# ---------------------------------------------------------------------------

class Extra(SQLModel, table=True):
    __tablename__ = "extras"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=100)
    price: float = Field(gt=0)
    category_id: Optional[int] = Field(default=None, foreign_key="categories.id")
    is_available: bool = Field(default=True)

    category: Optional["Category"] = Relationship(back_populates="extras")
    order_item_extras: List["OrderItemExtra"] = Relationship(back_populates="extra")


# ---------------------------------------------------------------------------
# MenuItem
# ---------------------------------------------------------------------------

class MenuItem(SQLModel, table=True):
    __tablename__ = "menu_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    category_id: int = Field(foreign_key="categories.id")
    name: str = Field(max_length=100, index=True)
    description: Optional[str] = Field(default=None, max_length=500)
    price: float = Field(gt=0)
    image_url: Optional[str] = Field(default=None, max_length=255)
    is_available: bool = Field(default=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    category: Optional["Category"] = Relationship(back_populates="menu_items")
    order_items: List["OrderItem"] = Relationship(back_populates="menu_item")
    specials: List["Special"] = Relationship(back_populates="menu_item")
    reviews: List["Review"] = Relationship(back_populates="menu_item")
    ingredients: List["MenuItemIngredient"] = Relationship(back_populates="menu_item")


# ---------------------------------------------------------------------------
# Address
# ---------------------------------------------------------------------------

class Address(SQLModel, table=True):
    __tablename__ = "addresses"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    street: str = Field(max_length=100)
    house_nr: str = Field(max_length=10)
    city: str = Field(max_length=50)
    postal_code: str = Field(max_length=10)

    user: Optional["User"] = Relationship(back_populates="addresses")
    delivery_infos: List["DeliveryInfo"] = Relationship(back_populates="address")


# ---------------------------------------------------------------------------
# Order
# ---------------------------------------------------------------------------

class Order(SQLModel, table=True):
    __tablename__ = "orders"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    order_type: str = Field(max_length=20)
    status: str = Field(default="pending", max_length=20)
    total_price: float = Field(ge=0)
    pickup_time: Optional[datetime] = Field(default=None)
    notes: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    user: Optional["User"] = Relationship(back_populates="orders")
    order_items: List["OrderItem"] = Relationship(
        back_populates="order",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    delivery_info: Optional["DeliveryInfo"] = Relationship(
        back_populates="order",
        sa_relationship_kwargs={"cascade": "all, delete-orphan", "uselist": False},
    )
    reviews: List["Review"] = Relationship(back_populates="order")


class OrderItem(SQLModel, table=True):
    __tablename__ = "order_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id", index=True)
    menu_item_id: int = Field(foreign_key="menu_items.id")
    quantity: int = Field(ge=1, le=99)
    unit_price: float = Field(gt=0)
    notes: Optional[str] = Field(default=None, max_length=200)

    order: Optional["Order"] = Relationship(back_populates="order_items")
    menu_item: Optional["MenuItem"] = Relationship(back_populates="order_items")
    extras: List["OrderItemExtra"] = Relationship(
        back_populates="order_item",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class OrderItemExtra(SQLModel, table=True):
    __tablename__ = "order_item_extras"

    id: Optional[int] = Field(default=None, primary_key=True)
    order_item_id: int = Field(foreign_key="order_items.id")
    extra_id: int = Field(foreign_key="extras.id")
    quantity: int = Field(default=1, ge=1)
    unit_price: float = Field(gt=0)

    order_item: Optional["OrderItem"] = Relationship(back_populates="extras")
    extra: Optional["Extra"] = Relationship(back_populates="order_item_extras")


class DeliveryInfo(SQLModel, table=True):
    __tablename__ = "delivery_infos"

    id: Optional[int] = Field(default=None, primary_key=True)
    order_id: int = Field(foreign_key="orders.id")
    address_id: int = Field(foreign_key="addresses.id")

    order: Optional["Order"] = Relationship(back_populates="delivery_info")
    address: Optional["Address"] = Relationship(back_populates="delivery_infos")


# ---------------------------------------------------------------------------
# Special
# ---------------------------------------------------------------------------

class Special(SQLModel, table=True):
    __tablename__ = "specials"

    id: Optional[int] = Field(default=None, primary_key=True)
    menu_item_id: int = Field(foreign_key="menu_items.id")
    created_by: int = Field(foreign_key="users.id")
    special_price: float = Field(gt=0)
    start_date: datetime
    end_date: datetime
    is_active: bool = Field(default=True)
    description: Optional[str] = Field(default=None, max_length=500)

    menu_item: Optional["MenuItem"] = Relationship(back_populates="specials")
    created_by_user: Optional["User"] = Relationship(back_populates="created_specials")


# ---------------------------------------------------------------------------
# Review
# ---------------------------------------------------------------------------

class Review(SQLModel, table=True):
    __tablename__ = "reviews"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id")
    menu_item_id: int = Field(foreign_key="menu_items.id")
    order_id: int = Field(foreign_key="orders.id")
    rating: int = Field(ge=1, le=5)
    comment: Optional[str] = Field(default=None, max_length=1000)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    user: Optional["User"] = Relationship(back_populates="reviews")
    menu_item: Optional["MenuItem"] = Relationship(back_populates="reviews")
    order: Optional["Order"] = Relationship(back_populates="reviews")
