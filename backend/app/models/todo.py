import uuid
from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class TodoStatus(StrEnum):
    PENDING = "pending"
    COMPLETED = "completed"
    MISSED = "missed"


class TodoPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Todo(Base):
    __tablename__ = "todos"
    __table_args__ = (
        Index("ix_todos_user_scheduled_date", "user_id", "scheduled_date"),
        Index("ix_todos_user_status", "user_id", "status"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(160))
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    scheduled_date: Mapped[date] = mapped_column(Date, index=True)
    original_scheduled_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    priority: Mapped[str] = mapped_column(String(20), default=TodoPriority.MEDIUM.value)
    status: Mapped[str] = mapped_column(String(20), default=TodoStatus.PENDING.value, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    missed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    miss_reason: Mapped[str | None] = mapped_column(String(500), nullable=True)
    miss_reason_code: Mapped[str | None] = mapped_column(String(40), nullable=True)
    miss_reason_text: Mapped[str | None] = mapped_column(String(500), nullable=True)
    carried_from_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    carry_forward_count: Mapped[int] = mapped_column(Integer, default=0, server_default="0")
    carry_forward_bonus_awarded: Mapped[bool] = mapped_column(Boolean, default=False, server_default="0")
    source_todo_id: Mapped[str | None] = mapped_column(
        ForeignKey("todos.id", ondelete="SET NULL"), nullable=True, index=True
    )

    user = relationship("User", back_populates="todos")
    transactions = relationship("PointTransaction", back_populates="todo")
