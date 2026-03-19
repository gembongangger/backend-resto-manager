"""add category to menu_items

Revision ID: 20260316_add_category
Revises: 20260316_add_cost
Create Date: 2026-03-16
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision = "20260316_add_category"
down_revision = "20260316_add_cost"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [c["name"] for c in inspector.get_columns("menu_items")]
    if "category" not in columns:
        with op.batch_alter_table("menu_items") as batch:
            batch.add_column(sa.Column("category", sa.String(length=80), nullable=True))


def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [c["name"] for c in inspector.get_columns("menu_items")]
    if "category" in columns:
        with op.batch_alter_table("menu_items") as batch:
            batch.drop_column("category")
