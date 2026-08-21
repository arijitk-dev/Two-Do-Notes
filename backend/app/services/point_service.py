from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.point_transaction import PointTransaction
from app.models.user import User


class PointService:
    """The ledger is the only source of truth for points and reward idempotency."""

    def award_once(
        self,
        db: Session,
        user: User,
        todo_id: str,
        transaction_type: str,
        points: int,
        description: str,
    ) -> PointTransaction:
        existing = db.scalar(select(PointTransaction).where(
            PointTransaction.user_id == user.id,
            PointTransaction.todo_id == todo_id,
            PointTransaction.transaction_type == transaction_type,
        ))
        if existing:
            return existing
        transaction = PointTransaction(
            user_id=user.id,
            todo_id=todo_id,
            transaction_type=transaction_type,
            points=points,
            description=description,
        )
        try:
            # The unique ledger constraint is the final protection for duplicate
            # requests. A savepoint lets the caller keep its surrounding Todo
            # transition intact when a concurrent request wins the race.
            with db.begin_nested():
                db.add(transaction)
                db.flush()
        except IntegrityError:
            existing = db.scalar(select(PointTransaction).where(
                PointTransaction.user_id == user.id,
                PointTransaction.todo_id == todo_id,
                PointTransaction.transaction_type == transaction_type,
            ))
            if existing:
                return existing
            raise
        return transaction
