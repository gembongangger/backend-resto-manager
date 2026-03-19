"""add price to kitchen_inventory

Revision ID: 20260319_kitchen_price
Revises: 20260319_unit_cost
Create Date: 2026-03-19

"""
from alembic import op
import sqlalchemy as sa

revision = '20260319_kitchen_price'
down_revision = '20260319_unit_cost'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('kitchen_inventory', sa.Column('price', sa.Float(), server_default='0', nullable=False))


def downgrade():
    op.drop_column('kitchen_inventory', 'price')
