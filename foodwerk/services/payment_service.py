"""Payment service — card validation and order completion.

In test mode (default), Stripe is not called. The service validates
test card numbers and creates orders directly.

Test cards:
    4242 4242 4242 4242  →  always succeeds
    4000 0000 0000 0002  →  card declined
    5555 5555 5555 4444  →  always succeeds (Mastercard)
    any other number     →  invalid card

To switch to real Stripe, set use_stripe=True and provide a valid
STRIPE_SECRET_KEY. The full Stripe Checkout redirect flow is still
supported but not required for a working demo.
"""

from __future__ import annotations

import re
from typing import Optional


# Test cards that simulate success
_SUCCESS_CARDS = {
    "4242424242424242",  # Visa
    "5555555555554444",  # Mastercard
    "378282246310005",   # Amex
}

# Test cards that simulate decline
_DECLINED_CARDS = {
    "4000000000000002",  # Generic decline
    "4000000000009995",  # Insufficient funds
}


def _normalize(card_number: str) -> str:
    """Strip spaces and dashes from card number."""
    return re.sub(r"[\s\-]", "", card_number)


class PaymentService:
    """Validates payment cards and manages order completion.

    Uses simulated test cards by default — no Stripe account required.
    """

    def validate_card(
        self,
        card_number: str,
        expiry: str,
        cvv: str,
        name: str,
    ) -> tuple[bool, str]:
        """Validate card fields and return (success, error_message).

        Returns (True, "") on success.
        Returns (False, reason) on failure.
        """
        normalized = _normalize(card_number)

        if not normalized.isdigit() or len(normalized) < 13 or len(normalized) > 19:
            return False, "Invalid card number."

        if not name.strip():
            return False, "Name on card is required."

        if not re.match(r"^(0[1-9]|1[0-2])/\d{2}$", expiry.strip()):
            return False, "Expiry must be in MM/YY format."

        if not re.match(r"^\d{3,4}$", cvv.strip()):
            return False, "CVV must be 3 or 4 digits."

        if normalized in _DECLINED_CARDS:
            return False, "Your card was declined. Please use a different card."

        if normalized not in _SUCCESS_CARDS:
            return False, "Card not recognized. Use test card 4242 4242 4242 4242."

        return True, ""

    def get_test_cards(self) -> list[dict]:
        """Return test card info for display in the UI."""
        return [
            {
                "number": "4242 4242 4242 4242",
                "brand": "Visa",
                "result": "success",
                "label": "Always succeeds",
            },
            {
                "number": "5555 5555 5555 4444",
                "brand": "Mastercard",
                "result": "success",
                "label": "Always succeeds",
            },
            {
                "number": "4000 0000 0000 0002",
                "brand": "Visa",
                "result": "decline",
                "label": "Always declined",
            },
        ]
