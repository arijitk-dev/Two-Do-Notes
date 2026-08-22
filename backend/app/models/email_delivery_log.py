import uuid
from datetime import datetime
from enum import Enum

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class EmailStatus(str, Enum):
    """Email delivery status."""
    SENT = "sent"
    FAILED = "failed"
    PENDING = "pending"


class EmailType(str, Enum):
    """Type of email being sent."""
    DAILY_TODO_REMINDER = "daily_todo_reminder"


class EmailDeliveryLog(Base):
    __tablename__ = "email_delivery_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    email_type: Mapped[EmailType] = mapped_column(SQLEnum(EmailType), nullable=False)
    scheduled_date: Mapped[str] = mapped_column(String(10), nullable=False)  # YYYY-MM-DD format
    status: Mapped[EmailStatus] = mapped_column(SQLEnum(EmailStatus), nullable=False)
    sent_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error_message: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationship
    user = relationship("User", backref="email_delivery_logs")

    __table_args__ = (
        # Unique constraint: only one email per user per type per date
        # This ensures idempotency
    )
