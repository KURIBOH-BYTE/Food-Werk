"""Receipt service — generates PDF receipts for orders."""

from __future__ import annotations

from io import BytesIO
from datetime import datetime
from typing import TYPE_CHECKING

from fpdf import FPDF

if TYPE_CHECKING:
    from ..domain.models import Order


class ReceiptService:

    def generate_pdf(self, order: "Order") -> bytes:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_margins(20, 20, 20)

        # Header
        pdf.set_font("Helvetica", "B", 28)
        pdf.set_text_color(230, 51, 18)
        pdf.cell(0, 12, "FOODWERK", ln=True, align="C")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 6, "Fast Food Delivery & Pickup", ln=True, align="C")
        pdf.ln(4)

        # Divider
        pdf.set_draw_color(230, 51, 18)
        pdf.set_line_width(0.8)
        pdf.line(20, pdf.get_y(), 190, pdf.get_y())
        pdf.ln(6)

        # Title
        pdf.set_font("Helvetica", "B", 16)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(0, 10, f"Quittung - Bestellung #{order.id}", ln=True)
        pdf.ln(2)

        # Order info
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(60, 60, 60)
        created = order.created_at.strftime("%d.%m.%Y %H:%M") if order.created_at else "-"
        order_type = "Lieferung" if order.order_type == "delivery" else "Abholung"
        status_map = {
            "pending": "Ausstehend", "preparing": "In Zubereitung",
            "ready": "Bereit", "delivered": "Geliefert", "collected": "Abgeholt",
        }
        status = status_map.get(order.status, order.status)

        if order.user:
            pdf.cell(0, 7, f"Kunde: {order.user.first_name} {order.user.last_name}", ln=True)
        pdf.cell(0, 7, f"Datum: {created}", ln=True)
        pdf.cell(0, 7, f"Bestellart: {order_type}", ln=True)
        pdf.cell(0, 7, f"Status: {status}", ln=True)
        pdf.ln(4)

        # Divider
        pdf.set_draw_color(200, 200, 200)
        pdf.set_line_width(0.3)
        pdf.line(20, pdf.get_y(), 190, pdf.get_y())
        pdf.ln(5)

        # Items header
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(30, 30, 30)
        pdf.cell(100, 8, "Artikel", border=0)
        pdf.cell(30, 8, "Menge", align="C", border=0)
        pdf.cell(40, 8, "Preis", align="R", border=0, ln=True)

        pdf.set_draw_color(200, 200, 200)
        pdf.line(20, pdf.get_y(), 190, pdf.get_y())
        pdf.ln(3)

        # Items
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(60, 60, 60)
        for oi in order.order_items:
            name = oi.menu_item.name if oi.menu_item else f"Artikel #{oi.menu_item_id}"
            line_total = oi.unit_price * oi.quantity
            pdf.cell(100, 7, name, border=0)
            pdf.cell(30, 7, str(oi.quantity), align="C", border=0)
            pdf.cell(40, 7, f"CHF {line_total:.2f}", align="R", border=0, ln=True)
            if oi.notes:
                pdf.set_font("Helvetica", "I", 9)
                pdf.set_text_color(130, 130, 130)
                pdf.cell(10, 5, "", border=0)
                pdf.cell(160, 5, f"  > {oi.notes}", ln=True)
                pdf.set_font("Helvetica", "", 11)
                pdf.set_text_color(60, 60, 60)

        pdf.ln(3)
        pdf.set_draw_color(200, 200, 200)
        pdf.line(20, pdf.get_y(), 190, pdf.get_y())
        pdf.ln(4)

        # Total
        subtotal = sum(oi.unit_price * oi.quantity for oi in order.order_items)
        discount = round(subtotal * 0.10, 2) if subtotal > 50 else 0.0

        if discount > 0:
            pdf.set_font("Helvetica", "", 11)
            pdf.set_text_color(60, 60, 60)
            pdf.cell(130, 7, "Zwischentotal", border=0)
            pdf.cell(40, 7, f"CHF {subtotal:.2f}", align="R", ln=True)
            pdf.set_text_color(39, 128, 61)
            pdf.cell(130, 7, "Rabatt (10%)", border=0)
            pdf.cell(40, 7, f"- CHF {discount:.2f}", align="R", ln=True)

        pdf.set_font("Helvetica", "B", 13)
        pdf.set_text_color(230, 51, 18)
        pdf.cell(130, 9, "TOTAL", border=0)
        pdf.cell(40, 9, f"CHF {order.total_price:.2f}", align="R", ln=True)

        pdf.ln(8)

        # Footer
        pdf.set_draw_color(230, 51, 18)
        pdf.set_line_width(0.8)
        pdf.line(20, pdf.get_y(), 190, pdf.get_y())
        pdf.ln(5)
        pdf.set_font("Helvetica", "I", 9)
        pdf.set_text_color(130, 130, 130)
        pdf.cell(0, 6, "Vielen Dank für Ihre Bestellung bei FoodWerk!", ln=True, align="C")

        return bytes(pdf.output())
