"""add is_active to users

Revision ID: add_is_active_to_users
Revises: 20260320_finance_entries
Create Date: 2026-03-19
"""
from alembic import op
import sqlalchemy as sa

revision = 'add_is_active_to_users'
down_revision = '20260320_finance_entries'
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'))

def downgrade():
    op.drop_column('users', 'is_active')
