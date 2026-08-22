"""Service for sending daily todo reminder emails."""
import logging
from datetime import datetime
from zoneinfo import ZoneInfo, available_timezones

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models.email_delivery_log import EmailDeliveryLog, EmailStatus, EmailType
from app.models.todo import Todo
from app.models.user import User

logger = logging.getLogger(__name__)
settings = get_settings()


class DailyReminderEmailService:
    """Service for sending daily reminder emails."""

    @staticmethod
    def validate_timezone(timezone_str: str) -> bool:
        """Validate timezone string against IANA timezone database."""
        if not timezone_str:
            return False
        try:
            ZoneInfo(timezone_str)
            return True
        except Exception:
            return False

    @staticmethod
    def get_today_date_for_user(timezone_str: str) -> str:
        """Get today's date in user's timezone as YYYY-MM-DD string."""
        try:
            if not DailyReminderEmailService.validate_timezone(timezone_str):
                logger.warning(f"Invalid timezone '{timezone_str}', using UTC")
                tz = ZoneInfo("UTC")
            else:
                tz = ZoneInfo(timezone_str)
            today = datetime.now(tz=tz).date()
            return today.isoformat()
        except Exception as e:
            logger.error(f"Error getting today's date for timezone {timezone_str}: {e}")
            return datetime.now(tz=ZoneInfo("UTC")).date().isoformat()

    @staticmethod
    def get_user_todos_for_today(db: Session, user_id: str, today_date: str) -> tuple[int, int]:
        """
        Get today's todo count and completion count for a user.
        
        Returns: (total_count, completed_count)
        """
        try:
            # Query todos for today
            today_todos = db.execute(
                select(func.count(Todo.id)).where(
                    (Todo.user_id == user_id) & (Todo.due_date == today_date)
                )
            ).scalar() or 0

            completed_todos = db.execute(
                select(func.count(Todo.id)).where(
                    (Todo.user_id == user_id)
                    & (Todo.due_date == today_date)
                    & (Todo.status == "completed")
                )
            ).scalar() or 0

            return today_todos, completed_todos
        except Exception as e:
            logger.error(f"Error getting todos for user {user_id}: {e}")
            return 0, 0

    @staticmethod
    def check_email_already_sent(db: Session, user_id: str, today_date: str) -> bool:
        """Check if email was already sent today (for idempotency)."""
        try:
            existing = db.execute(
                select(EmailDeliveryLog).where(
                    (EmailDeliveryLog.user_id == user_id)
                    & (EmailDeliveryLog.email_type == EmailType.DAILY_TODO_REMINDER)
                    & (EmailDeliveryLog.scheduled_date == today_date)
                    & (EmailDeliveryLog.status == EmailStatus.SENT)
                )
            ).first()
            return existing is not None
        except Exception as e:
            logger.error(f"Error checking email history for user {user_id}: {e}")
            return False

    @staticmethod
    def send_email_via_resend(
        email_to: str, todo_count: int, completed_count: int
    ) -> tuple[bool, str | None]:
        """
        Send email via Resend API.
        
        Returns: (success, error_message)
        """
        if not settings.resend_api_key:
            return False, "RESEND_API_KEY not configured"

        try:
            import resend  # Lazy import to avoid requiring Resend if not used
            
            resend.api_key = settings.resend_api_key

            # Generate email content
            subject = "🌅 Good morning — what's your plan today?"
            
            html_content = f"""
<html>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #333;">
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h1 style="margin-top: 0; color: #2c3e50;">Good morning!</h1>
        
        <p>Take a minute to decide what actually matters today.</p>
        
        <div style="background-color: #f5f5f5; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h2 style="margin-top: 0; color: #2c3e50;">Your Todo list for today:</h2>
            <p style="font-size: 16px; margin: 5px 0;">
                <strong>{todo_count} planned</strong>
            </p>
            <p style="font-size: 16px; margin: 5px 0;">
                <strong>{completed_count} completed</strong>
            </p>
        </div>
        
        <p style="color: #555; font-size: 14px;">
            Don't add Todos just to collect points.<br>
            Add only what you're genuinely committed to completing.
        </p>
        
        <p style="margin-top: 30px;">
            <a href="{settings.frontend_url}/todos" style="display: inline-block; background-color: #4CAF50; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; font-weight: bold;">Open Two Do Notes</a>
        </p>
        
        <p style="color: #999; font-size: 12px; margin-top: 40px; border-top: 1px solid #eee; padding-top: 20px;">
            — Two Do Notes<br>
            Personal productivity & accountability
        </p>
    </div>
</body>
</html>
            """

            plain_text = f"""Good morning!

Take a minute to decide what actually matters today.

Your Todo list for today:
{todo_count} planned
{completed_count} completed

Don't add Todos just to collect points.
Add only what you're genuinely committed to completing.

Open Two Do Notes:
{settings.frontend_url}/todos

— Two Do Notes
Personal productivity & accountability
            """

            response = resend.Emails.send(
                {
                    "from": settings.email_from,
                    "to": email_to,
                    "subject": subject,
                    "html": html_content,
                    "text": plain_text,
                }
            )

            if response.get("id"):
                return True, None
            else:
                error = response.get("error", "Unknown error")
                return False, str(error)

        except ImportError:
            return False, "resend library not installed"
        except Exception as e:
            logger.error(f"Error sending email via Resend: {e}")
            return False, str(e)

    @staticmethod
    def create_email_log(
        db: Session,
        user_id: str,
        today_date: str,
        success: bool,
        error_message: str | None = None,
    ) -> None:
        """Create email delivery log entry."""
        try:
            log = EmailDeliveryLog(
                user_id=user_id,
                email_type=EmailType.DAILY_TODO_REMINDER,
                scheduled_date=today_date,
                status=EmailStatus.SENT if success else EmailStatus.FAILED,
                sent_at=datetime.now(tz=ZoneInfo("UTC")) if success else None,
                error_message=error_message,
            )
            db.add(log)
            db.commit()
        except Exception as e:
            logger.error(f"Error creating email log: {e}")
            db.rollback()

    @staticmethod
    def process_daily_reminders(db: Session) -> dict:
        """
        Process and send daily reminder emails to all users.
        
        Returns:
            {
                "status": "completed",
                "processed": int,
                "sent": int,
                "skipped": int,
                "failed": int,
            }
        """
        stats = {"processed": 0, "sent": 0, "skipped": 0, "failed": 0}

        try:
            # Get all users
            users = db.execute(select(User)).scalars().all()
            logger.info(f"Found {len(users)} users")

            for user in users:
                stats["processed"] += 1

                # Validate timezone
                if not user.email:
                    logger.warning(f"User {user.id} has no email, skipping")
                    stats["skipped"] += 1
                    continue

                if not user.timezone or not DailyReminderEmailService.validate_timezone(user.timezone):
                    logger.warning(
                        f"User {user.id} has invalid timezone '{user.timezone}', using UTC"
                    )
                    # Use UTC as fallback, but don't modify the user record
                    user_tz = "UTC"
                else:
                    user_tz = user.timezone

                # Get today's date in user's timezone
                today_date = DailyReminderEmailService.get_today_date_for_user(user_tz)

                # Check idempotency
                if DailyReminderEmailService.check_email_already_sent(db, user.id, today_date):
                    logger.info(f"Email already sent to user {user.id} for {today_date}")
                    stats["skipped"] += 1
                    continue

                # Get todo counts
                todo_count, completed_count = DailyReminderEmailService.get_user_todos_for_today(
                    db, user.id, today_date
                )

                # Send email
                success, error = DailyReminderEmailService.send_email_via_resend(
                    user.email, todo_count, completed_count
                )

                # Log result
                DailyReminderEmailService.create_email_log(
                    db, user.id, today_date, success, error
                )

                if success:
                    logger.info(f"Email sent to user {user.id} ({user.email})")
                    stats["sent"] += 1
                else:
                    logger.error(f"Failed to send email to user {user.id}: {error}")
                    stats["failed"] += 1

        except Exception as e:
            logger.error(f"Error in process_daily_reminders: {e}")

        return stats
