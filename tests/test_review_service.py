from foodwerk.data_access.dao import ReviewDAO
from foodwerk.services.review_service import ReviewService


def _make_service(engine) -> ReviewService:
    return ReviewService(review_dao=ReviewDAO(engine))


class TestReviewService:
    def test_create_review(self, seeded_engine):
        svc = _make_service(seeded_engine)
        review = svc.create_review(user_id=1, menu_item_id=1, order_id=1, rating=5, comment="Great!")
        assert review.id is not None
        assert review.rating == 5
