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

def verify_drive_access(folder_or_file_id):
    """
    Verify if the current user has access to a specific Drive item.
    Access is granted if:
    1. User is an admin (access to all linked folders in class)
    2. Item is one of the folders linked to the user's class
    3. Item is a child (at any depth) of a folder linked to the user's class
    """
    if current_user.is_super_admin:
        return True
        
    from .models import DriveFolder
    # Get all folders linked to this user's class
    authorized_roots = DriveFolder.query.filter_by(class_id=current_user.class_id).all()
    if not authorized_roots:
        return False
        
    root_ids = {f.folder_id for f in authorized_roots}
    
    if folder_or_file_id in root_ids:
        return True
        
    # Check lineage via API
    client = DriveOAuthClient()
    current_id = folder_or_file_id
    
    # We allow a max depth to prevent infinite loops or huge API usage
    # Usually class structures aren't 20 levels deep.
    max_depth = 10
    
    visited = {current_id}
    
    while current_id and max_depth > 0:
        meta = client.get_file_metadata(current_id)
        if not meta:
            return False
            
        parents = meta.get('parents', [])
        if not parents:
            break
            
        # Check if any parent is an authorized root
        for p_id in parents:
            if p_id in root_ids:
                return True
            if p_id not in visited:
                current_id = p_id
                visited.add(p_id)
                break
        else:
            # If no new parents to visit
            break
            
        max_depth -= 1
        
    return False

@drive_bp.route('/cache-stats', methods=['GET'])
@login_required
def get_cache_stats():
    """Get RAM cache statistics for admin"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
    client = DriveOAuthClient()
    stats = client.get_cache_stats()
    return jsonify({
        'success': True,
        'stats': stats
    })

@drive_bp.route('/warmup', methods=['POST'])
@login_required
def run_warmup():
    """Manually trigger Drive cache warmup"""
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    client = DriveOAuthClient()
    if not client.is_authenticated():
        return jsonify({'success': False, 'message': 'Drive not authenticated'}), 401
    
    # Run warmup (async-like behavior by not waiting for full depth if it's too much? 
    # No, we'll just run it, maybe with smaller depth for manual trigger if needed)
    try:
        # We use a slightly smaller depth for manual trigger to avoid timeout, 
        # but 3 is usually fast enough for a چند hundred folders.
        client.warmup_cache(depth=3)
        return jsonify({'success': True, 'message': 'Warmup initiated successfully'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500

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
        'items': folders,
        'folders': folders
    })

@drive_bp.route('/folders', methods=['GET'])
@login_required
def get_linked_folders():
    """Get all linked Drive folders for the current class/user"""
    from .models import DriveFolder
    
    admin_view = request.args.get('admin_view', 'false').lower() == 'true'
    
    query = DriveFolder.query
    if current_user.is_admin and admin_view:
        # Admin sees all folders in their class (or all if super admin)
        if not current_user.is_super_admin:
            query = query.filter_by(class_id=current_user.class_id)
    else:
        # regular user only sees their own or public ones? 
        # For now, let's keep it simple: folders they own
        query = query.filter_by(user_id=current_user.id)
        
    folders = query.all()
    
    return jsonify([{
        'id': f.id,
        'folder_id': f.folder_id,
        'folder_name': f.folder_name,
        'user_id': f.user_id,
        'owner_name': f.user.username if f.user else 'Unknown',
        'file_count': f.file_count,
        'last_sync_at': f.last_sync_at.strftime('%Y-%m-%d %H:%M') if f.last_sync_at else None,
        'subject_id': f.subject_id,
        'subject_name': f.subject_rel.name if f.subject_rel else None
    } for f in folders])

@drive_bp.route('/folders', methods=['POST'])
@login_required
def add_linked_folder():
    """Link a new Google Drive folder"""
    from .models import DriveFolder, SchoolClass
    data = request.get_json()
    if not data or 'folder_id' not in data:
        return jsonify({'success': False, 'message': 'Folder ID required'}), 400
        
    folder_id = data.get('folder_id')
    folder_name = data.get('folder_name', 'New Folder')
    subject_id = data.get('subject_id')
    
    # Check if already exists
    existing = DriveFolder.query.filter_by(folder_id=folder_id, class_id=current_user.class_id).first()
    if existing:
        return jsonify({'success': False, 'message': 'Folder already linked'}), 400
        
    new_folder = DriveFolder(
        folder_id=folder_id,
        folder_name=folder_name,
        user_id=current_user.id,
        class_id=current_user.class_id,
        subject_id=subject_id,
        created_by_user_id=current_user.id
    )
    
    db.session.add(new_folder)
    db.session.commit()
    
    return jsonify({'success': True, 'folder': {'id': new_folder.id, 'name': new_folder.folder_name}})

@drive_bp.route('/folders/<int:id>', methods=['DELETE'])
@login_required
def delete_linked_folder(id):
    """Delete a linked folder"""
    from .models import DriveFolder
    folder = DriveFolder.query.get_or_404(id)
    
    if folder.user_id != current_user.id and not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
    db.session.delete(folder)
    db.session.commit()
    return jsonify({'success': True})

@drive_bp.route('/admin/users', methods=['GET'])
@login_required
def get_admin_users():
    """Get list of users for owner assignment (admin only)"""
    if not current_user.is_admin:
        return jsonify([]), 403
    from .models import User
    users = User.query.filter_by(class_id=current_user.class_id).all()
    return jsonify([{'id': u.id, 'username': u.username} for u in users])

@drive_bp.route('/folders/<int:id>', methods=['PATCH'])
@login_required
def update_linked_folder(id):
    """Update folder properties (e.g. owner)"""
    from .models import DriveFolder
    folder = DriveFolder.query.get_or_404(id)
    
    if not current_user.is_admin:
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
        
    data = request.get_json()
    if 'user_id' in data:
        folder.user_id = data['user_id']
        
    db.session.commit()
    return jsonify({'success': True})

@drive_bp.route('/files', methods=['GET'])
@login_required
def get_files():
    """Get files and folders from the authenticated Google Drive account"""
    client = DriveOAuthClient()
    if not client.is_authenticated():
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    parent_id = request.args.get('parent_id', 'root')
    page_token = request.args.get('pageToken')

    # Security Check: Non-admins cannot browse 'root'
    if not current_user.is_admin and parent_id == 'root':
        return jsonify({'success': False, 'message': 'Access denied'}), 403
    
    # Access Verification
    if not current_user.is_admin and not verify_drive_access(parent_id):
        return jsonify({'success': False, 'message': 'Access denied: Folder not linked to class'}), 403

    # Get items in parent (or root)
    items, next_page_token = client.list_items(parent_id=parent_id, page_token=page_token)
    
    if items is None:
        return jsonify({'success': False, 'message': 'Google Drive not connected or inaccessible'}), 401
    
    return jsonify({
        'success': True,
        'items': items,
        'files': items, # Keep key name 'files' for frontend compatibility
        'nextPageToken': next_page_token,
        'totalFiles': len(items)
    })

@drive_bp.route('/search', methods=['GET'])
@login_required
def search_files():
    """Search files in Drive (scoped to linked folders for non-admins)"""
    query = request.args.get('q', '')
    
    if not query:
        return jsonify({'success': False, 'message': 'Query required'}), 400
    
    client = DriveOAuthClient()
    if not client.is_authenticated():
        return jsonify({'success': False, 'message': 'Not authenticated'}), 401
    
    folder_ids = None
    if not current_user.is_admin:
        # Get all linked folders for this user
        from .models import DriveFolder
        # Users see folders for their class
        linked = DriveFolder.query.filter_by(class_id=current_user.class_id).all()
        # And potentially their own personal folders if we support that later (user_id=current_user.id)
        # Combine
        linked_personal = DriveFolder.query.filter_by(user_id=current_user.id).all()
        
        all_linked = set(linked + linked_personal)
        if not all_linked:
            return jsonify({'success': True, 'files': []}) # No folders, no results
            
        folder_ids = [f.folder_id for f in all_linked]

    # Search
    files = client.search_files(query, folder_ids=folder_ids)
    
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
    if not current_user.is_admin and not verify_drive_access(file_id):
        return jsonify({'success': False, 'message': 'Access denied'}), 403

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
    if not current_user.is_admin and not verify_drive_access(file_id):
        return jsonify({'success': False, 'message': 'Access denied'}), 403

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
