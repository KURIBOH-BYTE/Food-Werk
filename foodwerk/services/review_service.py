"""Review service — customer ratings and comments."""

from __future__ import annotations

from typing import Optional

from .base_service import BaseService
from ..data_access.dao import ReviewDAO
from ..domain.models import Review


class ReviewService(BaseService):

    def __init__(self, review_dao: ReviewDAO) -> None:
        self.review_dao = review_dao

    def get_by_id(self, entity_id: int) -> Optional[Review]:
        return self.review_dao.get_by_id(entity_id)

    def get_all(self) -> list[Review]:
        return self.review_dao.get_all()

    # ------------------------------------------------------------------

    def create_review(
        self,
        user_id: int,
        menu_item_id: int,
        order_id: int,
        rating: int,
        comment: Optional[str] = None,
    ) -> Review:
        if not 1 <= rating <= 5:
            raise ValueError("Rating must be between 1 and 5.")

        review = Review(
            user_id=user_id,
            menu_item_id=menu_item_id,
            order_id=order_id,
            rating=rating,
            comment=comment,
        )
        return self.review_dao.create(review)

    def get_reviews_for_item(self, menu_item_id: int) -> list[Review]:
        return self.review_dao.get_by_menu_item(menu_item_id)

    def get_average_rating(self, menu_item_id: int) -> Optional[float]:
        reviews = self.get_reviews_for_item(menu_item_id)
        if not reviews:
            return None
        return round(sum(r.rating for r in reviews) / len(reviews), 1)
