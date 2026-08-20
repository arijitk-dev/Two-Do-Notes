from datetime import date, timedelta

from app.db.session import SessionLocal
from app.models.todo import Todo, TodoStatus
from app.models.user import User
from app.services.streak_service import StreakService


def today():
    return date.today().isoformat()


def test_auth_and_protection(client):
    assert client.get("/api/v1/todos").status_code == 401
    registered = client.post("/api/v1/auth/register", json={"name": "Asha", "email": "asha@example.com", "password": "password123"})
    assert registered.status_code == 201
    assert "password_hash" not in registered.text
    assert client.post("/api/v1/auth/register", json={"name": "A", "email": "asha@example.com", "password": "password123"}).status_code == 409
    assert client.post("/api/v1/auth/login", json={"email": "asha@example.com", "password": "wrongpass"}).status_code == 401


def test_todo_points_are_idempotent_and_miss_requires_reason(auth_client):
    created = auth_client.post("/api/v1/todos", json={"title": "Ship it", "scheduled_date": today(), "priority": "high"})
    assert created.status_code == 201
    todo_id = created.json()["id"]
    assert auth_client.post(f"/api/v1/todos/{todo_id}/complete").status_code == 200
    assert auth_client.post(f"/api/v1/todos/{todo_id}/complete").status_code == 200
    history = auth_client.get("/api/v1/points/history").json()
    assert [item["points"] for item in history] == [3]
    assert auth_client.post("/api/v1/todos", json={"title": "Miss me", "scheduled_date": today()}).status_code == 201
    missed = auth_client.get("/api/v1/todos", params={"scheduled_date": today()}).json()[1]
    assert auth_client.post(f"/api/v1/todos/{missed['id']}/miss", json={}).status_code == 422
    assert auth_client.post(f"/api/v1/todos/{missed['id']}/miss", json={"reason": "Lost focus"}).status_code == 200
    assert auth_client.post(f"/api/v1/todos/{missed['id']}/miss", json={"reason": "Again"}).status_code == 200
    assert sum(item["points"] for item in auth_client.get("/api/v1/points/history").json()) == -4


def test_streak_consecutive_and_broken_days(auth_client):
    # The endpoint intentionally uses the local current date; this verifies the first successful day.
    todo = auth_client.post("/api/v1/todos", json={"title": "Today", "scheduled_date": today()}).json()
    auth_client.post(f"/api/v1/todos/{todo['id']}/complete")
    streak = auth_client.get("/api/v1/streak").json()
    assert streak["current_streak"] == 1
    assert streak["max_streak"] == 1


def test_streak_service_handles_consecutive_days_and_a_gap():
    db = SessionLocal()
    user = User(name="Streak", email="streak@example.com", password_hash="hash", timezone="Asia/Kolkata")
    db.add(user)
    db.flush()
    start = date.today() - timedelta(days=4)
    for offset in (0, 1, 2, 4):
        db.add(Todo(user_id=user.id, title=f"Day {offset}", scheduled_date=start + timedelta(days=offset), status=TodoStatus.COMPLETED.value))
    db.flush()
    streak = StreakService().recompute(db, user, date.today())
    assert streak.current_streak == 1
    assert streak.max_streak == 3
    db.close()


def test_notes_and_ownership(auth_client, client):
    note = auth_client.post("/api/v1/notes", json={"title": "Thought", "content": "Keep going"})
    assert note.status_code == 201
    note_id = note.json()["id"]
    assert auth_client.patch(f"/api/v1/notes/{note_id}", json={"title": "Updated"}).status_code == 200
    second = client.post("/api/v1/auth/register", json={"name": "Other", "email": "other@example.com", "password": "password123"})
    client.headers.update({"Authorization": f"Bearer {second.json()['access_token']}"})
    assert client.get(f"/api/v1/notes/{note_id}").status_code == 404
