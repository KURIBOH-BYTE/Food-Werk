"""NiceGUI pages — FoodWerk Dark Edition.

All routes registered by the Pages class.
Design: dark, bold, BigBurger-inspired aesthetic with real product images.
"""

from __future__ import annotations

from datetime import datetime

from nicegui import ui, app

from .controllers import AdminController, AuthController, PaymentController, ShoppingController
from .components import (
    STATUS_LABELS, cart_item_row, menu_card, navbar, order_card,
)

# Image map: menu item name (lowercase substring) -> static path
IMAGE_MAP = {
    "classic": "/static/images/classic_burger.png",
    "chicken": "/static/images/chicken_burger.png",
    "veggie":  "/static/images/veggie_burger.png",
    "cheese":  "/static/images/cheeseburger.png",
    "pizza":   "/static/images/pizza.png",
    "margher": "/static/images/pizza_margherita.png",
    "vegi":    "/static/images/pizza_vegi.png",
    "onion":   "/static/images/onion_rings.png",
    "milksha": "/static/images/milkshake.png",
    "cola":    "/static/images/cola.png",
    "eistee":  "/static/images/eistee.png",
    "wasser":  "/static/images/wasser.png",
    "water":   "/static/images/wasser.png",
    "cheesecake": "/static/images/cheesecake.png",
    "lava":    "/static/images/lava_cake.png",
    "sundae":  "/static/images/ice_cream.png",
    "churro":  "/static/images/churros.png",
}


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
    ) -> None:
        self._auth = auth
        self._shopping = shopping
        self._admin = admin
        self._payment = payment

    def register(self) -> None:
        """Wire all routes. Called once at startup from application.py."""

        auth = self._auth
        shopping = self._shopping
        admin = self._admin
        payment = self._payment

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
                    "flex:1;background:linear-gradient(135deg,#0a0a0a 0%,#1a0800 55%,#2a0f00 100%);"
                    "display:flex;flex-direction:column;justify-content:center;padding:80px;"
                ):
                    ui.html("""
                    <div style="font-family:'Bebas Neue',sans-serif;font-size:12px;letter-spacing:5px;color:#E63312;margin-bottom:20px">FOODWERK</div>
                    <div style="font-family:'Bebas Neue',sans-serif;font-size:clamp(60px,6.5vw,96px);line-height:0.88;color:#F5F0E8;margin-bottom:28px">
                      DEIN<br>KONTO.<br><span style="color:#E63312">DEINE</span><br>WELT.
                    </div>
                    <p style="font-size:15px;color:rgba(245,240,232,0.5);max-width:300px;line-height:1.8;margin:0 0 40px">
                      Login oder Konto erstellen — und sofort bestellen.
                    </p>
                    <div style="display:flex;gap:24px">
                      <div style="text-align:center">
                        <div style="font-family:'Bebas Neue',sans-serif;font-size:40px;color:#E63312">14</div>
                        <div style="font-size:10px;letter-spacing:2px;color:#555;text-transform:uppercase">Gerichte</div>
                      </div>
                      <div style="text-align:center">
                        <div style="font-family:'Bebas Neue',sans-serif;font-size:40px;color:#E63312">30'</div>
                        <div style="font-size:10px;letter-spacing:2px;color:#555;text-transform:uppercase">Lieferzeit</div>
                      </div>
                      <div style="text-align:center">
                        <div style="font-family:'Bebas Neue',sans-serif;font-size:40px;color:#E63312">100%</div>
                        <div style="font-size:10px;letter-spacing:2px;color:#555;text-transform:uppercase">Frisch</div>
                      </div>
                    </div>
                    """)

                # RIGHT — Form
                with ui.element("div").style(
                    "width:480px;flex-shrink:0;background:#111111;"
                    "border-left:1px solid rgba(255,255,255,0.06);"
                    "display:flex;flex-direction:column;justify-content:center;padding:64px 56px;"
                ):
                    ui.html('<div style="font-family:\'Bebas Neue\',sans-serif;font-size:42px;color:#F5F0E8;letter-spacing:2px;margin-bottom:4px">WILLKOMMEN</div>')
                    ui.html('<div style="font-size:13px;color:#555;margin-bottom:32px">Login oder Konto erstellen</div>')

                    with ui.tabs().props("color=red indicator-color=red dense") as tabs:
                        login_tab = ui.tab("Login").style("color:#F5F0E8;font-family:'Bebas Neue',sans-serif;font-size:16px;letter-spacing:2px")
                        register_tab = ui.tab("Registrieren").style("color:#F5F0E8;font-family:'Bebas Neue',sans-serif;font-size:16px;letter-spacing:2px")

                    with ui.tab_panels(tabs, value=login_tab).classes("w-full").style("background:transparent;margin-top:24px"):
                        with ui.tab_panel(login_tab).style("padding:0"):
                            email_in = ui.input("E-Mail").classes("w-full").style("margin-bottom:14px")
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
                                fn_in = ui.input("Vorname").style("flex:1")
                                ln_in = ui.input("Nachname").style("flex:1")
                            em_in = ui.input("E-Mail").classes("w-full").style("margin-top:12px")
                            ph_in = ui.input("Telefon (optional)").classes("w-full").style("margin-top:12px")
                            pw1_in = ui.input("Passwort", password=True, password_toggle_button=True).classes("w-full").style("margin-top:12px")
                            pw2_in = ui.input("Passwort bestätigen", password=True, password_toggle_button=True).classes("w-full").style("margin-top:12px")

                            def do_register() -> None:
                                if pw1_in.value != pw2_in.value:
                                    ui.notify("Passwörter stimmen nicht überein.", color="negative")
                                    return
                                try:
                                    user = auth.register(fn_in.value, ln_in.value, em_in.value, pw1_in.value, ph_in.value or None)
                                    auth.store_user(user)
                                    ui.notify(f"Konto erstellt! Willkommen, {user.first_name}!", color="positive")
                                    ui.navigate.to("/")
                                except ValueError as e:
                                    ui.notify(str(e), color="negative")

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
                    if item.get("description"):
                        ui.label(item["description"]).style("font-size:13px;color:#888;margin-bottom:8px")
                    price = item.get("special_price") or item["price"]
                    ui.html(f'<div style="font-size:20px;font-weight:700;color:#E63312;margin-bottom:16px">{price:.2f} CHF</div>')

                    if item.get("image_url"):
                        ui.image(item["image_url"]).style("width:100%;height:180px;object-fit:cover;margin-bottom:16px")

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
                            eff_price = captured_item.get("special_price") or captured_item["price"]
                            shopping.add_to_cart(
                                menu_item_id=captured_item["id"],
                                name=captured_item["name"],
                                unit_price=eff_price,
                                notes=notes,
                            )
                            dialog.close()
                            ui.notify(f"{captured_item['name']} hinzugefügt!", color="positive")

                        ui.button("In den Warenkorb", on_click=add_with_options).classes("fw-btn fw-btn-primary").style("padding:12px 24px")
                dialog.open()

            active_specials = shopping.get_active_specials()

            # Sticky category filter bar — sofort oben sichtbar
            specials_link = '<a href="#specials" class="fw-cat-link">⭐ Specials</a>' if active_specials else ''
            cat_links = ''.join(f'<a href="#{cat.name.lower()}" class="fw-cat-link">{cat.name}</a>' for cat in categories)
            ui.html(f'<div class="fw-cat-bar" style="margin-top:64px"><div class="fw-cat-bar-inner">{specials_link}{cat_links}</div></div>')

            # Specials — gleiche Karten wie alle anderen Items
            if active_specials:
                ui.html('<div id="specials" class="fw-cat-section"><div class="fw-cat-title"><div class="fw-section-label" style="margin:0">Specials</div><div class="fw-cat-title-line"></div></div></div>')
                with ui.element("div").classes("fw-items-grid").style("padding:0 60px 40px"):
                    for sp in active_specials:
                        mi = sp.menu_item
                        img = resolve_image(mi.name, mi.image_url)
                        item_dict = {
                            "id": mi.id, "name": mi.name,
                            "description": sp.description or mi.description,
                            "price": mi.price, "special_price": sp.special_price,
                            "image_url": img, "is_available": mi.is_available,
                            "ingredients": [{"name": mii.ingredient.name} for mii in mi.ingredients],
                        }
                        menu_card(item_dict, on_add_to_cart=show_add_dialog)

            # Kategorien
            for cat in categories:
                items = shopping.get_menu_items(category_id=cat.id, available_only=False)
                if not items:
                    continue
                ui.html(f'<div id="{cat.name.lower()}" class="fw-cat-section"><div class="fw-cat-title"><div class="fw-section-label" style="margin:0">{cat.name}</div><div class="fw-cat-title-line"></div></div></div>')
                with ui.element("div").classes("fw-items-grid").style("padding:0 60px 40px"):
                    for item in items:
                        img = resolve_image(item.name, item.image_url)
                        eff = shopping.get_effective_price(item)
                        item_dict = {
                            "id": item.id, "name": item.name,
                            "description": item.description, "price": item.price,
                            "image_url": img, "is_available": item.is_available,
                            "ingredients": [{"name": mii.ingredient.name} for mii in item.ingredients],
                        }
                        if eff < item.price:
                            item_dict["special_price"] = eff
                        menu_card(item_dict, on_add_to_cart=show_add_dialog)

        # ================================================================
        # CART
        # ================================================================
        @ui.page("/cart")
        def cart_page() -> None:
            navbar()
            cart = shopping.get_cart()

            # Full-height two-column layout — no scrolling needed
            with ui.element("div").style(
                "margin-top:64px;min-height:calc(100vh - 64px);display:flex;flex-direction:row"
            ):
                if cart.is_empty:
                    with ui.element("div").style(
                        "flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:24px"
                    ):
                        ui.html("""
                        <div style="text-align:center">
                          <div style="font-family:'Bebas Neue',sans-serif;font-size:80px;color:#222;line-height:1">LEER</div>
                          <div style="font-size:15px;color:#555;margin-top:8px">Dein Warenkorb ist noch leer.</div>
                        </div>
                        """)
                        ui.button("→ Zum Menü", on_click=lambda: ui.navigate.to("/menu")).classes("fw-btn fw-btn-primary").style("padding:14px 40px")
                    return

                # LEFT — item list
                left = ui.element("div").style(
                    "flex:1;padding:48px 60px;overflow-y:auto;border-right:1px solid rgba(255,255,255,0.06)"
                )
                # RIGHT — summary panel
                right = ui.element("div").style(
                    "width:360px;flex-shrink:0;background:#1a1a1a;padding:48px 40px;display:flex;flex-direction:column"
                )

                cart_container = ui.column().classes("w-full")
                total_label = None
                item_count_label = None

                def refresh() -> None:
                    nonlocal cart, total_label, item_count_label
                    cart = shopping.get_cart()
                    cart_container.clear()
                    with cart_container:
                        if cart.is_empty:
                            ui.navigate.to("/cart")
                            return
                        for i, item in enumerate(cart.items):
                            cart_item_row(item, i, on_remove=remove_item, on_update_qty=update_qty)
                    if total_label:
                        total_label.set_text(f"{cart.total:.2f} CHF")
                    if item_count_label:
                        item_count_label.set_text(f"{cart.item_count} {'Artikel' if cart.item_count == 1 else 'Artikel'}")

                def remove_item(index: int) -> None:
                    shopping.remove_from_cart(index)
                    refresh()

                def update_qty(index: int, qty: int) -> None:
                    shopping.update_cart_quantity(index, qty)
                    refresh()

                with left:
                    ui.html('<div style="font-size:11px;font-weight:700;letter-spacing:4px;text-transform:uppercase;color:#E63312;margin-bottom:8px">Deine Auswahl</div>')
                    ui.html('<div style="font-family:\'Bebas Neue\',sans-serif;font-size:52px;line-height:0.95;color:#F5F0E8;margin-bottom:32px">WARENKORB</div>')
                    with cart_container:
                        for i, item in enumerate(cart.items):
                            cart_item_row(item, i, on_remove=remove_item, on_update_qty=update_qty)

                with right:
                    ui.html('<div style="font-family:\'Bebas Neue\',sans-serif;font-size:28px;color:#F5F0E8;letter-spacing:1px;margin-bottom:28px">BESTELLÜBERSICHT</div>')

                    item_count_label = ui.label(f"{cart.item_count} Artikel").style(
                        "font-size:12px;color:#555;letter-spacing:1px;text-transform:uppercase;margin-bottom:20px"
                    )

                    ui.html('<div style="border-top:1px solid rgba(255,255,255,0.07);margin-bottom:20px"></div>')

                    with ui.row().style("justify-content:space-between;align-items:baseline;margin-bottom:8px"):
                        ui.label("Zwischensumme").style("font-size:13px;color:#888")
                        total_label = ui.label(f"{cart.total:.2f} CHF").style(
                            "font-family:'Bebas Neue',sans-serif;font-size:28px;color:#E63312;letter-spacing:1px"
                        )

                    ui.html('<div style="font-size:12px;color:#444;margin-bottom:28px">Liefergebühr wird beim Checkout berechnet.</div>')
                    ui.html('<div style="border-top:1px solid rgba(255,255,255,0.07);margin-bottom:28px"></div>')

                    ui.button("Zur Kasse →", on_click=lambda: ui.navigate.to("/checkout")).classes("fw-btn fw-btn-primary w-full").style("padding:16px;font-size:14px!important")
                    ui.button("← Weiter einkaufen", on_click=lambda: ui.navigate.to("/menu")).props("flat").classes("w-full").style("color:#555;margin-top:12px;padding:10px")

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

            ui.html('<div class="fw-page"><div class="fw-page-header"><div class="fw-section-label">Fast geschafft</div><div class="fw-section-title">KASSE</div></div>')

            with ui.element("div").style("padding:48px 60px;max-width:640px;margin:0 auto"):
                ui.html(f'<div style="font-family:Bebas Neue,sans-serif;font-size:28px;color:#E63312;margin-bottom:24px">Total: {cart.total:.2f} CHF</div>')

                order_type_toggle = ui.toggle(["delivery", "pickup"], value="pickup").props("color=red")
                address_box = ui.column().classes("w-full").style("margin-top:20px")
                pickup_box = ui.column().classes("w-full").style("margin-top:20px")
                notes_in = ui.textarea("Notizen (optional)").classes("w-full").style("margin-top:16px")

                street_in = house_nr_in = city_in = postal_in = pickup_time_in = None

                def update_form() -> None:
                    nonlocal street_in, house_nr_in, city_in, postal_in, pickup_time_in
                    address_box.clear()
                    pickup_box.clear()
                    if order_type_toggle.value == "delivery":
                        with address_box:
                            ui.label("Lieferadresse").style("font-family:Bebas Neue,sans-serif;font-size:22px;color:#F5F0E8;margin-bottom:12px")
                            street_in = ui.input("Strasse").classes("w-full")
                            house_nr_in = ui.input("Hausnummer").classes("w-full").style("margin-top:8px")
                            city_in = ui.input("Stadt").classes("w-full").style("margin-top:8px")
                            postal_in = ui.input("Postleitzahl").classes("w-full").style("margin-top:8px")
                    else:
                        with pickup_box:
                            ui.label("Abholzeit").style("font-family:Bebas Neue,sans-serif;font-size:22px;color:#F5F0E8;margin-bottom:12px")
                            pickup_time_in = ui.input("z.B. 18:30").classes("w-full")

                order_type_toggle.on_value_change(lambda: update_form())
                update_form()

                def go_to_payment() -> None:
                    if order_type_toggle.value == "delivery":
                        if not all([street_in and street_in.value, house_nr_in and house_nr_in.value,
                                    city_in and city_in.value, postal_in and postal_in.value]):
                            ui.notify("Bitte alle Adressfelder ausfüllen.", color="negative")
                            return
                    payment.save_pending_order(
                        user_id=user_data["id"],
                        order_type=order_type_toggle.value,
                        street=street_in.value if street_in else None,
                        house_nr=house_nr_in.value if house_nr_in else None,
                        city=city_in.value if city_in else None,
                        postal_code=postal_in.value if postal_in else None,
                        pickup_time=pickup_time_in.value if pickup_time_in else None,
                        notes=notes_in.value or None,
                    )
                    ui.navigate.to("/payment/checkout")

                ui.button("Weiter zur Zahlung →", icon="credit_card", on_click=go_to_payment).classes("fw-btn fw-btn-primary").style("margin-top:32px;padding:14px 32px;width:100%")

            ui.html("</div>")

        # ================================================================
        # PAYMENT CHECKOUT
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

            ui.html('<div class="fw-page"><div class="fw-page-header"><div class="fw-section-label">Sichere Zahlung</div><div class="fw-section-title">BEZAHLEN</div></div>')

            with ui.element("div").style("padding:48px 60px;max-width:600px;margin:0 auto"):
                ui.html(f'<div style="font-family:Bebas Neue,sans-serif;font-size:28px;color:#E63312;margin-bottom:24px">Betrag: {cart.total:.2f} CHF</div>')

                with ui.expansion("Testkarten anzeigen", icon="info").style("background:#1a1a1a;border:1px solid rgba(255,255,255,0.08);margin-bottom:24px"):
                    with ui.column().style("gap:8px;padding:8px 0"):
                        for card in payment.get_test_cards():
                            color = "#639922" if card["result"] == "success" else "#E63312"
                            ui.html(f'<div style="display:flex;align-items:center;gap:12px"><span style="background:{color};color:#fff;font-size:10px;font-weight:700;padding:3px 10px;text-transform:uppercase">{card["result"]}</span><span style="font-family:monospace;color:#F5F0E8;font-weight:700">{card["number"]}</span><span style="font-size:13px;color:#888">{card["brand"]} — {card["label"]}</span></div>')

                ui.html('<div style="background:#1a1a1a;border:1px solid rgba(255,255,255,0.08);padding:28px">')
                ui.label("Kartendaten").style("font-family:Bebas Neue,sans-serif;font-size:24px;color:#F5F0E8;margin-bottom:16px")

                card_in = ui.input("Kartennummer", placeholder="4242 4242 4242 4242", value="4242 4242 4242 4242").classes("w-full")
                with ui.row().classes("w-full").style("gap:16px;margin-top:12px"):
                    expiry_in = ui.input("Ablauf (MM/JJ)", placeholder="12/26", value="12/26").style("flex:1")
                    cvv_in = ui.input("CVV", placeholder="123", value="123").style("width:100px")
                name_in = ui.input(
                    "Name auf Karte",
                    value=f"{user_data['first_name']} {user_data.get('last_name', '')}".strip()
                ).classes("w-full").style("margin-top:12px")

                error_label = ui.label("").style("color:#E63312;font-size:13px;margin-top:8px")

                def pay() -> None:
                    ok, msg = payment.validate_card(card_in.value, expiry_in.value, cvv_in.value, name_in.value)
                    if not ok:
                        error_label.set_text(msg)
                        return
                    error_label.set_text("")
                    order = payment.complete_order()
                    if order:
                        ui.navigate.to("/payment/success")
                    else:
                        error_label.set_text("Bestellung konnte nicht abgeschlossen werden.")

                with ui.row().style("justify-content:space-between;margin-top:24px"):
                    ui.button("Zurück", on_click=lambda: ui.navigate.to("/checkout")).props("flat").style("color:#888")
                    ui.button("Jetzt bezahlen", icon="lock", on_click=pay).classes("fw-btn fw-btn-primary").style("padding:12px 28px")

                ui.html("</div>")

            ui.html("</div>")

        # ================================================================
        # PAYMENT SUCCESS
        # ================================================================
        @ui.page("/payment/success")
        def payment_success_page() -> None:
            navbar()
            order_id = app.storage.user.get("last_order_id")
            ui.html("""
            <div class="fw-page" style="display:flex;align-items:center;justify-content:center;min-height:80vh">
              <div style="text-align:center;padding:80px 40px">
                <div style="font-size:80px;margin-bottom:24px">✅</div>
                <div style="font-family:Bebas Neue,sans-serif;font-size:72px;color:#639922;line-height:1;margin-bottom:16px">BESTELLT!</div>
                <div style="font-size:17px;color:rgba(245,240,232,0.65);margin-bottom:40px">
                  Deine Bestellung ist bei uns eingegangen.<br>Wir bereiten sie frisch vor!
                </div>
            """)
            with ui.row().style("justify-content:center;gap:16px"):
                if order_id:
                    ui.button("Bestellung verfolgen", on_click=lambda: ui.navigate.to(f"/order/{order_id}")).classes("fw-btn fw-btn-primary").style("padding:14px 28px")
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
            ui.html('<div class="fw-page"><div class="fw-page-header"><div class="fw-section-label">Deine Bestellung</div><div class="fw-section-title">STATUS</div></div>')
            with ui.element("div").style("padding:48px 60px;max-width:640px;margin:0 auto"):
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
            ui.html("</div>")

        # ================================================================
        # SPECIALS
        # ================================================================
        @ui.page("/specials")
        def specials_page() -> None:
            navbar()
            specials = shopping.get_active_specials()

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
                        ui.html(f'<div style="font-family:Bebas Neue,sans-serif;font-size:32px;color:#F5F0E8;letter-spacing:1px;margin-bottom:4px">{item["name"]}</div>')
                        if item.get("description"):
                            ui.label(item["description"]).style("font-size:13px;color:#888;margin-bottom:8px")
                        price = item.get("special_price") or item["price"]
                        ui.html(f'<div style="font-size:20px;font-weight:700;color:#E63312;margin-bottom:16px">{price:.2f} CHF</div>')
                        if item.get("image_url"):
                            ui.image(item["image_url"]).style("width:100%;height:180px;object-fit:cover;margin-bottom:16px")
                        with ui.row().style("justify-content:flex-end;gap:12px;margin-top:20px"):
                            ui.button("Abbrechen", on_click=dialog.close).props("flat").style("color:#888")
                            def add_sp(i=item):
                                shopping.add_to_cart(i["id"], i["name"], i.get("special_price") or i["price"])
                                dialog.close()
                                ui.notify(f"{i['name']} hinzugefügt!", color="positive")
                            ui.button("In den Warenkorb", on_click=add_sp).classes("fw-btn fw-btn-primary").style("padding:12px 24px")
                    dialog.open()

                with ui.element("div").style("max-width:1600px;margin:0 auto;padding:40px 60px"):
                    with ui.element("div").classes("fw-items-grid"):
                        for sp in specials:
                            mi = sp.menu_item
                            img = resolve_image(mi.name, mi.image_url)
                            item_dict = {
                                "id": mi.id, "name": mi.name,
                                "description": sp.description or mi.description,
                                "price": mi.price, "special_price": sp.special_price,
                                "image_url": img, "is_available": mi.is_available,
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

            ui.html(f'<div class="fw-page"><div class="fw-page-header"><div class="fw-section-label">Dein Konto</div><div class="fw-section-title">{user_data["first_name"].upper()}<br>{user_data.get("last_name","").upper()}</div><div style="font-size:14px;color:#888;margin-top:8px">{user_data["email"]}</div></div>')

            with ui.element("div").style("padding:48px 60px;max-width:820px;margin:0 auto"):
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
                        })
            ui.html("</div>")

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

            ui.html('<div class="fw-page"><div class="fw-page-header"><div class="fw-section-label">Verwaltung</div><div class="fw-section-title">ADMIN<br>DASHBOARD</div></div>')

            with ui.element("div").style("max-width:1600px;margin:0 auto;padding:48px 60px"):
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

            ui.html("</div>")

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

            ui.html('<div class="fw-page"><div class="fw-page-header"><div class="fw-section-label">Verwaltung</div><div class="fw-section-title">MENÜ<br>VERWALTEN</div></div>')

            categories = admin.get_categories()
            items_container = ui.column().classes("w-full").style("max-width:1600px;margin:0 auto;padding:48px 60px")

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
            ui.html("</div>")

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

            ui.html('<div class="fw-page"><div class="fw-page-header"><div class="fw-section-label">Verwaltung</div><div class="fw-section-title">BESTELLUNGEN<br>VERWALTEN</div></div>')

            with ui.element("div").style("max-width:1600px;margin:0 auto;padding:48px 60px"):
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

            ui.html("</div>")

        # ================================================================
        # ADMIN — SPECIALS MANAGER
        # ================================================================
        @ui.page("/admin/specials")
        def admin_specials_page() -> None:
            navbar()
            user_data = auth.current_user()
            if not user_data or user_data.get("role") != "admin":
                ui.navigate.to("/")
                return

            ui.html('<div class="fw-page"><div class="fw-page-header"><div class="fw-section-label">Verwaltung</div><div class="fw-section-title">SPECIALS<br>VERWALTEN</div></div>')

            with ui.element("div").style("padding:48px 60px;max-width:900px;margin:0 auto"):
                ui.html('<div style="font-family:Bebas Neue,sans-serif;font-size:28px;color:#F5F0E8;letter-spacing:1px;margin-bottom:20px">NEUES SPECIAL ERSTELLEN</div>')
                with ui.element("div").classes("fw-admin-card").style("padding:28px"):
                    all_items = admin.get_all_menu_items()
                    item_options = {i.id: f"{i.name} ({i.price:.2f} CHF)" for i in all_items}
                    item_sel = ui.select(options=item_options, label="Menüartikel").classes("w-full")
                    sp_price = ui.number("Special-Preis (CHF)", min=0, step=0.5).classes("w-full").style("margin-top:12px")
                    sp_desc = ui.input("Beschreibung").classes("w-full").style("margin-top:12px")

                    with ui.row().classes("w-full").style("gap:16px;margin-top:12px"):
                        with ui.input("Startdatum (JJJJ-MM-TT)").classes("w-full") as start_in:
                            with ui.menu().props("no-parent-event") as sm:
                                with ui.date().bind_value(start_in):
                                    pass
                            with start_in.add_slot("append"):
                                ui.icon("edit_calendar").on("click", sm.open).classes("cursor-pointer").style("color:#E63312")
                        with ui.input("Enddatum (JJJJ-MM-TT)").classes("w-full") as end_in:
                            with ui.menu().props("no-parent-event") as em:
                                with ui.date().bind_value(end_in):
                                    pass
                            with end_in.add_slot("append"):
                                ui.icon("edit_calendar").on("click", em.open).classes("cursor-pointer").style("color:#E63312")

                    specials_container = ui.column().classes("w-full").style("margin-top:16px")

                    def create_special() -> None:
                        if not all([item_sel.value, sp_price.value, start_in.value, end_in.value]):
                            ui.notify("Bitte alle Pflichtfelder ausfüllen.", color="negative")
                            return
                        try:
                            admin.create_special(
                                menu_item_id=item_sel.value,
                                created_by=user_data["id"],
                                special_price=sp_price.value,
                                start_date=datetime.strptime(start_in.value, "%Y-%m-%d"),
                                end_date=datetime.strptime(end_in.value, "%Y-%m-%d"),
                                description=sp_desc.value or None,
                            )
                            ui.notify("Special erstellt!", color="positive")
                            refresh_specials()
                        except ValueError as e:
                            ui.notify(str(e), color="negative")

                    ui.button("Special erstellen", on_click=create_special).classes("fw-btn fw-btn-primary").style("margin-top:20px;padding:12px 28px")

                ui.html('<div style="font-family:Bebas Neue,sans-serif;font-size:28px;color:#F5F0E8;letter-spacing:1px;margin:36px 0 16px">BESTEHENDE SPECIALS</div>')

                def refresh_specials() -> None:
                    specials_container.clear()
                    with specials_container:
                        specials = admin.get_all_specials()
                        if not specials:
                            ui.label("Noch keine Specials.").style("color:#888")
                            return
                        for sp in specials:
                            active_color = "#639922" if sp.is_active else "#555"
                            active_label = "Aktiv" if sp.is_active else "Inaktiv"
                            with ui.element("div").classes("fw-admin-card").style("padding:16px 20px"):
                                with ui.row().style("align-items:center;justify-content:space-between;flex-wrap:wrap;gap:12px"):
                                    ui.label(sp.menu_item.name if sp.menu_item else "—").style("font-weight:700;color:#F5F0E8;font-size:16px")
                                    ui.label(f"{sp.special_price:.2f} CHF").style("color:#E63312;font-weight:700")
                                    ui.label(f"{sp.start_date.strftime('%d.%m.%Y')} – {sp.end_date.strftime('%d.%m.%Y')}").style("color:#888;font-size:13px")
                                    ui.html(f'<span style="background:{active_color};color:#fff;font-size:10px;font-weight:700;padding:3px 10px;letter-spacing:1px">{active_label}</span>')

                                    def toggle_sp(sid=sp.id, active=sp.is_active) -> None:
                                        admin.toggle_special(sid, not active)
                                        refresh_specials()

                                    ui.button("Deaktivieren" if sp.is_active else "Aktivieren", on_click=toggle_sp).classes("fw-btn").style("padding:6px 16px;font-size:11px!important;background:transparent;color:#888;border:1px solid #333")

                refresh_specials()

            ui.html("</div>")
