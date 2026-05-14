from datetime import datetime
from typing import List, Optional

from sqlmodel import SQLModel, Field, Relationship


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
    delivery_addresses: List["DeliveryAddress"] = Relationship(back_populates="user")
    created_menu_items: List["MenuItem"] = Relationship(back_populates="created_by")


class DeliveryAddress(SQLModel, table=True):
    __tablename__ = "delivery_addresses"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    label: Optional[str] = Field(default=None, max_length=50)
    street: str = Field(max_length=100)
    house_nr: str = Field(max_length=10)
    floor: Optional[str] = Field(default=None, max_length=20)
    city: str = Field(max_length=50)
    postal_code: str = Field(max_length=10)

    user: Optional["User"] = Relationship(back_populates="delivery_addresses")
    orders: List["Order"] = Relationship(back_populates="delivery_address")


class Category(SQLModel, table=True):
    __tablename__ = "categories"

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(max_length=50, index=True)
    description: Optional[str] = Field(default=None, max_length=200)

    menu_items: List["MenuItem"] = Relationship(back_populates="category")


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


class MenuItem(SQLModel, table=True):
    __tablename__ = "menu_items"

    id: Optional[int] = Field(default=None, primary_key=True)
    category_id: int = Field(foreign_key="categories.id")
    created_by_user_id: Optional[int] = Field(default=None, foreign_key="users.id")
    name: str = Field(max_length=100, index=True)
    description: Optional[str] = Field(default=None, max_length=500)
    price: float = Field(gt=0)
    image_url: Optional[str] = Field(default=None, max_length=255)
    is_available: bool = Field(default=True)
    is_special: bool = Field(default=False)
    discount_price: Optional[float] = Field(default=None, ge=0)
    discount_until: Optional[datetime] = Field(default=None)
    available_until: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    category: Optional["Category"] = Relationship(back_populates="menu_items")
    created_by: Optional["User"] = Relationship(back_populates="created_menu_items")
    order_items: List["OrderItem"] = Relationship(back_populates="menu_item")
    ingredients: List["MenuItemIngredient"] = Relationship(back_populates="menu_item")


class Order(SQLModel, table=True):
    __tablename__ = "orders"

    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="users.id", index=True)
    delivery_address_id: Optional[int] = Field(default=None, foreign_key="delivery_addresses.id")
    order_type: str = Field(max_length=20)
    status: str = Field(default="pending", max_length=20)
    total_price: float = Field(ge=0)
    pickup_time: Optional[datetime] = Field(default=None)
    notes: Optional[str] = Field(default=None, max_length=500)
    created_at: datetime = Field(default_factory=datetime.utcnow, index=True)

    user: Optional["User"] = Relationship(back_populates="orders")
    delivery_address: Optional["DeliveryAddress"] = Relationship(back_populates="orders")
    order_items: List["OrderItem"] = Relationship(
        back_populates="order",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


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
