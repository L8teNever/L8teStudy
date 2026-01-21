"""Add SubjectMapping table

Revision ID: add_subject_mapping
Revises: 
Create Date: 2026-01-21 11:52:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_subject_mapping'
down_revision = None
depends_on = None


def upgrade():
    # Create subject_mapping table
    op.create_table('subject_mapping',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('informal_name', sa.String(length=128), nullable=False),
        sa.Column('subject_id', sa.Integer(), nullable=False),
        sa.Column('class_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('is_global', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['class_id'], ['school_class.id'], ),
        sa.ForeignKeyConstraint(['subject_id'], ['subject.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('informal_name', 'class_id', 'user_id', name='_informal_name_scope_uc')
    )


def downgrade():
    op.drop_table('subject_mapping')
