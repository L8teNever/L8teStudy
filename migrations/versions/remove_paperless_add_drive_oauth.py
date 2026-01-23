"""Remove Paperless models and add Google Drive OAuth models

Revision ID: remove_paperless_add_drive_oauth
Revises: 
Create Date: 2026-01-23

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = 'remove_paperless_add_drive_oauth'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Drop Paperless tables
    op.drop_table('paperless_document_tags')
    op.drop_table('paperless_document')
    op.drop_table('paperless_tag')
    op.drop_table('paperless_correspondent')
    op.drop_table('paperless_document_type')
    op.drop_table('paperless_config')
    
    # Create Drive OAuth Token table
    op.create_table('drive_oauth_token',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('access_token', sa.Text(), nullable=False),
        sa.Column('refresh_token', sa.Text(), nullable=True),
        sa.Column('token_expiry', sa.DateTime(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Update DriveFolder table (remove old columns if they exist, add new ones)
    with op.batch_alter_table('drive_folder', schema=None) as batch_op:
        # Add new columns
        batch_op.add_column(sa.Column('is_active', sa.Boolean(), nullable=True, server_default='1'))
        batch_op.add_column(sa.Column('include_subfolders', sa.Boolean(), nullable=True, server_default='1'))
        batch_op.add_column(sa.Column('created_by_user_id', sa.Integer(), nullable=True))
        batch_op.create_foreign_key('fk_drive_folder_created_by', 'user', ['created_by_user_id'], ['id'])


def downgrade():
    # Recreate Paperless tables
    op.create_table('paperless_config',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('class_id', sa.Integer(), nullable=True),
        sa.Column('paperless_url', sa.String(length=500), nullable=False),
        sa.Column('api_token', sa.String(length=500), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('is_global', sa.Boolean(), nullable=True),
        sa.Column('auto_sync_enabled', sa.Boolean(), nullable=True),
        sa.Column('last_sync_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['class_id'], ['school_class.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # ... (other Paperless tables)
    
    # Drop Drive OAuth Token table
    op.drop_table('drive_oauth_token')
    
    # Remove new DriveFolder columns
    with op.batch_alter_table('drive_folder', schema=None) as batch_op:
        batch_op.drop_constraint('fk_drive_folder_created_by', type_='foreignkey')
        batch_op.drop_column('created_by_user_id')
        batch_op.drop_column('include_subfolders')
        batch_op.drop_column('is_active')
