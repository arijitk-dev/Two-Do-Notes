from datetime import date, timedelta

from sqlalchemy import select

from app.core.time import user_today
from app.db.session import SessionLocal
from app.models.todo import Todo, TodoStatus
from app.models.user import User


def make_old_todo(title: str, scheduled_date: date, user_email: str = "asha@example.com", **kwargs) -> Todo:
    db = SessionLocal()
    user = db.scalar(select(User).where(User.email == user_email))
    todo = Todo(
        user_id=user.id,
        title=title,
        scheduled_date=scheduled_date,
        original_scheduled_date=scheduled_date,
        status=TodoStatus.COMPLETED.value,
        **kwargs,
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)
    db.close()
    return todo


def test_todos_default_to_today_and_explicit_dates_work(auth_client):
    user = auth_client.get("/api/v1/auth/me").json()
    today = user_today(user["timezone"])
    yesterday = today - timedelta(days=1)
    auth_client.post("/api/v1/todos", json={"title": "Today", "scheduled_date": today.isoformat()})
    auth_client.post("/api/v1/todos", json={"title": "Yesterday", "scheduled_date": yesterday.isoformat()})

    assert [todo["title"] for todo in auth_client.get("/api/v1/todos").json()] == ["Today"]
    assert [todo["title"] for todo in auth_client.get("/api/v1/todos", params={"date": yesterday}).json()] == ["Yesterday"]


def test_history_is_bounded_owned_and_searchable(auth_client, client):
    user = auth_client.get("/api/v1/auth/me").json()
    today = user_today(user["timezone"])
    current = make_old_todo("Today history", today)
    recent = make_old_todo("Keep this", today - timedelta(days=14))
    make_old_todo("Too old", today - timedelta(days=15))

    history = auth_client.get("/api/v1/todos/history")
    assert history.status_code == 200
    assert [todo["id"] for todo in history.json()] == [current.id, recent.id]
    assert len(auth_client.get("/api/v1/todos/history", params={"search": "keep"}).json()) == 1

    other = client.post("/api/v1/auth/register", json={"name": "Other", "email": "history-other@example.com", "password": "password123"})
    client.headers.update({"Authorization": f"Bearer {other.json()['access_token']}"})
    assert client.get("/api/v1/todos/history").json() == []
    assert client.get(f"/api/v1/todos/{recent.id}/reuse").status_code == 405


def test_reuse_creates_new_todo_without_points_and_completion_is_normal(auth_client):
    user = auth_client.get("/api/v1/auth/me").json()
    today = user_today(user["timezone"])
    source = make_old_todo("Reusable", today - timedelta(days=1), description="Only copy this", priority="high")

    reused = auth_client.post(f"/api/v1/todos/{source.id}/reuse")
    assert reused.status_code == 201
    body = reused.json()
    assert body["id"] != source.id
    assert body["source_todo_id"] == source.id
    assert body["status"] == "pending"
    assert body["scheduled_date"] == today.isoformat()
    assert body["description"] == "Only copy this"
    assert auth_client.get("/api/v1/points/history").json() == []

    assert auth_client.post(f"/api/v1/todos/{body['id']}/complete").status_code == 200
    assert [(item["transaction_type"], item["points"]) for item in auth_client.get("/api/v1/points/history").json()] == [("TODO_COMPLETED", 3)]
    assert auth_client.post(f"/api/v1/todos/{source.id}/reuse").status_code == 409


def test_bulk_reuse_skips_equivalent_duplicates_and_rejects_expired_sources(auth_client):
    user = auth_client.get("/api/v1/auth/me").json()
    today = user_today(user["timezone"])
    first = make_old_todo("Same", today - timedelta(days=1), description="same", priority="medium")
    second = make_old_todo("Same", today - timedelta(days=2), description="same", priority="medium")
    bulk = auth_client.post("/api/v1/todos/reuse", json={"todo_ids": [first.id, second.id]})
    assert bulk.status_code == 201
    assert len(bulk.json()) == 1
    assert auth_client.get("/api/v1/points/history").json() == []

    expired = make_old_todo("Expired", today - timedelta(days=15))
    response = auth_client.post(f"/api/v1/todos/{expired.id}/reuse")
    assert response.status_code == 400
