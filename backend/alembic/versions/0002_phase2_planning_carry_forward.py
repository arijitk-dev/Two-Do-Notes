"""add phase 2 planning and carry-forward metadata"""
from alembic import op
import sqlalchemy as sa

revision = "0002_phase2_planning_carry_forward"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def _widen_alembic_version_column() -> None:
    """Allow revision identifiers longer than Alembic's 32-character default."""
    op.alter_column(
        "alembic_version",
        "version_num",
        existing_type=sa.String(length=32),
        type_=sa.String(length=64),
        existing_nullable=False,
    )


def upgrade() -> None:
    _widen_alembic_version_column()
    op.add_column("todos", sa.Column("original_scheduled_date", sa.Date(), nullable=True))
    op.add_column("todos", sa.Column("carried_from_date", sa.Date(), nullable=True))
    op.add_column("todos", sa.Column("carry_forward_count", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("todos", sa.Column("carry_forward_bonus_awarded", sa.Boolean(), nullable=False, server_default=sa.false()))
    op.execute("UPDATE todos SET original_scheduled_date = scheduled_date WHERE original_scheduled_date IS NULL")
    op.create_index("ix_todos_user_status", "todos", ["user_id", "status"])
    # The immutable point ledger relies on this database-level uniqueness rule.
    op.create_index("uq_point_transaction_todo_type", "point_transactions", ["todo_id", "transaction_type"], unique=True)


def downgrade() -> None:
    op.drop_index("uq_point_transaction_todo_type", table_name="point_transactions")
    op.drop_index("ix_todos_user_status", table_name="todos")
    op.drop_column("todos", "carry_forward_bonus_awarded")
    op.drop_column("todos", "carry_forward_count")
    op.drop_column("todos", "carried_from_date")
    op.drop_column("todos", "original_scheduled_date")
