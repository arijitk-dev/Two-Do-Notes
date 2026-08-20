from datetime import date

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.time import user_today
from app.models.todo import Todo, TodoStatus
from app.models.user import User
from app.repositories.todo_repository import TodoRepository


class CarryForwardService:
    def __init__(self, db: Session):
        self.db = db
        self.repository = TodoRepository()

    def carry_forward(self, user: User, todo_ids: list[str]) -> list[Todo]:
        today = user_today(user.timezone)
        tomorrow = today.fromordinal(today.toordinal() + 1)
        todos: list[Todo] = []
        for todo_id in todo_ids:
            todo = self.repository.get_for_update(self.db, user.id, todo_id)
            if not todo:
                raise HTTPException(status_code=404, detail="Todo not found")
            if todo.status != TodoStatus.PENDING.value:
                raise HTTPException(status_code=400, detail="Only pending Todos can be carried forward")
            if todo.scheduled_date == tomorrow and todo.carry_forward_count > 0:
                todos.append(todo)
                continue
            if todo.scheduled_date != today:
                raise HTTPException(status_code=400, detail="Only today's pending Todos can be carried forward")
            todo.carried_from_date = todo.scheduled_date
            todo.scheduled_date = tomorrow
            todo.carry_forward_count += 1
            todos.append(todo)
        self.db.commit()
        for todo in todos:
            self.db.refresh(todo)
        return todos
