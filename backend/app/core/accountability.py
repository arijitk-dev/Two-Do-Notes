from enum import StrEnum


TODO_COMPLETION_POINTS = 3
MISSED_TODO_PENALTY = -7
TOMORROW_PLANNING_POINTS = 2
CARRY_FORWARD_BONUS = 1
SUCCESSFUL_DAY_THRESHOLD = 0.80
OVERPLANNING_THRESHOLD = 0.70
OVERPLANNING_MIN_PLANNED_PER_DAY = 5
ACCOUNTABILITY_ROLLING_DAYS = 7
TODO_HISTORY_RETENTION_DAYS = 15


class MissReasonCode(StrEnum):
    NOT_ENOUGH_TIME = "not_enough_time"
    UNEXPECTED_WORK = "unexpected_work"
    LOST_FOCUS = "lost_focus"
    TOO_DIFFICULT = "too_difficult"
    POOR_PLANNING = "poor_planning"
    OTHER = "other"


MISS_REASON_LABELS: dict[str, str] = {
    MissReasonCode.NOT_ENOUGH_TIME.value: "Not enough time",
    MissReasonCode.UNEXPECTED_WORK.value: "Unexpected work",
    MissReasonCode.LOST_FOCUS.value: "Lost focus",
    MissReasonCode.TOO_DIFFICULT.value: "Task was too difficult",
    MissReasonCode.POOR_PLANNING.value: "Poor planning",
    MissReasonCode.OTHER.value: "Other",
}


ACCOUNTABILITY_MESSAGES = (
    "Don't optimize your score. Optimize yourself.",
    "A missed Todo is okay. A dishonest checkmark isn't.",
    "Points are a consequence, not the goal.",
    "Plan less. Finish more.",
    "Be honest about what you can actually do.",
    "Your score doesn't matter if the data isn't truthful.",
    "Don't make tomorrow's Todo list a wishlist.",
    "Commit to what you can realistically finish.",
)


def accountability_message(seed: str) -> str:
    """Select a stable message for a context without showing one on every action."""
    return ACCOUNTABILITY_MESSAGES[sum(ord(char) for char in seed) % len(ACCOUNTABILITY_MESSAGES)]


def miss_reason_label(code: str | None, fallback: str | None = None) -> str:
    if code and code in MISS_REASON_LABELS:
        return MISS_REASON_LABELS[code]
    return fallback or MISS_REASON_LABELS[MissReasonCode.OTHER.value]
