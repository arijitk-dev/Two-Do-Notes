from datetime import date

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.point_transaction import PointTransaction, TransactionType
from app.models.todo import Todo


class PointRepository:
    def total(self, db: Session, user_id: str) -> int:
        return int(db.scalar(select(func.coalesce(func.sum(PointTransaction.points), 0)).where(PointTransaction.user_id == user_id)) or 0)

    def history(self, db: Session, user_id: str) -> list[PointTransaction]:
        return list(db.scalars(select(PointTransaction).where(PointTransaction.user_id == user_id).order_by(PointTransaction.created_at.desc())))

    def planning_points_for_date(self, db: Session, user_id: str, scheduled_date: date) -> int:
        query = select(func.coalesce(func.sum(PointTransaction.points), 0)).join(
            Todo, Todo.id == PointTransaction.todo_id
        ).where(
            PointTransaction.user_id == user_id,
            PointTransaction.transaction_type == TransactionType.TODO_PLANNED_TOMORROW.value,
            Todo.scheduled_date == scheduled_date,
        )
        return int(db.scalar(query) or 0)
