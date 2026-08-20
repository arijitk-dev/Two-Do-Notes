from datetime import date, timedelta

from app.core.time import user_today, user_tomorrow


def tomorrow():
    return (date.today() + timedelta(days=1)).isoformat()


def test_planning_points_are_awarded_once_for_original_tomorrow_plan(auth_client):
    planned = auth_client.post("/api/v1/todos", json={"title": "Plan tomorrow", "scheduled_date": tomorrow()})
    assert planned.status_code == 201
    todo_id = planned.json()["id"]
    history = auth_client.get("/api/v1/points/history").json()
    assert [(item["transaction_type"], item["points"]) for item in history] == [("TODO_PLANNED_TOMORROW", 2)]

    assert auth_client.patch(f"/api/v1/todos/{todo_id}", json={"title": "Still planned"}).status_code == 200
    assert auth_client.patch(f"/api/v1/todos/{todo_id}", json={"scheduled_date": date.today().isoformat()}).status_code == 200
    assert auth_client.patch(f"/api/v1/todos/{todo_id}", json={"scheduled_date": tomorrow()}).status_code == 200
    assert len(auth_client.get("/api/v1/points/history").json()) == 1

    assert auth_client.post("/api/v1/todos", json={"title": "Today only", "scheduled_date": date.today().isoformat()}).status_code == 201
    assert auth_client.post("/api/v1/todos", json={"title": "Next week", "scheduled_date": (date.today() + timedelta(days=7)).isoformat()}).status_code == 201
    assert len(auth_client.get("/api/v1/points/history").json()) == 1


def test_calendar_returns_each_day_and_date_filter(auth_client):
    today = date.today()
    auth_client.post("/api/v1/todos", json={"title": "Calendar today", "scheduled_date": today.isoformat()})
    auth_client.post("/api/v1/todos", json={"title": "Calendar tomorrow", "scheduled_date": tomorrow()})
    calendar = auth_client.get("/api/v1/calendar", params={"year": today.year, "month": today.month})
    assert calendar.status_code == 200
    assert len(calendar.json()["days"]) == 31
    selected = auth_client.get("/api/v1/todos", params={"date": today.isoformat()})
    assert [todo["title"] for todo in selected.json()] == ["Calendar today"]


def test_carry_forward_has_no_move_points_and_first_completion_gets_one_bonus(auth_client, monkeypatch):
    today = date.today()
    created = auth_client.post("/api/v1/todos", json={"title": "Carry me", "scheduled_date": today.isoformat()}).json()
    todo_id = created["id"]
    moved = auth_client.post(f"/api/v1/todos/{todo_id}/carry-forward")
    assert moved.status_code == 200
    assert moved.json()["scheduled_date"] == tomorrow()
    assert moved.json()["carried_from_date"] == today.isoformat()
    assert moved.json()["carry_forward_count"] == 1
    assert auth_client.get("/api/v1/points/history").json() == []

    # Repeat the same carry request safely; it must not increment the count.
    repeated = auth_client.post(f"/api/v1/todos/{todo_id}/carry-forward")
    assert repeated.status_code == 200
    assert repeated.json()["carry_forward_count"] == 1

    monkeypatch.setattr("app.services.todo_service.user_today", lambda _timezone: user_tomorrow("Asia/Kolkata"))
    completed = auth_client.post(f"/api/v1/todos/{todo_id}/complete")
    assert completed.status_code == 200
    transactions = auth_client.get("/api/v1/points/history").json()
    assert sorted((item["transaction_type"], item["points"]) for item in transactions) == [
        ("CARRY_FORWARD_BONUS", 1), ("TODO_COMPLETED", 3)
    ]
    assert auth_client.post(f"/api/v1/todos/{todo_id}/complete").status_code == 200
    assert len(auth_client.get("/api/v1/points/history").json()) == 2


def test_completed_and_missed_todos_cannot_be_carried_forward(auth_client):
    today = date.today().isoformat()
    completed = auth_client.post("/api/v1/todos", json={"title": "Done", "scheduled_date": today}).json()
    assert auth_client.post(f"/api/v1/todos/{completed['id']}/complete").status_code == 200
    assert auth_client.post(f"/api/v1/todos/{completed['id']}/carry-forward").status_code == 400
    missed = auth_client.post("/api/v1/todos", json={"title": "Missed", "scheduled_date": today}).json()
    assert auth_client.post(f"/api/v1/todos/{missed['id']}/miss", json={"reason": "Unexpected work"}).status_code == 200
    assert auth_client.post(f"/api/v1/todos/{missed['id']}/carry-forward").status_code == 400

