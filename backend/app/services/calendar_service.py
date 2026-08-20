import calendar as calendar_module
from datetime import date

from sqlalchemy.orm import Session

from app.models.user import User
from app.repositories.todo_repository import TodoRepository
from app.schemas.calendar import CalendarDayResponse, CalendarResponse


class CalendarService:
    def month(self, db: Session, user: User, year: int, month: int) -> CalendarResponse:
        if month < 1 or month > 12:
            raise ValueError("Month must be between 1 and 12")
        last_day = calendar_module.monthrange(year, month)[1]
        start, end = date(year, month, 1), date(year, month, last_day)
        todos = TodoRepository().list_between(db, user.id, start, end)
        grouped = {day: [] for day in range(1, last_day + 1)}
        for todo in todos:
            grouped[todo.scheduled_date.day].append(todo)
        days = []
        for day, day_todos in grouped.items():
            days.append(CalendarDayResponse(
                date=date(year, month, day),
                todo_count=len(day_todos),
                pending_count=sum(todo.status == "pending" for todo in day_todos),
                completed_count=sum(todo.status == "completed" for todo in day_todos),
                missed_count=sum(todo.status == "missed" for todo in day_todos),
            ))
        return CalendarResponse(year=year, month=month, days=days)

