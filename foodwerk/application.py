"""Application composition root.

Design pattern: same as Pizzeria Reference Project's PizzaApplication.
FoodWerkApplication wires all DAOs, services, controllers, and pages
in one place. The rest of the code knows nothing about how objects
are constructed.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from nicegui import ui, app as nicegui_app

from .data_access.dao import (
    AddressDAO, CategoryDAO, ExtraDAO, MenuItemDAO,
    OrderDAO, ReviewDAO, SpecialDAO, UserDAO,
)
from .data_access.db import Database
from .services.auth_service import AuthService
from .services.cart_service import CartService
from .services.menu_service import MenuService
from .services.order_service import OrderService
from .services.payment_service import PaymentService
from .services.review_service import ReviewService
from .services.special_service import SpecialService
from .ui.controllers import AdminController, AuthController, PaymentController, ShoppingController
from .ui.pages import Pages


class FoodWerkApplication:
    """Composition root — wires the full dependency graph."""

    def __init__(
        self,
        database: Optional[Database] = None,
    ) -> None:
        # --- Database ---
        self.database = database or Database()
        self.database.init_schema_and_seed()
        engine = self.database.engine

        # --- DAOs ---
        user_dao = UserDAO(engine)
        category_dao = CategoryDAO(engine)
        menu_item_dao = MenuItemDAO(engine)
        extra_dao = ExtraDAO(engine)
        order_dao = OrderDAO(engine)
        address_dao = AddressDAO(engine)
        special_dao = SpecialDAO(engine)
        review_dao = ReviewDAO(engine)

        # --- Services ---
        auth_service = AuthService(user_dao=user_dao)
        menu_service = MenuService(
            menu_item_dao=menu_item_dao,
            category_dao=category_dao,
            extra_dao=extra_dao,
            special_dao=special_dao,
        )
        order_service = OrderService(order_dao=order_dao, address_dao=address_dao)
        special_service = SpecialService(special_dao=special_dao)
        self.review_service = ReviewService(review_dao=review_dao)

        payment_service = PaymentService()

        # --- Controllers ---
        auth_ctrl = AuthController(auth_service=auth_service)
        shopping_ctrl = ShoppingController(menu_service=menu_service, order_service=order_service)
        admin_ctrl = AdminController(
            menu_service=menu_service,
            order_service=order_service,
            special_service=special_service,
        )
        payment_ctrl = PaymentController(payment_service=payment_service, order_service=order_service)

        # --- Pages ---
        self._pages = Pages(
            auth=auth_ctrl,
            shopping=shopping_ctrl,
            admin=admin_ctrl,
            payment=payment_ctrl,
        )

    def run(self, host: str = "0.0.0.0", port: int = 8080, reload: bool = False) -> None:
        """Register all routes and start the NiceGUI server."""
        static_dir = Path(__file__).parent.parent / "frontend" / "static"
        nicegui_app.add_static_files("/static", str(static_dir))

        self._pages.register()

        ui.run(
            host=host,
            port=port,
            reload=reload,
            title="FoodWerk — Delivery & Pickup",
            favicon="/static/images/logo.png",
            storage_secret="foodwerk-secret-key-change-in-production",
        )
