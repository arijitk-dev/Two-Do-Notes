"""add source references for Todo history reuse"""

from alembic import op
import sqlalchemy as sa


revision = "0004_todo_history_reuse"
down_revision = "0003_phase3_accountability"
branch_labels = None
depends_on = None


def upgrade() -> None:
    column = sa.Column(
        "source_todo_id",
        sa.String(length=36),
        sa.ForeignKey("todos.id", name="fk_todos_source_todo_id", ondelete="SET NULL"),
        nullable=True,
    )
    op.add_column("todos", column)
    op.create_index("ix_todos_source_todo_id", "todos", ["source_todo_id"])


def downgrade() -> None:
    op.drop_index("ix_todos_source_todo_id", table_name="todos")
    op.drop_constraint("fk_todos_source_todo_id", "todos", type_="foreignkey")
    op.drop_column("todos", "source_todo_id")
