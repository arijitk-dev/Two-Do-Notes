from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.accountability import (
    ACCOUNTABILITY_ROLLING_DAYS,
    MISS_REASON_LABELS,
    OVERPLANNING_MIN_PLANNED_PER_DAY,
    OVERPLANNING_THRESHOLD,
    SUCCESSFUL_DAY_THRESHOLD,
    accountability_message,
    miss_reason_label,
)
from app.core.time import user_today, user_zone
from app.models.point_transaction import PointTransaction, TransactionType
from app.models.todo import Todo, TodoStatus
from app.models.user import User
from app.schemas.accountability import (
    AccountabilityResponse,
    DayMetricsResponse,
    MissReasonStat,
    PointBreakdownResponse,
)


@dataclass(frozen=True)
class DayMetrics:
    review_date: date
    planned: int
    completed: int
    missed: int
    carried_forward: int
    pending: int

    @property
    def resolved(self) -> int:
        return self.completed + self.missed + self.carried_forward

    @property
    def completion_rate(self) -> float:
        return self.completed / self.planned if self.planned else 0.0

    @property
    def neutral(self) -> bool:
        return self.planned == 0

    @property
    def successful(self) -> bool:
        return bool(self.planned) and self.resolved == self.planned and self.completion_rate >= SUCCESSFUL_DAY_THRESHOLD


class AccountabilityService:
    """Calculates accountability from Todo and point-ledger data, never stored metrics."""

    def _todos(self, db: Session, user: User) -> list[Todo]:
        return list(db.scalars(select(Todo).where(Todo.user_id == user.id)))

    @staticmethod
    def _belongs_to_day(todo: Todo, day: date) -> bool:
        initial_date = todo.original_scheduled_date or todo.scheduled_date
        return day in {initial_date, todo.scheduled_date, todo.carried_from_date}

    @staticmethod
    def _is_carried_for_day(todo: Todo, day: date) -> bool:
        if todo.carried_from_date == day:
            return True
        return bool(todo.carry_forward_count and todo.original_scheduled_date == day and todo.scheduled_date != day)

    def day_metrics(self, db: Session, user: User, review_date: date, todos: list[Todo] | None = None) -> DayMetrics:
        day_todos = [todo for todo in (todos if todos is not None else self._todos(db, user)) if self._belongs_to_day(todo, review_date)]
        completed = missed = carried = pending = 0
        for todo in day_todos:
            if self._is_carried_for_day(todo, review_date):
                carried += 1
            elif todo.status == TodoStatus.COMPLETED.value:
                completed += 1
            elif todo.status == TodoStatus.MISSED.value:
                missed += 1
            else:
                pending += 1
        return DayMetrics(review_date, len(day_todos), completed, missed, carried, pending)

    @staticmethod
    def _date_range(user: User, range_name: str, start_date: date | None, end_date: date | None) -> tuple[str, date, date]:
        today = user_today(user.timezone)
        if start_date or end_date:
            start = start_date or end_date or today
            end = end_date or start
            if start > end:
                raise ValueError("start_date cannot be after end_date")
            return "custom", start, end
        if range_name in {"today", "day"}:
            return "today", today, today
        if range_name in {"month", "current_month"}:
            return "month", today.replace(day=1), today
        return "7d", today - timedelta(days=ACCOUNTABILITY_ROLLING_DAYS - 1), today

    @staticmethod
    def _transaction_local_date(created_at: datetime, user: User) -> date:
        timestamp = created_at
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)
        return timestamp.astimezone(user_zone(user.timezone)).date()

    def _point_breakdown(self, db: Session, user: User, start: date, end: date) -> PointBreakdownResponse:
        transactions = db.scalars(select(PointTransaction).where(PointTransaction.user_id == user.id)).all()
        in_range = [tx for tx in transactions if start <= self._transaction_local_date(tx.created_at, user) <= end]
        completed = sum(tx.points for tx in in_range if tx.transaction_type == TransactionType.TODO_COMPLETED.value)
        planning = sum(tx.points for tx in in_range if tx.transaction_type == TransactionType.TODO_PLANNED_TOMORROW.value)
        carry = sum(tx.points for tx in in_range if tx.transaction_type == TransactionType.CARRY_FORWARD_BONUS.value)
        missed = sum(tx.points for tx in in_range if tx.transaction_type == TransactionType.TODO_MISSED.value)
        earned = sum(tx.points for tx in in_range if tx.points > 0)
        lost = abs(sum(tx.points for tx in in_range if tx.points < 0))
        return PointBreakdownResponse(
            completed_points=completed,
            planning_points=planning,
            carry_forward_bonus_points=carry,
            missed_points=missed,
            points_earned=earned,
            points_lost=lost,
            net_points=sum(tx.points for tx in in_range),
        )

    def _miss_reasons(self, todos: list[Todo], start: date, end: date) -> list[MissReasonStat]:
        missed = [todo for todo in todos if todo.status == TodoStatus.MISSED.value and start <= todo.scheduled_date <= end]
        counts: dict[str, int] = {}
        for todo in missed:
            code = todo.miss_reason_code or next((key for key, label in MISS_REASON_LABELS.items() if label.lower() == (todo.miss_reason or "").lower()), "other")
            counts[code] = counts.get(code, 0) + 1
        total = len(missed)
        return [
            MissReasonStat(code=code, label=miss_reason_label(code), count=count, percentage=round(count / total, 4) if total else 0.0)
            for code, count in sorted(counts.items(), key=lambda item: (-item[1], item[0]))
        ]

    def summary(
        self,
        db: Session,
        user: User,
        range_name: str = "7d",
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> AccountabilityResponse:
        resolved_name, start, end = self._date_range(user, range_name, start_date, end_date)
        todos = self._todos(db, user)
        daily = [self.day_metrics(db, user, start + timedelta(days=offset), todos) for offset in range((end - start).days + 1)]
        planned = sum(day.planned for day in daily)
        completed = sum(day.completed for day in daily)
        missed = sum(day.missed for day in daily)
        carried = sum(day.carried_forward for day in daily)
        pending = sum(day.pending for day in daily)
        denominator = planned or 1
        points = self._point_breakdown(db, user, start, end)
        average_planned = planned / len(daily) if daily else 0.0
        average_completed = completed / len(daily) if daily else 0.0
        overplanning = None
        if len(daily) >= ACCOUNTABILITY_ROLLING_DAYS and average_planned >= OVERPLANNING_MIN_PLANNED_PER_DAY and completed / denominator < OVERPLANNING_THRESHOLD:
            overplanning = "You may be consistently overplanning. Try reducing tomorrow's workload."
        from app.services.streak_service import StreakService

        streak = StreakService().recompute(db, user, end)
        return AccountabilityResponse(
            range_name=resolved_name,
            start_date=start,
            end_date=end,
            planned_count=planned,
            completed_count=completed,
            missed_count=missed,
            carried_forward_count=carried,
            pending_count=pending,
            completion_rate=round(completed / denominator, 4) if planned else 0.0,
            planning_accuracy=round(completed / denominator, 4) if planned else 0.0,
            miss_rate=round(missed / denominator, 4) if planned else 0.0,
            carry_forward_rate=round(carried / denominator, 4) if planned else 0.0,
            current_streak=streak.current_streak,
            max_streak=streak.max_streak,
            completed_points=points.completed_points,
            planning_points=points.planning_points,
            carry_forward_bonus_points=points.carry_forward_bonus_points,
            missed_points=points.missed_points,
            points_earned=points.points_earned,
            points_lost=points.points_lost,
            net_points=points.net_points,
            missed_reasons=self._miss_reasons(todos, start, end),
            average_planned_per_day=round(average_planned, 2),
            average_completed_per_day=round(average_completed, 2),
            overplanning_warning=overplanning,
            accountability_message=accountability_message(f"{user.id}:{resolved_name}:{end.isoformat()}"),
            daily=[DayMetricsResponse(**day.__dict__, resolved=day.resolved, completion_rate=round(day.completion_rate, 4), successful=day.successful, neutral=day.neutral) for day in daily],
        )
