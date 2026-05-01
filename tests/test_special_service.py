from datetime import datetime, timedelta
from foodwerk.data_access.dao import SpecialDAO
from foodwerk.services.special_service import SpecialService


def _make_service(engine) -> SpecialService:
    return SpecialService(special_dao=SpecialDAO(engine))


class TestSpecialService:
    def test_create_special(self, seeded_engine):
        svc = _make_service(seeded_engine)
        now = datetime.utcnow()
        special = svc.create_special(
            menu_item_id=1, created_by=1, special_price=9.90,
            start_date=now, end_date=now + timedelta(days=7),
            description="Test Special",
        )
        assert special.id is not None
        assert special.special_price == 9.90
        assert special.is_active is True

    def test_deactivate_special(self, seeded_engine):
        svc = _make_service(seeded_engine)
        now = datetime.utcnow()
        special = svc.create_special(
            menu_item_id=1, created_by=1, special_price=9.90,
            start_date=now, end_date=now + timedelta(days=7),
        )
        deactivated = svc.deactivate_special(special.id)
        assert deactivated.is_active is False
