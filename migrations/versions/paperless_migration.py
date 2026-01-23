"""Replace Google Drive with Paperless-NGX integration

Revision ID: paperless_migration
Revises: 
Create Date: 2026-01-23 09:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers, used by Alembic.
revision = 'paperless_migration'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create Paperless tables
    
    # PaperlessConfig
    op.create_table('paperless_config',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('class_id', sa.Integer(), nullable=True),
        sa.Column('paperless_url', sa.String(length=500), nullable=False),
        sa.Column('api_token', sa.String(length=500), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('is_global', sa.Boolean(), nullable=True, default=False),
        sa.Column('auto_sync_enabled', sa.Boolean(), nullable=True, default=True),
        sa.Column('last_sync_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['class_id'], ['school_class.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # PaperlessCorrespondent
    op.create_table('paperless_correspondent',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('config_id', sa.Integer(), nullable=False),
        sa.Column('paperless_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('cached_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['config_id'], ['paperless_config.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('config_id', 'paperless_id', name='_config_correspondent_uc')
    )
    
    # PaperlessDocumentType
    op.create_table('paperless_document_type',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('config_id', sa.Integer(), nullable=False),
        sa.Column('paperless_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('cached_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['config_id'], ['paperless_config.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('config_id', 'paperless_id', name='_config_doctype_uc')
    )
    
    # PaperlessTag
    op.create_table('paperless_tag',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('config_id', sa.Integer(), nullable=False),
        sa.Column('paperless_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=128), nullable=False),
        sa.Column('color', sa.String(length=7), nullable=True, default='#a6cee3'),
        sa.Column('is_inbox_tag', sa.Boolean(), nullable=True, default=False),
        sa.Column('cached_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['config_id'], ['paperless_config.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('config_id', 'paperless_id', name='_config_tag_uc')
    )
    
    # PaperlessDocument
    op.create_table('paperless_document',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('config_id', sa.Integer(), nullable=False),
        sa.Column('paperless_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=False),
        sa.Column('content', sa.Text(), nullable=True),
        sa.Column('created', sa.DateTime(), nullable=False),
        sa.Column('modified', sa.DateTime(), nullable=False),
        sa.Column('added', sa.DateTime(), nullable=False),
        sa.Column('original_filename', sa.String(length=500), nullable=True),
        sa.Column('archived_filename', sa.String(length=500), nullable=True),
        sa.Column('mime_type', sa.String(length=128), nullable=True),
        sa.Column('correspondent_id', sa.Integer(), nullable=True),
        sa.Column('document_type_id', sa.Integer(), nullable=True),
        sa.Column('subject_id', sa.Integer(), nullable=True),
        sa.Column('cached_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['config_id'], ['paperless_config.id'], ),
        sa.ForeignKeyConstraint(['correspondent_id'], ['paperless_correspondent.id'], ),
        sa.ForeignKeyConstraint(['document_type_id'], ['paperless_document_type.id'], ),
        sa.ForeignKeyConstraint(['subject_id'], ['subject.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('config_id', 'paperless_id', name='_config_document_uc')
    )
    
    # PaperlessDocumentTags (junction table)
    op.create_table('paperless_document_tags',
        sa.Column('document_id', sa.Integer(), nullable=False),
        sa.Column('tag_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['paperless_document.id'], ),
        sa.ForeignKeyConstraint(['tag_id'], ['paperless_tag.id'], ),
        sa.PrimaryKeyConstraint('document_id', 'tag_id')
    )
    
    # Drop old Drive tables (if they exist)
    # Note: In SQLite, we need to be careful with foreign keys
    try:
        op.drop_table('drive_file_content')
    except:
        pass
    
    try:
        op.drop_table('drive_file')
    except:
        pass
    
    try:
        op.drop_table('drive_folder')
    except:
        pass


def downgrade():
    # Drop Paperless tables
    op.drop_table('paperless_document_tags')
    op.drop_table('paperless_document')
    op.drop_table('paperless_tag')
    op.drop_table('paperless_document_type')
    op.drop_table('paperless_correspondent')
    op.drop_table('paperless_config')
    
    # Recreate Drive tables (basic structure)
    op.create_table('drive_folder',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('folder_id', sa.String(length=256), nullable=False),
        sa.Column('folder_name', sa.String(length=256), nullable=False),
        sa.Column('privacy_level', sa.String(length=20), nullable=True),
        sa.Column('is_root', sa.Boolean(), nullable=True),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('subject_id', sa.Integer(), nullable=True),
        sa.Column('sync_enabled', sa.Boolean(), nullable=True),
        sa.Column('last_sync_at', sa.DateTime(), nullable=True),
        sa.Column('sync_status', sa.String(length=50), nullable=True),
        sa.Column('sync_error', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['drive_folder.id'], ),
        sa.ForeignKeyConstraint(['subject_id'], ['subject.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'folder_id', name='_user_folder_uc')
    )
    
    op.create_table('drive_file',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('drive_folder_id', sa.Integer(), nullable=False),
        sa.Column('file_id', sa.String(length=256), nullable=False),
        sa.Column('filename', sa.String(length=512), nullable=False),
        sa.Column('encrypted_path', sa.String(length=512), nullable=False),
        sa.Column('file_hash', sa.String(length=64), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(length=128), nullable=False),
        sa.Column('subject_id', sa.Integer(), nullable=True),
        sa.Column('auto_mapped', sa.Boolean(), nullable=True),
        sa.Column('ocr_completed', sa.Boolean(), nullable=True),
        sa.Column('ocr_error', sa.Text(), nullable=True),
        sa.Column('parent_folder_name', sa.String(length=512), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['drive_folder_id'], ['drive_folder.id'], ),
        sa.ForeignKeyConstraint(['subject_id'], ['subject.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('drive_folder_id', 'file_id', name='_folder_file_uc')
    )
    
    op.create_table('drive_file_content',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('drive_file_id', sa.Integer(), nullable=False),
        sa.Column('content_text', sa.Text(), nullable=False),
        sa.Column('page_count', sa.Integer(), nullable=True),
        sa.Column('ocr_completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['drive_file_id'], ['drive_file.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('drive_file_id')
    )
