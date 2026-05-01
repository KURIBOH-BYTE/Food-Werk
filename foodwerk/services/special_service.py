"""Special service — time-limited deals."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from .base_service import BaseService
from ..data_access.dao import SpecialDAO
from ..domain.models import Special


class SpecialService(BaseService):

    def __init__(self, special_dao: SpecialDAO) -> None:
        self.special_dao = special_dao

    def get_by_id(self, entity_id: int) -> Optional[Special]:
        return self.special_dao.get_by_id(entity_id)

    def get_all(self) -> list[Special]:
        return self.special_dao.get_all()

    # ------------------------------------------------------------------

    def create_special(
        self,
        menu_item_id: int,
        created_by: int,
        special_price: float,
        start_date: datetime,
        end_date: datetime,
        description: Optional[str] = None,
    ) -> Special:
        if end_date <= start_date:
            raise ValueError("End date must be after start date.")
        if special_price <= 0:
            raise ValueError("Special price must be greater than 0.")

        special = Special(
            menu_item_id=menu_item_id,
            created_by=created_by,
            special_price=special_price,
            start_date=start_date,
            end_date=end_date,
            is_active=True,
            description=description,
        )
        return self.special_dao.create(special)

    def update_special(self, special_id: int, **kwargs) -> Special:
        special = self.special_dao.update(special_id, **kwargs)
        if not special:
            raise ValueError("Special not found.")
        return special

    def deactivate_special(self, special_id: int) -> Special:
        return self.update_special(special_id, is_active=False)
