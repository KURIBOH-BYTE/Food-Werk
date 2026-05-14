"""Payment service — Stripe Checkout integration.

Flow:
  1. User confirms order on /checkout
  2. Server creates a Stripe Checkout Session (redirect mode)
  3. User is redirected to Stripe's hosted payment page
  4. Stripe redirects back to /payment/success or /payment/cancel
  5. On success, the pending order is saved to the database

Setup:
  Set the environment variable STRIPE_SECRET_KEY to your Stripe secret key.
  Example (terminal before starting the app):
      export STRIPE_SECRET_KEY=sk_test_...

  Get your key at: https://dashboard.stripe.com/apikeys
  Use a Secret Key (sk_test_...), NOT a Restricted Key (rk_test_...).
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING

import stripe

if TYPE_CHECKING:
    from .cart_service import CartService


class PaymentService:
    """Creates Stripe Checkout Sessions for order payment."""

    def __init__(self) -> None:
        self._key = os.environ.get("STRIPE_SECRET_KEY", "")

    @property
    def is_configured(self) -> bool:
        return bool(self._key)

    def create_checkout_session(
        self,
        cart: "CartService",
        success_url: str,
        cancel_url: str,
    ) -> str:
        """Create a Stripe Checkout Session and return the redirect URL.

        Raises ValueError if STRIPE_SECRET_KEY is not set or Stripe returns an error.
        """
        if not self._key:
            raise ValueError(
                "Stripe nicht konfiguriert. "
                "Bitte STRIPE_SECRET_KEY als Umgebungsvariable setzen."
            )

        stripe.api_key = self._key

        line_items = []
        for item in cart.items:
            line_items.append({
                "price_data": {
                    "currency": "chf",
                    "product_data": {"name": item.name},
                    "unit_amount": int(round(item.unit_price * 100)),
                },
                "quantity": item.quantity,
            })

        try:
            session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=line_items,
                mode="payment",
                success_url=success_url,
                cancel_url=cancel_url,
            )
        except stripe.error.AuthenticationError:
            raise ValueError(
                "Ungültiger Stripe API-Key. "
                "Bitte einen Secret Key (sk_test_...) verwenden."
            )
        except stripe.error.StripeError as e:
            raise ValueError(f"Stripe-Fehler: {e.user_message or str(e)}")

        return session.url
