from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field


class MissReasonStat(BaseModel):
    code: str
    label: str
    count: int
    percentage: float


class PointBreakdownResponse(BaseModel):
    completed_points: int
    planning_points: int
    carry_forward_bonus_points: int
    missed_points: int
    points_earned: int
    points_lost: int
    net_points: int


class DayMetricsResponse(BaseModel):
    review_date: date
    planned: int
    completed: int
    missed: int
    carried_forward: int
    pending: int
    resolved: int
    completion_rate: float
    successful: bool
    neutral: bool


class AccountabilityResponse(BaseModel):
    range_name: str
    start_date: date
    end_date: date
    planned_count: int
    completed_count: int
    missed_count: int
    carried_forward_count: int
    pending_count: int
    completion_rate: float
    planning_accuracy: float
    miss_rate: float
    carry_forward_rate: float
    current_streak: int
    max_streak: int
    completed_points: int
    planning_points: int
    carry_forward_bonus_points: int
    missed_points: int
    points_earned: int
    points_lost: int
    net_points: int
    missed_reasons: list[MissReasonStat]
    average_planned_per_day: float
    average_completed_per_day: float
    overplanning_warning: str | None
    accountability_message: str
    daily: list[DayMetricsResponse] = Field(default_factory=list)


class DailyReviewUpsert(BaseModel):
    mood_score: int | None = Field(default=None, ge=1, le=5)
    went_well: str | None = Field(default=None, max_length=5000)
    improvement: str | None = Field(default=None, max_length=5000)


class DailyReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str | None
    review_date: date
    mood_score: int | None
    went_well: str | None
    improvement: str | None
    created_at: datetime | None
    updated_at: datetime | None
    stats: DayMetricsResponse
