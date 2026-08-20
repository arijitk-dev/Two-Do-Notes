from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.time import utc_now, user_today
from app.models.point_transaction import TransactionType
from app.models.todo import Todo, TodoStatus
from app.models.user import User
from app.schemas.todo import TodoCreate, TodoUpdate
from app.repositories.todo_repository import TodoRepository
from app.services.streak_service import StreakService
from app.services.point_service import PointService
from app.services.planning_service import PlanningService


class TodoService:
    def __init__(self, db: Session):
        self.db = db
        self.streaks = StreakService()
        self.repository = TodoRepository()
        self.points = PointService()
        self.planning = PlanningService(self.points)

    def get(self, user: User, todo_id: str) -> Todo:
        todo = self.repository.get(self.db, user.id, todo_id)
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        return todo

    def create(self, user: User, payload: TodoCreate) -> Todo:
        todo = Todo(
            user_id=user.id,
            original_scheduled_date=payload.scheduled_date,
            **payload.model_dump(),
        )
        self.db.add(todo)
        self.db.flush()
        self.planning.award_tomorrow_points_if_applicable(self.db, user, todo)
        self.db.commit()
        self.db.refresh(todo)
        return todo

    def update(self, user: User, todo_id: str, payload: TodoUpdate) -> Todo:
        todo = self.get(user, todo_id)
        if todo.status != TodoStatus.PENDING.value:
            raise HTTPException(status_code=400, detail="Only pending Todos can be edited")
        for key, value in payload.model_dump(exclude_unset=True).items():
            setattr(todo, key, value.strip() if isinstance(value, str) and key == "title" else value)
        if not todo.title.strip():
            raise HTTPException(status_code=422, detail="Todo title cannot be empty")
        self.db.commit()
        self.db.refresh(todo)
        return todo

    def delete(self, user: User, todo_id: str) -> None:
        todo = self.get(user, todo_id)
        self.db.delete(todo)
        self.db.commit()

    def complete(self, user: User, todo_id: str) -> Todo:
        todo = self.repository.get_for_update(self.db, user.id, todo_id)
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        today = user_today(user.timezone)
        if todo.scheduled_date != today:
            raise HTTPException(status_code=400, detail="Only today's Todos can be completed")
        if todo.status == TodoStatus.COMPLETED.value:
            return todo
        if todo.status != TodoStatus.PENDING.value:
            raise HTTPException(status_code=400, detail="Only pending Todos can be completed")
        todo.status = TodoStatus.COMPLETED.value
        todo.completed_at = utc_now()
        self.points.award_once(
            self.db, user, todo.id, TransactionType.TODO_COMPLETED.value,
            3, "Completed today's Todo",
        )
        if todo.carry_forward_count > 0 and not todo.carry_forward_bonus_awarded:
            self.points.award_once(
                self.db, user, todo.id, TransactionType.CARRY_FORWARD_BONUS.value,
                1, "Carry-forward completion bonus",
            )
            todo.carry_forward_bonus_awarded = True
        self.streaks.recompute(self.db, user, today)
        self.db.commit()
        self.db.refresh(todo)
        return todo

    def miss(self, user: User, todo_id: str, reason: str) -> Todo:
        todo = self.repository.get_for_update(self.db, user.id, todo_id)
        if not todo:
            raise HTTPException(status_code=404, detail="Todo not found")
        today = user_today(user.timezone)
        if todo.scheduled_date != today:
            raise HTTPException(status_code=400, detail="Only today's Todos can be missed")
        if todo.status == TodoStatus.MISSED.value:
            return todo
        if todo.status != TodoStatus.PENDING.value:
            raise HTTPException(status_code=400, detail="Only pending Todos can be missed")
        todo.status = TodoStatus.MISSED.value
        todo.missed_at = utc_now()
        todo.miss_reason = reason.strip()
        self.points.award_once(
            self.db, user, todo.id, TransactionType.TODO_MISSED.value,
            -7, f"Missed Todo: {reason.strip()}",
        )
        self.streaks.recompute(self.db, user, today)
        self.db.commit()
        self.db.refresh(todo)
        return todo
