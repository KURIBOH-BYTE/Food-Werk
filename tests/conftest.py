"""Shared test fixtures for FoodWerk tests.

Uses SQLModel with an in-memory SQLite database — no external setup required.
"""

from __future__ import annotations

import bcrypt
import pytest
from sqlmodel import SQLModel, Session, create_engine

from foodwerk.domain.models import (
    Category, Ingredient, MenuItem, MenuItemIngredient, User,
)
from foodwerk.data_access.dao import CategoryDAO, DeliveryAddressDAO, MenuItemDAO, OrderDAO, UserDAO


@pytest.fixture(scope="function")
def engine():
    """In-memory SQLite engine, fresh for every test function."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    SQLModel.metadata.create_all(engine)
    yield engine
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def daos(engine):
    """All DAOs wired to the in-memory engine."""
    return {
        "user": UserDAO(engine),
        "category": CategoryDAO(engine),
        "menu_item": MenuItemDAO(engine),
        "order": OrderDAO(engine),
        "address": DeliveryAddressDAO(engine),
    }


@pytest.fixture
def seeded_engine(engine):
    """Engine pre-populated with demo data for integration tests."""
    with Session(engine) as session:
        # Users
        admin = User(
            first_name="Admin", last_name="Test",
            email="admin@test.ch",
            password_hash=bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode(),
            role="admin",
        )
        customer = User(
            first_name="Roy", last_name="Fluckiger",
            email="roy@test.ch",
            password_hash=bcrypt.hashpw("password".encode(), bcrypt.gensalt()).decode(),
            role="customer",
        )
        session.add_all([admin, customer])
        session.flush()

        # Categories
        burgers = Category(name="Burgers", description="Juicy burgers")
        drinks = Category(name="Drinks", description="Beverages")
        session.add_all([burgers, drinks])
        session.flush()

        # Ingredients
        lettuce = Ingredient(name="Lettuce")
        tomato = Ingredient(name="Tomato")
        session.add_all([lettuce, tomato])
        session.flush()

        # Menu items
        classic = MenuItem(
            category_id=burgers.id, name="Classic Burger",
            description="Beef, lettuce, tomato", price=12.90, is_available=True,
        )
        cheeseburger = MenuItem(
            category_id=burgers.id, name="Cheeseburger",
            description="Double beef with cheddar", price=14.50, is_available=True,
        )
        cola = MenuItem(
            category_id=drinks.id, name="Cola",
            description="0.5l", price=3.90, is_available=True,
        )
        sold_out = MenuItem(
            category_id=burgers.id, name="Sold Out Burger",
            description="Not available", price=15.00, is_available=False,
        )
        session.add_all([classic, cheeseburger, cola, sold_out])
        session.flush()

        for ing in [lettuce, tomato]:
            session.add(MenuItemIngredient(menu_item_id=classic.id, ingredient_id=ing.id))

        session.commit()

    return engine
