"""
Paperless-NGX API Routes for L8teStudy
Handles all Paperless integration endpoints
"""

from flask import Blueprint, request, jsonify, send_file, current_app
from flask_login import login_required, current_user
from io import BytesIO
from datetime import datetime
import logging

from .models import (
    db, PaperlessConfig, PaperlessDocument, PaperlessTag,
    PaperlessCorrespondent, PaperlessDocumentType, Subject
)
from .paperless_client import PaperlessClient, PaperlessAPIError

logger = logging.getLogger(__name__)

paperless_bp = Blueprint('paperless', __name__, url_prefix='/api/paperless')


def get_user_paperless_config():
    """Get active Paperless config for current user"""
    # Priority: User config > Class config > Global config
    config = None
    
    # Check for user-specific config
    config = PaperlessConfig.query.filter_by(user_id=current_user.id, is_active=True).first()
    
    if not config and current_user.school_class:
        # Check for class config
        config = PaperlessConfig.query.filter_by(class_id=current_user.school_class.id, is_active=True).first()
    
    if not config:
        # Check for global config
        config = PaperlessConfig.query.filter_by(is_global=True, is_active=True).first()
    
    return config


def get_paperless_client():
    """Get Paperless client for current user"""
    config = get_user_paperless_config()
    if not config:
        raise PaperlessAPIError("No Paperless configuration found. Please configure Paperless in settings.")
    
    return PaperlessClient(config.paperless_url, config.get_api_token()), config


# --- Configuration ---

@paperless_bp.route('/config', methods=['GET'])
@login_required
def get_config():
    """Get current Paperless configuration"""
    try:
        config = get_user_paperless_config()
        
        if not config:
            return jsonify({
                'configured': False,
                'message': 'No Paperless configuration found'
            })
        
        return jsonify({
            'configured': True,
            'url': config.paperless_url,
            'is_active': config.is_active,
            'last_sync': config.last_sync_at.isoformat() if config.last_sync_at else None,
            'auto_sync': config.auto_sync_enabled
        })
        
    except Exception as e:
        logger.error(f"Error getting Paperless config: {e}")
        return jsonify({'error': str(e)}), 500


@paperless_bp.route('/config', methods=['POST', 'PUT'])
@login_required
def save_config():
    """Save Paperless configuration"""
    try:
        data = request.json
        
        if not data.get('url') or not data.get('token'):
            return jsonify({'success': False, 'message': 'URL and token required'}), 400
        
        # Test connection first
        try:
            test_client = PaperlessClient(data['url'], data['token'])
            result = test_client.test_connection()
            if not result['success']:
                return jsonify({'success': False, 'message': f"Connection failed: {result['message']}"}), 400
        except Exception as e:
            return jsonify({'success': False, 'message': f"Connection test failed: {str(e)}"}), 400
        
        # Determine scope (user, class, or global)
        scope = data.get('scope', 'user')  # user, class, global
        
        config = None
        
        if scope == 'user':
            # User-specific config
            config = PaperlessConfig.query.filter_by(user_id=current_user.id, is_active=True).first()
            if not config:
                config = PaperlessConfig(user_id=current_user.id)
                db.session.add(config)
        
        elif scope == 'class' and current_user.is_admin:
            # Class-wide config (only admins)
            if not current_user.school_class:
                return jsonify({'success': False, 'message': 'No class assigned'}), 400
            
            config = PaperlessConfig.query.filter_by(
                class_id=current_user.school_class.id,
                is_active=True
            ).first()
            
            if not config:
                config = PaperlessConfig(class_id=current_user.school_class.id)
                db.session.add(config)
        
        elif scope == 'global' and current_user.is_super_admin:
            # Global config (only super admins)
            config = PaperlessConfig.query.filter_by(is_global=True, is_active=True).first()
            if not config:
                config = PaperlessConfig(is_global=True)
                db.session.add(config)
        
        else:
            return jsonify({'success': False, 'message': 'Invalid scope or insufficient permissions'}), 403
        
        # Update config
        config.paperless_url = data['url'].rstrip('/')
        config.set_api_token(data['token'])
        config.auto_sync_enabled = data.get('auto_sync', True)
        config.updated_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Configuration saved successfully'})
        
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error saving Paperless config: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@paperless_bp.route('/config/test', methods=['POST'])
@login_required
def test_connection():
    """Test Paperless connection"""
    try:
        data = request.json
        
        if not data.get('url') or not data.get('token'):
            return jsonify({'success': False, 'message': 'URL and token required'}), 400
        
        client = PaperlessClient(data['url'], data['token'])
        result = client.test_connection()
        
        return jsonify(result)
        
    except Exception as e:
        logger.error(f"Connection test error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# --- Documents ---

@paperless_bp.route('/documents', methods=['GET'])
@login_required
def get_documents():
    """Get list of documents with filters"""
    try:
        client, config = get_paperless_client()
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 25, type=int)
        query = request.args.get('query')
        tags = request.args.get('tags')  # Comma-separated tag IDs
        correspondent = request.args.get('correspondent', type=int)
        document_type = request.args.get('document_type', type=int)
        ordering = request.args.get('ordering', '-created')
        
        # Parse tags
        tag_ids = None
        if tags:
            tag_ids = [int(t) for t in tags.split(',') if t.strip()]
        
        # Fetch from Paperless
        result = client.get_documents(
            page=page,
            page_size=page_size,
            query=query,
            tags=tag_ids,
            correspondent=correspondent,
            document_type=document_type,
            ordering=ordering
        )
        
        # Cache documents in database
        for doc_data in result.get('results', []):
            _cache_document(config, doc_data)
        
        db.session.commit()
        
        return jsonify(result)
        
    except PaperlessAPIError as e:
        logger.error(f"Paperless API error: {e}")
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        logger.error(f"Error getting documents: {e}")
        return jsonify({'error': str(e)}), 500


@paperless_bp.route('/documents/<int:doc_id>', methods=['GET'])
@login_required
def get_document(doc_id):
    """Get single document details"""
    try:
        client, config = get_paperless_client()
        
        doc_data = client.get_document(doc_id)
        
        # Cache document
        _cache_document(config, doc_data)
        db.session.commit()
        
        return jsonify(doc_data)
        
    except PaperlessAPIError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        logger.error(f"Error getting document: {e}")
        return jsonify({'error': str(e)}), 500


@paperless_bp.route('/documents/<int:doc_id>/download', methods=['GET'])
@login_required
def download_document(doc_id):
    """Download document file"""
    try:
        client, config = get_paperless_client()
        
        original = request.args.get('original', 'false').lower() == 'true'
        
        # Get document info first
        doc_data = client.get_document(doc_id)
        filename = doc_data.get('archived_file_name' if not original else 'original_file_name', f'document_{doc_id}.pdf')
        
        # Download file
        file_content = client.download_document(doc_id, original=original)
        
        return send_file(
            BytesIO(file_content),
            as_attachment=True,
            download_name=filename,
            mimetype='application/octet-stream'
        )
        
    except PaperlessAPIError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        logger.error(f"Error downloading document: {e}")
        return jsonify({'error': str(e)}), 500


@paperless_bp.route('/documents/<int:doc_id>/preview', methods=['GET'])
@login_required
def get_document_preview(doc_id):
    """Get document thumbnail"""
    try:
        client, config = get_paperless_client()
        
        image_content = client.get_document_preview(doc_id)
        
        return send_file(
            BytesIO(image_content),
            mimetype='image/png'
        )
        
    except PaperlessAPIError as e:
        return jsonify({'error': str(e)}), 404
    except Exception as e:
        logger.error(f"Error getting preview: {e}")
        return jsonify({'error': str(e)}), 500


@paperless_bp.route('/documents/upload', methods=['POST'])
@login_required
def upload_document():
    """Upload new document to Paperless"""
    try:
        client, config = get_paperless_client()
        
        if 'file' not in request.files:
            return jsonify({'success': False, 'message': 'No file provided'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'Empty filename'}), 400
        
        # Get metadata from form
        title = request.form.get('title')
        tags = request.form.get('tags')  # Comma-separated tag IDs
        correspondent = request.form.get('correspondent', type=int)
        document_type = request.form.get('document_type', type=int)
        
        # Parse tags
        tag_ids = None
        if tags:
            tag_ids = [int(t) for t in tags.split(',') if t.strip()]
        
        # Upload to Paperless
        result = client.upload_document(
            file_content=file.read(),
            filename=file.filename,
            title=title,
            tags=tag_ids,
            correspondent=correspondent,
            document_type=document_type
        )
        
        return jsonify({'success': True, 'result': result})
        
    except PaperlessAPIError as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        logger.error(f"Error uploading document: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@paperless_bp.route('/documents/<int:doc_id>', methods=['PATCH', 'PUT'])
@login_required
def update_document(doc_id):
    """Update document metadata"""
    try:
        client, config = get_paperless_client()
        
        data = request.json
        
        # Parse tags if provided
        tags = data.get('tags')
        if tags and isinstance(tags, str):
            tags = [int(t) for t in tags.split(',') if t.strip()]
        
        result = client.update_document(
            doc_id=doc_id,
            title=data.get('title'),
            tags=tags,
            correspondent=data.get('correspondent'),
            document_type=data.get('document_type')
        )
        
        # Update cache
        _cache_document(config, result)
        db.session.commit()
        
        return jsonify({'success': True, 'document': result})
        
    except PaperlessAPIError as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        logger.error(f"Error updating document: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


@paperless_bp.route('/documents/<int:doc_id>', methods=['DELETE'])
@login_required
def delete_document(doc_id):
    """Delete document from Paperless"""
    try:
        client, config = get_paperless_client()
        
        # Delete from Paperless
        client.delete_document(doc_id)
        
        # Delete from cache
        cached_doc = PaperlessDocument.query.filter_by(
            config_id=config.id,
            paperless_id=doc_id
        ).first()
        
        if cached_doc:
            db.session.delete(cached_doc)
            db.session.commit()
        
        return jsonify({'success': True})
        
    except PaperlessAPIError as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        logger.error(f"Error deleting document: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# --- Tags ---

@paperless_bp.route('/tags', methods=['GET'])
@login_required
def get_tags():
    """Get all tags"""
    try:
        client, config = get_paperless_client()
        
        tags = client.get_tags()
        
        # Cache tags
        for tag_data in tags:
            _cache_tag(config, tag_data)
        
        db.session.commit()
        
        return jsonify(tags)
        
    except PaperlessAPIError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        logger.error(f"Error getting tags: {e}")
        return jsonify({'error': str(e)}), 500


@paperless_bp.route('/tags', methods=['POST'])
@login_required
def create_tag():
    """Create new tag"""
    try:
        client, config = get_paperless_client()
        
        data = request.json
        if not data.get('name'):
            return jsonify({'success': False, 'message': 'Tag name required'}), 400
        
        tag = client.create_tag(
            name=data['name'],
            color=data.get('color', '#a6cee3')
        )
        
        # Cache tag
        _cache_tag(config, tag)
        db.session.commit()
        
        return jsonify({'success': True, 'tag': tag})
        
    except PaperlessAPIError as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        logger.error(f"Error creating tag: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# --- Correspondents ---

@paperless_bp.route('/correspondents', methods=['GET'])
@login_required
def get_correspondents():
    """Get all correspondents"""
    try:
        client, config = get_paperless_client()
        
        correspondents = client.get_correspondents()
        
        # Cache correspondents
        for corr_data in correspondents:
            _cache_correspondent(config, corr_data)
        
        db.session.commit()
        
        return jsonify(correspondents)
        
    except PaperlessAPIError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        logger.error(f"Error getting correspondents: {e}")
        return jsonify({'error': str(e)}), 500


@paperless_bp.route('/correspondents', methods=['POST'])
@login_required
def create_correspondent():
    """Create new correspondent"""
    try:
        client, config = get_paperless_client()
        
        data = request.json
        if not data.get('name'):
            return jsonify({'success': False, 'message': 'Correspondent name required'}), 400
        
        correspondent = client.create_correspondent(name=data['name'])
        
        # Cache correspondent
        _cache_correspondent(config, correspondent)
        db.session.commit()
        
        return jsonify({'success': True, 'correspondent': correspondent})
        
    except PaperlessAPIError as e:
        return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        logger.error(f"Error creating correspondent: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# --- Document Types ---

@paperless_bp.route('/document-types', methods=['GET'])
@login_required
def get_document_types():
    """Get all document types"""
    try:
        client, config = get_paperless_client()
        
        doc_types = client.get_document_types()
        
        # Cache document types
        for dt_data in doc_types:
            _cache_document_type(config, dt_data)
        
        db.session.commit()
        
        return jsonify(doc_types)
        
    except PaperlessAPIError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        logger.error(f"Error getting document types: {e}")
        return jsonify({'error': str(e)}), 500


# --- Search ---

@paperless_bp.route('/search', methods=['GET'])
@login_required
def search_documents():
    """Search documents"""
    try:
        query = request.args.get('q', '')
        if not query:
            return jsonify({'results': [], 'count': 0})
        
        client, config = get_paperless_client()
        
        page = request.args.get('page', 1, type=int)
        page_size = request.args.get('page_size', 25, type=int)
        
        result = client.search(query, page=page, page_size=page_size)
        
        return jsonify(result)
        
    except PaperlessAPIError as e:
        return jsonify({'error': str(e)}), 500
    except Exception as e:
        logger.error(f"Error searching documents: {e}")
        return jsonify({'error': str(e)}), 500


# --- Sync ---

@paperless_bp.route('/sync', methods=['POST'])
@login_required
def sync_documents():
    """Manually trigger sync from Paperless"""
    try:
        client, config = get_paperless_client()
        
        # Get all documents (paginated)
        page = 1
        total_synced = 0
        
        while True:
            result = client.get_documents(page=page, page_size=100)
            
            for doc_data in result.get('results', []):
                _cache_document(config, doc_data)
                total_synced += 1
            
            # Check if there are more pages
            if not result.get('next'):
                break
            
            page += 1
        
        # Sync tags
        tags = client.get_tags()
        for tag_data in tags:
            _cache_tag(config, tag_data)
        
        # Sync correspondents
        correspondents = client.get_correspondents()
        for corr_data in correspondents:
            _cache_correspondent(config, corr_data)
        
        # Sync document types
        doc_types = client.get_document_types()
        for dt_data in doc_types:
            _cache_document_type(config, dt_data)
        
        # Update last sync time
        config.last_sync_at = datetime.utcnow()
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'documents_synced': total_synced,
            'tags_synced': len(tags),
            'correspondents_synced': len(correspondents),
            'document_types_synced': len(doc_types)
        })
        
    except PaperlessAPIError as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': str(e)}), 500
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error syncing documents: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# --- Helper Functions ---

def _cache_document(config: PaperlessConfig, doc_data: dict):
    """Cache document in database"""
    doc = PaperlessDocument.query.filter_by(
        config_id=config.id,
        paperless_id=doc_data['id']
    ).first()
    
    if not doc:
        doc = PaperlessDocument(config_id=config.id, paperless_id=doc_data['id'])
        db.session.add(doc)
    
    doc.title = doc_data.get('title', '')
    doc.content = doc_data.get('content', '')
    doc.created = datetime.fromisoformat(doc_data['created'].replace('Z', '+00:00'))
    doc.modified = datetime.fromisoformat(doc_data['modified'].replace('Z', '+00:00'))
    doc.added = datetime.fromisoformat(doc_data['added'].replace('Z', '+00:00'))
    doc.original_filename = doc_data.get('original_file_name')
    doc.archived_filename = doc_data.get('archived_file_name')
    doc.mime_type = doc_data.get('mime_type')
    doc.cached_at = datetime.utcnow()
    
    # Handle tags (many-to-many)
    if 'tags' in doc_data:
        doc.tags.clear()
        for tag_id in doc_data['tags']:
            tag = PaperlessTag.query.filter_by(
                config_id=config.id,
                paperless_id=tag_id
            ).first()
            if tag:
                doc.tags.append(tag)


def _cache_tag(config: PaperlessConfig, tag_data: dict):
    """Cache tag in database"""
    tag = PaperlessTag.query.filter_by(
        config_id=config.id,
        paperless_id=tag_data['id']
    ).first()
    
    if not tag:
        tag = PaperlessTag(config_id=config.id, paperless_id=tag_data['id'])
        db.session.add(tag)
    
    tag.name = tag_data['name']
    tag.color = tag_data.get('color', '#a6cee3')
    tag.is_inbox_tag = tag_data.get('is_inbox_tag', False)
    tag.cached_at = datetime.utcnow()


def _cache_correspondent(config: PaperlessConfig, corr_data: dict):
    """Cache correspondent in database"""
    corr = PaperlessCorrespondent.query.filter_by(
        config_id=config.id,
        paperless_id=corr_data['id']
    ).first()
    
    if not corr:
        corr = PaperlessCorrespondent(config_id=config.id, paperless_id=corr_data['id'])
        db.session.add(corr)
    
    corr.name = corr_data['name']
    corr.cached_at = datetime.utcnow()


def _cache_document_type(config: PaperlessConfig, dt_data: dict):
    """Cache document type in database"""
    dt = PaperlessDocumentType.query.filter_by(
        config_id=config.id,
        paperless_id=dt_data['id']
    ).first()
    
    if not dt:
        dt = PaperlessDocumentType(config_id=config.id, paperless_id=dt_data['id'])
        db.session.add(dt)
    
    dt.name = dt_data['name']
    dt.cached_at = datetime.utcnow()
