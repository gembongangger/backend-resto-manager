"""add cost to menu_items

Revision ID: 20260316_add_cost
Revises: 
Create Date: 2026-03-16
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = "20260316_add_cost"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [c["name"] for c in inspector.get_columns("menu_items")]
    if "cost" not in columns:
        with op.batch_alter_table("menu_items") as batch:
            batch.add_column(sa.Column("cost", sa.Integer(), nullable=False, server_default="0"))


def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [c["name"] for c in inspector.get_columns("menu_items")]
    if "cost" in columns:
        with op.batch_alter_table("menu_items") as batch:
            batch.drop_column("cost")
