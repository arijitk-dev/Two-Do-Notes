"""add Phase 3 accountability and daily reviews"""
from alembic import op
import sqlalchemy as sa


revision = "0003_phase3_accountability"
down_revision = "0002_phase2_planning_carry_forward"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("todos", sa.Column("miss_reason_code", sa.String(length=40), nullable=True))
    op.add_column("todos", sa.Column("miss_reason_text", sa.String(length=500), nullable=True))
    op.create_table(
        "daily_reviews",
        sa.Column("id", sa.String(length=36), primary_key=True),
        sa.Column("user_id", sa.String(length=36), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("review_date", sa.Date(), nullable=False),
        sa.Column("mood_score", sa.Integer(), nullable=True),
        sa.Column("went_well", sa.Text(), nullable=True),
        sa.Column("improvement", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.UniqueConstraint("user_id", "review_date", name="uq_daily_review_user_date"),
    )
    op.create_index("ix_daily_reviews_user_id", "daily_reviews", ["user_id"])
    op.create_index("ix_daily_reviews_review_date", "daily_reviews", ["review_date"])


def downgrade() -> None:
    op.drop_index("ix_daily_reviews_review_date", table_name="daily_reviews")
    op.drop_index("ix_daily_reviews_user_id", table_name="daily_reviews")
    op.drop_table("daily_reviews")
    op.drop_column("todos", "miss_reason_text")
    op.drop_column("todos", "miss_reason_code")
