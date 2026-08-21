from sqlalchemy.orm import Session

from app.core.time import user_tomorrow
from app.core.accountability import TOMORROW_PLANNING_POINTS
from app.models.point_transaction import TransactionType
from app.models.todo import Todo
from app.models.user import User
from app.services.point_service import PointService


class PlanningService:
    def __init__(self, points: PointService | None = None):
        self.points = points or PointService()

    def award_tomorrow_points_if_applicable(self, db: Session, user: User, todo: Todo) -> None:
        if todo.scheduled_date == user_tomorrow(user.timezone):
            self.points.award_once(
                db, user, todo.id, TransactionType.TODO_PLANNED_TOMORROW.value,
                TOMORROW_PLANNING_POINTS, "Planned Todo for tomorrow",
            )
