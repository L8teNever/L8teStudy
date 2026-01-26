"""
Google Drive OAuth 2.0 Client
Handles authentication and API calls to Google Drive using OAuth tokens
"""
import os
import json
from datetime import datetime, timedelta
from flask import current_app, url_for
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from .models import DriveOAuthToken, db

# OAuth 2.0 Scopes
SCOPES = [
    'https://www.googleapis.com/auth/drive.readonly',
    'https://www.googleapis.com/auth/drive.metadata.readonly'
]

# Simple Server-Side RAM Cache (Global within worker)
# Format: { cache_key: (timestamp, data) }
_DRIVE_RAM_CACHE = {}
_CACHE_TTL = 86400 # 24 hours (for listings)
_DRIVE_CONTENT_CACHE = {} # { file_id: (modifiedTime, checksum, bytes) }

class DriveOAuthClient:
    """Client for Google Drive API using OAuth 2.0"""
    
    def __init__(self):
        self.client_id = os.environ.get('GOOGLE_CLIENT_ID')
        self.client_secret = os.environ.get('GOOGLE_CLIENT_SECRET')
        
    def get_authorization_url(self, redirect_uri):
        """Generate OAuth authorization URL"""
        client_config = {
            "web": {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri]
            }
        }
        
        flow = Flow.from_client_config(
            client_config,
            scopes=SCOPES,
            redirect_uri=redirect_uri
        )
        
        authorization_url, state = flow.authorization_url(
            access_type='offline',
            include_granted_scopes='true',
            prompt='consent'  # Force consent to get refresh token
        )
        
        return authorization_url, state
    
    def exchange_code_for_tokens(self, code, redirect_uri):
        """Exchange authorization code for access and refresh tokens"""
        client_config = {
            "web": {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri]
            }
        }
        
        flow = Flow.from_client_config(
            client_config,
            scopes=SCOPES,
            redirect_uri=redirect_uri
        )
        
        flow.fetch_token(code=code)
        credentials = flow.credentials
        
        # Store tokens in database
        token = DriveOAuthToken.query.filter_by(is_active=True).first()
        if not token:
            token = DriveOAuthToken()
            db.session.add(token)
        
        token.set_access_token(credentials.token)
        if credentials.refresh_token:
            token.set_refresh_token(credentials.refresh_token)
        
        if credentials.expiry:
            token.token_expiry = credentials.expiry
        
        token.is_active = True
        token.updated_at = datetime.utcnow()
        db.session.commit()
        
        return token
    
    def get_credentials(self):
        """Get valid credentials, refreshing if necessary"""
        token = DriveOAuthToken.query.filter_by(is_active=True).first()
        
        # Check environment variable fallback
        env_refresh_token = os.environ.get('GOOGLE_REFRESH_TOKEN')
        
        if not token and not env_refresh_token:
            return None
        
        if token:
            credentials = Credentials(
                token=token.get_access_token(),
                refresh_token=token.get_refresh_token(),
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.client_id,
                client_secret=self.client_secret,
                scopes=SCOPES
            )
            
            # Check if token is expired and refresh if needed
            if token.token_expiry and token.token_expiry < datetime.utcnow():
                from google.auth.transport.requests import Request
                try:
                    credentials.refresh(Request())
                    
                    # Update stored tokens
                    token.set_access_token(credentials.token)
                    if credentials.expiry:
                        token.token_expiry = credentials.expiry
                    token.updated_at = datetime.utcnow()
                    db.session.commit()
                except Exception as e:
                    current_app.logger.error(f"Failed to refresh DB token: {e}")
                    # If DB token refresh fails, try env fallback if available
                    if not env_refresh_token:
                        return None
        
        # If no DB token or refresh failed, try ENV token
        if not token and env_refresh_token:
            credentials = Credentials(
                token=None,
                refresh_token=env_refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=self.client_id,
                client_secret=self.client_secret,
                scopes=SCOPES
            )
            # It will refresh automatically on first use of the service
            
        return credentials
    
    def get_service(self):
        """Get authenticated Drive service (Service Account or OAuth)"""
        # 1. Try Service Account (Priority)
        service_account_info = current_app.config.get('GOOGLE_SERVICE_ACCOUNT_INFO')
        if service_account_info and isinstance(service_account_info, str):
            # Check if it's a placeholder or empty
            clean_info = service_account_info.strip()
            if clean_info and not clean_info.startswith('${') and clean_info.lower() != 'none':
                try:
                    from google.oauth2 import service_account
                    import json
                    info = json.loads(clean_info)
                    credentials = service_account.Credentials.from_service_account_info(
                        info, scopes=SCOPES
                    )
                    return build('drive', 'v3', credentials=credentials)
                except Exception as e:
                    current_app.logger.warning(f"Note: Service Account loading failed (normal if not using SA): {e}")
        elif service_account_info and isinstance(service_account_info, dict):
            try:
                from google.oauth2 import service_account
                credentials = service_account.Credentials.from_service_account_info(
                    service_account_info, scopes=SCOPES
                )
                return build('drive', 'v3', credentials=credentials)
            except Exception as e:
                current_app.logger.warning(f"Note: Service Account (dict) loading failed: {e}")

        # 2. Fallback to OAuth credentials
        credentials = self.get_credentials()
        if not credentials:
            return None
        
        return build('drive', 'v3', credentials=credentials)
    
    def _get_cache(self, key):
        """Internal helper to get item from RAM cache"""
        if key in _DRIVE_RAM_CACHE:
            timestamp, data = _DRIVE_RAM_CACHE[key]
            if (datetime.utcnow() - timestamp).total_seconds() < _CACHE_TTL:
                return data
            else:
                del _DRIVE_RAM_CACHE[key]
        return None

    def _set_cache(self, key, data):
        """Internal helper to set item in RAM cache"""
        _DRIVE_RAM_CACHE[key] = (datetime.utcnow(), data)
        # Prevent memory leaks: allowed up to 10k items for large RAM usage
        if len(_DRIVE_RAM_CACHE) > 10000:
            # Pop oldest (first entry)
            first_key = next(iter(_DRIVE_RAM_CACHE))
            del _DRIVE_RAM_CACHE[first_key]

    def list_items(self, parent_id='root', page_size=100, page_token=None):
        """List both folders and files in a parent directory"""
        # Cache key includes parent_id and token hash (to separate users)
        creds = self.get_credentials()
        creds_hash = hash(creds.token) if creds and creds.token else "no_auth"
        cache_key = f"list_{parent_id}_{page_token}_{creds_hash}"
        
        cached = self._get_cache(cache_key)
        if cached:
            return cached[0], cached[1]

        service = self.get_service()
        if not service:
            return None, None
        
        try:
            if parent_id == 'root':
                # Show items in root AND items shared with the account
                query = "('root' in parents or sharedWithMe = true) and trashed=false"
            else:
                query = f"'{parent_id}' in parents and trashed=false"
            
            results = service.files().list(
                q=query,
                pageSize=page_size,
                pageToken=page_token,
                fields="nextPageToken, files(id, name, mimeType, size, modifiedTime, webViewLink, parents, thumbnailLink, iconLink, owners)",
                orderBy="folder, name"
            ).execute()
            
            items = results.get('files', [])
            next_token = results.get('nextPageToken')
            
            self._set_cache(cache_key, (items, next_token))
            return items, next_token
        except HttpError as error:
            current_app.logger.error(f"Drive API error: {error}")
            return None, None
    
    def list_files_in_folder(self, folder_id, page_size=100, page_token=None, include_subfolders=True):
        """List all files in a folder (and optionally subfolders)"""
        service = self.get_service()
        if not service:
            return None, None
        
        try:
            if include_subfolders:
                # Search in folder and all subfolders
                query = f"'{folder_id}' in parents and trashed=false"
            else:
                # Only direct children
                query = f"'{folder_id}' in parents and mimeType!='application/vnd.google-apps.folder' and trashed=false"
            
            results = service.files().list(
                q=query,
                pageSize=page_size,
                pageToken=page_token,
                fields="nextPageToken, files(id, name, mimeType, size, modifiedTime, webViewLink, parents, thumbnailLink, iconLink)",
                orderBy="modifiedTime desc"
            ).execute()
            
            return results.get('files', []), results.get('nextPageToken')
        except HttpError as error:
            current_app.logger.error(f"Drive API error: {error}")
            return None, None
    
    def list_all_files(self, page_size=100, page_token=None):
        """List ALL files from the entire Drive (excluding folders and trashed files)"""
        service = self.get_service()
        if not service:
            return None, None
        
        try:
            # Query: All files that are not folders and not trashed
            query = "mimeType!='application/vnd.google-apps.folder' and trashed=false"
            
            results = service.files().list(
                q=query,
                pageSize=page_size,
                pageToken=page_token,
                fields="nextPageToken, files(id, name, mimeType, size, modifiedTime, webViewLink, parents, thumbnailLink, iconLink, owners)",
                orderBy="modifiedTime desc"
            ).execute()
            
            return results.get('files', []), results.get('nextPageToken')
        except HttpError as error:
            current_app.logger.error(f"Drive API error: {error}")
            return None, None
    
    def search_files(self, query_text, folder_ids=None, page_size=50):
        """Search files by name or content"""
        creds = self.get_credentials()
        creds_hash = hash(creds.token) if creds and creds.token else "no_auth"
        cache_key = f"search_{query_text}_{folder_ids}_{creds_hash}"
        
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        service = self.get_service()
        if not service:
            return None
        
        try:
            # Build search query
            query_parts = []
            
            # Search in name and full text
            query_parts.append(f"(name contains '{query_text}' or fullText contains '{query_text}')")
            
            # Limit to specific folders if provided
            if folder_ids:
                folder_conditions = " or ".join([f"'{fid}' in parents" for fid in folder_ids])
                query_parts.append(f"({folder_conditions})")
            
            # Exclude trashed files
            query_parts.append("trashed=false")
            
            query = " and ".join(query_parts)
            
            results = service.files().list(
                q=query,
                pageSize=page_size,
                fields="files(id, name, mimeType, size, modifiedTime, webViewLink, parents, thumbnailLink, iconLink, owners)",
                orderBy="modifiedTime desc"
            ).execute()
            
            items = results.get('files', [])
            self._set_cache(cache_key, items)
            return items
        except HttpError as error:
            current_app.logger.error(f"Drive API error: {error}")
            return None
    
    def get_file_metadata(self, file_id):
        """Get metadata for a specific file"""
        cache_key = f"meta_{file_id}"
        cached = self._get_cache(cache_key)
        if cached:
            return cached

        service = self.get_service()
        if not service:
            return None
        
        try:
            file = service.files().get(
                fileId=file_id,
                fields="id, name, mimeType, size, modifiedTime, webViewLink, parents, thumbnailLink, iconLink, description"
            ).execute()
            
            self._set_cache(cache_key, file)
            return file
        except HttpError as error:
            current_app.logger.error(f"Drive API error: {error}")
            return None
    
    def get_folder_path(self, folder_id):
        """Get full path of a folder"""
        service = self.get_service()
        if not service:
            return None
        
        path_parts = []
        current_id = folder_id
        
        try:
            while current_id and current_id != 'root':
                file = service.files().get(
                    fileId=current_id,
                    fields="id, name, parents"
                ).execute()
                
                path_parts.insert(0, file.get('name'))
                parents = file.get('parents', [])
                current_id = parents[0] if parents else None
            
            return '/' + '/'.join(path_parts) if path_parts else '/'
        except HttpError as error:
            current_app.logger.error(f"Drive API error: {error}")
            return None
    
    def is_authenticated(self):
        """Check if we have valid credentials (SA or OAuth)"""
        # Service Account is considered "always authenticated" if config exists and is valid
        sa_info = current_app.config.get('GOOGLE_SERVICE_ACCOUNT_INFO')
        if sa_info:
            if isinstance(sa_info, dict):
                return True
            if isinstance(sa_info, str):
                clean_info = sa_info.strip()
                if clean_info and not clean_info.startswith('${') and clean_info.lower() != 'none':
                    return True
        
        return self.get_credentials() is not None

    def download_file(self, file_id, mime_type=None):
        """Download file content or export Google Doc as PDF with RAM Caching and Validation"""
        service = self.get_service()
        if not service:
            return None
        
        try:
            # 1. Fetch current minimal metadata for validation (Always-Validate)
            # This is 1 small API call, much faster than a full download/export.
            current_meta = service.files().get(
                fileId=file_id,
                fields="id, modifiedTime, md5Checksum, mimeType"
            ).execute()
            
            m_time = current_meta.get('modifiedTime')
            checksum = current_meta.get('md5Checksum', '')
            mime_type = current_meta.get('mimeType')
            
            # 2. Check Content Cache
            cache_key = f"content_{file_id}"
            if cache_key in _DRIVE_CONTENT_CACHE:
                cached_mtime, cached_checksum, cached_data = _DRIVE_CONTENT_CACHE[cache_key]
                # Compare modified time and checksum (checksum is empty for Google Apps files)
                if cached_mtime == m_time and (not checksum or cached_checksum == checksum):
                    current_app.logger.info(f"Serving file from RAM cache: {file_id}")
                    return cached_data

            # 3. If not in cache or changed, Download/Export
            current_app.logger.info(f"Downloading/Exporting file (not in cache or outdated): {file_id}")
            if mime_type.startswith('application/vnd.google-apps.'):
                content = service.files().export(
                    fileId=file_id,
                    mimeType='application/pdf'
                ).execute()
            else:
                content = service.files().get_media(
                    fileId=file_id
                ).execute()

            # 4. Update Cache
            _DRIVE_CONTENT_CACHE[cache_key] = (m_time, checksum, content)
            
            # Simple LRU-ish: Limit to 500 files or ~4-6 GB (assuming avg file size)
            if len(_DRIVE_CONTENT_CACHE) > 500:
                # Remove oldest entry
                _DRIVE_CONTENT_CACHE.pop(next(iter(_DRIVE_CONTENT_CACHE)))
                
            return content
            
        except HttpError as error:
            current_app.logger.error(f"Drive download error: {error}")
            return None

    def warmup_cache(self, depth=10):
        """Warmup the RAM cache by pre-crawling the Drive structure (deeper)"""
        try:
            current_app.logger.info(f"Starting deep Drive RAM Warmup (Depth: {depth})...")
            self._warmup_recursive('root', depth)
            current_app.logger.info("Deep Drive RAM Warmup completed.")
        except Exception as e:
            current_app.logger.error(f"Cache Warmup failed: {e}")

    def get_cache_stats(self):
        """Calculate RAM usage of the caches"""
        import sys
        
        # 1. Content Cache (File Bytes)
        content_count = len(_DRIVE_CONTENT_CACHE)
        content_bytes = sum(len(data[2]) for data in _DRIVE_CONTENT_CACHE.values())
        
        # 2. Metadata Cache (Listings)
        listing_count = len(_DRIVE_RAM_CACHE)
        # Estimate size of listings (rough estimate as sys.getsizeof isn't recursive)
        listing_bytes = sum(sys.getsizeof(data[1]) for data in _DRIVE_RAM_CACHE.values())
        
        return {
            'content_count': content_count,
            'content_size_mb': round(content_bytes / (1024 * 1024), 2),
            'metadata_count': listing_count,
            'metadata_size_mb': round(listing_bytes / (1024 * 1024), 2),
            'total_size_mb': round((content_bytes + listing_bytes) / (1024 * 1024), 2),
            'limit_mb': 8192
        }

    def _warmup_recursive(self, parent_id, remaining_depth):
        if remaining_depth < 0:
            return
            
        # 1. List items (will automatically cache)
        items, _ = self.list_items(parent_id)
        if items is None:
            current_app.logger.warning(f"Warmup: Failed to list items for {parent_id} (Auth error or folder inaccessible)")
            return
            
        if not items:
            current_app.logger.info(f"Warmup: Folder {parent_id} is empty.")
            return
            
        current_app.logger.info(f"Warmup: Cached {len(items)} items for {parent_id}")
            
        # 2. Recurse into folders
        if remaining_depth > 0:
            for item in items:
                if item['mimeType'] == 'application/vnd.google-apps.folder':
                    self._warmup_recursive(item['id'], remaining_depth - 1)
