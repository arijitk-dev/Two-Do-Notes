from datetime import date

from fastapi import APIRouter, HTTPException, Query

from app.api.deps import CurrentUser, DbSession
from app.schemas.accountability import AccountabilityResponse
from app.services.accountability_service import AccountabilityService


router = APIRouter(prefix="/accountability", tags=["accountability"])


@router.get("", response_model=AccountabilityResponse)
def accountability(
    user: CurrentUser,
    db: DbSession,
    range_name: str = Query(default="7d", alias="range", pattern="^(today|day|7d|month|current_month)$"),
    start_date: date | None = Query(default=None),
    end_date: date | None = Query(default=None),
):
    try:
        result = AccountabilityService().summary(db, user, range_name, start_date, end_date)
        db.commit()
        return result
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
