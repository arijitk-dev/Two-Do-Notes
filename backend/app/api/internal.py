"""Internal job endpoints (triggered by GitHub Actions and other schedulers)."""
import logging
from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.services.daily_reminder_email_service import DailyReminderEmailService

logger = logging.getLogger(__name__)
settings = get_settings()
router = APIRouter(prefix="/internal/jobs", tags=["internal"])


@router.post("/daily-todo-reminder")
async def trigger_daily_todo_reminder(
    x_cron_secret: str = Header(None),
    db: Session = Depends(get_db),
) -> dict:
    """
    Trigger the daily todo reminder email job.
    
    This endpoint is called by GitHub Actions on a schedule.
    It requires a valid CRON_SECRET for authorization.
    """
    # Validate secret
    if not settings.cron_secret:
        logger.error("CRON_SECRET not configured on server")
        raise HTTPException(status_code=500, detail="Server misconfigured")

    if not x_cron_secret:
        logger.warning("Daily reminder job called without secret")
        raise HTTPException(status_code=401, detail="Unauthorized")

    if x_cron_secret != settings.cron_secret:
        logger.warning("Daily reminder job called with invalid secret")
        raise HTTPException(status_code=403, detail="Forbidden")

    # Process reminders
    logger.info("Starting daily todo reminder job")
    stats = DailyReminderEmailService.process_daily_reminders(db)
    logger.info(f"Daily reminder job completed: {stats}")

    return {
        "status": "completed",
        "processed": stats["processed"],
        "sent": stats["sent"],
        "skipped": stats["skipped"],
        "failed": stats["failed"],
    }
