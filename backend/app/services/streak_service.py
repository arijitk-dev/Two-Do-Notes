from datetime import date, timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.streak import Streak
from app.models.todo import Todo
from app.models.user import User
from app.services.accountability_service import AccountabilityService


class StreakService:
    """Daily accountability rules live here so the Phase 3 definition can evolve independently."""

    def recompute(self, db: Session, user: User, through_date: date) -> Streak:
        todos = list(db.scalars(select(Todo).where(Todo.user_id == user.id)))
        relevant_dates = [
            candidate
            for todo in todos
            for candidate in (todo.original_scheduled_date, todo.scheduled_date, todo.carried_from_date)
            if candidate and candidate <= through_date
        ]
        successful: list[date] = []
        longest = current = 0
        previous_accountable_success = False
        if relevant_dates:
            start = min(relevant_dates)
            metrics = AccountabilityService()
            latest_planned_date = max(
                day for day in relevant_dates
                if metrics.day_metrics(db, user, day, todos).planned > 0
            )
            for offset in range((latest_planned_date - start).days + 1):
                day = start + timedelta(days=offset)
                day_metrics = metrics.day_metrics(db, user, day, todos)
                if day_metrics.neutral:
                    # An empty day is neutral for planning metrics, but the
                    # existing streak contract treats a calendar gap as a
                    # break between successful-day runs.
                    current = 0
                    previous_accountable_success = False
                    continue
                if day_metrics.successful:
                    current = current + 1 if previous_accountable_success else 1
                    longest = max(longest, current)
                    successful.append(day)
                    previous_accountable_success = True
                else:
                    current = 0
                    previous_accountable_success = False
        streak = db.scalar(select(Streak).where(Streak.user_id == user.id))
        if not streak:
            streak = Streak(user_id=user.id)
            db.add(streak)
        streak.current_streak = current if successful else 0
        streak.max_streak = longest
        streak.last_successful_date = successful[-1] if successful else None
        db.flush()
        return streak
