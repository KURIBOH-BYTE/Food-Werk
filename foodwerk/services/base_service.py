"""Abstract base class for all services.

Design pattern: Abstract Base Class (ABC) — forces every service to
implement ``get_by_id`` and ``get_all``. Services receive DAOs in their
constructor, never raw sessions.
"""

from __future__ import annotations

from abc import ABC, abstractmethod


class BaseService(ABC):
    """Common interface for all FoodWerk services."""

    @abstractmethod
    def get_by_id(self, entity_id: int):
        """Return a single entity by its primary key."""

    @abstractmethod
    def get_all(self):
        """Return all entities of this type."""
