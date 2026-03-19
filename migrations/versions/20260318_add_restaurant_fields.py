"""add address and phone to restaurants

Revision ID: 20260318_add_restaurant_fields
Revises: 20260317_add_image_url
Create Date: 2026-03-18

"""
from alembic import op
import sqlalchemy as sa

revision = '20260318_add_restaurant_fields'
down_revision = '20260317_add_image_url'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('restaurants', sa.Column('address', sa.Text(), server_default='', nullable=False))
    op.add_column('restaurants', sa.Column('phone', sa.String(20), server_default='', nullable=False))


def downgrade():
    op.drop_column('restaurants', 'phone')
    op.drop_column('restaurants', 'address')
