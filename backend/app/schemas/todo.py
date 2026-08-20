from datetime import date, datetime
from enum import StrEnum

from pydantic import BaseModel, ConfigDict, Field, model_validator


class Priority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TodoStatusResponse(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    MISSED = "missed"


class TodoCreate(BaseModel):
    title: str = Field(min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=5000)
    scheduled_date: date
    priority: Priority = Priority.MEDIUM

    @model_validator(mode="after")
    def clean_title(self):
        self.title = self.title.strip()
        if not self.title:
            raise ValueError("Todo title cannot be empty")
        return self


class TodoUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=5000)
    scheduled_date: date | None = None
    priority: Priority | None = None


class TodoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    title: str
    description: str | None
    scheduled_date: date
    original_scheduled_date: date | None
    priority: str
    status: str
    created_at: datetime
    updated_at: datetime
    completed_at: datetime | None
    missed_at: datetime | None
    miss_reason: str | None
    carried_from_date: date | None
    carry_forward_count: int
    carry_forward_bonus_awarded: bool


class MissTodoRequest(BaseModel):
    reason: str = Field(min_length=1, max_length=500)

    @model_validator(mode="after")
    def clean_reason(self):
        self.reason = self.reason.strip()
        if not self.reason:
            raise ValueError("A reason is required")
        return self


class CarryForwardRequest(BaseModel):
    todo_ids: list[str] = Field(min_length=1, max_length=100)

