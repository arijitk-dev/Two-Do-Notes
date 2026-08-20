from fastapi import APIRouter
from app.api.deps import CurrentUser, DbSession
from app.repositories.point_repository import PointRepository
from app.schemas.common import PointTransactionResponse

router = APIRouter(prefix="/points", tags=["points"])


@router.get("", response_model=dict[str, int])
def points_summary(user: CurrentUser, db: DbSession):
    return {"total_points": PointRepository().total(db, user.id)}


@router.get("/history", response_model=list[PointTransactionResponse])
def points_history(user: CurrentUser, db: DbSession):
    return PointRepository().history(db, user.id)
