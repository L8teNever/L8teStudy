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
    
    def list_items(self, parent_id='root', page_size=100, page_token=None):
        """List both folders and files in a parent directory"""
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
            
            return results.get('files', []), results.get('nextPageToken')
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
            
            return results.get('files', [])
        except HttpError as error:
            current_app.logger.error(f"Drive API error: {error}")
            return None
    
    def get_file_metadata(self, file_id):
        """Get metadata for a specific file"""
        service = self.get_service()
        if not service:
            return None
        
        try:
            file = service.files().get(
                fileId=file_id,
                fields="id, name, mimeType, size, modifiedTime, webViewLink, parents, thumbnailLink, iconLink, description"
            ).execute()
            
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
        """Download file content or export Google Doc as PDF"""
        service = self.get_service()
        if not service:
            return None
        
        try:
            # If no mime_type provided, fetch metadata first
            if not mime_type:
                meta = self.get_file_metadata(file_id)
                if not meta:
                    return None
                mime_type = meta.get('mimeType')

            # Handle Google Apps files (export to PDF)
            if mime_type.startswith('application/vnd.google-apps.'):
                return service.files().export(
                    fileId=file_id,
                    mimeType='application/pdf'
                ).execute()
            else:
                # Handle regular files (download as media)
                return service.files().get_media(
                    fileId=file_id
                ).execute()
        except HttpError as error:
            current_app.logger.error(f"Drive download error: {error}")
            return None
