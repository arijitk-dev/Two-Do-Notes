from datetime import date

from fastapi import APIRouter

from app.api.deps import CurrentUser, DbSession
from app.schemas.accountability import DailyReviewResponse, DailyReviewUpsert
from app.services.daily_review_service import DailyReviewService


router = APIRouter(prefix="/reviews", tags=["daily reviews"])


@router.get("/{review_date}", response_model=DailyReviewResponse)
def get_review(review_date: date, user: CurrentUser, db: DbSession):
    return DailyReviewService(db).get(user, review_date)


@router.post("/{review_date}", response_model=DailyReviewResponse)
def create_review(review_date: date, payload: DailyReviewUpsert, user: CurrentUser, db: DbSession):
    return DailyReviewService(db).save(user, review_date, payload)


@router.patch("/{review_date}", response_model=DailyReviewResponse)
def update_review(review_date: date, payload: DailyReviewUpsert, user: CurrentUser, db: DbSession):
    return DailyReviewService(db).save(user, review_date, payload)
