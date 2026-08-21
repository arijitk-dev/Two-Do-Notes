import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class DailyReview(Base):
    __tablename__ = "daily_reviews"
    __table_args__ = (UniqueConstraint("user_id", "review_date", name="uq_daily_review_user_date"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), index=True)
    review_date: Mapped[date] = mapped_column(Date, index=True)
    mood_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    went_well: Mapped[str | None] = mapped_column(Text, nullable=True)
    improvement: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="daily_reviews")
