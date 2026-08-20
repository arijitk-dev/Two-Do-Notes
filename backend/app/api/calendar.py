from fastapi import APIRouter, HTTPException, Query

from app.api.deps import CurrentUser, DbSession
from app.schemas.calendar import CalendarResponse
from app.services.calendar_service import CalendarService

router = APIRouter(prefix="/calendar", tags=["calendar"])


@router.get("", response_model=CalendarResponse)
def get_calendar(
    user: CurrentUser,
    db: DbSession,
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
):
    try:
        return CalendarService().month(db, user, year, month)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

