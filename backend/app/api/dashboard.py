from fastapi import APIRouter
from app.api.deps import CurrentUser, DbSession
from app.core.time import user_today, user_tomorrow
from app.repositories.note_repository import NoteRepository
from app.repositories.point_repository import PointRepository
from app.repositories.todo_repository import TodoRepository
from app.schemas.common import DashboardResponse
from app.services.accountability_service import AccountabilityService

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("", response_model=DashboardResponse)
def dashboard(user: CurrentUser, db: DbSession):
    today = user_today(user.timezone)
    todos = TodoRepository().list(db, user.id, today)
    tomorrow = user_tomorrow(user.timezone)
    unfinished = TodoRepository().unresolved(db, user.id, today)
    tomorrow_todos = TodoRepository().list(db, user.id, tomorrow)
    notes = NoteRepository().list(db, user.id, limit=3)
    total = PointRepository().total(db, user.id)
    tomorrow_planned_points = PointRepository().planning_points_for_date(db, user.id, tomorrow)
    accountability = AccountabilityService().summary(db, user, range_name="today")
    db.commit()
    return DashboardResponse(
        today=today, tomorrow=tomorrow, user_name=user.name, total_points=total,
        today_completed=accountability.completed_count, today_total=accountability.planned_count,
        current_streak=accountability.current_streak, max_streak=accountability.max_streak,
        todos=todos, unfinished_todos=unfinished, tomorrow_todos=tomorrow_todos,
        tomorrow_planned_points=tomorrow_planned_points, recent_notes=notes, accountability=accountability,
    )
