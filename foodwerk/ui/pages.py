"""NiceGUI pages — FoodWerk Dark Edition.

All routes registered by the Pages class.
Design: dark, bold, BigBurger-inspired aesthetic with real product images.
"""

from __future__ import annotations

import re
from datetime import datetime

from nicegui import ui, app
from fastapi.responses import Response

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
_PHONE_RE = re.compile(r"^\+?[\d\s\-\(\)]{7,20}$")
_SPECIAL_RE = re.compile(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?`~]")
_NAME_RE = re.compile(r"^[A-Za-zÀ-öø-ÿ\s\-']+$")

from .controllers import AdminController, AuthController, PaymentController, ReceiptController, ShoppingController
from .components import (
    STATUS_LABELS, cart_item_row, menu_card, navbar, order_card,
)

# Image map: menu item name (lowercase substring) -> static path
IMAGE_MAP = {
    # More specific keys FIRST — otherwise "cheese" would match "Cheesecake"
    "cheesecake":  "/static/images/cheesecake.png",
    "cheeseburger":"/static/images/cheeseburger.png",
    "pizza margherita": "/static/images/pizza_margherita.png",
    "pizza vegi":  "/static/images/pizza_vegi.png",
    "pizza vegetariana": "/static/images/pizza_vegi.png",
    "french fries":"/static/images/fries.png",
    "chicken nugget": "/static/images/nuggets.png",
    "iced tea":    "/static/images/eistee.png",
    "milkshake":   "/static/images/milkshake.png",
    # Shorter keys after
    "classic":     "/static/images/classic_burger.png",
    "chicken":     "/static/images/chicken_burger.png",
    "veggie":      "/static/images/veggie_burger.png",
    "cheese":      "/static/images/cheeseburger.png",
    "pizza":       "/static/images/pizza.png",
    "margher":     "/static/images/pizza_margherita.png",
    "vegi":        "/static/images/pizza_vegi.png",
    "onion":       "/static/images/onion_rings.png",
    "cola":        "/static/images/cola.png",
    "eistee":      "/static/images/eistee.png",
    "wasser":      "/static/images/wasser.png",
    "water":       "/static/images/wasser.png",
    "brownie":     "/static/images/Brownie.png",
    "fries":       "/static/images/fries.png",
    "french":      "/static/images/fries.png",
    "nugget":      "/static/images/nuggets.png",
}


def _active_price(price: float, discount_price, discount_until) -> float:
    """Return the currently active price considering any time-limited discount."""
    if discount_price is not None:
        if discount_until is None or discount_until >= datetime.utcnow():
            return discount_price
    return price


def resolve_image(name: str, fallback: str | None = None) -> str | None:
    """Return the best matching static image path for a menu item name."""
    lower = name.lower()
    for key, path in IMAGE_MAP.items():
        if key in lower:
            return path
    return fallback


class Pages:
    """Registers all NiceGUI routes (UI boundary)."""

    def __init__(
        self,
        auth: AuthController,
        shopping: ShoppingController,
        admin: AdminController,
        payment: PaymentController,
        receipt: ReceiptController | None = None,
    ) -> None:
        self._auth = auth
        self._shopping = shopping
        self._admin = admin
        self._payment = payment
        self._receipt = receipt

    def register(self) -> None:
        """Wire all routes. Called once at startup from application.py."""

        auth = self._auth
        shopping = self._shopping
        admin = self._admin
        payment = self._payment
        receipt = self._receipt

        # ================================================================
        # RECEIPT DOWNLOAD (FastAPI endpoint — returns PDF bytes)
        # ================================================================
        @app.get("/receipt/{order_id}")
        def download_receipt(order_id: int) -> Response:
            if not receipt:
                return Response(content="Receipt service unavailable", status_code=503)
            pdf_bytes = receipt.generate_pdf(order_id)
            if pdf_bytes is None:
                return Response(content="Order not found", status_code=404)
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={"Content-Disposition": f'attachment; filename="receipt_{order_id}.pdf"'},
            )

        # ================================================================
        # HOME
        # ================================================================
        @ui.page("/")
        def home_page() -> None:
            navbar()

            # ---- Hero ----
            ui.html("""
            <div class="w-full min-h-[92vh] flex items-center relative overflow-hidden" style="background:linear-gradient(135deg,#0a0a0a 0%,#1a0800 60%,#2a0f00 100%)">
              <div class="absolute font-display text-[28vw] text-[rgba(255,255,255,0.025)] leading-[1] top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 whitespace-nowrap select-none pointer-events-none">FW</div>
              <div class="px-[60px] relative z-[2] max-w-[680px]">
                <h1 class="font-display text-[clamp(72px,11vw,130px)] leading-[0.88] text-[#F5F0E8] mb-6">YOUR<br><span class="text-[#E63312]">FOOD.</span><br>YOUR CRAFT.</h1>
                <p class="text-[17px] text-[rgba(245,240,232,0.65)] leading-[1.6] mb-10 max-w-[420px]">Handcrafted burgers, crispy sides and frosty drinks – freshly prepared, right to you.</p>
                <div class="flex gap-4 flex-wrap">
                  <a href="/menu" class="bg-[#E63312] text-white font-display text-[16px] tracking-[2px] px-9 py-[14px] no-underline hover:bg-[#c4290e] transition-colors">TO THE MENU</a>
                  <a href="/specials" class="bg-transparent text-[#F5F0E8] font-display text-[16px] tracking-[2px] px-9 py-[14px] no-underline border border-[rgba(245,240,232,0.35)]">SPECIALS</a>
                </div>
              </div>
              <img class="absolute right-[5%] top-1/2 -translate-y-1/2 w-[44vw] max-w-[580px] h-auto object-cover rounded-[4px] shadow-[0_0_120px_rgba(230,51,18,0.18)]" src="/static/images/menu_collage.png" alt="FoodWerk Menu">
            </div>
            """)

            # ---- Ticker ----
            ticker_text = "&nbsp;&nbsp;FOOD WERK &bull; HANDCRAFTED &bull; FRESH &bull; OPEN DAILY &bull; " * 4
            ui.html(f'<div class="w-full bg-[#E63312] py-[13px] overflow-hidden whitespace-nowrap"><span class="fw-ticker-inner">{ticker_text}{ticker_text}</span></div>')

            # ---- Stats ----
            ui.html("""
            <div class="w-full bg-[#E63312] py-14 px-[60px] flex">
              <div class="flex-1 text-center border-r border-[rgba(255,255,255,0.2)] px-4">
                <div class="font-display text-[68px] text-white leading-[1]">14</div>
                <div class="text-[11px] font-bold tracking-[2px] uppercase text-[rgba(255,255,255,0.75)] mt-[6px]">Dishes on Menu</div>
              </div>
              <div class="flex-1 text-center border-r border-[rgba(255,255,255,0.2)] px-4">
                <div class="font-display text-[68px] text-white leading-[1]">100%</div>
                <div class="text-[11px] font-bold tracking-[2px] uppercase text-[rgba(255,255,255,0.75)] mt-[6px]">Fresh Ingredients</div>
              </div>
              <div class="flex-1 text-center border-r border-[rgba(255,255,255,0.2)] px-4">
                <div class="font-display text-[68px] text-white leading-[1]">CHF 15</div>
                <div class="text-[11px] font-bold tracking-[2px] uppercase text-[rgba(255,255,255,0.75)] mt-[6px]">Starting at</div>
              </div>
              <div class="flex-1 text-center px-4">
                <div class="font-display text-[68px] text-white leading-[1]">30'</div>
                <div class="text-[11px] font-bold tracking-[2px] uppercase text-[rgba(255,255,255,0.75)] mt-[6px]">Delivery Time</div>
              </div>
            </div>
            """)

            # ---- Featured menu grid ----
            categories = shopping.get_categories()
            all_items: list[dict] = []
            for cat in categories:
                for item in shopping.get_menu_items(category_id=cat.id, available_only=True):
                    img = resolve_image(item.name, item.image_url)
                    all_items.append({"name": item.name, "price": item.price, "image_url": img})

            featured = all_items[:4]
            if featured:
                ui.html('<div class="bg-[#0e0e0e]"><div class="max-w-[1600px] mx-auto px-[60px] py-20">')
                ui.html('<div class="text-[11px] font-bold tracking-[4px] uppercase text-[#E63312] mb-3">What We Do</div>')
                ui.html('<div class="font-display text-[clamp(32px,4vw,52px)] leading-[0.95] text-[#F5F0E8] mb-4">OUR<br>HITS</div>')

                grid_html = '<div class="grid grid-cols-3 gap-[3px]">'
                for idx, it in enumerate(featured):
                    extra_class = "big" if idx == 0 else ""
                    img_tag = f'<img src="{it["image_url"]}" alt="{it["name"]}" loading="lazy">' if it.get("image_url") else ""
                    badge = '<div class="absolute top-4 left-4 z-[3] bg-[#F5C842] text-[#111] text-[10px] font-bold tracking-[2px] uppercase px-[10px] py-1">Best Seller</div>' if idx == 0 else ""
                    grid_html += f"""
                    <a href="/menu" class="fw-menu-card {extra_class}" style="text-decoration:none">
                      {img_tag}
                      {badge}
                      <div class="relative z-[2]">
                        <div class="font-display text-[28px] text-[#F5F0E8] tracking-[1px]">{it["name"]}</div>
                        <div class="text-[14px] text-[#E63312] font-bold mt-1">CHF {it["price"]:.2f}</div>
                      </div>
                    </a>"""
                grid_html += "</div>"
                ui.html(grid_html)

                ui.html("""
                <div class="text-center mt-12">
                  <a href="/menu" class="bg-[#E63312] text-white font-display text-[16px] tracking-[2px] px-9 py-[14px] no-underline">FULL MENU →</a>
                </div>
                </div></div>
                """)

        # ================================================================
        # LOGIN / REGISTER
        # ================================================================
        @ui.page("/login")
        def login_page() -> None:
            navbar()
            with ui.element("div").classes("min-h-screen pt-16 flex flex-row"):
                # LEFT — Branding panel
                with ui.element("div").classes(
                    "flex-1 min-w-[520px] relative overflow-hidden flex flex-col justify-center p-[100px_80px]"
                ).style(
                    "background:linear-gradient(160deg,#0d0d0d 0%,#1c0a00 40%,#2e1000 70%,#1a0500 100%)"
                ):
                    ui.html("""
                    <div class="absolute inset-0 pointer-events-none overflow-hidden">
                      <div class="absolute -top-20 -right-20 w-[420px] h-[420px] rounded-full" style="background:radial-gradient(circle,rgba(230,51,18,0.18) 0%,transparent 70%)"></div>
                      <div class="absolute -bottom-[60px] -left-[60px] w-[300px] h-[300px] rounded-full" style="background:radial-gradient(circle,rgba(230,51,18,0.10) 0%,transparent 70%)"></div>
                      <div class="absolute font-display text-[32vw] text-[rgba(255,255,255,0.025)] leading-[1] top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 whitespace-nowrap select-none">FW</div>
                    </div>

                    <div class="relative z-[2]">
                      <div class="inline-block bg-[#E63312] text-white font-display text-[11px] tracking-[5px] px-[14px] py-[5px] mb-7">FOODWERK</div>
                      <div class="font-display text-[clamp(80px,8vw,120px)] leading-[0.88] text-[#F5F0E8] mb-8">
                        YOUR<br>ACCOUNT.<br><span class="text-[#E63312]">YOUR</span><br>WORLD.
                      </div>
                      <p class="text-[17px] text-[rgba(245,240,232,0.75)] max-w-[380px] leading-[1.9] mb-12">
                        Log in or create an account — and order right away.
                      </p>
                      <div class="flex gap-0 border-t border-[rgba(255,255,255,0.1)] pt-8">
                        <div class="flex-1 pr-8 border-r border-[rgba(255,255,255,0.1)]">
                          <div class="font-display text-[56px] text-[#E63312] leading-[1]">14</div>
                          <div class="text-[12px] font-bold tracking-[3px] text-[rgba(245,240,232,0.8)] uppercase mt-[6px]">Dishes</div>
                        </div>
                        <div class="flex-1 px-8 border-r border-[rgba(255,255,255,0.1)]">
                          <div class="font-display text-[56px] text-[#E63312] leading-[1]">30'</div>
                          <div class="text-[12px] font-bold tracking-[3px] text-[rgba(245,240,232,0.8)] uppercase mt-[6px]">Delivery</div>
                        </div>
                        <div class="flex-1 pl-8">
                          <div class="font-display text-[56px] text-[#E63312] leading-[1]">100%</div>
                          <div class="text-[12px] font-bold tracking-[3px] text-[rgba(245,240,232,0.8)] uppercase mt-[6px]">Fresh</div>
                        </div>
                      </div>
                    </div>
                    """)

                # RIGHT — Form panel
                with ui.element("div").classes(
                    "w-[520px] flex-shrink-0 flex flex-col justify-center p-[72px_64px] border-l border-[rgba(230,51,18,0.15)]"
                ).style("background:linear-gradient(180deg,#161616 0%,#111111 100%)"):
                    ui.html('<div class="font-display text-[42px] text-[#F5F0E8] tracking-[2px] mb-1">WELCOME</div>')
                    ui.html('<div class="text-[13px] text-[#555] mb-8">Log in or create an account</div>')

                    with ui.tabs().props("color=red indicator-color=red dense") as tabs:
                        login_tab = ui.tab("Login").classes("font-display text-[16px] tracking-[2px] text-[#F5F0E8]")
                        register_tab = ui.tab("Register").classes("font-display text-[16px] tracking-[2px] text-[#F5F0E8]")

                    with ui.tab_panels(tabs, value=login_tab).classes("w-full").style("background:transparent;margin-top:24px"):
                        with ui.tab_panel(login_tab).style("padding:0"):
                            email_in = ui.input(
                                "E-Mail",
                                validation={"Please enter a valid email": lambda v: bool(_EMAIL_RE.match(v.strip())) if v.strip() else True},
                            ).classes("w-full").style("margin-bottom:14px")
                            pw_in = ui.input("Password", password=True, password_toggle_button=True).classes("w-full")

                            def do_login() -> None:
                                user = auth.login(email_in.value, pw_in.value)
                                if user:
                                    auth.store_user(user)
                                    ui.notify(f"Welcome, {user.first_name}!", color="positive")
                                    ui.navigate.to("/")
                                else:
                                    ui.notify("Incorrect email or password.", color="negative")

                            ui.button("Log in →", on_click=do_login).classes("fw-btn fw-btn-primary w-full").style("margin-top:24px;padding:15px")

                        with ui.tab_panel(register_tab).style("padding:0"):
                            with ui.row().classes("w-full gap-[10px]"):
                                fn_in = ui.input(
                                    "First Name",
                                    validation={
                                        "Required": lambda v: bool(v.strip()),
                                        "No special characters allowed": lambda v: bool(_NAME_RE.match(v.strip())) if v.strip() else True,
                                    },
                                ).classes("flex-1")
                                ln_in = ui.input(
                                    "Last Name",
                                    validation={
                                        "Required": lambda v: bool(v.strip()),
                                        "No special characters allowed": lambda v: bool(_NAME_RE.match(v.strip())) if v.strip() else True,
                                    },
                                ).classes("flex-1")
                            em_in = ui.input(
                                "E-Mail",
                                validation={"Please enter a valid email": lambda v: bool(_EMAIL_RE.match(v.strip())) if v.strip() else True},
                            ).classes("w-full").style("margin-top:12px")
                            ph_in = ui.input(
                                "Phone (optional)",
                                validation={"Invalid phone number (e.g. +41 79 123 45 67)": lambda v: bool(_PHONE_RE.match(v.strip())) if v.strip() else True},
                            ).classes("w-full").style("margin-top:12px")
                            pw1_in = ui.input(
                                "Password",
                                password=True,
                                password_toggle_button=True,
                                validation={
                                    "At least 8 characters required": lambda v: len(v) >= 8 if v else True,
                                    "At least one special character required (!@#$%...)": lambda v: bool(_SPECIAL_RE.search(v)) if v else True,
                                },
                            ).classes("w-full").style("margin-top:12px")
                            pw2_in = ui.input(
                                "Confirm Password",
                                password=True,
                                password_toggle_button=True,
                                validation={"Passwords do not match": lambda v: v == pw1_in.value if v else True},
                            ).classes("w-full").style("margin-top:12px")

                            def do_register() -> None:
                                try:
                                    user = auth.register(fn_in.value, ln_in.value, em_in.value, pw1_in.value, ph_in.value or None)
                                    if pw1_in.value != pw2_in.value:
                                        ui.notify("Passwords do not match.", color="negative")
                                        return
                                    auth.store_user(user)
                                    ui.notify(f"Account created! Welcome, {user.first_name}!", color="positive")
                                    ui.navigate.to("/")
                                except ValueError as e:
                                    for msg in str(e).split("\n"):
                                        ui.notify(msg, color="negative")

                            ui.button("Create Account →", on_click=do_register).classes("fw-btn fw-btn-primary w-full").style("margin-top:24px;padding:15px")

        # ================================================================
        # MENU
        # ================================================================
        @ui.page("/menu")
        def menu_page() -> None:
            navbar()
            categories = shopping.get_categories()

            def show_add_dialog(item: dict) -> None:
                with ui.dialog() as dialog, ui.element("div").classes(
                    "bg-[#1a1a1a] border border-[rgba(255,255,255,0.1)] p-8 min-w-[380px]"
                ):
                    ui.html(f'<div class="font-display text-[32px] text-[#F5F0E8] tracking-[1px] mb-1">{item["name"]}</div>')
                    if item.get("is_special"):
                        ui.html('<span class="bg-[#F5C842] text-[#111] text-[9px] font-bold tracking-[2px] px-2 py-[3px] uppercase">SPECIAL</span>')
                    if item.get("description"):
                        ui.label(item["description"]).classes("text-[13px] text-[#888] mb-2")
                    price = _active_price(item["price"], item.get("discount_price"), item.get("discount_until"))
                    price_html = f'<span class="text-[20px] font-bold text-[#E63312]">{price:.2f} CHF</span>'
                    if item.get("discount_price") and price < item["price"]:
                        price_html += f'<span class="text-[13px] text-[#555] line-through ml-2">{item["price"]:.2f} CHF</span>'
                    ui.html(f'<div class="mb-4">{price_html}</div>')

                    if item.get("image_url"):
                        ui.image(item["image_url"]).classes("w-full h-auto object-contain mb-4")

                    flavor_select = None
                    if "milkshake" in item["name"].lower() or "milchshake" in item["name"].lower():
                        ui.label("Choose Flavor:").classes("font-bold text-[#F5F0E8] mb-1")
                        flavor_select = ui.select(["Vanilla", "Chocolate", "Strawberry"], value="Vanilla").classes("w-full")

                    water_select = None
                    if "water" in item["name"].lower() or "wasser" in item["name"].lower():
                        ui.label("Type:").classes("font-bold text-[#F5F0E8] mb-1")
                        water_select = ui.select(["Still", "Sparkling"], value="Still").classes("w-full")

                    ingredient_checks: dict[str, ui.checkbox] = {}
                    if item.get("ingredients"):
                        ui.html('<div class="font-bold text-[#F5F0E8] mt-3 mb-1">Customize:</div>')
                        ui.label("Uncheck to remove").classes("text-[12px] text-[#666] mb-2")
                        for ing in item["ingredients"]:
                            cb = ui.checkbox(ing["name"], value=True).classes("text-[#F5F0E8]")
                            ingredient_checks[ing["name"]] = cb

                    with ui.row().classes("justify-end gap-3 mt-5"):
                        ui.button("Cancel", on_click=dialog.close).props("flat").classes("text-[#888]")

                        def add_with_options(captured_item=item) -> None:
                            removed = [n for n, cb in ingredient_checks.items() if not cb.value]
                            parts = []
                            if flavor_select and flavor_select.value:
                                parts.append(f"Flavor: {flavor_select.value}")
                            if water_select and water_select.value:
                                parts.append(f"Type: {water_select.value}")
                            if removed:
                                parts.append("Without: " + ", ".join(removed))
                            notes = " | ".join(parts) if parts else None
                            eff_price = _active_price(
                                captured_item["price"],
                                captured_item.get("discount_price"),
                                captured_item.get("discount_until"),
                            )
                            shopping.add_to_cart(
                                menu_item_id=captured_item["id"],
                                name=captured_item["name"],
                                unit_price=eff_price,
                                notes=notes,
                            )
                            count = shopping.get_cart().item_count
                            ui.run_javascript(f'''
                                var b = document.getElementById("fw-cart-badge");
                                if (b) {{ b.textContent = "{count}"; b.style.display = "inline-block"; }}
                            ''')
                            dialog.close()
                            ui.notify(f"{captured_item['name']} added!", color="positive")

                        ui.button("Add to Cart", on_click=add_with_options).classes("fw-btn fw-btn-primary py-3 px-6")
                dialog.open()

            # Sticky category filter bar
            cat_links = ''.join(f'<a href="#{cat.name.lower()}" class="fw-cat-link">{cat.name}</a>' for cat in categories)
            ui.html(
                f'<div class="sticky top-16 z-[100] bg-[#111111] border-b border-[rgba(255,255,255,0.07)] w-full mt-16">'
                f'<div class="max-w-[1600px] mx-auto px-[52px] flex gap-0 overflow-x-auto">'
                f'{cat_links}</div></div>'
            )

            # Categories + item grids
            for cat in categories:
                items = shopping.get_menu_items(category_id=cat.id, available_only=False)
                if not items:
                    continue
                ui.html(
                    f'<div id="{cat.name.lower()}" class="scroll-mt-28 pt-8">'
                    f'<div class="max-w-[1600px] mx-auto px-[60px] pb-[14px] flex items-center gap-4">'
                    f'<div class="text-[11px] font-bold tracking-[4px] uppercase text-[#E63312]">{cat.name}</div>'
                    f'<div class="flex-1 h-px bg-[rgba(255,255,255,0.07)]"></div>'
                    f'</div></div>'
                )
                with ui.element("div").classes("grid grid-cols-4 gap-4 px-[60px] pb-10"):
                    for item in items:
                        img = resolve_image(item.name, item.image_url)
                        item_dict = {
                            "id": item.id, "name": item.name,
                            "description": item.description, "price": item.price,
                            "image_url": img, "is_available": item.is_available,
                            "is_special": item.is_special,
                            "discount_price": item.discount_price,
                            "discount_until": item.discount_until,
                            "ingredients": [{"name": mii.ingredient.name} for mii in item.ingredients],
                        }
                        menu_card(item_dict, on_add_to_cart=show_add_dialog)

        # ================================================================
        # CART
        # ================================================================
        @ui.page("/cart")
        def cart_page() -> None:
            navbar()
            ui.add_head_html("""<style>
            .fw-cart-wrap { margin-top:64px; min-height:calc(100vh - 64px); display:grid; grid-template-columns:1fr 380px; width:100%; }
            .fw-cart-left { padding:48px 60px; overflow-y:auto; border-right:1px solid rgba(255,255,255,0.07); }
            .fw-cart-right { background:#1a1a1a; padding:48px 40px; display:flex; flex-direction:column; }
            </style>""")

            cart = shopping.get_cart()

            if cart.is_empty:
                with ui.element("div").classes(
                    "mt-16 min-h-[calc(100vh-64px)] flex flex-col items-center justify-center gap-6"
                ):
                    ui.html(
                        '<div class="text-center">'
                        '<div class="font-display text-[80px] text-[#222] leading-[1]">EMPTY</div>'
                        '<div class="text-[15px] text-[#555] mt-2">Your cart is empty.</div>'
                        '</div>'
                    )
                    ui.button("→ To the Menu", on_click=lambda: ui.navigate.to("/menu")).classes("fw-btn fw-btn-primary py-[14px] px-10")
                return

            total_lbl = None
            count_lbl = None
            items_div = None

            def _build_items(container, c) -> None:
                container.clear()
                for idx, it in enumerate(c.items):
                    with container:
                        with ui.element("div").classes(
                            "flex items-center gap-4 py-5 border-b border-[rgba(255,255,255,0.07)] w-full"
                        ):
                            with ui.element("div").classes("flex-1 min-w-0"):
                                ui.label(it.name).classes(
                                    "font-display text-[22px] text-[#F5F0E8] tracking-[1px] leading-[1.1]"
                                )
                                if it.notes:
                                    ui.label(it.notes).classes("text-[12px] text-[#666] mt-[2px]")
                            with ui.element("div").classes("flex items-center gap-2"):
                                (
                                    ui.button("−", on_click=lambda i=idx, q=it.quantity: _dec(i, q))
                                    .props("flat")
                                    .classes("w-[28px] h-[28px] min-w-0 p-0 text-[#F5F0E8] text-[18px] leading-[1] border border-[rgba(255,255,255,0.25)]")
                                )
                                ui.label(str(it.quantity)).classes(
                                    "min-w-[24px] text-center text-[16px] font-bold text-[#F5F0E8]"
                                )
                                (
                                    ui.button("+", on_click=lambda i=idx, q=it.quantity: _inc(i, q))
                                    .props("flat")
                                    .classes("w-[28px] h-[28px] min-w-0 p-0 text-[#F5F0E8] text-[18px] leading-[1] border border-[rgba(255,255,255,0.25)]")
                                )
                            ui.label(f"{it.total:.2f} CHF").classes(
                                "text-[16px] font-bold text-[#E63312] whitespace-nowrap"
                            )
                            (
                                ui.button("✕", on_click=lambda i=idx: _remove(i))
                                .props("flat")
                                .classes("text-[#444] min-w-0 p-1 text-[16px]")
                            )

            def _refresh() -> None:
                nonlocal total_lbl, count_lbl, items_div
                c = shopping.get_cart()
                if c.is_empty:
                    ui.navigate.to("/cart")
                    return
                _build_items(items_div, c)
                total_lbl.set_text(f"{c.total:.2f} CHF")
                count_lbl.set_text(f"{c.item_count} items")

            def _remove(i: int) -> None:
                shopping.remove_from_cart(i)
                _refresh()

            def _dec(i: int, q: int) -> None:
                if q <= 1:
                    shopping.remove_from_cart(i)
                else:
                    shopping.update_cart_quantity(i, q - 1)
                _refresh()

            def _inc(i: int, q: int) -> None:
                shopping.update_cart_quantity(i, q + 1)
                _refresh()

            with ui.element("div").classes("fw-cart-wrap"):
                with ui.element("div").classes("fw-cart-left"):
                    ui.html('<div class="text-[11px] font-bold tracking-[4px] uppercase text-[#E63312] mb-2">Your Selection</div>')
                    ui.html('<div class="font-display text-[52px] leading-[0.95] text-[#F5F0E8] mb-8">CART</div>')
                    with ui.element("div").classes("w-full") as items_div:
                        _build_items(items_div, cart)

                with ui.element("div").classes("fw-cart-right"):
                    ui.html('<div class="font-display text-[28px] text-[#F5F0E8] tracking-[1px] mb-6">ORDER SUMMARY</div>')
                    count_lbl = ui.label(f"{cart.item_count} items").classes(
                        "text-[12px] text-[#555] tracking-[2px] uppercase mb-5"
                    )
                    ui.html('<div class="border-t border-[rgba(255,255,255,0.07)] mb-5"></div>')
                    ui.html('<div class="flex justify-between items-baseline mb-[6px]"><span class="text-[13px] text-[#888]">Subtotal</span></div>')
                    total_lbl = ui.label(f"{cart.total:.2f} CHF").classes(
                        "font-display text-[32px] text-[#E63312] tracking-[1px] mb-2"
                    )
                    ui.html('<div class="text-[12px] text-[#444] mb-7">Delivery fee calculated at checkout.</div>')
                    ui.html('<div class="border-t border-[rgba(255,255,255,0.07)] mb-7"></div>')
                    ui.button("Checkout →", on_click=lambda: ui.navigate.to("/checkout")).classes("fw-btn fw-btn-primary w-full").style("padding:16px;font-size:14px!important")
                    ui.button("← Continue Shopping", on_click=lambda: ui.navigate.to("/menu")).props("flat").classes("w-full text-[#555] mt-3").style("padding:10px")

        # ================================================================
        # CHECKOUT
        # ================================================================
        @ui.page("/checkout")
        def checkout_page() -> None:
            navbar()
            user_data = auth.current_user()
            if not user_data:
                ui.navigate.to("/login")
                return
            cart = shopping.get_cart()
            if cart.is_empty:
                ui.navigate.to("/cart")
                return

            with ui.element("div").classes("pt-16 bg-[#111111] w-full"):
                ui.html(
                    '<div class="bg-[#1a1a1a] px-[60px] py-5 border-b border-[rgba(255,255,255,0.07)]">'
                    '<div class="text-[11px] font-bold tracking-[4px] uppercase text-[#E63312] mb-[6px]">Almost there</div>'
                    '<div class="font-display text-[40px] leading-[1] text-[#F5F0E8]">CHECKOUT</div>'
                    '</div>'
                )
            with ui.element("div").classes("px-[60px] py-6 max-w-[640px] mx-auto bg-[#111111]"):
                ui.html(f'<div class="font-display text-[24px] text-[#E63312] mb-4">Total: {cart.total:.2f} CHF</div>')

                order_type_toggle = ui.toggle(["delivery", "pickup"], value="pickup").props("color=red")
                address_box = ui.column().classes("w-full mt-4")
                pickup_box = ui.column().classes("w-full mt-4")
                notes_in = ui.textarea("Notes (optional)").classes("w-full").style("margin-top:12px;font-size:16px").props("outlined rows=2")

                selected_address_id: dict = {"value": None}
                street_in = house_nr_in = floor_in = city_in = postal_in = label_in = pickup_time_in = None

                def update_form() -> None:
                    nonlocal street_in, house_nr_in, floor_in, city_in, postal_in, label_in, pickup_time_in
                    address_box.clear()
                    pickup_box.clear()
                    selected_address_id["value"] = None

                    if order_type_toggle.value == "delivery":
                        saved = auth.get_delivery_addresses(user_data["id"])
                        with address_box:
                            ui.label("Delivery Address").classes("font-display text-[22px] text-[#F5F0E8] mb-4")

                            new_form = ui.column().classes("w-full")

                            if saved:
                                ui.label("Saved Addresses").classes(
                                    "text-[11px] font-bold tracking-[3px] text-[#E63312] uppercase mb-2"
                                )
                                for addr in saved:
                                    line = f"{addr.street} {addr.house_nr}, {addr.postal_code} {addr.city}"
                                    if addr.label:
                                        line = f"{addr.label} — {line}"

                                    def select_addr(a=addr) -> None:
                                        selected_address_id["value"] = a.id
                                        new_form.set_visibility(False)
                                        ui.notify(f"Address selected: {a.street} {a.house_nr}", color="positive")

                                    with ui.element("div").classes(
                                        "bg-[#1a1a1a] border border-[rgba(255,255,255,0.08)] px-[18px] py-[14px] mb-2 cursor-pointer flex justify-between items-center"
                                    ):
                                        ui.label(line).classes("text-[#F5F0E8] text-[14px]")
                                        ui.button("Select", on_click=select_addr).classes("fw-btn fw-btn-primary").style("padding:6px 16px;font-size:11px!important")

                                ui.html('<div class="border-t border-[rgba(255,255,255,0.07)] my-5"></div>')
                                ui.label("Or enter a new address").classes(
                                    "text-[11px] font-bold tracking-[3px] text-[#888] uppercase mb-3"
                                )

                            with new_form:
                                label_in = ui.input("Label (optional, e.g. Home)").classes("w-full").style("margin-bottom:8px;font-size:16px").props("outlined dense=false")
                                street_in = ui.input(
                                    "Street *",
                                    validation={
                                        "Required": lambda v: bool(v.strip()),
                                        "Street must contain letters": lambda v: bool(re.search(r'[a-zA-ZÀ-öø-ÿ]', v.strip())) if v.strip() else True,
                                    },
                                ).classes("w-full").style("font-size:16px").props("outlined dense=false")
                                house_nr_in = ui.input(
                                    "House Number *",
                                    validation={
                                        "Required": lambda v: bool(v.strip()),
                                        "Must be a number (e.g. 12 or 12a)": lambda v: bool(re.match(r'^\d+[a-zA-Z]?$', v.strip())) if v.strip() else True,
                                    },
                                ).classes("w-full").style("margin-top:8px;font-size:16px").props("outlined dense=false")
                                floor_in = ui.input("Floor (optional)").classes("w-full").style("margin-top:8px;font-size:16px").props("outlined dense=false")
                                city_in = ui.input(
                                    "City *",
                                    validation={
                                        "Required": lambda v: bool(v.strip()),
                                        "City must contain letters only": lambda v: bool(re.match(r'^[a-zA-ZÀ-öø-ÿ\s\-]+$', v.strip())) if v.strip() else True,
                                    },
                                ).classes("w-full").style("margin-top:8px;font-size:16px").props("outlined dense=false")
                                postal_in = ui.input(
                                    "Postal Code *",
                                    validation={
                                        "Required": lambda v: bool(v.strip()),
                                        "Must be 4 digits (e.g. 8001)": lambda v: bool(re.match(r'^\d{4}$', v.strip())) if v.strip() else True,
                                    },
                                ).classes("w-full").style("margin-top:8px;font-size:16px").props("outlined dense=false")

                    else:
                        with pickup_box:
                            ui.label("Pickup Time").classes("font-display text-[22px] text-[#F5F0E8] mb-3")
                            from datetime import datetime as _now, timedelta as _td
                            _base = _now.now() + _td(minutes=30)
                            _base = _base.replace(second=0, microsecond=0)
                            _mins = ((_base.minute + 14) // 15) * 15
                            if _mins >= 60:
                                _base = _base.replace(hour=_base.hour + 1, minute=_mins - 60)
                            else:
                                _base = _base.replace(minute=_mins)
                            _slots = [(_base + _td(minutes=15 * i)).strftime("%H:%M") for i in range(8)]
                            pickup_time_in = ui.select(_slots, value=_slots[0], label="Choose Pickup Time").classes("w-full").style("font-size:16px").props("outlined")

                order_type_toggle.on_value_change(lambda: update_form())
                update_form()

                def go_to_payment() -> None:
                    addr_id = selected_address_id["value"]

                    if order_type_toggle.value == "pickup":
                        if not pickup_time_in or not pickup_time_in.value:
                            ui.notify("Please select a pickup time.", color="negative")
                            return

                    if order_type_toggle.value == "delivery" and not addr_id:
                        missing = []
                        if not street_in or not street_in.value.strip(): missing.append("Street")
                        if not house_nr_in or not house_nr_in.value.strip(): missing.append("House Number")
                        if not city_in or not city_in.value.strip(): missing.append("City")
                        if not postal_in or not postal_in.value.strip(): missing.append("Postal Code")
                        if missing:
                            ui.notify(f"Required field(s) missing: {', '.join(missing)}", color="negative")
                            return
                        if not re.search(r'[a-zA-ZÀ-öø-ÿ]', street_in.value.strip()):
                            ui.notify("Street must contain letters.", color="negative")
                            return
                        if not re.match(r'^\d+[a-zA-Z]?$', house_nr_in.value.strip()):
                            ui.notify("House number must be a number (e.g. 12 or 12a).", color="negative")
                            return
                        if not re.match(r'^[a-zA-ZÀ-öø-ÿ\s\-]+$', city_in.value.strip()):
                            ui.notify("City must contain letters only.", color="negative")
                            return
                        if not re.match(r'^\d{4}$', postal_in.value.strip()):
                            ui.notify("Postal code must be 4 digits (e.g. 8001).", color="negative")
                            return
                        try:
                            new_addr = auth.add_delivery_address(
                                user_id=user_data["id"],
                                street=street_in.value,
                                house_nr=house_nr_in.value,
                                city=city_in.value,
                                postal_code=postal_in.value,
                                floor=floor_in.value if floor_in and floor_in.value else None,
                                label=label_in.value if label_in and label_in.value else None,
                            )
                            addr_id = new_addr.id
                        except ValueError as e:
                            ui.notify(str(e), color="negative")
                            return

                    payment.save_pending_order(
                        user_id=user_data["id"],
                        order_type=order_type_toggle.value,
                        delivery_address_id=addr_id,
                        pickup_time=pickup_time_in.value if pickup_time_in and pickup_time_in.value.strip() else None,
                        notes=notes_in.value or None,
                    )
                    ui.navigate.to("/payment/checkout")

                ui.button("Proceed to Payment →", icon="credit_card", on_click=go_to_payment).classes("fw-btn fw-btn-primary w-full").style("margin-top:20px;padding:16px 32px;font-size:15px!important")

        # ================================================================
        # PAYMENT CHECKOUT — Stripe redirect
        # ================================================================
        @ui.page("/payment/checkout")
        def payment_checkout_page() -> None:
            navbar()
            user_data = auth.current_user()
            if not user_data:
                ui.navigate.to("/login")
                return
            cart = shopping.get_cart()
            if cart.is_empty:
                ui.navigate.to("/cart")
                return
            pending = app.storage.user.get("pending_order")
            if not pending:
                ui.navigate.to("/checkout")
                return

            with ui.element("div").classes("pt-16 bg-[#111111] w-full"):
                ui.html(
                    '<div class="bg-[#1a1a1a] px-[60px] py-5 border-b border-[rgba(255,255,255,0.07)]">'
                    '<div class="text-[11px] font-bold tracking-[4px] uppercase text-[#E63312] mb-[6px]">Secure Payment</div>'
                    '<div class="font-display text-[40px] leading-[1] text-[#F5F0E8]">PAYMENT</div>'
                    '</div>'
                )

            with ui.element("div").classes("px-[60px] py-6 max-w-[600px] mx-auto bg-[#111111]"):
                ui.html(f'<div class="font-display text-[28px] text-[#E63312] mb-2">Amount: {cart.total:.2f} CHF</div>')
                ui.html('<div class="text-[13px] text-[#666] mb-6">You will be redirected to Stripe to securely complete your payment.</div>')

                with ui.element("div").classes("bg-[#1a1a1a] border border-[rgba(255,255,255,0.08)] p-6 mb-6"):
                    ui.label("Order Summary").classes("font-display text-[20px] text-[#F5F0E8] mb-3")
                    for item in cart.items:
                        ui.label(f"{item.quantity}× {item.name} — {item.total:.2f} CHF").classes("text-[13px] text-[#aaa]")
                    ui.html('<div class="border-t border-[rgba(255,255,255,0.07)] my-3"></div>')
                    ui.label(f"Total: {cart.total:.2f} CHF").classes("font-bold text-[#E63312]")

                error_label = ui.label("").classes("text-[#E63312] text-[13px] mb-3")

                def go_to_stripe() -> None:
                    import secrets as _secrets
                    try:
                        # Save full session state server-side before the Stripe redirect.
                        # Stripe's cross-site redirect can lose the NiceGUI session cookie,
                        # so we store everything in app.storage.general (server-side, no cookie)
                        # and restore it on the success page via the token in the URL.
                        token = _secrets.token_urlsafe(16)
                        app.storage.general[f"pw_{token}"] = {
                            "user": app.storage.user.get("user"),
                            "pending": app.storage.user.get("pending_order"),
                            "cart": shopping.get_cart().to_dict_list(),
                        }
                        url = payment.create_stripe_session(
                            base_url="http://localhost:8080",
                            success_token=token,
                        )
                        ui.navigate.to(url)
                    except ValueError as e:
                        error_label.set_text(str(e))

                with ui.row().classes("justify-between items-center"):
                    ui.button("← Back", on_click=lambda: ui.navigate.to("/checkout")).props("flat").classes("text-[#888]")
                    ui.button("Pay with Stripe", icon="lock", on_click=go_to_stripe).classes("fw-btn fw-btn-primary").style("padding:14px 32px;font-size:14px!important")

                ui.html("""
                <div class="flex items-center gap-2 mt-5 text-[#555] text-[12px]">
                  <span>🔒</span>
                  <span>Secure payment via Stripe — your card details are never stored on our servers.</span>
                </div>
                """)

        # ================================================================
        # PAYMENT SUCCESS
        # ================================================================
        @ui.page("/payment/success")
        def payment_success_page(token: str = "") -> None:
            # Restore session from server-side storage if Stripe redirect lost the cookie.
            if token:
                stored = app.storage.general.pop(f"pw_{token}", None)
                if stored:
                    if stored.get("user") and not app.storage.user.get("user"):
                        app.storage.user["user"] = stored["user"]
                    if stored.get("pending") and not app.storage.user.get("pending_order"):
                        app.storage.user["pending_order"] = stored["pending"]
                    if stored.get("cart") and not app.storage.user.get("cart_items"):
                        app.storage.user["cart_items"] = stored["cart"]

            navbar()
            order = payment.complete_order()
            order_id = order.id if order else app.storage.user.get("last_order_id")

            with ui.element("div").classes("pt-16 min-h-screen bg-[#111111] flex items-center justify-center"):
                with ui.element("div").classes("text-center px-10 py-20"):
                    ui.html('<div class="text-[80px] mb-6">✅</div>')
                    ui.html('<div class="font-display text-[72px] text-[#639922] leading-[1] mb-4">PAID!</div>')
                    ui.html(
                        '<div class="text-[17px] text-[rgba(245,240,232,0.65)] mb-10">'
                        'Payment successful — your order has been received.<br>We are preparing it fresh for you!'
                        '</div>'
                    )
                    with ui.row().classes("justify-center gap-4"):
                        ui.button("Track Order", on_click=lambda: ui.navigate.to("/profile")).classes("fw-btn fw-btn-primary py-[14px] px-7")
                        ui.button("Back to Menu", on_click=lambda: ui.navigate.to("/menu")).classes("fw-btn fw-btn-outline py-[14px] px-7")

        # ================================================================
        # PAYMENT CANCEL
        # ================================================================
        @ui.page("/payment/cancel")
        def payment_cancel_page() -> None:
            navbar()
            with ui.element("div").classes("pt-16 min-h-screen bg-[#111111] flex items-center justify-center"):
                with ui.element("div").classes("text-center px-10 py-20"):
                    ui.html('<div class="text-[80px] mb-6">❌</div>')
                    ui.html('<div class="font-display text-[72px] text-[#E63312] leading-[1] mb-4">CANCELLED</div>')
                    ui.html('<div class="text-[17px] text-[rgba(245,240,232,0.65)] mb-10">No charge was made. Your cart is still intact.</div>')
                    with ui.row().classes("justify-center gap-4"):
                        ui.button("To Cart", on_click=lambda: ui.navigate.to("/cart")).classes("fw-btn fw-btn-primary py-[14px] px-7")
                        ui.button("To Menu", on_click=lambda: ui.navigate.to("/menu")).classes("fw-btn fw-btn-outline py-[14px] px-7")

        # ================================================================
        # ORDER STATUS
        # ================================================================
        @ui.page("/order/{order_id}")
        def order_status_page(order_id: int) -> None:
            navbar()
            user_data = auth.current_user()
            if not user_data:
                ui.navigate.to("/login")
                return
            order = shopping.get_order(order_id)
            with ui.element("div").classes("pt-16 bg-[#111111] w-full"):
                ui.html(
                    '<div class="bg-[#1a1a1a] px-[60px] py-5 border-b border-[rgba(255,255,255,0.07)]">'
                    '<div class="text-[11px] font-bold tracking-[4px] uppercase text-[#E63312] mb-[6px]">Your Order</div>'
                    '<div class="font-display text-[40px] leading-[1] text-[#F5F0E8]">STATUS</div>'
                    '</div>'
                )
            with ui.element("div").classes("px-[60px] py-6 max-w-[640px] mx-auto bg-[#111111]"):
                if not order:
                    ui.label("Order not found.").classes("text-[#E63312] text-[18px]")
                else:
                    items_data = [
                        {"quantity": oi.quantity, "name": oi.menu_item.name, "total": oi.unit_price * oi.quantity}
                        for oi in order.order_items
                    ]
                    order_card({
                        "id": order.id, "status": order.status,
                        "order_type": order.order_type,
                        "created_at": order.created_at.strftime("%d.%m.%Y %H:%M"),
                        "total_price": order.total_price,
                        "items": items_data,
                    })

        # ================================================================
        # SPECIALS
        # ================================================================
        @ui.page("/specials")
        def specials_page() -> None:
            navbar()
            specials = shopping.get_specials()

            ui.html("""
            <div class="mt-16 border-b border-[rgba(230,51,18,0.2)] px-[60px] py-12" style="background:#1a0800">
              <div class="max-w-[1600px] mx-auto">
                <div class="text-[11px] font-bold tracking-[4px] uppercase text-[#E63312] mb-[10px]">Don't Miss</div>
                <div class="font-display text-[clamp(48px,6vw,80px)] leading-[0.95] text-[#F5F0E8]">CURRENT<br>SPECIALS</div>
              </div>
            </div>
            """)

            if not specials:
                ui.html('<div class="text-center py-[120px]"><div class="font-display text-[48px] text-[#333]">NO SPECIALS ACTIVE</div></div>')
                with ui.element("div").classes("flex justify-center"):
                    ui.button("To the Menu", on_click=lambda: ui.navigate.to("/menu")).classes("fw-btn fw-btn-primary py-[14px] px-8")
            else:
                def show_special_dialog(item: dict) -> None:
                    with ui.dialog() as dialog, ui.element("div").classes(
                        "bg-[#1a1a1a] border border-[rgba(255,255,255,0.1)] p-8 min-w-[380px]"
                    ):
                        ui.html('<span class="bg-[#F5C842] text-[#111] text-[9px] font-bold tracking-[2px] px-2 py-[3px] uppercase">SPECIAL</span>')
                        ui.html(f'<div class="font-display text-[32px] text-[#F5F0E8] tracking-[1px] mt-2 mb-1">{item["name"]}</div>')
                        if item.get("description"):
                            ui.label(item["description"]).classes("text-[13px] text-[#888] mb-2")
                        eff = _active_price(item["price"], item.get("discount_price"), item.get("discount_until"))
                        price_html = f'<span class="text-[20px] font-bold text-[#E63312]">{eff:.2f} CHF</span>'
                        if item.get("discount_price") and eff < item["price"]:
                            price_html += f'<span class="text-[13px] text-[#555] line-through ml-2">{item["price"]:.2f} CHF</span>'
                        ui.html(f'<div class="mb-4">{price_html}</div>')
                        if item.get("image_url"):
                            ui.image(item["image_url"]).classes("w-full h-auto object-contain mb-4")
                        with ui.row().classes("justify-end gap-3 mt-5"):
                            ui.button("Cancel", on_click=dialog.close).props("flat").classes("text-[#888]")
                            def add_sp(i=item):
                                p = _active_price(i["price"], i.get("discount_price"), i.get("discount_until"))
                                shopping.add_to_cart(i["id"], i["name"], p)
                                count = shopping.get_cart().item_count
                                ui.run_javascript(f'''
                                    var b = document.getElementById("fw-cart-badge");
                                    if (b) {{ b.textContent = "{count}"; b.style.display = "inline-block"; }}
                                ''')
                                dialog.close()
                                ui.notify(f"{i['name']} added!", color="positive")
                            ui.button("Add to Cart", on_click=add_sp).classes("fw-btn fw-btn-primary py-3 px-6")
                    dialog.open()

                with ui.element("div").classes("max-w-[1600px] mx-auto px-[60px] py-10"):
                    with ui.element("div").classes("grid grid-cols-4 gap-4"):
                        for sp in specials:
                            img = resolve_image(sp.name, sp.image_url)
                            item_dict = {
                                "id": sp.id, "name": sp.name,
                                "description": sp.description,
                                "price": sp.price,
                                "image_url": img, "is_available": sp.is_available,
                                "is_special": sp.is_special,
                                "discount_price": sp.discount_price,
                                "discount_until": sp.discount_until,
                                "ingredients": [],
                            }
                            menu_card(item_dict, on_add_to_cart=show_special_dialog)

        # ================================================================
        # PROFILE
        # ================================================================
        @ui.page("/profile")
        def profile_page() -> None:
            navbar()
            user_data = auth.current_user()
            if not user_data:
                ui.navigate.to("/login")
                return
            orders = shopping.get_user_orders(user_data["id"])

            with ui.element("div").classes("pt-16 bg-[#111111] w-full"):
                ui.html(
                    f'<div class="bg-[#1a1a1a] px-[60px] py-5 border-b border-[rgba(255,255,255,0.07)]">'
                    f'<div class="text-[11px] font-bold tracking-[4px] uppercase text-[#E63312] mb-[6px]">Your Account</div>'
                    f'<div class="font-display text-[40px] leading-[1] text-[#F5F0E8]">{user_data["first_name"].upper()} {user_data.get("last_name","").upper()}</div>'
                    f'<div class="text-[14px] text-[#888] mt-[6px]">{user_data["email"]}</div>'
                    f'</div>'
                )
            with ui.element("div").classes("px-[60px] py-6 max-w-[820px] mx-auto bg-[#111111]"):
                ui.html('<div class="font-display text-[36px] text-[#F5F0E8] tracking-[1px] mb-6">YOUR ORDERS</div>')
                if not orders:
                    ui.label("No orders yet.").classes("text-[#888] text-[15px]")
                else:
                    for o in orders:
                        items_data = [
                            {"quantity": oi.quantity, "name": oi.menu_item.name, "total": oi.unit_price * oi.quantity}
                            for oi in o.order_items
                        ]
                        order_card({
                            "id": o.id, "status": o.status,
                            "order_type": o.order_type,
                            "created_at": o.created_at.strftime("%d.%m.%Y %H:%M"),
                            "total_price": o.total_price,
                            "items": items_data,
                        }, receipt_id=o.id)

        # ================================================================
        # ADMIN — DASHBOARD
        # ================================================================
        @ui.page("/admin")
        def admin_dashboard() -> None:
            navbar()
            user_data = auth.current_user()
            if not user_data or user_data.get("role") not in ("admin", "employee"):
                ui.navigate.to("/")
                return

            with ui.element("div").classes("pt-16 bg-[#111111] w-full"):
                ui.html(
                    '<div class="bg-[#1a1a1a] px-[60px] py-5 border-b border-[rgba(255,255,255,0.07)]">'
                    '<div class="text-[11px] font-bold tracking-[4px] uppercase text-[#E63312] mb-[6px]">Management</div>'
                    '<div class="font-display text-[40px] leading-[1] text-[#F5F0E8]">ADMIN DASHBOARD</div>'
                    '</div>'
                )
            with ui.element("div").classes("max-w-[1600px] mx-auto px-[60px] py-6 bg-[#111111]"):
                with ui.row().classes("gap-3 mb-12"):
                    ui.button("Manage Menu", on_click=lambda: ui.navigate.to("/admin/menu")).classes("fw-btn fw-btn-primary py-3 px-6")
                    ui.button("Orders", on_click=lambda: ui.navigate.to("/admin/orders")).classes("fw-btn fw-btn-outline py-3 px-6")
                    if user_data.get("role") == "admin":
                        ui.button("Specials", on_click=lambda: ui.navigate.to("/admin/specials")).classes("fw-btn fw-btn-outline py-3 px-6")

                ui.html('<div class="font-display text-[32px] text-[#F5F0E8] tracking-[1px] mb-5">ACTIVE ORDERS</div>')

                active = [o for o in admin.get_all_orders() if o.status in ("pending", "preparing", "ready")]
                if not active:
                    ui.label("No active orders.").classes("text-[#888]")
                else:
                    for order in active:
                        sc = {"pending": "#F5C842", "preparing": "#378ADD", "ready": "#639922"}.get(order.status, "#888")
                        with ui.element("div").classes("fw-admin-card p-5 mb-3"):
                            with ui.row().classes("items-center justify-between flex-wrap gap-3"):
                                ui.html(f'<div class="font-display text-[22px] text-[#F5F0E8]">#{order.id} — {order.user.first_name} {order.user.last_name}</div>')
                                ui.html(f'<span class="text-[#111] text-[10px] font-bold px-3 py-1 tracking-[2px] uppercase" style="background:{sc}">{order.status.upper()}</span>')
                                ui.label("Delivery" if order.order_type == "delivery" else "Pickup").classes("text-[#888] text-[13px]")
                                ui.label(f"{order.total_price:.2f} CHF").classes("font-bold text-[#E63312]")

                                next_map = {
                                    "pending": "preparing",
                                    "preparing": "ready",
                                    "ready": "delivered" if order.order_type == "delivery" else "collected",
                                }

                                def advance(oid=order.id, cur=order.status) -> None:
                                    if cur in next_map:
                                        admin.update_order_status(oid, next_map[cur])
                                        ui.navigate.to("/admin")

                                ui.button("Next Status →", on_click=advance).classes("fw-btn fw-btn-primary").style("padding:8px 18px;font-size:11px!important")

        # ================================================================
        # ADMIN — MENU MANAGER
        # ================================================================
        @ui.page("/admin/menu")
        def admin_menu_page() -> None:
            navbar()
            user_data = auth.current_user()
            if not user_data or user_data.get("role") not in ("admin", "employee"):
                ui.navigate.to("/")
                return

            with ui.element("div").classes("pt-16 bg-[#111111] w-full"):
                ui.html(
                    '<div class="bg-[#1a1a1a] px-[60px] py-5 border-b border-[rgba(255,255,255,0.07)]">'
                    '<div class="text-[11px] font-bold tracking-[4px] uppercase text-[#E63312] mb-[6px]">Management</div>'
                    '<div class="font-display text-[40px] leading-[1] text-[#F5F0E8]">MANAGE MENU</div>'
                    '</div>'
                )
            categories = admin.get_categories()
            items_container = ui.column().classes("w-full max-w-[1600px] mx-auto px-[60px] py-6 bg-[#111111]")

            def refresh_items() -> None:
                items_container.clear()
                with items_container:
                    for cat in categories:
                        items = admin.get_menu_items_by_category(cat.id)
                        if not items:
                            continue
                        ui.html(f'<div class="font-display text-[28px] text-[#F5F0E8] tracking-[1px] mt-6 mb-3">{cat.name.upper()}</div>')
                        for item in items:
                            avail_color = "#639922" if item.is_available else "#E63312"
                            avail_label = "Available" if item.is_available else "Sold Out"
                            with ui.element("div").classes("fw-admin-card px-5 py-4"):
                                with ui.row().classes("items-center justify-between flex-wrap gap-3"):
                                    ui.label(item.name).classes("font-bold text-[#F5F0E8] text-[16px]")
                                    ui.label(f"{item.price:.2f} CHF").classes("text-[#E63312] font-bold")
                                    ui.html(f'<span class="text-white text-[10px] font-bold px-[10px] py-[3px] tracking-[1px]" style="background:{avail_color}">{avail_label}</span>')

                                    def toggle(iid=item.id, cur=item.is_available) -> None:
                                        admin.set_item_availability(iid, not cur)
                                        refresh_items()

                                    btn_label = "Mark as Sold Out" if item.is_available else "Mark as Available"
                                    ui.button(btn_label, on_click=toggle).classes("fw-btn").style(
                                        f"padding:6px 16px;font-size:11px!important;"
                                        f"background:{'rgba(230,51,18,0.15)' if item.is_available else 'rgba(99,153,34,0.15)'};"
                                        f"color:{'#E63312' if item.is_available else '#639922'};"
                                        f"border:1px solid {'#E63312' if item.is_available else '#639922'};"
                                    )

            refresh_items()

        # ================================================================
        # ADMIN — ORDER MANAGER
        # ================================================================
        @ui.page("/admin/orders")
        def admin_orders_page() -> None:
            navbar()
            user_data = auth.current_user()
            if not user_data or user_data.get("role") not in ("admin", "employee"):
                ui.navigate.to("/")
                return

            with ui.element("div").classes("pt-16 bg-[#111111] w-full"):
                ui.html(
                    '<div class="bg-[#1a1a1a] px-[60px] py-5 border-b border-[rgba(255,255,255,0.07)]">'
                    '<div class="text-[11px] font-bold tracking-[4px] uppercase text-[#E63312] mb-[6px]">Management</div>'
                    '<div class="font-display text-[40px] leading-[1] text-[#F5F0E8]">MANAGE ORDERS</div>'
                    '</div>'
                )
            with ui.element("div").classes("max-w-[1600px] mx-auto px-[60px] py-6 bg-[#111111]"):
                status_filter = ui.select(
                    options={"all": "All", "pending": "Pending", "preparing": "Preparing",
                             "ready": "Ready", "delivered": "Delivered", "collected": "Collected"},
                    value="all", label="Filter by Status",
                ).classes("min-w-[200px] mb-6")

                orders_container = ui.column().classes("w-full")

                def refresh_orders() -> None:
                    orders_container.clear()
                    status = None if status_filter.value == "all" else status_filter.value
                    orders = admin.get_all_orders(status=status)
                    with orders_container:
                        if not orders:
                            ui.label("No orders found.").classes("text-[#888]")
                            return
                        for order in orders:
                            with ui.element("div").classes("fw-admin-card px-5 py-4"):
                                with ui.row().classes("items-center justify-between flex-wrap gap-3"):
                                    ui.label(f"#{order.id}").classes("font-display text-[22px] text-[#F5F0E8]")
                                    ui.label(f"{order.user.first_name} {order.user.last_name}").classes("text-[#aaa]")
                                    ui.label("Delivery" if order.order_type == "delivery" else "Pickup").classes("text-[#888] text-[13px]")
                                    ui.label(f"{order.total_price:.2f} CHF").classes("font-bold text-[#E63312]")
                                    ui.label(order.created_at.strftime("%d.%m.%Y %H:%M")).classes("text-[12px] text-[#555]")

                                    status_sel = ui.select(
                                        options=list(STATUS_LABELS.keys()),
                                        value=order.status, label="Status",
                                    ).classes("min-w-[140px]")

                                    def save_status(oid=order.id, sel=status_sel) -> None:
                                        admin.update_order_status(oid, sel.value)
                                        ui.notify(f"Status #{oid} updated.", color="positive")

                                    ui.button("Save", on_click=save_status).classes("fw-btn fw-btn-primary").style("padding:6px 16px;font-size:11px!important")

                status_filter.on_value_change(lambda: refresh_orders())
                refresh_orders()

        # ================================================================
        # ADMIN — SPECIALS MANAGER
        # ================================================================
        @ui.page("/admin/specials")
        def admin_specials_page() -> None:
            from pathlib import Path as _Path
            navbar()
            user_data = auth.current_user()
            if not user_data or user_data.get("role") != "admin":
                ui.navigate.to("/")
                return

            with ui.element("div").classes("pt-16 bg-[#111111] w-full"):
                ui.html(
                    '<div class="bg-[#1a1a1a] px-[60px] py-5 border-b border-[rgba(255,255,255,0.07)]">'
                    '<div class="text-[11px] font-bold tracking-[4px] uppercase text-[#E63312] mb-[6px]">Management</div>'
                    '<div class="font-display text-[40px] leading-[1] text-[#F5F0E8]">SPECIALS & DISCOUNTS</div>'
                    '</div>'
                )
            all_items = admin.get_all_menu_items()
            item_options = {i.id: f"{i.name} ({i.price:.2f} CHF)" for i in all_items}

            IMAGES_DIR = _Path(__file__).parent.parent.parent / "frontend" / "static" / "images"

            with ui.element("div").classes("px-[60px] py-6 max-w-[960px] mx-auto bg-[#111111]"):

                # ---- SECTION 1: Create new special ----
                ui.html('<div class="font-display text-[28px] text-[#F5F0E8] tracking-[1px] mb-4">CREATE NEW SPECIAL</div>')
                ui.html('<div class="text-[13px] text-[#888] mb-5">Fill in all required fields (*) to create a new special.</div>')

                categories = admin.get_categories()
                cat_options = {c.id: c.name for c in categories}

                specials_list_container = ui.column().classes("w-full")
                new_uploaded_url: dict = {"value": None}

                with ui.element("div").classes("fw-admin-card p-7"):
                    sp_name_in = ui.input("Name *").classes("w-full").props("outlined dense=false").style("font-size:16px")
                    sp_cat_in = ui.select(options=cat_options, label="Category *").classes("w-full").style("margin-top:12px;font-size:16px").props("outlined")
                    sp_price_in = ui.number("Regular Price (CHF) *", min=0.01, step=0.10).classes("w-full").style("margin-top:12px;font-size:16px").props("outlined dense=false")
                    sp_desc_in = ui.textarea("Description (optional)").classes("w-full").style("margin-top:12px;font-size:16px").props("outlined rows=2")
                    sp_disc_in = ui.number("Discount Price (CHF, optional)", min=0.01, step=0.10).classes("w-full").style("margin-top:12px;font-size:16px").props("outlined dense=false")

                    with ui.input("Discount valid until (optional)").classes("w-full").style("margin-top:12px;font-size:16px").props("outlined dense=false") as sp_until_in:
                        with ui.menu().props("no-parent-event") as sp_menu:
                            with ui.date().props(':options="(d) => d >= new Date().toISOString().slice(0,10).replaceAll(\'-\',\'\/\')"').bind_value(sp_until_in):
                                pass
                        with sp_until_in.add_slot("append"):
                            ui.icon("edit_calendar").on("click", sp_menu.open).classes("cursor-pointer text-[#E63312]")

                    ui.html('<div class="text-[13px] text-[#aaa] mt-4 mb-2">Upload Image (optional)</div>')
                    new_upload_preview = ui.html("").classes("mt-2")

                    def handle_new_image(e) -> None:
                        suffix = _Path(e.name).suffix.lower()
                        filename = f"special_new_{int(__import__('time').time())}{suffix}"
                        dest = IMAGES_DIR / filename
                        dest.write_bytes(e.content.read())
                        new_uploaded_url["value"] = f"/static/images/{filename}"
                        new_upload_preview.set_content(
                            f'<img src="{new_uploaded_url["value"]}" class="max-h-[120px] rounded-lg mt-2 border border-[#333]">'
                        )
                        ui.notify("Image uploaded.", color="positive")

                    ui.upload(label="Choose Image", on_upload=handle_new_image, auto_upload=True, max_file_size=10_000_000,
                    ).props('accept=".png,.jpg,.jpeg,.webp" flat bordered').classes("w-full").style("background:#1a1a1a;border:1px solid #333;border-radius:8px")

                    def create_special() -> None:
                        errors = []
                        if not sp_name_in.value or not sp_name_in.value.strip():
                            errors.append("Name")
                        if not sp_cat_in.value:
                            errors.append("Category")
                        if not sp_price_in.value or float(sp_price_in.value) <= 0:
                            errors.append("Regular Price")
                        if errors:
                            ui.notify(f"Required field(s) missing: {', '.join(errors)}", color="negative")
                            return
                        disc_price = float(sp_disc_in.value) if sp_disc_in.value else None
                        until_dt = datetime.strptime(sp_until_in.value, "%Y-%m-%d") if sp_until_in.value else None
                        try:
                            item = admin.create_menu_item(
                                category_id=sp_cat_in.value,
                                name=sp_name_in.value.strip(),
                                description=sp_desc_in.value.strip() or None,
                                price=float(sp_price_in.value),
                                image_url=new_uploaded_url["value"],
                                is_special=True,
                                discount_price=disc_price,
                                discount_until=until_dt,
                                created_by_user_id=user_data["id"],
                            )
                            sp_name_in.set_value("")
                            sp_price_in.set_value(None)
                            sp_desc_in.set_value("")
                            sp_disc_in.set_value(None)
                            sp_until_in.set_value("")
                            new_uploaded_url["value"] = None
                            new_upload_preview.set_content("")
                            ui.notify(f"Special '{item.name}' created!", color="positive")
                            refresh_specials_list()
                        except ValueError as e:
                            ui.notify(str(e), color="negative")

                    ui.button("Create Special →", on_click=create_special).classes("fw-btn fw-btn-primary w-full").style("margin-top:20px;padding:14px 32px")

                # ---- SECTION 2: Set Discount ----
                ui.html('<div class="font-display text-[28px] text-[#F5F0E8] tracking-[1px] mt-10 mb-4">SET DISCOUNT</div>')
                ui.html('<div class="text-[13px] text-[#888] mb-5">Set a discount price for an item. Leave end date empty = permanently active until manually changed.</div>')

                with ui.element("div").classes("fw-admin-card p-7"):
                    disc_item_sel = ui.select(options=item_options, label="Select Menu Item").classes("w-full")
                    disc_price_in = ui.number(
                        "Discount Price (CHF)", min=0.01, step=0.10,
                        validation={"Price must be greater than 0": lambda v: float(v) > 0 if v else True},
                    ).classes("w-full mt-4")

                    with ui.input("Discount valid until (empty = permanent)").classes("w-full mt-4") as disc_until_in:
                        with ui.menu().props("no-parent-event") as disc_menu:
                            with ui.date().props(':options="(d) => d >= new Date().toISOString().slice(0,10).replaceAll(\'-\',\'\/\')"').bind_value(disc_until_in):
                                pass
                        with disc_until_in.add_slot("append"):
                            ui.icon("edit_calendar").on("click", disc_menu.open).classes("cursor-pointer text-[#E63312]")

                    def save_discount() -> None:
                        if not disc_item_sel.value:
                            ui.notify("Please select an item.", color="negative")
                            return
                        if not disc_price_in.value:
                            ui.notify("Please enter a discount price.", color="negative")
                            return
                        if disc_until_in.value:
                            try:
                                until_dt = datetime.strptime(disc_until_in.value, "%Y-%m-%d")
                                from datetime import date as _date
                                if until_dt.date() < _date.today():
                                    ui.notify("End date cannot be in the past.", color="negative")
                                    return
                            except ValueError:
                                until_dt = None
                        else:
                            until_dt = None
                        try:
                            admin.set_item_discount(disc_item_sel.value, float(disc_price_in.value), until_dt)
                            disc_item_sel.set_value(None)
                            disc_price_in.set_value(None)
                            disc_until_in.set_value("")
                            ui.notify("Discount set!", color="positive")
                            refresh_discounts_list()
                        except ValueError as e:
                            ui.notify(str(e), color="negative")

                    ui.button("Set Discount", on_click=save_discount).classes("fw-btn fw-btn-primary").style("margin-top:20px;padding:12px 28px")

                # ---- SECTION 3: Active Discounts ----
                ui.html('<div class="font-display text-[28px] text-[#F5F0E8] tracking-[1px] mt-10 mb-4">ACTIVE DISCOUNTS</div>')
                active_discounts_container = ui.column().classes("w-full")

                def refresh_discounts_list() -> None:
                    active_discounts_container.clear()
                    items_with_discount = [i for i in admin.get_all_menu_items() if i.discount_price is not None]
                    with active_discounts_container:
                        if not items_with_discount:
                            ui.label("No active discounts.").classes("text-[#888]")
                            return
                        for it in items_with_discount:
                            eff = _active_price(it.price, it.discount_price, it.discount_until)
                            with ui.element("div").classes("fw-admin-card px-5 py-4"):
                                with ui.row().classes("items-center justify-between flex-wrap gap-3"):
                                    ui.label(it.name).classes("font-bold text-[#F5F0E8] text-[16px]")
                                    with ui.column().classes("gap-[2px]"):
                                        ui.label(f"{eff:.2f} CHF").classes("text-[#E63312] font-bold")
                                        ui.label(f"Regular Price: {it.price:.2f} CHF").classes("text-[11px] text-[#555] line-through")
                                        until_str = it.discount_until.strftime("%d.%m.%Y") if it.discount_until else "permanent"
                                        ui.label(f"Discount until: {until_str}").classes("text-[11px] text-[#888]")

                                    def remove_disc(iid=it.id, iname=it.name) -> None:
                                        admin.set_item_discount(iid, None, None)
                                        ui.notify(f"Discount '{iname}' removed.", color="positive")
                                        refresh_discounts_list()

                                    ui.button("Delete", on_click=remove_disc).classes("fw-btn").style(
                                        "padding:6px 14px;font-size:11px!important;background:transparent;color:#E63312;border:1px solid #E63312"
                                    )

                refresh_discounts_list()

                # ---- SECTION 4: Active Specials ----
                ui.html('<div class="font-display text-[28px] text-[#F5F0E8] tracking-[1px] mt-10 mb-4">ACTIVE SPECIALS</div>')
                active_specials_container = ui.column().classes("w-full")

                def refresh_specials_list() -> None:
                    specials_list_container.clear()
                    active_specials_container.clear()
                    specials = admin.get_specials()
                    with active_specials_container:
                        if not specials:
                            ui.label("No active specials.").classes("text-[#888]")
                            return
                        for sp in specials:
                            eff = _active_price(sp.price, sp.discount_price, sp.discount_until)
                            with ui.element("div").classes("fw-admin-card px-5 py-4"):
                                with ui.row().classes("items-center justify-between flex-wrap gap-3"):
                                    ui.label(sp.name).classes("font-bold text-[#F5F0E8] text-[16px]")
                                    with ui.column().classes("gap-[2px]"):
                                        if sp.discount_price and eff < sp.price:
                                            ui.label(f"{eff:.2f} CHF").classes("text-[#E63312] font-bold")
                                            ui.label(f"Regular Price: {sp.price:.2f} CHF").classes("text-[11px] text-[#555] line-through")
                                            until_str = sp.discount_until.strftime("%d.%m.%Y") if sp.discount_until else "permanent"
                                            ui.label(f"Discount until: {until_str}").classes("text-[11px] text-[#888]")
                                        else:
                                            ui.label(f"{sp.price:.2f} CHF").classes("text-[#E63312] font-bold")
                                    ui.html('<span class="bg-[#F5C842] text-[#111] text-[10px] font-bold px-[10px] py-[3px] tracking-[1px]">SPECIAL</span>')

                                    def delete_special(iid=sp.id, sname=sp.name) -> None:
                                        admin.delete_menu_item(iid)
                                        ui.notify(f"'{sname}' deleted.", color="positive")
                                        refresh_specials_list()

                                    ui.button("Delete", on_click=delete_special).classes("fw-btn").style(
                                        "padding:6px 14px;font-size:11px!important;background:transparent;color:#E63312;border:1px solid #E63312"
                                    )

                refresh_specials_list()

        # ================================================================
        # LOGOUT
        # ================================================================
        @ui.page("/logout")
        def logout_page() -> None:
            app.storage.user.clear()
            ui.navigate.to("/")
