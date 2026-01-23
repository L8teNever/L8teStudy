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
        
        if not token:
            return None
        
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
            credentials.refresh(Request())
            
            # Update stored tokens
            token.set_access_token(credentials.token)
            if credentials.expiry:
                token.token_expiry = credentials.expiry
            token.updated_at = datetime.utcnow()
            db.session.commit()
        
        return credentials
    
    def get_service(self):
        """Get authenticated Drive service"""
        credentials = self.get_credentials()
        if not credentials:
            return None
        
        return build('drive', 'v3', credentials=credentials)
    
    def list_folders(self, parent_id='root', page_size=100):
        """List folders in Drive"""
        service = self.get_service()
        if not service:
            return None
        
        try:
            query = f"'{parent_id}' in parents and mimeType='application/vnd.google-apps.folder' and trashed=false"
            results = service.files().list(
                q=query,
                pageSize=page_size,
                fields="files(id, name, parents, webViewLink, modifiedTime)"
            ).execute()
            
            return results.get('files', [])
        except HttpError as error:
            current_app.logger.error(f"Drive API error: {error}")
            return None
    
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
                fields="files(id, name, mimeType, size, modifiedTime, webViewLink, parents, thumbnailLink, iconLink)",
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
        """Check if we have valid OAuth credentials"""
        return self.get_credentials() is not None
