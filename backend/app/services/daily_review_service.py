from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.daily_review import DailyReview
from app.models.user import User
from app.schemas.accountability import DailyReviewResponse, DailyReviewUpsert, DayMetricsResponse
from app.services.accountability_service import AccountabilityService


class DailyReviewService:
    def __init__(self, db: Session):
        self.db = db
        self.accountability = AccountabilityService()

    def get(self, user: User, review_date: date) -> DailyReviewResponse:
        review = self.db.scalar(select(DailyReview).where(DailyReview.user_id == user.id, DailyReview.review_date == review_date))
        stats = self.accountability.day_metrics(self.db, user, review_date)
        return self._response(review, stats)

    def save(self, user: User, review_date: date, payload: DailyReviewUpsert) -> DailyReviewResponse:
        review = self.db.scalar(select(DailyReview).where(DailyReview.user_id == user.id, DailyReview.review_date == review_date).with_for_update())
        values = payload.model_dump(exclude_unset=True)
        if review:
            for key, value in values.items():
                setattr(review, key, value)
        else:
            values = payload.model_dump()
        if review is None:
            review = DailyReview(user_id=user.id, review_date=review_date, **values)
            self.db.add(review)
        self.db.commit()
        self.db.refresh(review)
        return self._response(review, self.accountability.day_metrics(self.db, user, review_date))

    @staticmethod
    def _response(review: DailyReview | None, stats) -> DailyReviewResponse:
        return DailyReviewResponse(
            id=review.id if review else None,
            review_date=stats.review_date,
            mood_score=review.mood_score if review else None,
            went_well=review.went_well if review else None,
            improvement=review.improvement if review else None,
            created_at=review.created_at if review else None,
            updated_at=review.updated_at if review else None,
            stats=DayMetricsResponse(
                review_date=stats.review_date,
                planned=stats.planned,
                completed=stats.completed,
                missed=stats.missed,
                carried_forward=stats.carried_forward,
                pending=stats.pending,
                resolved=stats.resolved,
                completion_rate=round(stats.completion_rate, 4),
                successful=stats.successful,
                neutral=stats.neutral,
            ),
        )
