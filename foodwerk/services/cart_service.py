"""In-memory cart — no database access.

CartItem and CartService are pure business-logic objects.
They are serialized to/from dicts so they can be stored in NiceGUI's
server-side user storage (app.storage.user) between page navigations.
"""

from __future__ import annotations


class CartItem:
    """One line in the shopping cart."""

    def __init__(
        self,
        menu_item_id: int,
        name: str,
        quantity: int,
        unit_price: float,
        extras: list[dict] | None = None,
        notes: str | None = None,
    ) -> None:
        self.menu_item_id = menu_item_id
        self.name = name
        self.quantity = quantity
        self.unit_price = unit_price
        self.extras: list[dict] = extras or []
        self.notes = notes

    @property
    def extras_total(self) -> float:
        return sum(e["price"] * e.get("quantity", 1) for e in self.extras)

    @property
    def total(self) -> float:
        return round((self.unit_price + self.extras_total) * self.quantity, 2)

    def to_dict(self) -> dict:
        return {
            "menu_item_id": self.menu_item_id,
            "name": self.name,
            "quantity": self.quantity,
            "unit_price": self.unit_price,
            "extras": self.extras,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> CartItem:
        return cls(
            menu_item_id=data["menu_item_id"],
            name=data["name"],
            quantity=data["quantity"],
            unit_price=data["unit_price"],
            extras=data.get("extras", []),
            notes=data.get("notes"),
        )


class CartService:
    """Server-side in-memory shopping cart.

    Instances are ephemeral — reconstructed from storage on each request
    and serialized back after every mutation.
    """

    def __init__(self, items: list[CartItem] | None = None) -> None:
        self.items: list[CartItem] = items or []

    def add_item(
        self,
        menu_item_id: int,
        name: str,
        unit_price: float,
        quantity: int = 1,
        extras: list[dict] | None = None,
        notes: str | None = None,
    ) -> None:
        if quantity < 1:
            raise ValueError("Quantity must be at least 1.")
        for item in self.items:
            if item.menu_item_id == menu_item_id and item.extras == (extras or []) and item.notes == notes:
                item.quantity += quantity
                return
        self.items.append(CartItem(menu_item_id, name, quantity, unit_price, extras, notes))

    def remove_item(self, index: int) -> None:
        if 0 <= index < len(self.items):
            self.items.pop(index)

    def update_quantity(self, index: int, quantity: int) -> None:
        if quantity < 1:
            raise ValueError("Quantity must be at least 1.")
        if 0 <= index < len(self.items):
            self.items[index].quantity = quantity

    def clear(self) -> None:
        self.items.clear()

    @property
    def subtotal(self) -> float:
        return round(sum(item.total for item in self.items), 2)

    @property
    def discount(self) -> float:
        """10% discount when subtotal exceeds CHF 50."""
        if self.subtotal > 50.0:
            return round(self.subtotal * 0.10, 2)
        return 0.0

    @property
    def total(self) -> float:
        return round(self.subtotal - self.discount, 2)

    @property
    def item_count(self) -> int:
        return sum(item.quantity for item in self.items)

    @property
    def is_empty(self) -> bool:
        return len(self.items) == 0

    def to_dict_list(self) -> list[dict]:
        return [item.to_dict() for item in self.items]

    @classmethod
    def from_dict_list(cls, data: list[dict]) -> CartService:
        return cls(items=[CartItem.from_dict(d) for d in data])
