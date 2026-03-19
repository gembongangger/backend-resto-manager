"""add menu_categories table and menu_items.category_id

Revision ID: 20260316_add_menu_categories
Revises: 20260316_add_category
Create Date: 2026-03-16
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text

# revision identifiers, used by Alembic.
revision = "20260316_add_menu_categories"
down_revision = "20260316_add_category"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    tables = inspector.get_table_names()

    if "menu_categories" not in tables:
        op.create_table(
            "menu_categories",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("restaurant_id", sa.Integer(), sa.ForeignKey("restaurants.id"), nullable=False),
            sa.Column("name", sa.String(length=80), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
            sa.UniqueConstraint("restaurant_id", "name", name="uq_menu_category_restaurant_name"),
        )

    columns = [c["name"] for c in inspector.get_columns("menu_items")]
    if "category_id" not in columns:
        with op.batch_alter_table("menu_items") as batch:
            batch.add_column(sa.Column("category_id", sa.Integer(), nullable=True))
            batch.create_foreign_key(
                "fk_menu_items_category_id",
                "menu_categories",
                ["category_id"],
                ["id"],
            )

    # Migrate existing string category -> category_id
    if "category" in columns:
        op.execute(
            text(
                "INSERT OR IGNORE INTO menu_categories (restaurant_id, name, created_at) "
                "SELECT DISTINCT restaurant_id, category, CURRENT_TIMESTAMP "
                "FROM menu_items WHERE category IS NOT NULL AND category != ''"
            )
        )
        op.execute(
            text(
                "UPDATE menu_items SET category_id = ("
                "SELECT id FROM menu_categories c "
                "WHERE c.restaurant_id = menu_items.restaurant_id AND c.name = menu_items.category"
                ") WHERE category IS NOT NULL AND category != ''"
            )
        )


def downgrade():
    bind = op.get_bind()
    inspector = inspect(bind)
    columns = [c["name"] for c in inspector.get_columns("menu_items")]
    if "category_id" in columns:
        with op.batch_alter_table("menu_items") as batch:
            batch.drop_column("category_id")

    tables = inspector.get_table_names()
    if "menu_categories" in tables:
        op.drop_table("menu_categories")
