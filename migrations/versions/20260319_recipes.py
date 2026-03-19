"""add margin_percent to restaurants and create recipes table

Revision ID: 20260319_recipes
Revises: 20260318_add_restaurant_fields
Create Date: 2026-03-19

"""
from alembic import op
import sqlalchemy as sa

revision = '20260319_recipes'
down_revision = '20260318_add_restaurant_fields'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('restaurants', sa.Column('margin_percent', sa.Float(), server_default='30', nullable=False))
    op.create_table('recipes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('menu_item_id', sa.Integer(), nullable=False),
        sa.Column('inventory_item_id', sa.Integer(), nullable=False),
        sa.Column('quantity', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['menu_item_id'], ['menu_items.id']),
        sa.ForeignKeyConstraint(['inventory_item_id'], ['kitchen_inventory.id']),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('recipes')
    op.drop_column('restaurants', 'margin_percent')
