from __future__ import annotations

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.todo import Todo


class TodoRepository:
    def get(self, db: Session, user_id: str, todo_id: str) -> Todo | None:
        return db.scalar(select(Todo).where(Todo.id == todo_id, Todo.user_id == user_id))

    def get_for_update(self, db: Session, user_id: str, todo_id: str) -> Todo | None:
        return db.scalar(select(Todo).where(Todo.id == todo_id, Todo.user_id == user_id).with_for_update())

    def list(
        self,
        db: Session,
        user_id: str,
        scheduled_date: date | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
    ) -> list[Todo]:
        query = select(Todo).where(Todo.user_id == user_id).order_by(Todo.scheduled_date, Todo.created_at)
        if scheduled_date:
            query = query.where(Todo.scheduled_date == scheduled_date)
        elif start_date or end_date:
            lower = start_date or end_date
            upper = end_date or start_date
            query = query.where(Todo.scheduled_date >= lower, Todo.scheduled_date <= upper)
        return list(db.scalars(query))

    def list_between(self, db: Session, user_id: str, start: date, end: date) -> list[Todo]:
        query = select(Todo).where(
            Todo.user_id == user_id,
            Todo.scheduled_date >= start,
            Todo.scheduled_date <= end,
        ).order_by(Todo.scheduled_date, Todo.created_at)
        return list(db.scalars(query))

    def history(
        self, db: Session, user_id: str, start: date, end: date, search: str | None = None
    ) -> list[Todo]:
        query = select(Todo).where(
            Todo.user_id == user_id,
            Todo.scheduled_date >= start,
            Todo.scheduled_date <= end,
        )
        if search:
            query = query.where(Todo.title.ilike(f"%{search}%") | Todo.description.ilike(f"%{search}%"))
        query = query.order_by(Todo.scheduled_date.desc(), Todo.created_at.desc())
        return list(db.scalars(query))

    def unresolved(self, db: Session, user_id: str, scheduled_date: date) -> list[Todo]:
        query = select(Todo).where(
            Todo.user_id == user_id,
            Todo.scheduled_date == scheduled_date,
            Todo.status == "pending",
        ).order_by(Todo.created_at)
        return list(db.scalars(query))
