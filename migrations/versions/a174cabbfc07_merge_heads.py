"""Merge heads

Revision ID: a174cabbfc07
Revises: add_subject_mapping, paperless_migration, remove_paperless_add_drive_oauth
Create Date: 2026-01-26 11:11:10.464775

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a174cabbfc07'
down_revision = ('add_subject_mapping', 'paperless_migration', 'remove_paperless_add_drive_oauth')
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
