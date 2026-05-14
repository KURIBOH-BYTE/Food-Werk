from __future__ import annotations

import bcrypt
from datetime import datetime, timedelta
from sqlmodel import Session

from ..domain.models import Category, Ingredient, MenuItem, MenuItemIngredient, User


class FoodWerkSeeder:

    def seed(self, session: Session) -> None:
        self._seed_users(session)
        session.flush()
        categories = self._seed_categories(session)
        session.flush()
        ingredients = self._seed_ingredients(session)
        session.flush()
        self._seed_menu_items(session, categories, ingredients)
        print("FoodWerk: Demo-Daten wurden geladen!")

    def _seed_users(self, session: Session) -> None:
        session.add_all([
            User(
                first_name="Admin", last_name="FoodWerk",
                email="admin@foodwerk.ch",
                password_hash=bcrypt.hashpw("admin123".encode(), bcrypt.gensalt()).decode(),
                phone="+41 79 123 45 67",
                role="admin",
            ),
            User(
                first_name="Max", last_name="Muster",
                email="max@foodwerk.ch",
                password_hash=bcrypt.hashpw("employee123".encode(), bcrypt.gensalt()).decode(),
                phone="+41 79 765 43 21",
                role="employee",
            ),
        ])

    def _seed_categories(self, session: Session) -> dict[str, Category]:
        cats = {
            "burgers":  Category(name="Burgers",  description="Juicy burgers, freshly prepared"),
            "pizza":    Category(name="Pizza",     description="Crispy pizzas fresh from the oven"),
            "sides":    Category(name="Sides",     description="Side dishes and snacks"),
            "drinks":   Category(name="Drinks",    description="Refreshing beverages"),
            "desserts": Category(name="Desserts",  description="Sweet temptations"),
            "specials": Category(name="Specials",  description="Limited time offers"),
        }
        session.add_all(cats.values())
        return cats

    def _seed_ingredients(self, session: Session) -> dict[str, Ingredient]:
        names = [
            "Lettuce", "Tomato", "Onions", "Pickle", "Cheddar",
            "Bacon", "Jalapeños", "Beef", "Chicken Fillet", "Veggie Patty",
            "Ketchup", "Mayonnaise", "Mustard", "BBQ Sauce",
            "Mozzarella", "Pepperoni", "Mushrooms", "Bell Pepper", "Olives",
            "Tomato Sauce", "Oregano",
        ]
        ingredients: dict[str, Ingredient] = {}
        for name in names:
            ing = Ingredient(name=name)
            session.add(ing)
            ingredients[name] = ing
        return ingredients

    def _seed_menu_items(
        self,
        session: Session,
        cats: dict[str, Category],
        ings: dict[str, Ingredient],
    ) -> None:
        now = datetime.utcnow()

        burgers_list = [
            (MenuItem(
                category_id=cats["burgers"].id, name="Classic Burger",
                description="Beef, lettuce, tomato, onions", price=12.90,
                image_url="/static/images/classic_burger.png",
            ), ["Beef", "Lettuce", "Tomato", "Onions", "Pickle", "Ketchup", "Mayonnaise"]),
            (MenuItem(
                category_id=cats["burgers"].id, name="Cheeseburger",
                description="Double beef with melted cheddar", price=14.50,
                image_url="/static/images/cheeseburger.png",
            ), ["Beef", "Cheddar", "Lettuce", "Tomato", "Onions", "Pickle", "Ketchup", "Mustard"]),
            (MenuItem(
                category_id=cats["burgers"].id, name="Chicken Burger",
                description="Crispy chicken fillet with lettuce", price=13.90,
                image_url="/static/images/chicken_burger.png",
            ), ["Chicken Fillet", "Lettuce", "Tomato", "Mayonnaise"]),
            (MenuItem(
                category_id=cats["burgers"].id, name="Veggie Burger",
                description="Homemade veggie patty", price=13.50,
                image_url="/static/images/veggie_burger.png",
            ), ["Veggie Patty", "Lettuce", "Tomato", "Onions", "Pickle", "Ketchup"]),
        ]
        for item, ing_names in burgers_list:
            session.add(item)
            session.flush()
            for name in ing_names:
                session.add(MenuItemIngredient(menu_item_id=item.id, ingredient_id=ings[name].id))

        pizzas_list = [
            (MenuItem(
                category_id=cats["pizza"].id, name="Pizza Margherita",
                description="Tomato sauce, mozzarella, oregano", price=14.90,
                image_url="/static/images/pizza_margherita.png",
            ), ["Tomato Sauce", "Mozzarella", "Oregano"]),
            (MenuItem(
                category_id=cats["pizza"].id, name="Pizza Pepperoni",
                description="Tomato sauce, mozzarella, pepperoni", price=17.90,
                image_url="/static/images/pizza.png",
            ), ["Tomato Sauce", "Mozzarella", "Pepperoni", "Oregano"]),
            (MenuItem(
                category_id=cats["pizza"].id, name="Pizza Vegetariana",
                description="Tomato sauce, mozzarella, mushrooms, bell pepper, olives", price=16.90,
                image_url="/static/images/pizza_vegi.png",
            ), ["Tomato Sauce", "Mozzarella", "Mushrooms", "Bell Pepper", "Olives"]),
        ]
        for item, ing_names in pizzas_list:
            session.add(item)
            session.flush()
            for name in ing_names:
                session.add(MenuItemIngredient(menu_item_id=item.id, ingredient_id=ings[name].id))

        sides = [
            MenuItem(category_id=cats["sides"].id, name="French Fries", description="Crispy and golden", price=5.50, image_url="/static/images/fries.png"),
            MenuItem(category_id=cats["sides"].id, name="Onion Rings", description="Breaded onion rings", price=6.50, image_url="/static/images/onion_rings.png"),
            MenuItem(category_id=cats["sides"].id, name="Chicken Nuggets", description="6 pieces, crispy", price=7.90, image_url="/static/images/nuggets.png"),
        ]
        drinks = [
            MenuItem(category_id=cats["drinks"].id, name="Cola", description="0.5l", price=3.90, image_url="/static/images/cola.png"),
            MenuItem(category_id=cats["drinks"].id, name="Iced Tea", description="Peach, 0.5l", price=3.90, image_url="/static/images/eistee.png"),
            MenuItem(category_id=cats["drinks"].id, name="Water", description="Still or sparkling, 0.5l", price=2.90, image_url="/static/images/wasser.png"),
            MenuItem(category_id=cats["drinks"].id, name="Milkshake", description="Vanilla, chocolate, or strawberry", price=6.90, image_url="/static/images/milkshake.png"),
        ]
        desserts = [
            MenuItem(category_id=cats["desserts"].id, name="Brownie", description="Warm chocolate brownie", price=5.90, image_url="/static/images/Brownie.png"),
            MenuItem(category_id=cats["desserts"].id, name="Cheesecake", description="Creamy New York style", price=6.50, image_url="/static/images/cheesecake.png"),
        ]
        session.add_all(sides + drinks + desserts)
