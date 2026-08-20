from datetime import date

from pydantic import BaseModel


class CalendarDayResponse(BaseModel):
    date: date
    todo_count: int
    pending_count: int
    completed_count: int
    missed_count: int


class CalendarResponse(BaseModel):
    year: int
    month: int
    days: list[CalendarDayResponse]

