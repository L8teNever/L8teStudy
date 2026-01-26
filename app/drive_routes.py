"""
Google Drive OAuth Routes
Handles OAuth flow and Drive file management
"""
from flask import Blueprint, request, jsonify, redirect, url_for, session, current_app, send_file
from flask_login import login_required, current_user
from .models import DriveOAuthToken, db
from .drive_oauth_client import DriveOAuthClient
from datetime import datetime
from io import BytesIO

drive_bp = Blueprint('drive', __name__, url_prefix='/api/drive')

@drive_bp.route('/auth/status', methods=['GET'])
@login_required
def auth_status():
    """Check if Drive is authenticated (all users)"""
    client = DriveOAuthClient()
    is_authenticated = client.is_authenticated()
    
    # Check if specifically Service Account is used
    sa_info = current_app.config.get('GOOGLE_SERVICE_ACCOUNT_INFO')
    is_sa = False
    if sa_info:
        if isinstance(sa_info, dict):
            is_sa = True
        elif isinstance(sa_info, str):
            clean_info = sa_info.strip()
            is_sa = clean_info and not clean_info.startswith('${') and clean_info.lower() != 'none'
    
    return jsonify({
        'authenticated': is_authenticated,
        'method': 'service_account' if is_sa else 'oauth'
    })

@drive_bp.route('/auth/start', methods=['GET'])
@login_required
def start_auth():
    """Start OAuth flow"""
    if not current_user.is_super_admin:
        return jsonify({'success': False, 'message': 'Only super admins can authenticate'}), 403
    
    client = DriveOAuthClient()
    redirect_uri = url_for('drive.oauth_callback', _external=True)
    
    authorization_url, state = client.get_authorization_url(redirect_uri)
    
    # Store state in session for verification
    session['oauth_state'] = state
    
    return jsonify({
        'authorization_url': authorization_url
    })

@drive_bp.route('/auth/callback', methods=['GET'])
def oauth_callback():
    """OAuth callback handler"""
    # Verify state
    state = request.args.get('state')
    if state != session.get('oauth_state'):
        return "Invalid state parameter", 400
    
    code = request.args.get('code')
    if not code:
        return "No authorization code received", 400
    
    client = DriveOAuthClient()
    redirect_uri = url_for('drive.oauth_callback', _external=True)
    
    try:
        client.exchange_code_for_tokens(code, redirect_uri)
        return redirect('/?drive_auth=success')
    except Exception as e:
        current_app.logger.error(f"OAuth error: {e}")
        return redirect('/?drive_auth=error')

@drive_bp.route('/auth/revoke', methods=['POST'])
@login_required
def revoke_auth():
    """Revoke OAuth tokens"""
    if not current_user.is_super_admin:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    # Delete all tokens
    DriveOAuthToken.query.delete()
    db.session.commit()
    
    return jsonify({'success': True})

@drive_bp.route('/browse', methods=['GET'])
@login_required
def browse_folders():
    """Browse Drive folders (for admin folder selection)"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    parent_id = request.args.get('parent_id', 'root')
    
    client = DriveOAuthClient()
    if not client.is_authenticated():
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    # We use list_items now, but filter for folders if needed, 
    # though usually browse is for picking folders anyway.
    items, _ = client.list_items(parent_id)
    
    if items is None:
        return jsonify({'success': False, 'message': 'Failed to fetch folders'}), 500
    
    # Filter for folders only for the picker
    folders = [i for i in items if i['mimeType'] == 'application/vnd.google-apps.folder']
    
    return jsonify({
        'success': True,
        'folders': folders
    })

@drive_bp.route('/files', methods=['GET'])
@login_required
def get_files():
    """Get files and folders from the authenticated Google Drive account"""
    client = DriveOAuthClient()
    if not client.is_authenticated():
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    parent_id = request.args.get('parent_id', 'root')
    page_token = request.args.get('pageToken')
    
    # Get items in parent (or root)
    items, next_page_token = client.list_items(parent_id=parent_id, page_token=page_token)
    
    if items is None:
        return jsonify({'success': False, 'message': 'Failed to fetch items'}), 500
    
    return jsonify({
        'success': True,
        'files': items, # Keep key name 'files' for frontend compatibility
        'nextPageToken': next_page_token,
        'parent_id': parent_id
    })

@drive_bp.route('/search', methods=['GET'])
@login_required
def search_files():
    """Search ALL files in the entire Drive"""
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({'success': False, 'message': 'Query required'}), 400
    
    client = DriveOAuthClient()
    if not client.is_authenticated():
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    # Search in entire Drive (no folder restrictions)
    files = client.search_files(query, folder_ids=None)
    
    if files is None:
        return jsonify({'success': False, 'message': 'Search failed'}), 500
    
    return jsonify({
        'success': True,
        'files': files
    })

@drive_bp.route('/file/<file_id>', methods=['GET'])
@login_required
def get_file_metadata(file_id):
    """Get metadata for a specific file"""
    client = DriveOAuthClient()
    if not client.is_authenticated():
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    file = client.get_file_metadata(file_id)
    
    if file is None:
        return jsonify({'success': False, 'message': 'File not found'}), 404
    
    return jsonify({
        'success': True,
        'file': file
    })

@drive_bp.route('/file/<file_id>/download', methods=['GET'])
@login_required
def download_file(file_id):
    """Download or view a file from Google Drive as PDF"""
    client = DriveOAuthClient()
    if not client.is_authenticated():
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    # Get metadata to know the filename and mime type
    meta = client.get_file_metadata(file_id)
    if not meta:
        return jsonify({'success': False, 'message': 'File not found'}), 404
    
    mime_type = meta.get('mimeType')
    filename = meta.get('name')
    
    # Download/Export
    content = client.download_file(file_id, mime_type)
    if not content:
        return jsonify({'success': False, 'message': 'Download failed'}), 500
    
    # If it was a Google Doc, we exported it as PDF
    if mime_type.startswith('application/vnd.google-apps.'):
        mime_type = 'application/pdf'
        if not filename.endswith('.pdf'):
            filename += '.pdf'
    
    inline = request.args.get('inline', 'true').lower() == 'true'
    
    return send_file(
        BytesIO(content),
        mimetype=mime_type,
        as_attachment=not inline,
        download_name=filename
    )
