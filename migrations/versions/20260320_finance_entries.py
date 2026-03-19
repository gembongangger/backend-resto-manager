"""create finance entries table

Revision ID: 20260320_finance_entries
Revises: 20260319_kitchen_price
Create Date: 2026-03-20

"""
from alembic import op
import sqlalchemy as sa


revision = "20260320_finance_entries"
down_revision = "20260319_kitchen_price"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "finance_entries",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("restaurant_id", sa.Integer(), nullable=False),
        sa.Column("created_by", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=120), nullable=False),
        sa.Column("entry_type", sa.String(length=20), nullable=False),
        sa.Column("amount", sa.Float(), nullable=False),
        sa.Column("notes", sa.String(length=255), nullable=True),
        sa.Column("entry_date", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.CheckConstraint(
            "entry_type in ('salary', 'owner_draw', 'expense')",
            name="ck_finance_entries_entry_type",
        ),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.ForeignKeyConstraint(["restaurant_id"], ["restaurants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_finance_entries_restaurant_id", "finance_entries", ["restaurant_id"], unique=False)
    op.create_index("ix_finance_entries_entry_date", "finance_entries", ["entry_date"], unique=False)


def downgrade():
    op.drop_index("ix_finance_entries_entry_date", table_name="finance_entries")
    op.drop_index("ix_finance_entries_restaurant_id", table_name="finance_entries")
    op.drop_table("finance_entries")
