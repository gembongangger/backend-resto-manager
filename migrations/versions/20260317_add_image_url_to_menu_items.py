"""add image_url to menu_items

Revision ID: 20260317_add_image_url
Revises: b340562d27da
Create Date: 2026-03-17 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260317_add_image_url'
down_revision = 'b340562d27da'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('menu_items', schema=None) as batch_op:
        batch_op.add_column(sa.Column('image_url', sa.String(length=255), nullable=True))


def downgrade():
    with op.batch_alter_table('menu_items', schema=None) as batch_op:
        batch_op.drop_column('image_url')
