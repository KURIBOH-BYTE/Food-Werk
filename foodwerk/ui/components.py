"""Reusable NiceGUI UI components — FoodWerk Dark Edition.

Dark, bold design inspired by premium burger restaurant aesthetics.
"""

from __future__ import annotations

from nicegui import ui, app

from ..services.cart_service import CartService, CartItem

STATUS_COLORS: dict[str, str] = {
    "pending": "orange",
    "preparing": "blue",
    "ready": "green",
    "delivered": "grey",
    "collected": "grey",
}

STATUS_LABELS: dict[str, str] = {
    "pending": "Pending",
    "preparing": "Preparing",
    "ready": "Ready",
    "delivered": "Delivered",
    "collected": "Collected",
}

FW_CSS = """
<link href="https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Barlow:wght@400;600;700&display=swap" rel="stylesheet">
<style>
  :root {
    --fw-red:    #E63312;
    --fw-dark:   #111111;
    --fw-dark2:  #1a1a1a;
    --fw-dark3:  #222222;
    --fw-cream:  #F5F0E8;
    --fw-yellow: #F5C842;
    --fw-gray:   #888888;
    --fw-border: rgba(255,255,255,0.07);
  }
  body, .q-page { background: var(--fw-dark) !important; color: var(--fw-cream) !important; font-family: 'Barlow', sans-serif !important; min-width: 1200px; overflow-x: auto; }
  .q-header { background: transparent !important; box-shadow: none !important; }
  /* Fix NiceGUI's default align-items:flex-start which causes left-only layout */
  .nicegui-content {
    align-items: stretch !important;
    padding: 0 !important;
    gap: 0 !important;
    width: 100% !important;
  }
  .nicegui-column {
    align-items: stretch !important;
    width: 100% !important;
  }
  .q-page { padding: 0 !important; }
  .fw-nav {
    position: fixed; top: 0; left: 0; right: 0; z-index: 999;
    height: 64px;
    background: rgba(17,17,17,0.95); border-bottom: 1px solid var(--fw-border);
    backdrop-filter: blur(8px);
  }
  .fw-nav-inner {
    max-width: 1600px; margin: 0 auto; height: 100%; padding: 0 60px;
    display: flex; align-items: center; justify-content: space-between;
  }
  .fw-logo { font-family: 'Bebas Neue', sans-serif; font-size: 28px; letter-spacing: 2px; color: var(--fw-red); text-decoration: none; }
  .fw-logo span { color: var(--fw-cream); }
  .fw-nav-links { display: flex; gap: 28px; align-items: center; list-style: none; margin: 0; padding: 0; }
  .fw-nav-links a { color: var(--fw-cream); text-decoration: none; font-size: 12px; font-weight: 700; letter-spacing: 1.5px; text-transform: uppercase; transition: color .2s; }
  .fw-nav-links a:hover { color: var(--fw-red); }
  .fw-cart-badge { background: var(--fw-red); color: #fff; font-size: 10px; font-weight: 700; padding: 2px 7px; border-radius: 20px; margin-left: 4px; }
  .fw-btn { font-family: 'Barlow', sans-serif !important; font-weight: 700 !important; font-size: 13px !important; letter-spacing: 1.5px !important; text-transform: uppercase !important; border-radius: 0 !important; }
  .fw-btn-primary { background: var(--fw-red) !important; color: #fff !important; border: none !important; }
  .fw-btn-outline { background: transparent !important; color: var(--fw-cream) !important; border: 1.5px solid rgba(245,240,232,0.3) !important; }
  .fw-page { padding-top: 64px; min-height: 100vh; background: var(--fw-dark); width: 100%; }
  .fw-section { padding: 80px 60px; }
  .fw-section-label { font-size: 11px; font-weight: 700; letter-spacing: 4px; text-transform: uppercase; color: var(--fw-red); margin-bottom: 12px; }
  .fw-section-title { font-family: 'Bebas Neue', sans-serif; font-size: clamp(48px, 6vw, 80px); line-height: 0.95; color: var(--fw-cream); margin-bottom: 48px; }
  .fw-hero { width: 100%; min-height: 92vh; display: flex; align-items: center; background: linear-gradient(135deg, #0a0a0a 0%, #1a0800 60%, #2a0f00 100%); position: relative; overflow: hidden; }
  .fw-hero-bg { position: absolute; font-family: 'Bebas Neue', sans-serif; font-size: 28vw; color: rgba(255,255,255,0.025); line-height: 1; top: 50%; left: 50%; transform: translate(-50%, -50%); white-space: nowrap; user-select: none; pointer-events: none; }
  .fw-hero-content { padding: 0 60px; position: relative; z-index: 2; max-width: 680px; }
  .fw-hero-tag { display: inline-block; background: var(--fw-red); color: #fff; font-size: 11px; font-weight: 700; letter-spacing: 3px; text-transform: uppercase; padding: 6px 16px; margin-bottom: 24px; }
  .fw-hero-title { font-family: 'Bebas Neue', sans-serif; font-size: clamp(72px, 11vw, 130px); line-height: 0.88; color: var(--fw-cream); margin-bottom: 24px; }
  .fw-hero-title span { color: var(--fw-red); }
  .fw-hero-sub { font-size: 17px; color: rgba(245,240,232,0.65); line-height: 1.6; margin-bottom: 40px; max-width: 420px; }
  .fw-hero-img { position: absolute; right: 5%; top: 50%; transform: translateY(-50%); width: 44vw; max-width: 580px; height: auto; object-fit: cover; border-radius: 4px; box-shadow: 0 0 120px rgba(230,51,18,0.18); }
  .fw-ticker { width: 100%; background: var(--fw-red); padding: 13px 0; overflow: hidden; white-space: nowrap; }
  .fw-ticker-inner { display: inline-block; font-family: 'Bebas Neue', sans-serif; font-size: 18px; letter-spacing: 3px; color: #fff; animation: fwtick 24s linear infinite; }
  @keyframes fwtick { from { transform: translateX(0); } to { transform: translateX(-50%); } }
  .fw-stats { width: 100%; background: var(--fw-red); padding: 56px 60px; display: flex; }
  .fw-stat { flex: 1; text-align: center; border-right: 1px solid rgba(255,255,255,0.2); padding: 16px; }
  .fw-stat:last-child { border-right: none; }
  .fw-stat-num { font-family: 'Bebas Neue', sans-serif; font-size: 68px; color: #fff; line-height: 1; }
  .fw-stat-label { font-size: 11px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; color: rgba(255,255,255,0.75); margin-top: 6px; }
  /* Item cards — Lieferando/UberEats inspired */
  .fw-items-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; }
  .fw-item-card { background: #1a1a1a; border: 1px solid rgba(255,255,255,0.07); overflow: hidden; cursor: pointer; display: flex; flex-direction: column; transition: border-color .2s, transform .2s, box-shadow .2s; }
  .fw-item-card:hover { border-color: var(--fw-red); transform: translateY(-3px); box-shadow: 0 8px 32px rgba(230,51,18,0.12); }
  .fw-item-card.unavailable { opacity: 0.45; pointer-events: none; }
  .fw-item-thumb { width: 100%; aspect-ratio: 4/3; object-fit: cover; display: block; }
  .fw-item-thumb-empty { width: 100%; aspect-ratio: 4/3; background: linear-gradient(135deg,#1a0a00,#2a1200); display: flex; align-items: center; justify-content: center; }
  .fw-item-body { padding: 14px 16px 16px; display: flex; flex-direction: column; flex: 1; }
  .fw-item-name { font-family: 'Bebas Neue', sans-serif; font-size: 20px; color: var(--fw-cream); letter-spacing: 1px; line-height: 1.1; margin-bottom: 4px; }
  .fw-item-desc { font-size: 12px; color: #666; line-height: 1.4; margin-bottom: 12px; flex: 1; }
  .fw-item-footer { display: flex; align-items: center; justify-content: space-between; margin-top: auto; gap: 8px; }
  .fw-item-price { font-size: 17px; font-weight: 700; color: var(--fw-red); }
  .fw-item-original { font-size: 12px; color: #555; text-decoration: line-through; }
  .fw-item-badge { position: absolute; top: 10px; left: 10px; background: var(--fw-yellow); color: #111; font-size: 9px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; padding: 3px 8px; }
  .fw-item-add { background: var(--fw-red); color: #fff; border: none; font-family: 'Barlow',sans-serif; font-weight: 700; font-size: 11px; letter-spacing: 1px; text-transform: uppercase; padding: 8px 14px; cursor: pointer; white-space: nowrap; transition: background .2s; }
  .fw-item-add:hover { background: #c4290e; }
  /* Legacy menu grid kept for home page */
  .fw-menu-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 3px; }
  .fw-menu-card { position: relative; overflow: hidden; cursor: pointer; transition: transform .3s; aspect-ratio: 1; display: flex; flex-direction: column; justify-content: flex-end; padding: 24px; background: var(--fw-dark2); }
  .fw-menu-card:hover { transform: scale(1.02); z-index: 2; }
  .fw-menu-card::before { content: ''; position: absolute; inset: 0; background: linear-gradient(to top, rgba(0,0,0,0.88) 0%, transparent 55%); z-index: 1; }
  .fw-menu-card img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; transition: transform .5s; }
  .fw-menu-card:hover img { transform: scale(1.06); }
  .fw-menu-card-body { position: relative; z-index: 2; }
  .fw-menu-card-name { font-family: 'Bebas Neue', sans-serif; font-size: 28px; color: var(--fw-cream); letter-spacing: 1px; }
  .fw-menu-card-price { font-size: 14px; color: var(--fw-red); font-weight: 700; margin-top: 4px; }
  .fw-menu-card-badge { position: absolute; top: 16px; left: 16px; z-index: 3; background: var(--fw-yellow); color: #111; font-size: 10px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; padding: 4px 10px; }
  .fw-menu-card.big { grid-column: span 2; aspect-ratio: 2/1; }
  /* Category filter bar */
  .fw-cat-bar { position: sticky; top: 64px; z-index: 100; background: #111111; border-bottom: 1px solid rgba(255,255,255,0.07); width: 100%; }
  .fw-cat-bar-inner { max-width: 1600px; margin: 0 auto; padding: 0 52px; display: flex; gap: 0; overflow-x: auto; scrollbar-width: none; }
  .fw-cat-bar-inner::-webkit-scrollbar { display: none; }
  .fw-cat-link { color: rgba(245,240,232,0.5); text-decoration: none; font-size: 11px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; padding: 14px 20px; display: block; border-bottom: 2px solid transparent; transition: color .2s, border-color .2s; white-space: nowrap; }
  .fw-cat-link:hover { color: var(--fw-cream); border-bottom-color: var(--fw-red); }
  .fw-cat-link.active { color: var(--fw-cream); border-bottom-color: var(--fw-red); }
  /* Section anchors */
  .fw-cat-section { scroll-margin-top: 112px; padding: 32px 0 0; }
  .fw-cat-title { max-width: 1600px; margin: 0 auto; padding: 0 60px 14px; display: flex; align-items: center; gap: 16px; }
  .fw-cat-title-line { flex: 1; height: 1px; background: rgba(255,255,255,0.07); }
  /* Legacy special card kept for specials page */
  .fw-special-card { background: var(--fw-dark2); padding: 28px; border: 1px solid var(--fw-border); display: flex; align-items: center; gap: 24px; transition: border-color .2s; }
  .fw-special-card:hover { border-color: var(--fw-red); }
  .fw-special-img { width: 120px; height: 100px; object-fit: cover; border-radius: 2px; flex-shrink: 0; }
  .fw-special-name { font-family: 'Bebas Neue', sans-serif; font-size: 26px; color: var(--fw-cream); letter-spacing: 1px; }
  .fw-special-desc { font-size: 13px; color: var(--fw-gray); margin: 6px 0; line-height: 1.5; }
  .fw-special-price { font-size: 20px; font-weight: 700; color: var(--fw-red); }
  .fw-special-original { font-size: 13px; color: var(--fw-gray); text-decoration: line-through; margin-left: 8px; }
  .fw-card { background: var(--fw-dark2) !important; border: 1px solid var(--fw-border) !important; border-radius: 0 !important; color: var(--fw-cream) !important; }
  .fw-page-header { width: 100%; background: var(--fw-dark2); padding: 56px 60px; border-bottom: 1px solid var(--fw-border); }
  .fw-order-card { background: var(--fw-dark2); border: 1px solid var(--fw-border); padding: 20px; margin-bottom: 12px; }
  .fw-admin-card { background: var(--fw-dark2) !important; border: 1px solid var(--fw-border) !important; border-radius: 0 !important; color: var(--fw-cream) !important; margin-bottom: 12px; }
  .q-field__control { background: rgba(255,255,255,0.05) !important; }
  .q-field__label { color: rgba(245,240,232,0.6) !important; }
  input, textarea { color: var(--fw-cream) !important; }
  .q-select__dropdown-icon { color: var(--fw-cream) !important; }
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: var(--fw-dark); }
  ::-webkit-scrollbar-thumb { background: var(--fw-red); }
</style>
"""


def inject_styles() -> None:
    ui.add_head_html(FW_CSS)
    ui.query('.nicegui-content').style('align-items: stretch; padding: 0; gap: 0; width: 100%')
    ui.query('.nicegui-column').style('align-items: stretch; width: 100%')


def navbar(cart: CartService | None = None) -> None:
    """Fixed dark top navbar."""
    inject_styles()
    if cart is None:
        cart = CartService.from_dict_list(app.storage.user.get("cart_items", []))
    user = app.storage.user.get("user")
    cart_count = cart.item_count

    cart_label = f'Warenkorb{"<span class=fw-cart-badge>" + str(cart_count) + "</span>" if cart_count else ""}'

    extra_links = ""
    if user:
        if user.get("role") in ("admin", "employee"):
            extra_links += '<li><a href="/admin">Admin</a></li>'
        extra_links += f'<li><a href="/profile">{user["first_name"]}</a></li>'
        extra_links += '<li><a href="#" id="fw-logout-link">Logout</a></li>'
    else:
        extra_links += '<li><a href="/login">Login</a></li>'

    ui.html(f"""
    <nav class="fw-nav">
      <div class="fw-nav-inner">
        <a class="fw-logo" href="/">FOOD<span>WERK</span></a>
        <ul class="fw-nav-links">
          <li><a href="/menu">Menü</a></li>
          <li><a href="/specials">Specials</a></li>
          <li><a href="/cart">{cart_label}</a></li>
          {extra_links}
        </ul>
      </div>
    </nav>
    """)

    if user:
        ui.add_body_html("""
        <script>
          var ll = document.getElementById('fw-logout-link');
          if(ll){ ll.addEventListener('click', function(e){
            e.preventDefault();
            window.location.href='/';
          }); }
        </script>
        """)
        # Real logout via NiceGUI storage
        def do_logout():
            app.storage.user.clear()
            ui.navigate.to("/")
        # We hook via a hidden button trick — NiceGUI handles the JS event
        with ui.element("div").style("display:none"):
            ui.button("logout_hidden", on_click=do_logout).props("id=fw-logout-btn")
        ui.add_body_html("""
        <script>
          var ll2 = document.getElementById('fw-logout-link');
          if(ll2){ ll2.addEventListener('click', function(e){
            e.preventDefault();
            document.getElementById('fw-logout-btn')?.click();
          }); }
        </script>
        """)


def menu_card(item: dict, on_add_to_cart=None) -> None:
    """Modern item card — image top, content bottom."""
    is_available = item.get("is_available", True)
    has_special = bool(item.get("special_price"))
    price = item.get("special_price") or item["price"]

    if item.get("image_url"):
        img_html = f'<img class="fw-item-thumb" src="{item["image_url"]}" alt="{item["name"]}" loading="lazy">'
    else:
        img_html = '<div class="fw-item-thumb-empty"><span style="font-family:\'Bebas Neue\',sans-serif;font-size:32px;color:#333">FW</span></div>'

    badge_html = '<div class="fw-item-badge">Special</div>' if has_special else ""
    original_html = f'<span class="fw-item-original">{item["price"]:.2f}</span>' if has_special else ""
    desc = item.get("description") or ""
    desc_html = f'<div class="fw-item-desc">{desc[:60]}{"…" if len(desc) > 60 else ""}</div>' if desc else '<div class="fw-item-desc"></div>'

    card_class = "fw-item-card" + ("" if is_available else " unavailable")

    with ui.element("div").classes(card_class).style("position:relative"):
        ui.html(f"""
          {img_html}
          {badge_html}
          <div class="fw-item-body">
            <div class="fw-item-name">{item["name"]}</div>
            {desc_html}
            <div class="fw-item-footer">
              <div>
                <span class="fw-item-price">{price:.2f} CHF</span>
                {original_html}
              </div>
            </div>
          </div>
        """)
        if is_available and on_add_to_cart:
            ui.button(
                "+ Warenkorb",
                on_click=lambda i=item: on_add_to_cart(i),
            ).classes("fw-btn fw-btn-primary").style(
                "position:absolute;bottom:14px;right:14px;font-size:10px!important;padding:7px 12px;"
            )


def cart_item_row(item: CartItem, index: int, on_remove=None, on_update_qty=None) -> None:
    """One row in the dark shopping cart."""
    with ui.element("div").style(
        "display:flex;align-items:center;justify-content:space-between;"
        "padding:16px 0;border-bottom:1px solid rgba(255,255,255,0.07);"
    ):
        with ui.column().style("flex:1;gap:2px"):
            ui.label(item.name).style(
                "font-family:'Bebas Neue',sans-serif;font-size:20px;color:#F5F0E8;letter-spacing:1px"
            )
            if item.extras:
                ui.label(", ".join(f"+{e['name']}" for e in item.extras)).style("font-size:12px;color:#888")
            if item.notes:
                ui.label(f"Notiz: {item.notes}").style("font-size:12px;color:#666;font-style:italic")

        with ui.row().style("align-items:center;gap:8px"):
            ui.button(icon="remove", on_click=lambda i=index: _decrease(i, item.quantity, on_update_qty, on_remove)).props("round flat size=sm").style("color:#F5F0E8")
            ui.label(str(item.quantity)).style("font-size:18px;font-weight:700;min-width:24px;text-align:center;color:#F5F0E8")
            ui.button(icon="add", on_click=lambda i=index: on_update_qty(i, item.quantity + 1) if on_update_qty else None).props("round flat size=sm").style("color:#F5F0E8")

        ui.label(f"{item.total:.2f} CHF").style("font-weight:700;min-width:90px;text-align:right;color:#E63312;font-size:16px")
        ui.button(icon="delete", on_click=lambda i=index: on_remove(i) if on_remove else None).props("round flat size=sm").style("color:#555")


def _decrease(index: int, current_qty: int, on_update_qty, on_remove) -> None:
    if current_qty <= 1:
        if on_remove:
            on_remove(index)
    elif on_update_qty:
        on_update_qty(index, current_qty - 1)


def order_card(order: dict) -> None:
    """Dark styled order summary card."""
    status = order.get("status", "pending")
    sc = {"pending": "#F5C842", "preparing": "#378ADD", "ready": "#639922", "delivered": "#888", "collected": "#888"}.get(status, "#888")

    with ui.element("div").classes("fw-order-card"):
        with ui.row().style("width:100%;align-items:center;justify-content:space-between"):
            ui.label(f"Bestellung #{order['id']}").style("font-family:'Bebas Neue',sans-serif;font-size:22px;color:#F5F0E8;letter-spacing:1px")
            ui.html(f'<span style="background:{sc};color:#111;font-size:10px;font-weight:700;letter-spacing:2px;text-transform:uppercase;padding:4px 12px">{STATUS_LABELS.get(status, status)}</span>')
        ui.label(f"{'Lieferung' if order['order_type'] == 'delivery' else 'Abholung'} · {order['created_at']}").style("font-size:13px;color:#888;margin-top:4px")
        if order.get("items"):
            ui.html('<div style="border-top:1px solid rgba(255,255,255,0.07);margin:12px 0"></div>')
            for it in order["items"]:
                ui.label(f"{it['quantity']}× {it['name']} — {it['total']:.2f} CHF").style("font-size:13px;color:#aaa")
        ui.html('<div style="border-top:1px solid rgba(255,255,255,0.07);margin:12px 0"></div>')
        ui.label(f"Total: {order['total_price']:.2f} CHF").style("font-weight:700;color:#E63312;font-size:17px")
