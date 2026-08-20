import uuid
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class TransactionType(StrEnum):
    TODO_COMPLETED = "TODO_COMPLETED"
    TODO_MISSED = "TODO_MISSED"
    TODO_PLANNED_TOMORROW = "TODO_PLANNED_TOMORROW"
    CARRY_FORWARD_BONUS = "CARRY_FORWARD_BONUS"


class PointTransaction(Base):
    __tablename__ = "point_transactions"
    __table_args__ = (UniqueConstraint("todo_id", "transaction_type", name="uq_point_transaction_todo_type"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    todo_id: Mapped[str | None] = mapped_column(ForeignKey("todos.id", ondelete="SET NULL"), nullable=True, index=True)
    transaction_type: Mapped[str] = mapped_column(String(40), index=True)
    points: Mapped[int] = mapped_column(Integer)
    description: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user = relationship("User", back_populates="point_transactions")
    todo = relationship("Todo", back_populates="transactions")
