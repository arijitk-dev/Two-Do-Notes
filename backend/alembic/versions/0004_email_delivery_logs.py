"""Add email_delivery_logs table for tracking reminder emails

Revision ID: 0004_email_delivery_logs
Revises: 0003_phase3_accountability
Create Date: 2026-08-22 16:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0004_email_delivery_logs'
down_revision = '0003_phase3_accountability'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create email delivery logs table
    op.create_table(
        'email_delivery_logs',
        sa.Column('id', sa.String(36), nullable=False),
        sa.Column('user_id', sa.String(36), nullable=False),
        sa.Column('email_type', sa.Enum('DAILY_TODO_REMINDER', name='emailtype', native_enum=False), nullable=False),
        sa.Column('scheduled_date', sa.String(10), nullable=False),
        sa.Column('status', sa.Enum('SENT', 'FAILED', 'PENDING', name='emailstatus', native_enum=False), nullable=False),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.String(1000), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'email_type', 'scheduled_date', name='uq_email_delivery_logs_user_type_date'),
    )
    op.create_index('ix_email_delivery_logs_user_id', 'email_delivery_logs', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_email_delivery_logs_user_id', table_name='email_delivery_logs')
    op.drop_table('email_delivery_logs')
