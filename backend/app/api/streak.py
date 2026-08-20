from fastapi import APIRouter
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.core.time import user_today
from app.models.streak import Streak
from app.schemas.common import StreakResponse
from app.services.streak_service import StreakService

router = APIRouter(prefix="/streak", tags=["streak"])


@router.get("", response_model=StreakResponse)
def get_streak(user: CurrentUser, db: DbSession):
    streak = StreakService().recompute(db, user, user_today(user.timezone))
    db.commit()
    return streak

