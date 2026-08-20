from datetime import date, datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.note import NoteResponse
from app.schemas.todo import TodoResponse


class PointTransactionResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    todo_id: str | None
    transaction_type: str
    points: int
    description: str
    created_at: datetime


class StreakResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    current_streak: int
    max_streak: int
    last_successful_date: date | None


class DashboardResponse(BaseModel):
    today: date
    tomorrow: date
    user_name: str
    total_points: int
    today_completed: int
    today_total: int
    current_streak: int
    max_streak: int
    todos: list[TodoResponse]
    unfinished_todos: list[TodoResponse]
    tomorrow_todos: list[TodoResponse]
    tomorrow_planned_points: int
    recent_notes: list[NoteResponse]
