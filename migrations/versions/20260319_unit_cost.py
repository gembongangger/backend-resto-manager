"""add unit_cost to kitchen_inventory

Revision ID: 20260319_unit_cost
Revises: 20260319_recipes
Create Date: 2026-03-19

"""
from alembic import op
import sqlalchemy as sa

revision = '20260319_unit_cost'
down_revision = '20260319_recipes'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('kitchen_inventory', sa.Column('unit_cost', sa.Float(), server_default='0', nullable=False))


def downgrade():
    op.drop_column('kitchen_inventory', 'unit_cost')
