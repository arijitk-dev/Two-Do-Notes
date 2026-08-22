"""Tests for daily reminder email feature."""
import os
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from zoneinfo import ZoneInfo

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.orm import Session

# Configure test database and environment before importing app
os.environ["DATABASE_URL"] = "sqlite:///./test_two_do_notes.db"
os.environ["JWT_SECRET"] = "test-secret"
os.environ["CRON_SECRET"] = "test-cron-secret"
os.environ["RESEND_API_KEY"] = "test-resend-key"
os.environ["FRONTEND_URL"] = "http://localhost:5173"

from app.db.session import Base, SessionLocal, engine
from app.main import app
from app.models import User, Todo
from app.models.email_delivery_log import EmailDeliveryLog, EmailStatus, EmailType
from app.services.daily_reminder_email_service import DailyReminderEmailService


@pytest.fixture(autouse=True)
def clean_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def db():
    """Get database session for tests."""
    db = SessionLocal()
    yield db
    db.close()


@pytest.fixture
def test_user(db):
    """Create a test user."""
    user = User(
        name="Test User",
        email="test@example.com",
        password_hash="hashed_password",
        timezone="Asia/Kolkata",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_user_invalid_timezone(db):
    """Create a test user with invalid timezone."""
    user = User(
        name="Invalid TZ User",
        email="invalid@example.com",
        password_hash="hashed_password",
        timezone="InvalidTimezone",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


class TestDailyReminderService:
    """Test DailyReminderEmailService methods."""

    def test_validate_timezone_valid(self):
        """Test timezone validation with valid timezone."""
        assert DailyReminderEmailService.validate_timezone("Asia/Kolkata") is True
        assert DailyReminderEmailService.validate_timezone("America/New_York") is True
        assert DailyReminderEmailService.validate_timezone("UTC") is True

    def test_validate_timezone_invalid(self):
        """Test timezone validation with invalid timezone."""
        assert DailyReminderEmailService.validate_timezone("InvalidTimezone") is False
        assert DailyReminderEmailService.validate_timezone("string") is False
        assert DailyReminderEmailService.validate_timezone("") is False
        assert DailyReminderEmailService.validate_timezone(None) is False

    def test_get_today_date_for_user_valid_timezone(self):
        """Test getting today's date for user with valid timezone."""
        date_str = DailyReminderEmailService.get_today_date_for_user("Asia/Kolkata")
        assert len(date_str) == 10  # YYYY-MM-DD format
        assert date_str.count("-") == 2

    def test_get_today_date_for_user_invalid_timezone(self):
        """Test getting today's date for user with invalid timezone falls back to UTC."""
        date_str = DailyReminderEmailService.get_today_date_for_user("InvalidTimezone")
        assert len(date_str) == 10  # YYYY-MM-DD format
        assert date_str.count("-") == 2

    def test_check_email_already_sent_not_sent(self, db, test_user):
        """Test email check when email hasn't been sent."""
        today_date = DailyReminderEmailService.get_today_date_for_user("Asia/Kolkata")
        result = DailyReminderEmailService.check_email_already_sent(db, test_user.id, today_date)
        assert result is False

    def test_check_email_already_sent_already_sent(self, db, test_user):
        """Test email check when email has been sent."""
        today_date = DailyReminderEmailService.get_today_date_for_user("Asia/Kolkata")
        
        # Create a sent email log
        log = EmailDeliveryLog(
            user_id=test_user.id,
            email_type=EmailType.DAILY_TODO_REMINDER,
            scheduled_date=today_date,
            status=EmailStatus.SENT,
        )
        db.add(log)
        db.commit()
        
        result = DailyReminderEmailService.check_email_already_sent(db, test_user.id, today_date)
        assert result is True

    def test_get_user_todos_for_today_no_todos(self, db, test_user):
        """Test getting todo count when user has no todos."""
        today_date = DailyReminderEmailService.get_today_date_for_user("Asia/Kolkata")
        todo_count, completed_count = DailyReminderEmailService.get_user_todos_for_today(
            db, test_user.id, today_date
        )
        assert todo_count == 0
        assert completed_count == 0

    def test_send_email_via_resend_no_key(self):
        """Test sending email without API key configured."""
        with patch("app.services.daily_reminder_email_service.settings") as mock_settings:
            mock_settings.resend_api_key = ""
            success, error = DailyReminderEmailService.send_email_via_resend(
                "test@example.com", 1, 0
            )
            assert success is False
            assert "not configured" in error

    def test_send_email_via_resend_library_not_installed(self):
        """Test sending email when resend library is not available."""
        with patch("app.services.daily_reminder_email_service.settings") as mock_settings:
            mock_settings.resend_api_key = "test-key"
            mock_settings.email_from = "test@example.com"
            mock_settings.frontend_url = "http://localhost:5173"
            
            # Mock the import to raise ImportError
            with patch("builtins.__import__", side_effect=ImportError("No module named 'resend'")):
                success, error = DailyReminderEmailService.send_email_via_resend(
                    "user@example.com", 1, 0
                )
                assert success is False
                assert "resend library not installed" in error


    def test_create_email_log(self, db, test_user):
        """Test creating email delivery log."""
        today_date = DailyReminderEmailService.get_today_date_for_user("Asia/Kolkata")
        
        DailyReminderEmailService.create_email_log(
            db, test_user.id, today_date, success=True, error_message=None
        )
        
        log = db.query(EmailDeliveryLog).filter_by(
            user_id=test_user.id, 
            scheduled_date=today_date
        ).first()
        
        assert log is not None
        assert log.status == EmailStatus.SENT
        assert log.email_type == EmailType.DAILY_TODO_REMINDER
        assert log.sent_at is not None

    def test_create_email_log_failure(self, db, test_user):
        """Test creating email delivery log for failure."""
        today_date = DailyReminderEmailService.get_today_date_for_user("Asia/Kolkata")
        
        DailyReminderEmailService.create_email_log(
            db, test_user.id, today_date, success=False, error_message="Network error"
        )
        
        log = db.query(EmailDeliveryLog).filter_by(
            user_id=test_user.id,
            scheduled_date=today_date
        ).first()
        
        assert log is not None
        assert log.status == EmailStatus.FAILED
        assert log.error_message == "Network error"
        assert log.sent_at is None

    def test_process_daily_reminders_success(self, db, test_user):
        """Test processing daily reminders for multiple users."""
        with patch.object(
            DailyReminderEmailService,
            "send_email_via_resend",
            return_value=(True, None),
        ):
            # Create another user with valid email
            user2 = User(
                name="Another User",
                email="another@example.com",
                password_hash="hashed",
                timezone="America/New_York",
            )
            db.add(user2)
            db.commit()
            
            stats = DailyReminderEmailService.process_daily_reminders(db)
            
            assert stats["processed"] == 2
            assert stats["sent"] == 2
            assert stats["skipped"] == 0
            assert stats["failed"] == 0


    def test_process_daily_reminders_idempotency(self, db, test_user):
        """Test that duplicate emails are not sent."""
        with patch.object(
            DailyReminderEmailService,
            "send_email_via_resend",
            return_value=(True, None),
        ) as mock_send:
            today_date = DailyReminderEmailService.get_today_date_for_user("Asia/Kolkata")
            
            # First run
            stats1 = DailyReminderEmailService.process_daily_reminders(db)
            assert stats1["sent"] == 1
            
            # Reset mock
            mock_send.reset_mock()
            
            # Second run (should skip due to already sent)
            stats2 = DailyReminderEmailService.process_daily_reminders(db)
            assert stats2["skipped"] == 1
            assert stats2["sent"] == 0
            assert mock_send.call_count == 0


class TestDailyReminderEndpoint:
    """Test the daily reminder API endpoint."""

    def test_endpoint_missing_secret(self, client):
        """Test endpoint without secret header."""
        response = client.post("/internal/jobs/daily-todo-reminder")
        assert response.status_code in (401, 500)  # Either 401 or 500 if secret not configured

    def test_endpoint_invalid_secret(self, client):
        """Test endpoint with invalid secret."""
        with patch("app.api.internal.settings") as mock_settings:
            mock_settings.cron_secret = "valid-secret"
            response = client.post(
                "/internal/jobs/daily-todo-reminder",
                headers={"X-Cron-Secret": "wrong-secret"}
            )
            assert response.status_code == 403

    def test_endpoint_valid_secret(self, client):
        """Test endpoint with valid secret."""
        with patch("app.api.internal.settings") as mock_settings:
            mock_settings.cron_secret = "test-cron-secret"
            with patch.object(
                DailyReminderEmailService,
                "process_daily_reminders",
                return_value={"processed": 1, "sent": 1, "skipped": 0, "failed": 0},
            ):
                response = client.post(
                    "/internal/jobs/daily-todo-reminder",
                    headers={"X-Cron-Secret": "test-cron-secret"}
                )
                
                assert response.status_code == 200
                data = response.json()
                assert data["status"] == "completed"
                assert data["processed"] == 1
                assert data["sent"] == 1

    def test_endpoint_returns_stats(self, client):
        """Test that endpoint returns correct stats."""
        with patch("app.api.internal.settings") as mock_settings:
            mock_settings.cron_secret = "test-cron-secret"
            with patch.object(
                DailyReminderEmailService,
                "process_daily_reminders",
                return_value={"processed": 3, "sent": 2, "skipped": 1, "failed": 0},
            ):
                response = client.post(
                    "/internal/jobs/daily-todo-reminder",
                    headers={"X-Cron-Secret": "test-cron-secret"}
                )
                
                data = response.json()
                assert data["processed"] == 3
                assert data["sent"] == 2
                assert data["skipped"] == 1
                assert data["failed"] == 0


