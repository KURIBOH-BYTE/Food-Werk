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
  /* Custom font utility used via class="font-display" */
  .font-display { font-family: 'Bebas Neue', sans-serif !important; }

  /* NiceGUI / Quasar layout overrides — cannot be expressed with Tailwind alone */
  body, .q-page { background: #111111 !important; color: #F5F0E8 !important; font-family: 'Barlow', sans-serif !important; overflow-x: hidden; }
  .q-header { background: transparent !important; box-shadow: none !important; }
  .nicegui-content { align-items: stretch !important; padding: 0 !important; gap: 0 !important; width: 100% !important; }
  .nicegui-column { align-items: stretch !important; width: 100% !important; }
  .q-page { padding: 0 !important; }

  /* Quasar form field overrides */
  .q-field__control { background: rgba(255,255,255,0.05) !important; }
  .q-field__label { color: rgba(245,240,232,0.6) !important; }
  input, textarea { color: #F5F0E8 !important; }
  .q-select__dropdown-icon { color: #F5F0E8 !important; }
  .q-field__native, .q-field__input { color: #F5F0E8 !important; }
  .q-menu { background: #1a1a1a !important; border: 1px solid rgba(255,255,255,0.1) !important; }
  .q-item { color: #F5F0E8 !important; font-size: 16px !important; padding: 12px 16px !important; }
  .q-item:hover, .q-item--active { background: rgba(230,51,18,0.15) !important; color: #fff !important; }
  .q-item--active { color: #E63312 !important; font-weight: 700 !important; }

  /* Quasar date picker overrides */
  .q-date { background: #1a1a1a !important; color: #F5F0E8 !important; border: 1px solid rgba(255,255,255,0.1); }
  .q-date__header { background: #E63312 !important; }
  .q-date__header-title, .q-date__header-subtitle { color: #fff !important; }
  .q-date__calendar-item .q-btn { color: #F5F0E8 !important; }
  .q-date__calendar-item .q-btn.bg-primary { background: #E63312 !important; color: #fff !important; }
  .q-date__navigation .q-btn { color: #F5F0E8 !important; }
  .q-date__years-item .q-btn, .q-date__months-item .q-btn { color: #F5F0E8 !important; }
  .q-date__calendar-weekdays > div { color: #888 !important; }
  .q-date__today .q-btn { border: 1px solid #E63312 !important; }

  /* Custom scrollbar */
  ::-webkit-scrollbar { width: 6px; }
  ::-webkit-scrollbar-track { background: #111111; }
  ::-webkit-scrollbar-thumb { background: #E63312; }

  /* Ticker animation — keyframes not expressible in Tailwind */
  @keyframes fwtick { from { transform: translateX(0); } to { transform: translateX(-50%); } }
  .fw-ticker-inner { display: inline-block; font-family: 'Bebas Neue', sans-serif; font-size: 18px; letter-spacing: 3px; color: #fff; animation: fwtick 24s linear infinite; }

  /* Menu card: ::before gradient overlay + image hover scale — requires pseudo-elements */
  .fw-menu-card { position: relative; overflow: hidden; cursor: pointer; transition: transform .3s; aspect-ratio: 1; display: flex; flex-direction: column; justify-content: flex-end; padding: 24px; background: #1a1a1a; }
  .fw-menu-card:hover { transform: scale(1.02); z-index: 2; }
  .fw-menu-card::before { content: ''; position: absolute; inset: 0; background: linear-gradient(to top, rgba(0,0,0,0.88) 0%, transparent 55%); z-index: 1; }
  .fw-menu-card img { position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; transition: transform .5s; }
  .fw-menu-card:hover img { transform: scale(1.06); }
  .fw-menu-card.big { grid-column: span 2; aspect-ratio: 2/1; }

  /* Item card: hover transitions & unavailable state */
  .fw-item-card { transition: border-color .2s, transform .2s, box-shadow .2s; }
  .fw-item-card:hover { border-color: #E63312 !important; transform: translateY(-3px); box-shadow: 0 8px 32px rgba(230,51,18,0.12); }
  .fw-item-card.unavailable { opacity: 0.45; pointer-events: none; }

  /* Category filter link: active/hover border underline */
  .fw-cat-link { display: block; color: rgba(245,240,232,0.5); text-decoration: none; font-size: 11px; font-weight: 700; letter-spacing: 2px; text-transform: uppercase; padding: 14px 20px; border-bottom: 2px solid transparent; transition: color .2s, border-color .2s; white-space: nowrap; }
  .fw-cat-link:hover, .fw-cat-link.active { color: #F5F0E8; border-bottom-color: #E63312; }

  /* Quasar button overrides for fw-btn variants */
  .fw-btn { font-family: 'Barlow', sans-serif !important; font-weight: 700 !important; font-size: 13px !important; letter-spacing: 1.5px !important; text-transform: uppercase !important; border-radius: 0 !important; }
  .fw-btn-primary { background: #E63312 !important; color: #fff !important; border: none !important; }
  .fw-btn-outline { background: transparent !important; color: #F5F0E8 !important; border: 1.5px solid rgba(245,240,232,0.3) !important; }

  /* Shared card containers */
  .fw-order-card { background: #1a1a1a; border: 1px solid rgba(255,255,255,0.07); padding: 20px; margin-bottom: 12px; }
  .fw-admin-card { background: #1a1a1a !important; border: 1px solid rgba(255,255,255,0.07) !important; border-radius: 0 !important; color: #F5F0E8 !important; margin-bottom: 12px; }
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

    badge_display = "inline-block" if cart_count else "none"
    cart_label = (
        f'Cart<span id="fw-cart-badge" '
        f'class="bg-[#E63312] text-white text-[10px] font-bold px-[7px] py-[2px] rounded-[20px] ml-1" '
        f'style="display:{badge_display}">{cart_count}</span>'
    )

    nav_link = 'class="text-[#F5F0E8] no-underline text-[12px] font-bold tracking-[1.5px] uppercase hover:text-[#E63312] transition-colors"'

    extra_links = ""
    if user:
        if user.get("role") in ("admin", "employee"):
            extra_links += f'<li><a {nav_link} href="/admin">Admin</a></li>'
        extra_links += f'<li><a {nav_link} href="/profile">Account</a></li>'
        extra_links += f'<li><a {nav_link} href="/logout">Logout</a></li>'
    else:
        extra_links += f'<li><a {nav_link} href="/login">Login</a></li>'

    ui.html(f"""
    <nav class="fixed top-0 left-0 right-0 z-[999] h-16 bg-[rgba(17,17,17,0.95)] border-b border-[rgba(255,255,255,0.07)] backdrop-blur-sm">
      <div class="max-w-[1600px] mx-auto h-full px-[60px] flex items-center justify-between">
        <a class="font-display text-[28px] tracking-[2px] text-[#E63312] no-underline select-none" href="/" draggable="false">FOOD<span class="text-[#F5F0E8]">WERK</span></a>
        <ul class="flex gap-7 items-center list-none m-0 p-0">
          <li><a {nav_link} href="/menu">Menu</a></li>
          <li><a {nav_link} href="/specials">Specials</a></li>
          <li><a {nav_link} href="/cart">{cart_label}</a></li>
          {extra_links}
        </ul>
      </div>
    </nav>
    """)


def menu_card(item: dict, on_add_to_cart=None) -> None:
    """Modern item card — image top, content bottom."""
    from datetime import datetime as _dt
    is_available = item.get("is_available", True)
    is_special = item.get("is_special", False)

    discount_price = item.get("discount_price")
    discount_until = item.get("discount_until")
    discount_active = (
        discount_price is not None
        and (discount_until is None or discount_until >= _dt.utcnow())
    )
    effective_price = discount_price if discount_active else item["price"]

    if item.get("image_url"):
        img_html = f'<img class="w-full aspect-[4/3] object-cover block" src="{item["image_url"]}" alt="{item["name"]}" loading="lazy">'
    else:
        img_html = '<div class="w-full aspect-[4/3] flex items-center justify-center" style="background:linear-gradient(135deg,#1a0a00,#2a1200)"><span class="font-display text-[32px] text-[#333]">FW</span></div>'

    badge_html = '<div class="absolute top-[10px] left-[10px] bg-[#F5C842] text-[#111] text-[9px] font-bold tracking-[2px] uppercase px-2 py-[3px]">Special</div>' if is_special else ""
    unavailable_badge_html = '<div class="absolute top-[10px] right-[10px] bg-[rgba(0,0,0,0.75)] text-[#aaa] text-[9px] font-bold tracking-[2px] uppercase px-2 py-[3px] border border-[rgba(255,255,255,0.15)]">Not Available</div>' if not is_available else ""
    original_html = f'<span class="text-[12px] text-[#555] line-through ml-1">{item["price"]:.2f}</span>' if discount_active else ""
    desc = item.get("description") or ""
    desc_html = f'<div class="text-[12px] text-[#666] leading-[1.4] mb-3 flex-1">{desc[:60]}{"…" if len(desc) > 60 else ""}</div>' if desc else '<div class="flex-1"></div>'

    card_class = "fw-item-card bg-[#1a1a1a] border border-[rgba(255,255,255,0.07)] overflow-hidden cursor-pointer flex flex-col relative"
    if not is_available:
        card_class += " unavailable"

    with ui.element("div").classes(card_class):
        ui.html(f"""
          {img_html}
          {badge_html}
          {unavailable_badge_html}
          <div class="p-4 flex flex-col flex-1">
            <div class="font-display text-[20px] text-[#F5F0E8] tracking-[1px] leading-[1.1] mb-1">{item["name"]}</div>
            {desc_html}
            <div class="flex items-center justify-between mt-auto gap-2">
              <div>
                <span class="text-[17px] font-bold text-[#E63312]">{effective_price:.2f} CHF</span>
                {original_html}
              </div>
            </div>
          </div>
        """)
        if is_available and on_add_to_cart:
            ui.button(
                "+ Add to Cart",
                on_click=lambda i=item: on_add_to_cart(i),
            ).classes("fw-btn fw-btn-primary absolute bottom-[14px] right-[14px]").style(
                "font-size:10px!important;padding:7px 12px;"
            )


def cart_item_row(item: CartItem, index: int, on_remove=None, on_update_qty=None) -> None:
    """One row in the dark shopping cart."""
    with ui.element("div").classes("flex items-center justify-between py-4 border-b border-[rgba(255,255,255,0.07)]"):
        with ui.column().classes("flex-1 gap-[2px]"):
            ui.label(item.name).classes("font-display text-[20px] text-[#F5F0E8] tracking-[1px]")
            if item.extras:
                ui.label(", ".join(f"+{e['name']}" for e in item.extras)).classes("text-[12px] text-[#888]")
            if item.notes:
                ui.label(f"Note: {item.notes}").classes("text-[12px] text-[#666] italic")

        with ui.row().classes("items-center gap-2"):
            ui.button(icon="remove", on_click=lambda i=index: _decrease(i, item.quantity, on_update_qty, on_remove)).props("round flat size=sm").classes("text-[#F5F0E8]")
            ui.label(str(item.quantity)).classes("text-[18px] font-bold min-w-[24px] text-center text-[#F5F0E8]")
            ui.button(icon="add", on_click=lambda i=index: on_update_qty(i, item.quantity + 1) if on_update_qty else None).props("round flat size=sm").classes("text-[#F5F0E8]")

        ui.label(f"{item.total:.2f} CHF").classes("font-bold min-w-[90px] text-right text-[#E63312] text-[16px]")
        ui.button(icon="delete", on_click=lambda i=index: on_remove(i) if on_remove else None).props("round flat size=sm").classes("text-[#555]")


def _decrease(index: int, current_qty: int, on_update_qty, on_remove) -> None:
    if current_qty <= 1:
        if on_remove:
            on_remove(index)
    elif on_update_qty:
        on_update_qty(index, current_qty - 1)


def order_card(order: dict, receipt_id: int | None = None) -> None:
    """Dark styled order summary card."""
    status = order.get("status", "pending")
    sc = {"pending": "#F5C842", "preparing": "#378ADD", "ready": "#639922", "delivered": "#888", "collected": "#888"}.get(status, "#888")

    with ui.element("div").classes("fw-order-card"):
        with ui.row().classes("w-full items-center justify-between"):
            ui.label(f"Order #{order['id']}").classes("font-display text-[22px] text-[#F5F0E8] tracking-[1px]")
            ui.html(f'<span class="text-[#111] text-[10px] font-bold tracking-[2px] uppercase px-3 py-1" style="background:{sc}">{STATUS_LABELS.get(status, status)}</span>')
        ui.label(
            f"{'Delivery' if order['order_type'] == 'delivery' else 'Pickup'} · {order['created_at']}"
        ).classes("text-[13px] text-[#888] mt-1")
        if order.get("items"):
            ui.html('<div class="border-t border-[rgba(255,255,255,0.07)] my-3"></div>')
            for it in order["items"]:
                ui.label(f"{it['quantity']}× {it['name']} — {it['total']:.2f} CHF").classes("text-[13px] text-[#aaa]")
        ui.html('<div class="border-t border-[rgba(255,255,255,0.07)] my-3"></div>')
        with ui.row().classes("w-full items-center justify-between"):
            ui.label(f"Total: {order['total_price']:.2f} CHF").classes("font-bold text-[#E63312] text-[17px]")
            if receipt_id is not None:
                ui.html(
                    f'<a href="/receipt/{receipt_id}" target="_blank" download="receipt_{receipt_id}.pdf" '
                    f'class="inline-flex items-center gap-[5px] bg-transparent text-[#E63312] '
                    f'border border-[#E63312] font-display text-[12px] tracking-[2px] '
                    f'px-[14px] py-[6px] no-underline uppercase">&#x2193; Receipt</a>'
                )
