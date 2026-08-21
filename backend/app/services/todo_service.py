from datetime import timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.time import utc_now, user_today
from app.core.accountability import (
    CARRY_FORWARD_BONUS,
    MISS_REASON_LABELS,
    MISSED_TODO_PENALTY,
    TODO_HISTORY_RETENTION_DAYS,
    TODO_COMPLETION_POINTS,
    miss_reason_label,
)
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

    @staticmethod
    def _normalized(value: str | None) -> str:
        return " ".join((value or "").split()).casefold()

    def _is_equivalent(self, first: Todo, second: Todo) -> bool:
        return (
            self._normalized(first.title) == self._normalized(second.title)
            and self._normalized(first.description) == self._normalized(second.description)
            and first.priority == second.priority
        )

    def _reuse_one(self, user: User, source_id: str, today, today_todos: list[Todo]) -> Todo | None:
        source = self.repository.get_for_update(self.db, user.id, source_id)
        if not source:
            raise HTTPException(status_code=404, detail="Historical Todo not found")
        history_start = today - timedelta(days=TODO_HISTORY_RETENTION_DAYS - 1)
        history_end = today - timedelta(days=1)
        if source.scheduled_date < history_start or source.scheduled_date > history_end:
            raise HTTPException(status_code=400, detail="This Todo is outside the 15-day reuse window")
        if any(self._is_equivalent(source, todo) for todo in today_todos):
            return None
        todo = Todo(
            user_id=user.id,
            title=source.title,
            description=source.description,
            scheduled_date=today,
            original_scheduled_date=today,
            priority=source.priority,
            source_todo_id=source.id,
        )
        self.db.add(todo)
        self.db.flush()
        today_todos.append(todo)
        return todo

    def reuse(self, user: User, source_id: str, allow_duplicate_skip: bool = False) -> Todo:
        today = user_today(user.timezone)
        today_todos = self.repository.list(self.db, user.id, scheduled_date=today)
        todo = self._reuse_one(user, source_id, today, today_todos)
        if todo is None:
            if allow_duplicate_skip:
                raise HTTPException(status_code=409, detail="This Todo is already on today's Todo list")
            raise HTTPException(status_code=409, detail="This Todo is already on today's Todo list")
        self.db.commit()
        self.db.refresh(todo)
        return todo

    def reuse_many(self, user: User, source_ids: list[str]) -> list[Todo]:
        today = user_today(user.timezone)
        today_todos = self.repository.list(self.db, user.id, scheduled_date=today)
        created: list[Todo] = []
        for source_id in dict.fromkeys(source_ids):
            todo = self._reuse_one(user, source_id, today, today_todos)
            if todo is not None:
                created.append(todo)
        self.db.commit()
        for todo in created:
            self.db.refresh(todo)
        return created

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
            TODO_COMPLETION_POINTS, "Completed today's Todo",
        )
        if todo.carry_forward_count > 0 and not todo.carry_forward_bonus_awarded:
            self.points.award_once(
                self.db, user, todo.id, TransactionType.CARRY_FORWARD_BONUS.value,
                CARRY_FORWARD_BONUS, "Carry-forward completion bonus",
            )
            todo.carry_forward_bonus_awarded = True
        self.streaks.recompute(self.db, user, today)
        self.db.commit()
        self.db.refresh(todo)
        return todo

    def miss(self, user: User, todo_id: str, reason: str, reason_code: str | None = None, reason_text: str | None = None) -> Todo:
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
        normalized_code = reason_code if reason_code in MISS_REASON_LABELS else None
        if normalized_code is None:
            normalized_code = next(
                (code for code, label in MISS_REASON_LABELS.items() if label.lower() == reason.strip().lower()),
                "other",
            )
        display_reason = reason_text.strip() if normalized_code == "other" and reason_text else miss_reason_label(normalized_code, reason.strip())
        todo.status = TodoStatus.MISSED.value
        todo.missed_at = utc_now()
        todo.miss_reason = display_reason
        todo.miss_reason_code = normalized_code
        todo.miss_reason_text = reason_text.strip() if reason_text else None
        self.points.award_once(
            self.db, user, todo.id, TransactionType.TODO_MISSED.value,
            MISSED_TODO_PENALTY, f"Missed Todo: {display_reason}",
        )
        self.streaks.recompute(self.db, user, today)
        self.db.commit()
        self.db.refresh(todo)
        return todo
