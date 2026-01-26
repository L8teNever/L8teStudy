"""
Google Drive OAuth Routes
Handles OAuth flow and Drive file management
"""
from flask import Blueprint, request, jsonify, redirect, url_for, session, current_app
from flask_login import login_required, current_user
from .models import DriveFolder, DriveOAuthToken, Subject, db
from .drive_oauth_client import DriveOAuthClient
from datetime import datetime

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
    
    folders = client.list_folders(parent_id)
    
    if folders is None:
        return jsonify({'success': False, 'message': 'Failed to fetch folders'}), 500
    
    return jsonify({
        'success': True,
        'folders': folders
    })

@drive_bp.route('/folders', methods=['GET'])
@login_required
def get_selected_folders():
    """Get admin-selected folders"""
    folders = DriveFolder.query.filter_by(is_active=True).all()
    
    return jsonify([{
        'id': f.id,
        'drive_folder_id': f.drive_folder_id,
        'folder_name': f.folder_name,
        'folder_path': f.folder_path,
        'subject_id': f.subject_id,
        'include_subfolders': f.include_subfolders,
        'created_at': f.created_at.isoformat() if f.created_at else None
    } for f in folders])

@drive_bp.route('/folders', methods=['POST'])
@login_required
def add_folder():
    """Add a folder to display (admin only)"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    data = request.json
    drive_folder_id = data.get('drive_folder_id')
    folder_name = data.get('folder_name')
    
    if not drive_folder_id or not folder_name:
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    
    # Check if folder already exists
    existing = DriveFolder.query.filter_by(drive_folder_id=drive_folder_id).first()
    if existing:
        return jsonify({'success': False, 'message': 'Folder already added'}), 400
    
    # Get folder path
    client = DriveOAuthClient()
    folder_path = client.get_folder_path(drive_folder_id)
    
    folder = DriveFolder(
        drive_folder_id=drive_folder_id,
        folder_name=folder_name,
        folder_path=folder_path,
        subject_id=data.get('subject_id'),
        include_subfolders=data.get('include_subfolders', True),
        created_by_user_id=current_user.id
    )
    
    db.session.add(folder)
    db.session.commit()
    
    return jsonify({
        'success': True,
        'folder': {
            'id': folder.id,
            'drive_folder_id': folder.drive_folder_id,
            'folder_name': folder.folder_name,
            'folder_path': folder.folder_path
        }
    })

@drive_bp.route('/folders/<int:folder_id>', methods=['DELETE'])
@login_required
def remove_folder(folder_id):
    """Remove a folder from display (admin only)"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    folder = DriveFolder.query.get_or_404(folder_id)
    db.session.delete(folder)
    db.session.commit()
    
    return jsonify({'success': True})

@drive_bp.route('/folders/<int:folder_id>', methods=['PUT'])
@login_required
def update_folder(folder_id):
    """Update folder settings (admin only)"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    folder = DriveFolder.query.get_or_404(folder_id)
    data = request.json
    
    if 'subject_id' in data:
        folder.subject_id = data['subject_id']
    if 'include_subfolders' in data:
        folder.include_subfolders = data['include_subfolders']
    if 'is_active' in data:
        folder.is_active = data['is_active']
    
    db.session.commit()
    
    return jsonify({'success': True})

@drive_bp.route('/files', methods=['GET'])
@login_required
def get_files():
    """Get ALL files from the authenticated Google Drive account"""
    client = DriveOAuthClient()
    if not client.is_authenticated():
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    page_token = request.args.get('pageToken')
    
    # Get all files from entire Drive (not just specific folders)
    files, next_page_token = client.list_all_files(page_token=page_token)
    
    if files is None:
        return jsonify({'success': False, 'message': 'Failed to fetch files'}), 500
    
    return jsonify({
        'success': True,
        'files': files,
        'nextPageToken': next_page_token
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
