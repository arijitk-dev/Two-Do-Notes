from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.streak import Streak
from app.models.todo import Todo, TodoStatus
from app.models.user import User


class StreakService:
    """Daily accountability rules live here so the Phase 3 definition can evolve independently."""

    def recompute(self, db: Session, user: User, through_date: date) -> Streak:
        todos = list(db.scalars(select(Todo).where(Todo.user_id == user.id, Todo.scheduled_date <= through_date)))
        by_day: dict[date, list[Todo]] = {}
        for todo in todos:
            by_day.setdefault(todo.scheduled_date, []).append(todo)
        successful = sorted(
            day for day, day_todos in by_day.items()
            if any(todo.status == TodoStatus.COMPLETED.value for todo in day_todos)
            and all(todo.status != TodoStatus.PENDING.value for todo in day_todos)
        )
        longest = current = 0
        previous: date | None = None
        for day in successful:
            current = current + 1 if previous and day == previous + timedelta(days=1) else 1
            longest = max(longest, current)
            previous = day
        streak = db.scalar(select(Streak).where(Streak.user_id == user.id))
        if not streak:
            streak = Streak(user_id=user.id)
            db.add(streak)
        streak.current_streak = current if successful else 0
        streak.max_streak = longest
        streak.last_successful_date = successful[-1] if successful else None
        db.flush()
        return streak

