from datetime import date, timedelta

import pytest
from sqlalchemy import select

from app.core.accountability import SUCCESSFUL_DAY_THRESHOLD
from app.db.session import SessionLocal
from app.models.todo import Todo, TodoStatus
from app.models.user import User
from app.services.accountability_service import AccountabilityService
from app.services.streak_service import StreakService


def test_miss_reason_code_is_required_and_penalty_is_idempotent(auth_client):
    today = date.today().isoformat()
    todo = auth_client.post("/api/v1/todos", json={"title": "Miss honestly", "scheduled_date": today}).json()
    response = auth_client.post(f"/api/v1/todos/{todo['id']}/miss", json={"reason_code": "poor_planning"})
    assert response.status_code == 200
    assert response.json()["miss_reason_code"] == "poor_planning"
    assert response.json()["miss_reason"] == "Poor planning"
    assert auth_client.post(f"/api/v1/todos/{todo['id']}/miss", json={"reason_code": "lost_focus"}).status_code == 200
    history = auth_client.get("/api/v1/points/history").json()
    assert [(item["transaction_type"], item["points"]) for item in history] == [("TODO_MISSED", -7)]


def test_daily_review_is_optional_updatable_and_owned(auth_client, client):
    review_date = date.today().isoformat()
    empty = auth_client.get(f"/api/v1/reviews/{review_date}")
    assert empty.status_code == 200
    assert empty.json()["id"] is None
    created = auth_client.post(f"/api/v1/reviews/{review_date}", json={"mood_score": 4, "went_well": "Focused work"})
    assert created.status_code == 200
    assert created.json()["mood_score"] == 4
    updated = auth_client.patch(f"/api/v1/reviews/{review_date}", json={"mood_score": 5, "improvement": "Plan less"})
    assert updated.status_code == 200
    assert updated.json()["mood_score"] == 5
    assert updated.json()["went_well"] == "Focused work"

    other = client.post("/api/v1/auth/register", json={"name": "Other", "email": "review-other@example.com", "password": "password123"})
    client.headers.update({"Authorization": f"Bearer {other.json()['access_token']}"})
    assert client.get(f"/api/v1/reviews/{review_date}").json()["id"] is None


def test_successful_day_requires_resolution_and_eighty_percent(auth_client):
    db = SessionLocal()
    user = db.scalar(select(User).where(User.email == "asha@example.com"))
    review_date = date.today() - timedelta(days=1)
    for index in range(5):
        db.add(Todo(user_id=user.id, title=f"Done {index}", scheduled_date=review_date, original_scheduled_date=review_date, status=TodoStatus.COMPLETED.value))
    db.add(Todo(
        user_id=user.id,
        title="Carried",
        scheduled_date=review_date + timedelta(days=1),
        original_scheduled_date=review_date,
        carried_from_date=review_date,
        carry_forward_count=1,
        status=TodoStatus.PENDING.value,
    ))
    db.commit()
    metrics = AccountabilityService().day_metrics(db, user, review_date)
    assert (metrics.planned, metrics.completed, metrics.carried_forward, metrics.resolved) == (6, 5, 1, 6)
    assert metrics.completion_rate == 5 / 6
    assert metrics.successful is True
    assert metrics.completion_rate >= SUCCESSFUL_DAY_THRESHOLD
    db.close()


def test_accountability_summary_has_point_breakdown_and_reason_stats(auth_client):
    today = date.today().isoformat()
    todos = [auth_client.post("/api/v1/todos", json={"title": f"Todo {index}", "scheduled_date": today}).json() for index in range(6)]
    for todo in todos[:5]:
        assert auth_client.post(f"/api/v1/todos/{todo['id']}/complete").status_code == 200
    assert auth_client.post(f"/api/v1/todos/{todos[5]['id']}/miss", json={"reason_code": "not_enough_time"}).status_code == 200
    summary = auth_client.get("/api/v1/accountability", params={"range": "today"})
    assert summary.status_code == 200
    body = summary.json()
    assert body["planned_count"] == 6
    assert body["completed_count"] == 5
    assert body["missed_count"] == 1
    assert body["completion_rate"] == pytest.approx(5 / 6, abs=0.0001)
    assert body["planning_accuracy"] == pytest.approx(5 / 6, abs=0.0001)
    assert body["completed_points"] == 15
    assert body["missed_points"] == -7
    assert body["net_points"] == 8
    assert body["missed_reasons"] == [{"code": "not_enough_time", "label": "Not enough time", "count": 1, "percentage": 1.0}]


def test_streak_uses_successful_days_and_preserves_best_run():
    db = SessionLocal()
    user = User(name="Phase Three", email="phase-three@example.com", password_hash="hash", timezone="Asia/Kolkata")
    db.add(user)
    db.flush()
    start = date.today() - timedelta(days=4)
    for offset, completed_count, missed_count in ((0, 6, 0), (1, 5, 1), (2, 4, 2), (4, 6, 0)):
        for index in range(completed_count):
            db.add(Todo(user_id=user.id, title=f"Done {offset}-{index}", scheduled_date=start + timedelta(days=offset), original_scheduled_date=start + timedelta(days=offset), status=TodoStatus.COMPLETED.value))
        for index in range(missed_count):
            db.add(Todo(user_id=user.id, title=f"Missed {offset}-{index}", scheduled_date=start + timedelta(days=offset), original_scheduled_date=start + timedelta(days=offset), status=TodoStatus.MISSED.value, miss_reason="Lost focus", miss_reason_code="lost_focus"))
    db.flush()
    streak = StreakService().recompute(db, user, date.today())
    assert streak.max_streak == 2
    assert streak.current_streak == 1
    db.close()
