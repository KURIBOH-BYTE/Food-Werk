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

from .controllers import AdminController, AuthController, PaymentController, ShoppingController
from ..services.receipt_service import ReceiptService
from ..services.order_service import OrderService
from .components import (
    STATUS_LABELS, cart_item_row, menu_card, navbar, order_card,
)

# Image map: menu item name (lowercase substring) -> static path
IMAGE_MAP = {
    # Spezifischere Keys ZUERST — sonst trifft "cheese" auf "Cheesecake"
    "cheesecake":  "/static/images/cheesecake.png",
    "cheeseburger":"/static/images/cheeseburger.png",
    "pizza margherita": "/static/images/pizza_margherita.png",
    "pizza vegi":  "/static/images/pizza_vegi.png",
    "pizza vegetariana": "/static/images/pizza_vegi.png",
    "french fries":"/static/images/fries.png",
    "chicken nugget": "/static/images/nuggets.png",
    "iced tea":    "/static/images/eistee.png",
    "milkshake":   "/static/images/milkshake.png",
    # Kürzere Keys danach
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
        receipt: ReceiptService | None = None,
        order_service: OrderService | None = None,
    ) -> None:
        self._auth = auth
        self._shopping = shopping
        self._admin = admin
        self._payment = payment
        self._receipt = receipt
        self._order_service = order_service

    def register(self) -> None:
        """Wire all routes. Called once at startup from application.py."""

        auth = self._auth
        shopping = self._shopping
        admin = self._admin
        payment = self._payment
        receipt_svc = self._receipt
        order_svc = self._order_service

        # ================================================================
        # RECEIPT DOWNLOAD (FastAPI endpoint — returns PDF bytes)
        # ================================================================
        @app.get("/receipt/{order_id}")
        def download_receipt(order_id: int) -> Response:
            if not order_svc or not receipt_svc:
                return Response(content="Receipt service unavailable", status_code=503)
            order = order_svc.get_by_id(order_id)
            if not order:
                return Response(content="Order not found", status_code=404)
            pdf_bytes = receipt_svc.generate_pdf(order)
            return Response(
                content=pdf_bytes,
                media_type="application/pdf",
                headers={"Content-Disposition": f'attachment; filename="quittung_{order_id}.pdf"'},
            )

        # ================================================================
        # HOME
        # ================================================================
        @ui.page("/")
        def home_page() -> None:
            navbar()

            # ---- Hero ----
            ui.html("""
            <div class="fw-hero">
              <div class="fw-hero-bg">FW</div>
              <div class="fw-hero-content">
                <h1 class="fw-hero-title">DEIN<br><span>FOOD.</span><br>DEIN WERK.</h1>
                <p class="fw-hero-sub">Handgemachte Burger, knusprige Sides und frostige Drinks –
                   frisch zubereitet, direkt zu dir.</p>
                <div style="display:flex;gap:16px;flex-wrap:wrap">
                  <a href="/menu" style="background:#E63312;color:#fff;font-family:'Bebas Neue',sans-serif;
                     font-size:16px;letter-spacing:2px;padding:14px 36px;text-decoration:none;
                     transition:background .2s">ZUM MENÜ</a>
                  <a href="/specials" style="background:transparent;color:#F5F0E8;font-family:'Bebas Neue',sans-serif;
                     font-size:16px;letter-spacing:2px;padding:14px 36px;text-decoration:none;
                     border:1.5px solid rgba(245,240,232,0.35)">SPECIALS</a>
                </div>
              </div>
              <img class="fw-hero-img" src="/static/images/menu_collage.png" alt="FoodWerk Menu">
            </div>
            """)

            # ---- Ticker ----
            ticker_text = "&nbsp;&nbsp;FOOD WERK &bull; HANDGEMACHT &bull; FRISCH &bull; TÄGLICH GEÖFFNET &bull; " * 4
            ui.html(f'<div class="fw-ticker"><span class="fw-ticker-inner">{ticker_text}{ticker_text}</span></div>')

            # ---- Stats ----
            ui.html("""
            <div class="fw-stats">
              <div class="fw-stat"><div class="fw-stat-num">14</div><div class="fw-stat-label">Gerichte im Menü</div></div>
              <div class="fw-stat"><div class="fw-stat-num">100%</div><div class="fw-stat-label">Frische Zutaten</div></div>
              <div class="fw-stat"><div class="fw-stat-num">CHF 15</div><div class="fw-stat-label">Ab Preis</div></div>
              <div class="fw-stat"><div class="fw-stat-num">30'</div><div class="fw-stat-label">Lieferzeit</div></div>
            </div>
            """)

            # ---- Featured menu grid ----
            categories = shopping.get_categories()
            all_items: list[dict] = []
            for cat in categories:
                for item in shopping.get_menu_items(category_id=cat.id, available_only=True):
                    img = resolve_image(item.name, item.image_url)
                    all_items.append({"name": item.name, "price": item.price, "image_url": img})

            # pick up to 4 items for the home grid
            featured = all_items[:4]
            if featured:
                ui.html('<div style="background:#0e0e0e"><div style="max-width:1600px;margin:0 auto;padding:80px 60px">')
                ui.html('<div class="fw-section-label">Was wir machen</div>')
                ui.html('<div class="fw-section-title">UNSERE<br>HITS</div>')

                grid_html = '<div class="fw-menu-grid">'
                for idx, it in enumerate(featured):
                    extra_class = "big" if idx == 0 else ""
                    img_tag = f'<img src="{it["image_url"]}" alt="{it["name"]}" loading="lazy">' if it.get("image_url") else ""
                    badge = '<div class="fw-menu-card-badge">Bestseller</div>' if idx == 0 else ""
                    grid_html += f"""
                    <a href="/menu" class="fw-menu-card {extra_class}" style="text-decoration:none">
                      {img_tag}
                      {badge}
                      <div class="fw-menu-card-body">
                        <div class="fw-menu-card-name">{it["name"]}</div>
                        <div class="fw-menu-card-price">CHF {it["price"]:.2f}</div>
                      </div>
                    </a>"""
                grid_html += "</div>"
                ui.html(grid_html)

                ui.html("""
                <div style="text-align:center;margin-top:48px">
                  <a href="/menu" style="background:#E63312;color:#fff;font-family:'Bebas Neue',sans-serif;
                     font-size:16px;letter-spacing:2px;padding:14px 36px;text-decoration:none">
                     GANZES MENÜ →
                  </a>
                </div>
                </div></div>
                """)

        # ================================================================
        # LOGIN / REGISTER
        # ================================================================
        @ui.page("/login")
        def login_page() -> None:
            navbar()
            # Outer wrapper: full-height flex row
            with ui.element("div").style(
                "min-height:100vh;padding-top:64px;display:flex;flex-direction:row"
            ):
                # LEFT — Branding
                with ui.element("div").style(
                    "flex:1;min-width:520px;position:relative;overflow:hidden;"
                    "background:linear-gradient(160deg,#0d0d0d 0%,#1c0a00 40%,#2e1000 70%,#1a0500 100%);"
                    "display:flex;flex-direction:column;justify-content:center;padding:100px 80px;"
                ):
                    ui.html("""
                    <div style="position:absolute;inset:0;pointer-events:none;overflow:hidden">
                      <div style="position:absolute;top:-80px;right:-80px;width:420px;height:420px;
                                  background:radial-gradient(circle,rgba(230,51,18,0.18) 0%,transparent 70%);border-radius:50%"></div>
                      <div style="position:absolute;bottom:-60px;left:-60px;width:300px;height:300px;
                                  background:radial-gradient(circle,rgba(230,51,18,0.10) 0%,transparent 70%);border-radius:50%"></div>
                      <div style="position:absolute;font-family:'Bebas Neue',sans-serif;font-size:32vw;
                                  color:rgba(255,255,255,0.025);line-height:1;top:50%;left:50%;
                                  transform:translate(-50%,-50%);white-space:nowrap;user-select:none">FW</div>
                    </div>

                    <div style="position:relative;z-index:2">
                      <div style="display:inline-block;background:#E63312;color:#fff;font-family:'Bebas Neue',sans-serif;
                                  font-size:11px;letter-spacing:5px;padding:5px 14px;margin-bottom:28px">FOODWERK</div>
                      <div style="font-family:'Bebas Neue',sans-serif;font-size:clamp(80px,8vw,120px);line-height:0.88;color:#F5F0E8;margin-bottom:32px">
                        DEIN<br>KONTO.<br><span style="color:#E63312">DEINE</span><br>WELT.
                      </div>
                      <p style="font-size:17px;color:rgba(245,240,232,0.75);max-width:380px;line-height:1.9;margin:0 0 48px">
                        Login oder Konto erstellen — und sofort bestellen.
                      </p>
                      <div style="display:flex;gap:0;border-top:1px solid rgba(255,255,255,0.1);padding-top:32px">
                        <div style="flex:1;padding-right:32px;border-right:1px solid rgba(255,255,255,0.1)">
                          <div style="font-family:'Bebas Neue',sans-serif;font-size:56px;color:#E63312;line-height:1">14</div>
                          <div style="font-size:12px;font-weight:700;letter-spacing:3px;color:rgba(245,240,232,0.8);text-transform:uppercase;margin-top:6px">Gerichte</div>
                        </div>
                        <div style="flex:1;padding:0 32px;border-right:1px solid rgba(255,255,255,0.1)">
                          <div style="font-family:'Bebas Neue',sans-serif;font-size:56px;color:#E63312;line-height:1">30'</div>
                          <div style="font-size:12px;font-weight:700;letter-spacing:3px;color:rgba(245,240,232,0.8);text-transform:uppercase;margin-top:6px">Lieferzeit</div>
                        </div>
                        <div style="flex:1;padding-left:32px">
                          <div style="font-family:'Bebas Neue',sans-serif;font-size:56px;color:#E63312;line-height:1">100%</div>
                          <div style="font-size:12px;font-weight:700;letter-spacing:3px;color:rgba(245,240,232,0.8);text-transform:uppercase;margin-top:6px">Frisch</div>
                        </div>
                      </div>
                    </div>
                    """)

                # RIGHT — Form
                with ui.element("div").style(
                    "width:520px;flex-shrink:0;"
                    "background:linear-gradient(180deg,#161616 0%,#111111 100%);"
                    "border-left:1px solid rgba(230,51,18,0.15);"
                    "display:flex;flex-direction:column;justify-content:center;padding:72px 64px;"
                ):
                    ui.html('<div style="font-family:\'Bebas Neue\',sans-serif;font-size:42px;color:#F5F0E8;letter-spacing:2px;margin-bottom:4px">WILLKOMMEN</div>')
                    ui.html('<div style="font-size:13px;color:#555;margin-bottom:32px">Login oder Konto erstellen</div>')

                    with ui.tabs().props("color=red indicator-color=red dense") as tabs:
                        login_tab = ui.tab("Login").style("color:#F5F0E8;font-family:'Bebas Neue',sans-serif;font-size:16px;letter-spacing:2px")
                        register_tab = ui.tab("Registrieren").style("color:#F5F0E8;font-family:'Bebas Neue',sans-serif;font-size:16px;letter-spacing:2px")

                    with ui.tab_panels(tabs, value=login_tab).classes("w-full").style("background:transparent;margin-top:24px"):
                        with ui.tab_panel(login_tab).style("padding:0"):
                            email_in = ui.input(
                                "E-Mail",
                                validation={"Bitte eine gültige E-Mail eingeben": lambda v: bool(_EMAIL_RE.match(v.strip())) if v.strip() else True},
                            ).classes("w-full").style("margin-bottom:14px")
                            pw_in = ui.input("Passwort", password=True, password_toggle_button=True).classes("w-full")

                            def do_login() -> None:
                                user = auth.login(email_in.value, pw_in.value)
                                if user:
                                    auth.store_user(user)
                                    ui.notify(f"Willkommen, {user.first_name}!", color="positive")
                                    ui.navigate.to("/")
                                else:
                                    ui.notify("E-Mail oder Passwort falsch.", color="negative")

                            ui.button("Einloggen →", on_click=do_login).classes("fw-btn fw-btn-primary w-full").style("margin-top:24px;padding:15px")

                        with ui.tab_panel(register_tab).style("padding:0"):
                            with ui.row().classes("w-full").style("gap:10px"):
                                fn_in = ui.input(
                                    "Vorname",
                                    validation={
                                        "Pflichtfeld": lambda v: bool(v.strip()),
                                        "Keine Sonderzeichen erlaubt": lambda v: bool(_NAME_RE.match(v.strip())) if v.strip() else True,
                                    },
                                ).style("flex:1")
                                ln_in = ui.input(
                                    "Nachname",
                                    validation={
                                        "Pflichtfeld": lambda v: bool(v.strip()),
                                        "Keine Sonderzeichen erlaubt": lambda v: bool(_NAME_RE.match(v.strip())) if v.strip() else True,
                                    },
                                ).style("flex:1")
                            em_in = ui.input(
                                "E-Mail",
                                validation={"Bitte eine gültige E-Mail eingeben": lambda v: bool(_EMAIL_RE.match(v.strip())) if v.strip() else True},
                            ).classes("w-full").style("margin-top:12px")
                            ph_in = ui.input(
                                "Telefon (optional)",
                                validation={"Ungültige Telefonnummer (z.B. +41 79 123 45 67)": lambda v: bool(_PHONE_RE.match(v.strip())) if v.strip() else True},
                            ).classes("w-full").style("margin-top:12px")
                            pw1_in = ui.input(
                                "Passwort",
                                password=True,
                                password_toggle_button=True,
                                validation={
                                    "Mindestens 8 Zeichen erforderlich": lambda v: len(v) >= 8 if v else True,
                                    "Mindestens ein Sonderzeichen erforderlich (!@#$%...)": lambda v: bool(_SPECIAL_RE.search(v)) if v else True,
                                },
                            ).classes("w-full").style("margin-top:12px")
                            pw2_in = ui.input(
                                "Passwort bestätigen",
                                password=True,
                                password_toggle_button=True,
                                validation={"Passwörter stimmen nicht überein": lambda v: v == pw1_in.value if v else True},
                            ).classes("w-full").style("margin-top:12px")

                            def do_register() -> None:
                                try:
                                    user = auth.register(fn_in.value, ln_in.value, em_in.value, pw1_in.value, ph_in.value or None)
                                    if pw1_in.value != pw2_in.value:
                                        ui.notify("Passwörter stimmen nicht überein.", color="negative")
                                        return
                                    auth.store_user(user)
                                    ui.notify(f"Konto erstellt! Willkommen, {user.first_name}!", color="positive")
                                    ui.navigate.to("/")
                                except ValueError as e:
                                    for msg in str(e).split("\n"):
                                        ui.notify(msg, color="negative")

                            ui.button("Konto erstellen →", on_click=do_register).classes("fw-btn fw-btn-primary w-full").style("margin-top:24px;padding:15px")

        # ================================================================
        # MENU
        # ================================================================
        @ui.page("/menu")
        def menu_page() -> None:
            navbar()
            categories = shopping.get_categories()

            def show_add_dialog(item: dict) -> None:
                with ui.dialog() as dialog, ui.element("div").style(
                    "background:#1a1a1a;border:1px solid rgba(255,255,255,0.1);padding:32px;min-width:380px"
                ):
                    ui.html(f'<div style="font-family:Bebas Neue,sans-serif;font-size:32px;color:#F5F0E8;letter-spacing:1px;margin-bottom:4px">{item["name"]}</div>')
                    if item.get("is_special"):
                        ui.html('<span style="background:#F5C842;color:#111;font-size:9px;font-weight:700;letter-spacing:2px;padding:3px 8px;text-transform:uppercase">SPECIAL</span>')
                    if item.get("description"):
                        ui.label(item["description"]).style("font-size:13px;color:#888;margin-bottom:8px")
                    price = _active_price(item["price"], item.get("discount_price"), item.get("discount_until"))
                    price_html = f'<span style="font-size:20px;font-weight:700;color:#E63312">{price:.2f} CHF</span>'
                    if item.get("discount_price") and price < item["price"]:
                        price_html += f'<span style="font-size:13px;color:#555;text-decoration:line-through;margin-left:8px">{item["price"]:.2f} CHF</span>'
                    ui.html(f'<div style="margin-bottom:16px">{price_html}</div>')

                    if item.get("image_url"):
                        ui.image(item["image_url"]).style("width:100%;height:auto;object-fit:contain;margin-bottom:16px")

                    flavor_select = None
                    if "milkshake" in item["name"].lower() or "milchshake" in item["name"].lower():
                        ui.label("Geschmack wählen:").style("font-weight:700;color:#F5F0E8;margin-bottom:4px")
                        flavor_select = ui.select(["Vanilla", "Chocolate", "Strawberry"], value="Vanilla").classes("w-full")

                    water_select = None
                    if "water" in item["name"].lower() or "wasser" in item["name"].lower():
                        ui.label("Art:").style("font-weight:700;color:#F5F0E8;margin-bottom:4px")
                        water_select = ui.select(["Still", "Sparkling"], value="Still").classes("w-full")

                    ingredient_checks: dict[str, ui.checkbox] = {}
                    if item.get("ingredients"):
                        ui.html('<div style="font-weight:700;color:#F5F0E8;margin:12px 0 4px">Anpassen:</div>')
                        ui.label("Häkchen entfernen zum Weglassen").style("font-size:12px;color:#666;margin-bottom:8px")
                        for ing in item["ingredients"]:
                            cb = ui.checkbox(ing["name"], value=True).style("color:#F5F0E8")
                            ingredient_checks[ing["name"]] = cb

                    with ui.row().style("justify-content:flex-end;gap:12px;margin-top:20px"):
                        ui.button("Abbrechen", on_click=dialog.close).props("flat").style("color:#888")

                        def add_with_options(captured_item=item) -> None:
                            removed = [n for n, cb in ingredient_checks.items() if not cb.value]
                            parts = []
                            if flavor_select and flavor_select.value:
                                parts.append(f"Flavor: {flavor_select.value}")
                            if water_select and water_select.value:
                                parts.append(f"Type: {water_select.value}")
                            if removed:
                                parts.append("Ohne: " + ", ".join(removed))
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
                                if (b) {{ b.textContent = "{count}"; b.style.display = "inline"; }}
                            ''')
                            dialog.close()
                            ui.notify(f"{captured_item['name']} hinzugefügt!", color="positive")

                        ui.button("In den Warenkorb", on_click=add_with_options).classes("fw-btn fw-btn-primary").style("padding:12px 24px")
                dialog.open()

            # Sticky category filter bar — sofort oben sichtbar
            cat_links = ''.join(f'<a href="#{cat.name.lower()}" class="fw-cat-link">{cat.name}</a>' for cat in categories)
            ui.html(f'<div class="fw-cat-bar" style="margin-top:64px"><div class="fw-cat-bar-inner">{cat_links}</div></div>')

            # Kategorien
            for cat in categories:
                items = shopping.get_menu_items(category_id=cat.id, available_only=False)
                if not items:
                    continue
                ui.html(f'<div id="{cat.name.lower()}" class="fw-cat-section"><div class="fw-cat-title"><div class="fw-section-label" style="margin:0">{cat.name}</div><div class="fw-cat-title-line"></div></div></div>')
                with ui.element("div").classes("fw-items-grid").style("padding:0 60px 40px"):
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
            .fw-cart-wrap{margin-top:64px;min-height:calc(100vh - 64px);display:grid;grid-template-columns:1fr 380px;width:100%}
            .fw-cart-left{padding:48px 60px;overflow-y:auto;border-right:1px solid rgba(255,255,255,0.07)}
            .fw-cart-right{background:#1a1a1a;padding:48px 40px;display:flex;flex-direction:column}
            </style>""")

            cart = shopping.get_cart()

            if cart.is_empty:
                with ui.element("div").style(
                    "margin-top:64px;min-height:calc(100vh - 64px);display:flex;flex-direction:column;"
                    "align-items:center;justify-content:center;gap:24px"
                ):
                    ui.html('<div style="text-align:center"><div style="font-family:\'Bebas Neue\',sans-serif;font-size:80px;color:#222;line-height:1">LEER</div><div style="font-size:15px;color:#555;margin-top:8px">Dein Warenkorb ist noch leer.</div></div>')
                    ui.button("→ Zum Menü", on_click=lambda: ui.navigate.to("/menu")).classes("fw-btn fw-btn-primary").style("padding:14px 40px")
                return

            total_lbl = None
            count_lbl = None
            items_div = None

            def _build_items(container, c) -> None:
                container.clear()
                for idx, it in enumerate(c.items):
                    with container:
                        with ui.element("div").style(
                            "display:flex;align-items:center;gap:16px;padding:20px 0;"
                            "border-bottom:1px solid rgba(255,255,255,0.07);width:100%"
                        ):
                            # Name / notes
                            with ui.element("div").style("flex:1;min-width:0"):
                                ui.label(it.name).style(
                                    "font-family:'Bebas Neue',sans-serif;font-size:22px;"
                                    "color:#F5F0E8;letter-spacing:1px;line-height:1.1"
                                )
                                if it.notes:
                                    ui.label(it.notes).style("font-size:12px;color:#666;margin-top:2px")
                            # Qty controls
                            with ui.element("div").style("display:flex;align-items:center;gap:8px"):
                                (
                                    ui.button("−", on_click=lambda i=idx, q=it.quantity: _dec(i, q))
                                    .props("flat")
                                    .style("width:28px;height:28px;min-width:0;padding:0;"
                                           "border:1px solid rgba(255,255,255,0.25);color:#F5F0E8;"
                                           "font-size:18px;line-height:1")
                                )
                                ui.label(str(it.quantity)).style(
                                    "min-width:24px;text-align:center;font-size:16px;font-weight:700;color:#F5F0E8"
                                )
                                (
                                    ui.button("+", on_click=lambda i=idx, q=it.quantity: _inc(i, q))
                                    .props("flat")
                                    .style("width:28px;height:28px;min-width:0;padding:0;"
                                           "border:1px solid rgba(255,255,255,0.25);color:#F5F0E8;"
                                           "font-size:18px;line-height:1")
                                )
                            # Price
                            ui.label(f"{it.total:.2f} CHF").style(
                                "font-size:16px;font-weight:700;color:#E63312;white-space:nowrap"
                            )
                            # Delete
                            (
                                ui.button("✕", on_click=lambda i=idx: _remove(i))
                                .props("flat")
                                .style("color:#444;min-width:0;padding:4px;font-size:16px")
                            )

            def _refresh() -> None:
                nonlocal total_lbl, count_lbl, items_div
                c = shopping.get_cart()
                if c.is_empty:
                    ui.navigate.to("/cart")
                    return
                _build_items(items_div, c)
                total_lbl.set_text(f"{c.total:.2f} CHF")
                count_lbl.set_text(f"{c.item_count} Artikel")

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
                # LEFT
                with ui.element("div").classes("fw-cart-left"):
                    ui.html('<div style="font-size:11px;font-weight:700;letter-spacing:4px;text-transform:uppercase;color:#E63312;margin-bottom:8px">Deine Auswahl</div>')
                    ui.html('<div style="font-family:\'Bebas Neue\',sans-serif;font-size:52px;line-height:0.95;color:#F5F0E8;margin-bottom:32px">WARENKORB</div>')
                    with ui.element("div").style("width:100%") as items_div:
                        _build_items(items_div, cart)

                # RIGHT
                with ui.element("div").classes("fw-cart-right"):
                    ui.html('<div style="font-family:\'Bebas Neue\',sans-serif;font-size:28px;color:#F5F0E8;letter-spacing:1px;margin-bottom:24px">BESTELLÜBERSICHT</div>')
                    count_lbl = ui.label(f"{cart.item_count} Artikel").style("font-size:12px;color:#555;letter-spacing:2px;text-transform:uppercase;margin-bottom:20px")
                    ui.html('<div style="border-top:1px solid rgba(255,255,255,0.07);margin-bottom:20px"></div>')
                    ui.html('<div style="display:flex;justify-content:space-between;align-items:baseline;margin-bottom:6px"><span style="font-size:13px;color:#888">Zwischensumme</span></div>')
                    total_lbl = ui.label(f"{cart.total:.2f} CHF").style("font-family:'Bebas Neue',sans-serif;font-size:32px;color:#E63312;letter-spacing:1px;margin-bottom:8px")
                    ui.html('<div style="font-size:12px;color:#444;margin-bottom:28px">Liefergebühr wird beim Checkout berechnet.</div>')
                    ui.html('<div style="border-top:1px solid rgba(255,255,255,0.07);margin-bottom:28px"></div>')
                    ui.button("Zur Kasse →", on_click=lambda: ui.navigate.to("/checkout")).classes("fw-btn fw-btn-primary").style("width:100%;padding:16px;font-size:14px!important")
                    ui.button("← Weiter einkaufen", on_click=lambda: ui.navigate.to("/menu")).props("flat").style("width:100%;color:#555;margin-top:12px;padding:10px")

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

            with ui.element("div").style("padding-top:64px;background:#111111;width:100%"):
                ui.html('<div style="background:#1a1a1a;padding:20px 60px;border-bottom:1px solid rgba(255,255,255,0.07)"><div style="font-size:11px;font-weight:700;letter-spacing:4px;text-transform:uppercase;color:#E63312;margin-bottom:6px">Fast geschafft</div><div style="font-family:\'Bebas Neue\',sans-serif;font-size:40px;line-height:1;color:#F5F0E8">KASSE</div></div>')
            with ui.element("div").style("padding:24px 60px;max-width:640px;margin:0 auto;background:#111111"):
                ui.html(f'<div style="font-family:Bebas Neue,sans-serif;font-size:24px;color:#E63312;margin-bottom:16px">Total: {cart.total:.2f} CHF</div>')

                order_type_toggle = ui.toggle(["delivery", "pickup"], value="pickup").props("color=red")
                address_box = ui.column().classes("w-full").style("margin-top:16px")
                pickup_box = ui.column().classes("w-full").style("margin-top:16px")
                notes_in = ui.textarea("Notizen (optional)").classes("w-full").style("margin-top:12px;font-size:16px").props("outlined rows=2")

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
                            ui.label("Lieferadresse").style("font-family:Bebas Neue,sans-serif;font-size:22px;color:#F5F0E8;margin-bottom:16px")

                            new_form = ui.column().classes("w-full")

                            if saved:
                                ui.label("Gespeicherte Adressen").style("font-size:11px;font-weight:700;letter-spacing:3px;color:#E63312;text-transform:uppercase;margin-bottom:8px")
                                for addr in saved:
                                    line = f"{addr.street} {addr.house_nr}, {addr.postal_code} {addr.city}"
                                    if addr.label:
                                        line = f"{addr.label} — {line}"

                                    def select_addr(a=addr) -> None:
                                        selected_address_id["value"] = a.id
                                        new_form.set_visibility(False)
                                        ui.notify(f"Adresse ausgewählt: {a.street} {a.house_nr}", color="positive")

                                    with ui.element("div").style(
                                        "background:#1a1a1a;border:1px solid rgba(255,255,255,0.08);"
                                        "padding:14px 18px;margin-bottom:8px;cursor:pointer;"
                                        "display:flex;justify-content:space-between;align-items:center"
                                    ):
                                        ui.label(line).style("color:#F5F0E8;font-size:14px")
                                        ui.button("Auswählen", on_click=select_addr).classes("fw-btn fw-btn-primary").style("padding:6px 16px;font-size:11px!important")

                                ui.html('<div style="border-top:1px solid rgba(255,255,255,0.07);margin:20px 0"></div>')
                                ui.label("Oder neue Adresse eingeben").style("font-size:11px;font-weight:700;letter-spacing:3px;color:#888;text-transform:uppercase;margin-bottom:12px")

                            with new_form:
                                label_in = ui.input("Bezeichnung (optional, z.B. Zuhause)").classes("w-full").style("margin-bottom:8px;font-size:16px").props("outlined dense=false")
                                street_in = ui.input(
                                    "Strasse *",
                                    validation={
                                        "Pflichtfeld": lambda v: bool(v.strip()),
                                        "Strasse muss Buchstaben enthalten": lambda v: bool(re.search(r'[a-zA-ZÀ-öø-ÿ]', v.strip())) if v.strip() else True,
                                    },
                                ).classes("w-full").style("font-size:16px").props("outlined dense=false")
                                house_nr_in = ui.input(
                                    "Hausnummer *",
                                    validation={
                                        "Pflichtfeld": lambda v: bool(v.strip()),
                                        "Muss eine Zahl sein (z.B. 12 oder 12a)": lambda v: bool(re.match(r'^\d+[a-zA-Z]?$', v.strip())) if v.strip() else True,
                                    },
                                ).classes("w-full").style("margin-top:8px;font-size:16px").props("outlined dense=false")
                                floor_in = ui.input("Stockwerk (optional)").classes("w-full").style("margin-top:8px;font-size:16px").props("outlined dense=false")
                                city_in = ui.input(
                                    "Stadt *",
                                    validation={
                                        "Pflichtfeld": lambda v: bool(v.strip()),
                                        "Stadt darf nur Buchstaben enthalten": lambda v: bool(re.match(r'^[a-zA-ZÀ-öø-ÿ\s\-]+$', v.strip())) if v.strip() else True,
                                    },
                                ).classes("w-full").style("margin-top:8px;font-size:16px").props("outlined dense=false")
                                postal_in = ui.input(
                                    "Postleitzahl *",
                                    validation={
                                        "Pflichtfeld": lambda v: bool(v.strip()),
                                        "Muss 4-stellig sein (z.B. 8001)": lambda v: bool(re.match(r'^\d{4}$', v.strip())) if v.strip() else True,
                                    },
                                ).classes("w-full").style("margin-top:8px;font-size:16px").props("outlined dense=false")

                    else:
                        with pickup_box:
                            ui.label("Abholzeit").style("font-family:Bebas Neue,sans-serif;font-size:22px;color:#F5F0E8;margin-bottom:12px")
                            from datetime import datetime as _now, timedelta as _td
                            _base = _now.now() + _td(minutes=30)
                            _base = _base.replace(second=0, microsecond=0)
                            _mins = ((_base.minute + 14) // 15) * 15
                            if _mins >= 60:
                                _base = _base.replace(hour=_base.hour + 1, minute=_mins - 60)
                            else:
                                _base = _base.replace(minute=_mins)
                            _slots = [(_base + _td(minutes=15 * i)).strftime("%H:%M") for i in range(8)]
                            pickup_time_in = ui.select(_slots, value=_slots[0], label="Abholzeit wählen").classes("w-full").style("font-size:16px").props("outlined")

                order_type_toggle.on_value_change(lambda: update_form())
                update_form()

                def go_to_payment() -> None:
                    addr_id = selected_address_id["value"]

                    if order_type_toggle.value == "pickup":
                        if not pickup_time_in or not pickup_time_in.value:
                            ui.notify("Bitte eine Abholzeit auswählen.", color="negative")
                            return

                    if order_type_toggle.value == "delivery" and not addr_id:
                        missing = []
                        if not street_in or not street_in.value.strip(): missing.append("Strasse")
                        if not house_nr_in or not house_nr_in.value.strip(): missing.append("Hausnummer")
                        if not city_in or not city_in.value.strip(): missing.append("Stadt")
                        if not postal_in or not postal_in.value.strip(): missing.append("Postleitzahl")
                        if missing:
                            ui.notify(f"Pflichtfeld(er) fehlen: {', '.join(missing)}", color="negative")
                            return
                        if not re.search(r'[a-zA-ZÀ-öø-ÿ]', street_in.value.strip()):
                            ui.notify("Strasse muss Buchstaben enthalten.", color="negative")
                            return
                        if not re.match(r'^\d+[a-zA-Z]?$', house_nr_in.value.strip()):
                            ui.notify("Hausnummer muss eine Zahl sein (z.B. 12 oder 12a).", color="negative")
                            return
                        if not re.match(r'^[a-zA-ZÀ-öø-ÿ\s\-]+$', city_in.value.strip()):
                            ui.notify("Stadt darf nur Buchstaben enthalten.", color="negative")
                            return
                        if not re.match(r'^\d{4}$', postal_in.value.strip()):
                            ui.notify("Postleitzahl muss 4-stellig sein (z.B. 8001).", color="negative")
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

                ui.button("Weiter zur Zahlung →", icon="credit_card", on_click=go_to_payment).classes("fw-btn fw-btn-primary").style("margin-top:20px;padding:16px 32px;width:100%;font-size:15px!important")

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

            with ui.element("div").style("padding-top:64px;background:#111111;width:100%"):
                ui.html('<div style="background:#1a1a1a;padding:20px 60px;border-bottom:1px solid rgba(255,255,255,0.07)"><div style="font-size:11px;font-weight:700;letter-spacing:4px;text-transform:uppercase;color:#E63312;margin-bottom:6px">Sichere Zahlung</div><div style="font-family:\'Bebas Neue\',sans-serif;font-size:40px;line-height:1;color:#F5F0E8">BEZAHLEN</div></div>')

            with ui.element("div").style("padding:24px 60px;max-width:600px;margin:0 auto;background:#111111"):
                ui.html(f'<div style="font-family:Bebas Neue,sans-serif;font-size:28px;color:#E63312;margin-bottom:8px">Betrag: {cart.total:.2f} CHF</div>')
                ui.html('<div style="font-size:13px;color:#666;margin-bottom:24px">Du wirst zu Stripe weitergeleitet, um die Zahlung sicher abzuschliessen.</div>')

                with ui.element("div").style("background:#1a1a1a;border:1px solid rgba(255,255,255,0.08);padding:24px;margin-bottom:24px"):
                    ui.label("Bestellübersicht").style("font-family:Bebas Neue,sans-serif;font-size:20px;color:#F5F0E8;margin-bottom:12px")
                    for item in cart.items:
                        ui.label(f"{item.quantity}× {item.name} — {item.total:.2f} CHF").style("font-size:13px;color:#aaa")
                    ui.html('<div style="border-top:1px solid rgba(255,255,255,0.07);margin:12px 0"></div>')
                    ui.label(f"Total: {cart.total:.2f} CHF").style("font-weight:700;color:#E63312")

                error_label = ui.label("").style("color:#E63312;font-size:13px;margin-bottom:12px")

                def go_to_stripe() -> None:
                    try:
                        url = payment.create_stripe_session(base_url="http://localhost:8080")
                        ui.navigate.to(url)
                    except ValueError as e:
                        error_label.set_text(str(e))

                with ui.row().style("justify-content:space-between;align-items:center"):
                    ui.button("← Zurück", on_click=lambda: ui.navigate.to("/checkout")).props("flat").style("color:#888")
                    ui.button("Mit Stripe bezahlen", icon="lock", on_click=go_to_stripe).classes("fw-btn fw-btn-primary").style("padding:14px 32px;font-size:14px!important")

                ui.html("""
                <div style="display:flex;align-items:center;gap:8px;margin-top:20px;color:#555;font-size:12px">
                  <span>🔒</span>
                  <span>Sichere Zahlung über Stripe — deine Kartendaten werden nie auf unseren Servern gespeichert.</span>
                </div>
                """)

        # ================================================================
        # PAYMENT SUCCESS — Stripe redirects here after payment
        # ================================================================
        @ui.page("/payment/success")
        def payment_success_page() -> None:
            navbar()
            # Create the order now that Stripe confirmed payment
            order = payment.complete_order()
            order_id = order.id if order else app.storage.user.get("last_order_id")

            ui.html("""
            <div class="fw-page" style="display:flex;align-items:center;justify-content:center;min-height:80vh">
              <div style="text-align:center;padding:80px 40px">
                <div style="font-size:80px;margin-bottom:24px">✅</div>
                <div style="font-family:Bebas Neue,sans-serif;font-size:72px;color:#639922;line-height:1;margin-bottom:16px">BEZAHLT!</div>
                <div style="font-size:17px;color:rgba(245,240,232,0.65);margin-bottom:40px">
                  Zahlung erfolgreich — deine Bestellung ist bei uns eingegangen.<br>Wir bereiten sie frisch vor!
                </div>
            """)
            with ui.row().style("justify-content:center;gap:16px"):
                ui.button("Bestellung verfolgen", on_click=lambda: ui.navigate.to("/profile")).classes("fw-btn fw-btn-primary").style("padding:14px 28px")
                ui.button("Zurück zum Menü", on_click=lambda: ui.navigate.to("/menu")).classes("fw-btn fw-btn-outline").style("padding:14px 28px")
            ui.html("</div></div>")

        # ================================================================
        # PAYMENT CANCEL
        # ================================================================
        @ui.page("/payment/cancel")
        def payment_cancel_page() -> None:
            navbar()
            ui.html("""
            <div class="fw-page" style="display:flex;align-items:center;justify-content:center;min-height:80vh">
              <div style="text-align:center;padding:80px 40px">
                <div style="font-size:80px;margin-bottom:24px">❌</div>
                <div style="font-family:Bebas Neue,sans-serif;font-size:72px;color:#E63312;line-height:1;margin-bottom:16px">ABGEBROCHEN</div>
                <div style="font-size:17px;color:rgba(245,240,232,0.65);margin-bottom:40px">Keine Gebühr wurde erhoben. Dein Warenkorb ist noch vollständig.</div>
            """)
            with ui.row().style("justify-content:center;gap:16px"):
                ui.button("Zum Warenkorb", on_click=lambda: ui.navigate.to("/cart")).classes("fw-btn fw-btn-primary").style("padding:14px 28px")
                ui.button("Zum Menü", on_click=lambda: ui.navigate.to("/menu")).classes("fw-btn fw-btn-outline").style("padding:14px 28px")
            ui.html("</div></div>")

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
            with ui.element("div").style("padding-top:64px;background:#111111;width:100%"):
                ui.html('<div style="background:#1a1a1a;padding:20px 60px;border-bottom:1px solid rgba(255,255,255,0.07)"><div style="font-size:11px;font-weight:700;letter-spacing:4px;text-transform:uppercase;color:#E63312;margin-bottom:6px">Deine Bestellung</div><div style="font-family:\'Bebas Neue\',sans-serif;font-size:40px;line-height:1;color:#F5F0E8">STATUS</div></div>')
            with ui.element("div").style("padding:24px 60px;max-width:640px;margin:0 auto;background:#111111"):
                if not order:
                    ui.label("Bestellung nicht gefunden.").style("color:#E63312;font-size:18px")
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

            # Hero header bar
            ui.html("""
            <div style="margin-top:64px;background:#1a0800;border-bottom:1px solid rgba(230,51,18,0.2);padding:48px 60px">
              <div style="max-width:1600px;margin:0 auto">
                <div style="font-size:11px;font-weight:700;letter-spacing:4px;text-transform:uppercase;color:#E63312;margin-bottom:10px">Nicht verpassen</div>
                <div style="font-family:'Bebas Neue',sans-serif;font-size:clamp(48px,6vw,80px);line-height:0.95;color:#F5F0E8">AKTUELLE<br>SPECIALS</div>
              </div>
            </div>
            """)

            if not specials:
                ui.html('<div style="text-align:center;padding:120px 0"><div style="font-family:Bebas Neue,sans-serif;font-size:48px;color:#333">KEINE SPECIALS AKTIV</div></div>')
                with ui.element("div").style("display:flex;justify-content:center"):
                    ui.button("Zum Menü", on_click=lambda: ui.navigate.to("/menu")).classes("fw-btn fw-btn-primary").style("padding:14px 32px")
            else:
                def show_special_dialog(item: dict) -> None:
                    with ui.dialog() as dialog, ui.element("div").style(
                        "background:#1a1a1a;border:1px solid rgba(255,255,255,0.1);padding:32px;min-width:380px"
                    ):
                        ui.html('<span style="background:#F5C842;color:#111;font-size:9px;font-weight:700;letter-spacing:2px;padding:3px 8px;text-transform:uppercase">SPECIAL</span>')
                        ui.html(f'<div style="font-family:Bebas Neue,sans-serif;font-size:32px;color:#F5F0E8;letter-spacing:1px;margin:8px 0 4px">{item["name"]}</div>')
                        if item.get("description"):
                            ui.label(item["description"]).style("font-size:13px;color:#888;margin-bottom:8px")
                        eff = _active_price(item["price"], item.get("discount_price"), item.get("discount_until"))
                        price_html = f'<span style="font-size:20px;font-weight:700;color:#E63312">{eff:.2f} CHF</span>'
                        if item.get("discount_price") and eff < item["price"]:
                            price_html += f'<span style="font-size:13px;color:#555;text-decoration:line-through;margin-left:8px">{item["price"]:.2f} CHF</span>'
                        ui.html(f'<div style="margin-bottom:16px">{price_html}</div>')
                        if item.get("image_url"):
                            ui.image(item["image_url"]).style("width:100%;height:auto;object-fit:contain;margin-bottom:16px")
                        with ui.row().style("justify-content:flex-end;gap:12px;margin-top:20px"):
                            ui.button("Abbrechen", on_click=dialog.close).props("flat").style("color:#888")
                            def add_sp(i=item):
                                p = _active_price(i["price"], i.get("discount_price"), i.get("discount_until"))
                                shopping.add_to_cart(i["id"], i["name"], p)
                                count = shopping.get_cart().item_count
                                ui.run_javascript(f'''
                                    var b = document.getElementById("fw-cart-badge");
                                    if (b) {{ b.textContent = "{count}"; b.style.display = "inline"; }}
                                ''')
                                dialog.close()
                                ui.notify(f"{i['name']} hinzugefügt!", color="positive")
                            ui.button("In den Warenkorb", on_click=add_sp).classes("fw-btn fw-btn-primary").style("padding:12px 24px")
                    dialog.open()

                with ui.element("div").style("max-width:1600px;margin:0 auto;padding:40px 60px"):
                    with ui.element("div").classes("fw-items-grid"):
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

            with ui.element("div").style("padding-top:64px;background:#111111;width:100%"):
                ui.html(f'<div style="background:#1a1a1a;padding:20px 60px;border-bottom:1px solid rgba(255,255,255,0.07)"><div style="font-size:11px;font-weight:700;letter-spacing:4px;text-transform:uppercase;color:#E63312;margin-bottom:6px">Dein Konto</div><div style="font-family:\'Bebas Neue\',sans-serif;font-size:40px;line-height:1;color:#F5F0E8">{user_data["first_name"].upper()} {user_data.get("last_name","").upper()}</div><div style="font-size:14px;color:#888;margin-top:6px">{user_data["email"]}</div></div>')
            with ui.element("div").style("padding:24px 60px;max-width:820px;margin:0 auto;background:#111111"):
                ui.html('<div style="font-family:Bebas Neue,sans-serif;font-size:36px;color:#F5F0E8;letter-spacing:1px;margin-bottom:24px">DEINE BESTELLUNGEN</div>')
                if not orders:
                    ui.label("Noch keine Bestellungen.").style("color:#888;font-size:15px")
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

            with ui.element("div").style("padding-top:64px;background:#111111;width:100%"):
                ui.html('<div style="background:#1a1a1a;padding:20px 60px;border-bottom:1px solid rgba(255,255,255,0.07)"><div style="font-size:11px;font-weight:700;letter-spacing:4px;text-transform:uppercase;color:#E63312;margin-bottom:6px">Verwaltung</div><div style="font-family:\'Bebas Neue\',sans-serif;font-size:40px;line-height:1;color:#F5F0E8">ADMIN DASHBOARD</div></div>')
            with ui.element("div").style("max-width:1600px;margin:0 auto;padding:24px 60px;background:#111111"):
                with ui.row().style("gap:12px;margin-bottom:48px"):
                    ui.button("Menü verwalten", on_click=lambda: ui.navigate.to("/admin/menu")).classes("fw-btn fw-btn-primary").style("padding:12px 24px")
                    ui.button("Bestellungen", on_click=lambda: ui.navigate.to("/admin/orders")).classes("fw-btn fw-btn-outline").style("padding:12px 24px")
                    if user_data.get("role") == "admin":
                        ui.button("Specials", on_click=lambda: ui.navigate.to("/admin/specials")).classes("fw-btn fw-btn-outline").style("padding:12px 24px")

                ui.html('<div style="font-family:Bebas Neue,sans-serif;font-size:32px;color:#F5F0E8;letter-spacing:1px;margin-bottom:20px">AKTIVE BESTELLUNGEN</div>')

                active = [o for o in admin.get_all_orders() if o.status in ("pending", "preparing", "ready")]
                if not active:
                    ui.label("Keine aktiven Bestellungen.").style("color:#888")
                else:
                    for order in active:
                        sc = {"pending": "#F5C842", "preparing": "#378ADD", "ready": "#639922"}.get(order.status, "#888")
                        with ui.element("div").classes("fw-admin-card").style("padding:20px;margin-bottom:12px"):
                            with ui.row().style("align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px"):
                                ui.html(f'<div style="font-family:Bebas Neue,sans-serif;font-size:22px;color:#F5F0E8">#{order.id} — {order.user.first_name} {order.user.last_name}</div>')
                                ui.html(f'<span style="background:{sc};color:#111;font-size:10px;font-weight:700;padding:4px 12px;letter-spacing:2px;text-transform:uppercase">{order.status.upper()}</span>')
                                ui.label("Lieferung" if order.order_type == "delivery" else "Abholung").style("color:#888;font-size:13px")
                                ui.label(f"{order.total_price:.2f} CHF").style("font-weight:700;color:#E63312")

                                next_map = {
                                    "pending": "preparing",
                                    "preparing": "ready",
                                    "ready": "delivered" if order.order_type == "delivery" else "collected",
                                }

                                def advance(oid=order.id, cur=order.status) -> None:
                                    if cur in next_map:
                                        admin.update_order_status(oid, next_map[cur])
                                        ui.navigate.to("/admin")

                                ui.button("Nächster Status →", on_click=advance).classes("fw-btn fw-btn-primary").style("padding:8px 18px;font-size:11px!important")

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

            with ui.element("div").style("padding-top:64px;background:#111111;width:100%"):
                ui.html('<div style="background:#1a1a1a;padding:20px 60px;border-bottom:1px solid rgba(255,255,255,0.07)"><div style="font-size:11px;font-weight:700;letter-spacing:4px;text-transform:uppercase;color:#E63312;margin-bottom:6px">Verwaltung</div><div style="font-family:\'Bebas Neue\',sans-serif;font-size:40px;line-height:1;color:#F5F0E8">MENÜ VERWALTEN</div></div>')
            categories = admin.get_categories()
            items_container = ui.column().classes("w-full").style("max-width:1600px;margin:0 auto;padding:24px 60px;background:#111111")

            def refresh_items() -> None:
                items_container.clear()
                with items_container:
                    for cat in categories:
                        items = admin.get_menu_items_by_category(cat.id)
                        if not items:
                            continue
                        ui.html(f'<div style="font-family:Bebas Neue,sans-serif;font-size:28px;color:#F5F0E8;letter-spacing:1px;margin:24px 0 12px">{cat.name.upper()}</div>')
                        for item in items:
                            avail_color = "#639922" if item.is_available else "#E63312"
                            avail_label = "Verfügbar" if item.is_available else "Ausverkauft"
                            with ui.element("div").classes("fw-admin-card").style("padding:16px 20px"):
                                with ui.row().style("align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px"):
                                    ui.label(item.name).style("font-weight:700;color:#F5F0E8;font-size:16px")
                                    ui.label(f"{item.price:.2f} CHF").style("color:#E63312;font-weight:700")
                                    ui.html(f'<span style="background:{avail_color};color:#fff;font-size:10px;font-weight:700;padding:3px 10px;letter-spacing:1px">{avail_label}</span>')

                                    def toggle(iid=item.id, cur=item.is_available) -> None:
                                        admin.set_item_availability(iid, not cur)
                                        refresh_items()

                                    btn_label = "Ausverkauft markieren" if item.is_available else "Verfügbar markieren"
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

            with ui.element("div").style("padding-top:64px;background:#111111;width:100%"):
                ui.html('<div style="background:#1a1a1a;padding:20px 60px;border-bottom:1px solid rgba(255,255,255,0.07)"><div style="font-size:11px;font-weight:700;letter-spacing:4px;text-transform:uppercase;color:#E63312;margin-bottom:6px">Verwaltung</div><div style="font-family:\'Bebas Neue\',sans-serif;font-size:40px;line-height:1;color:#F5F0E8">BESTELLUNGEN VERWALTEN</div></div>')
            with ui.element("div").style("max-width:1600px;margin:0 auto;padding:24px 60px;background:#111111"):
                status_filter = ui.select(
                    options={"all": "Alle", "pending": "Ausstehend", "preparing": "In Zubereitung",
                             "ready": "Bereit", "delivered": "Geliefert", "collected": "Abgeholt"},
                    value="all", label="Status filtern",
                ).style("min-width:200px;margin-bottom:24px")

                orders_container = ui.column().classes("w-full")

                def refresh_orders() -> None:
                    orders_container.clear()
                    status = None if status_filter.value == "all" else status_filter.value
                    orders = admin.get_all_orders(status=status)
                    with orders_container:
                        if not orders:
                            ui.label("Keine Bestellungen gefunden.").style("color:#888")
                            return
                        for order in orders:
                            with ui.element("div").classes("fw-admin-card").style("padding:16px 20px"):
                                with ui.row().style("align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px"):
                                    ui.label(f"#{order.id}").style("font-family:Bebas Neue,sans-serif;font-size:22px;color:#F5F0E8")
                                    ui.label(f"{order.user.first_name} {order.user.last_name}").style("color:#aaa")
                                    ui.label("Lieferung" if order.order_type == "delivery" else "Abholung").style("color:#888;font-size:13px")
                                    ui.label(f"{order.total_price:.2f} CHF").style("font-weight:700;color:#E63312")
                                    ui.label(order.created_at.strftime("%d.%m.%Y %H:%M")).style("font-size:12px;color:#555")

                                    status_sel = ui.select(
                                        options=list(STATUS_LABELS.keys()),
                                        value=order.status, label="Status",
                                    ).style("min-width:140px")

                                    def save_status(oid=order.id, sel=status_sel) -> None:
                                        admin.update_order_status(oid, sel.value)
                                        ui.notify(f"Status #{oid} aktualisiert.", color="positive")

                                    ui.button("Speichern", on_click=save_status).classes("fw-btn fw-btn-primary").style("padding:6px 16px;font-size:11px!important")

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

            ui.add_head_html("""<style>
            .q-date { background:#1a1a1a !important; color:#F5F0E8 !important; border:1px solid rgba(255,255,255,0.1); }
            .q-date__header { background:#E63312 !important; }
            .q-date__header-title, .q-date__header-subtitle { color:#fff !important; }
            .q-date__calendar-item .q-btn { color:#F5F0E8 !important; }
            .q-date__calendar-item .q-btn.bg-primary { background:#E63312 !important; color:#fff !important; }
            .q-date__navigation .q-btn { color:#F5F0E8 !important; }
            .q-date__years-item .q-btn, .q-date__months-item .q-btn { color:#F5F0E8 !important; }
            .q-date__calendar-weekdays > div { color:#888 !important; }
            .q-date__today .q-btn { border:1px solid #E63312 !important; }
            </style>""")

            with ui.element("div").style("padding-top:64px;background:#111111;width:100%"):
                ui.html('<div style="background:#1a1a1a;padding:20px 60px;border-bottom:1px solid rgba(255,255,255,0.07)"><div style="font-size:11px;font-weight:700;letter-spacing:4px;text-transform:uppercase;color:#E63312;margin-bottom:6px">Verwaltung</div><div style="font-family:\'Bebas Neue\',sans-serif;font-size:40px;line-height:1;color:#F5F0E8">SPECIALS & RABATTE</div></div>')
            all_items = admin.get_all_menu_items()
            item_options = {i.id: f"{i.name} ({i.price:.2f} CHF)" for i in all_items}

            IMAGES_DIR = _Path(__file__).parent.parent.parent / "frontend" / "static" / "images"

            with ui.element("div").style("padding:24px 60px;max-width:960px;margin:0 auto;background:#111111"):

                # ---- SECTION 1: Neues Special erstellen ----
                ui.html('<div style="font-family:Bebas Neue,sans-serif;font-size:28px;color:#F5F0E8;letter-spacing:1px;margin-bottom:16px">NEUES SPECIAL ERSTELLEN</div>')
                ui.html('<div style="font-size:13px;color:#888;margin-bottom:20px">Fülle alle Pflichtfelder (*) aus um ein neues Special zu erstellen.</div>')

                categories = admin.get_categories()
                cat_options = {c.id: c.name for c in categories}

                specials_list_container = ui.column().classes("w-full")
                new_uploaded_url: dict = {"value": None}

                with ui.element("div").classes("fw-admin-card").style("padding:28px"):
                    sp_name_in = ui.input("Name *").classes("w-full").props("outlined dense=false").style("font-size:16px")
                    sp_cat_in = ui.select(options=cat_options, label="Kategorie *").classes("w-full").style("margin-top:12px;font-size:16px").props("outlined")
                    sp_price_in = ui.number("Normalpreis (CHF) *", min=0.01, step=0.10).classes("w-full").style("margin-top:12px;font-size:16px").props("outlined dense=false")
                    sp_desc_in = ui.textarea("Beschreibung (optional)").classes("w-full").style("margin-top:12px;font-size:16px").props("outlined rows=2")
                    sp_disc_in = ui.number("Rabattpreis (CHF, optional)", min=0.01, step=0.10).classes("w-full").style("margin-top:12px;font-size:16px").props("outlined dense=false")

                    with ui.input("Rabatt gültig bis (optional)").classes("w-full").style("margin-top:12px;font-size:16px").props("outlined dense=false") as sp_until_in:
                        with ui.menu().props("no-parent-event") as sp_menu:
                            with ui.date().props(':options="(d) => d >= new Date().toISOString().slice(0,10).replaceAll(\'-\',\'\/\')"').bind_value(sp_until_in):
                                pass
                        with sp_until_in.add_slot("append"):
                            ui.icon("edit_calendar").on("click", sp_menu.open).classes("cursor-pointer").style("color:#E63312")

                    ui.html('<div style="font-size:13px;color:#aaa;margin:16px 0 8px">Bild hochladen (optional)</div>')
                    new_upload_preview = ui.html("").style("margin-top:8px")

                    def handle_new_image(e) -> None:
                        suffix = _Path(e.name).suffix.lower()
                        filename = f"special_new_{int(__import__('time').time())}{suffix}"
                        dest = IMAGES_DIR / filename
                        dest.write_bytes(e.content.read())
                        new_uploaded_url["value"] = f"/static/images/{filename}"
                        new_upload_preview.set_content(
                            f'<img src="{new_uploaded_url["value"]}" style="max-height:120px;border-radius:8px;margin-top:8px;border:1px solid #333">'
                        )
                        ui.notify("Bild hochgeladen.", color="positive")

                    ui.upload(label="Bild wählen", on_upload=handle_new_image, auto_upload=True, max_file_size=10_000_000,
                    ).props('accept=".png,.jpg,.jpeg,.webp" flat bordered').classes("w-full").style("background:#1a1a1a;border:1px solid #333;border-radius:8px")

                    def create_special() -> None:
                        errors = []
                        if not sp_name_in.value or not sp_name_in.value.strip():
                            errors.append("Name")
                        if not sp_cat_in.value:
                            errors.append("Kategorie")
                        if not sp_price_in.value or float(sp_price_in.value) <= 0:
                            errors.append("Normalpreis")
                        if errors:
                            ui.notify(f"Pflichtfeld(er) fehlen: {', '.join(errors)}", color="negative")
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
                            ui.notify(f"Special '{item.name}' erstellt!", color="positive")
                            refresh_specials_list()
                        except ValueError as e:
                            ui.notify(str(e), color="negative")

                    ui.button("Special erstellen →", on_click=create_special).classes("fw-btn fw-btn-primary").style("margin-top:20px;padding:14px 32px;width:100%")

                # ---- SECTION 2: Rabatt festlegen ----
                ui.html('<div style="font-family:Bebas Neue,sans-serif;font-size:28px;color:#F5F0E8;letter-spacing:1px;margin:40px 0 16px">RABATT FESTLEGEN</div>')
                ui.html('<div style="font-size:13px;color:#888;margin-bottom:20px">Setzt einen Rabattpreis für einen Artikel. Enddatum leer lassen = dauerhaft aktiv bis zur manuellen Änderung.</div>')

                with ui.element("div").classes("fw-admin-card").style("padding:28px"):
                    disc_item_sel = ui.select(options=item_options, label="Menüartikel wählen").classes("w-full")
                    disc_price_in = ui.number(
                        "Rabattpreis (CHF)", min=0.01, step=0.10,
                        validation={"Preis muss grösser als 0 sein": lambda v: float(v) > 0 if v else True},
                    ).classes("w-full").style("margin-top:16px")

                    with ui.input("Rabatt gültig bis (leer = dauerhaft)").classes("w-full").style("margin-top:16px") as disc_until_in:
                        with ui.menu().props("no-parent-event") as disc_menu:
                            with ui.date().props(':options="(d) => d >= new Date().toISOString().slice(0,10).replaceAll(\'-\',\'\/\')"').bind_value(disc_until_in):
                                pass
                        with disc_until_in.add_slot("append"):
                            ui.icon("edit_calendar").on("click", disc_menu.open).classes("cursor-pointer").style("color:#E63312")

                    def save_discount() -> None:
                        if not disc_item_sel.value:
                            ui.notify("Bitte einen Artikel auswählen.", color="negative")
                            return
                        if not disc_price_in.value:
                            ui.notify("Bitte einen Rabattpreis eingeben.", color="negative")
                            return
                        if disc_until_in.value:
                            try:
                                until_dt = datetime.strptime(disc_until_in.value, "%Y-%m-%d")
                                from datetime import date as _date
                                if until_dt.date() < _date.today():
                                    ui.notify("Enddatum darf nicht in der Vergangenheit liegen.", color="negative")
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
                            ui.notify("Rabatt gesetzt!", color="positive")
                            refresh_discounts_list()
                        except ValueError as e:
                            ui.notify(str(e), color="negative")

                    ui.button("Rabatt setzen", on_click=save_discount).classes("fw-btn fw-btn-primary").style("margin-top:20px;padding:12px 28px")

                # ---- SECTION 3: Aktive Rabatte ----
                ui.html('<div style="font-family:Bebas Neue,sans-serif;font-size:28px;color:#F5F0E8;letter-spacing:1px;margin:40px 0 16px">AKTIVE RABATTE</div>')
                active_discounts_container = ui.column().classes("w-full")

                def refresh_discounts_list() -> None:
                    active_discounts_container.clear()
                    items_with_discount = [i for i in admin.get_all_menu_items() if i.discount_price is not None]
                    with active_discounts_container:
                        if not items_with_discount:
                            ui.label("Keine aktiven Rabatte.").style("color:#888")
                            return
                        for it in items_with_discount:
                            eff = _active_price(it.price, it.discount_price, it.discount_until)
                            with ui.element("div").classes("fw-admin-card").style("padding:16px 20px"):
                                with ui.row().style("align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px"):
                                    ui.label(it.name).style("font-weight:700;color:#F5F0E8;font-size:16px")
                                    with ui.column().style("gap:2px"):
                                        ui.label(f"{eff:.2f} CHF").style("color:#E63312;font-weight:700")
                                        ui.label(f"Normalpreis: {it.price:.2f} CHF").style("font-size:11px;color:#555;text-decoration:line-through")
                                        until_str = it.discount_until.strftime("%d.%m.%Y") if it.discount_until else "dauerhaft"
                                        ui.label(f"Rabatt bis: {until_str}").style("font-size:11px;color:#888")

                                    def remove_disc(iid=it.id, iname=it.name) -> None:
                                        admin.set_item_discount(iid, None, None)
                                        ui.notify(f"Rabatt '{iname}' entfernt.", color="positive")
                                        refresh_discounts_list()

                                    ui.button("Löschen", on_click=remove_disc).classes("fw-btn").style(
                                        "padding:6px 14px;font-size:11px!important;background:transparent;color:#E63312;border:1px solid #E63312"
                                    )

                refresh_discounts_list()

                # ---- SECTION 4: Aktive Specials ----
                ui.html('<div style="font-family:Bebas Neue,sans-serif;font-size:28px;color:#F5F0E8;letter-spacing:1px;margin:40px 0 16px">AKTIVE SPECIALS</div>')
                active_specials_container = ui.column().classes("w-full")

                def refresh_specials_list() -> None:
                    specials_list_container.clear()
                    active_specials_container.clear()
                    specials = admin.get_specials()
                    with active_specials_container:
                        if not specials:
                            ui.label("Keine aktiven Specials.").style("color:#888")
                            return
                        for sp in specials:
                            eff = _active_price(sp.price, sp.discount_price, sp.discount_until)
                            with ui.element("div").classes("fw-admin-card").style("padding:16px 20px"):
                                with ui.row().style("align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px"):
                                    ui.label(sp.name).style("font-weight:700;color:#F5F0E8;font-size:16px")
                                    # Price display
                                    price_col = ui.column().style("gap:2px")
                                    with price_col:
                                        if sp.discount_price and eff < sp.price:
                                            ui.label(f"{eff:.2f} CHF").style("color:#E63312;font-weight:700")
                                            ui.label(f"Normalpreis: {sp.price:.2f} CHF").style("font-size:11px;color:#555;text-decoration:line-through")
                                            until_str = sp.discount_until.strftime("%d.%m.%Y") if sp.discount_until else "dauerhaft"
                                            ui.label(f"Rabatt bis: {until_str}").style("font-size:11px;color:#888")
                                        else:
                                            ui.label(f"{sp.price:.2f} CHF").style("color:#E63312;font-weight:700")
                                    ui.html('<span style="background:#F5C842;color:#111;font-size:10px;font-weight:700;padding:3px 10px;letter-spacing:1px">SPECIAL</span>')

                                    def delete_special(iid=sp.id, sname=sp.name) -> None:
                                        admin.delete_menu_item(iid)
                                        ui.notify(f"'{sname}' gelöscht.", color="positive")
                                        refresh_specials_list()

                                    ui.button("Löschen", on_click=delete_special).classes("fw-btn").style(
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
