from datetime import date

from fastapi import APIRouter, Query, Response, status
from app.api.deps import CurrentUser, DbSession
from app.core.time import user_today
from app.repositories.todo_repository import TodoRepository
from app.schemas.todo import CarryForwardRequest, MissTodoRequest, TodoCreate, TodoResponse, TodoUpdate
from app.services.carry_forward_service import CarryForwardService
from app.services.todo_service import TodoService

router = APIRouter(prefix="/todos", tags=["todos"])


@router.get("", response_model=list[TodoResponse])
def list_todos(
    user: CurrentUser,
    db: DbSession,
    date_filter: date | None = Query(default=None, alias="date"),
    scheduled_date: date | None = Query(default=None),
):
    return TodoRepository().list(db, user.id, date_filter or scheduled_date)


@router.post("", response_model=TodoResponse, status_code=status.HTTP_201_CREATED)
def create_todo(payload: TodoCreate, user: CurrentUser, db: DbSession):
    return TodoService(db).create(user, payload)


@router.get("/unresolved", response_model=list[TodoResponse])
def unresolved_todos(user: CurrentUser, db: DbSession, date_filter: date | None = Query(default=None, alias="date")):
    return TodoRepository().unresolved(db, user.id, date_filter or user_today(user.timezone))


@router.post("/carry-forward", response_model=list[TodoResponse])
def carry_forward_todos(payload: CarryForwardRequest, user: CurrentUser, db: DbSession):
    return CarryForwardService(db).carry_forward(user, payload.todo_ids)


@router.post("/{todo_id}/carry-forward", response_model=TodoResponse)
def carry_forward_todo(todo_id: str, user: CurrentUser, db: DbSession):
    return CarryForwardService(db).carry_forward(user, [todo_id])[0]


@router.get("/{todo_id}", response_model=TodoResponse)
def get_todo(todo_id: str, user: CurrentUser, db: DbSession):
    return TodoService(db).get(user, todo_id)


@router.patch("/{todo_id}", response_model=TodoResponse)
def update_todo(todo_id: str, payload: TodoUpdate, user: CurrentUser, db: DbSession):
    return TodoService(db).update(user, todo_id, payload)


@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(todo_id: str, user: CurrentUser, db: DbSession):
    TodoService(db).delete(user, todo_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/{todo_id}/complete", response_model=TodoResponse)
def complete_todo(todo_id: str, user: CurrentUser, db: DbSession):
    return TodoService(db).complete(user, todo_id)


@router.post("/{todo_id}/miss", response_model=TodoResponse)
def miss_todo(todo_id: str, payload: MissTodoRequest, user: CurrentUser, db: DbSession):
    return TodoService(db).miss(user, todo_id, payload.reason)
