"""
Google Drive API Client für L8teStudy
Handles authentication and file operations with Google Drive
"""

import os
import io
from typing import List, Dict, Optional, BinaryIO
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
from flask import current_app


class DriveClientError(Exception):
    """Custom exception for Drive client errors"""
    pass


class GoogleDriveClient:
    """
    Google Drive API Client
    
    Features:
    - Service Account authentication
    - List files in folder
    - Download files
    - Get file metadata
    - Read-only access
    """
    
    SCOPES = ['https://www.googleapis.com/auth/drive.readonly']
    
    def __init__(self, service_account_file: Optional[str] = None):
        """
        Initialize Google Drive client
        """
        import json
        self.service = None
        
        # 1. Try JSON Info (Direct string from Env)
        service_account_info = current_app.config.get('GOOGLE_SERVICE_ACCOUNT_INFO')
        if service_account_info:
            try:
                # If it's a string, parse it
                if isinstance(service_account_info, str):
                    info = json.loads(service_account_info)
                else:
                    info = service_account_info
                
                credentials = service_account.Credentials.from_service_account_info(
                    info, scopes=self.SCOPES
                )
                self.service = build('drive', 'v3', credentials=credentials)
                return
            except Exception as e:
                current_app.logger.error(f"Failed to load Drive credentials from INFO: {e}")

        # 2. Try File Path
        if service_account_file is None:
            service_account_file = current_app.config.get('GOOGLE_SERVICE_ACCOUNT_FILE')
        
        if service_account_file and os.path.exists(service_account_file):
            try:
                credentials = service_account.Credentials.from_service_account_file(
                    service_account_file,
                    scopes=self.SCOPES
                )
                self.service = build('drive', 'v3', credentials=credentials)
                return
            except Exception as e:
                current_app.logger.error(f"Failed to load Drive credentials from FILE: {e}")

        raise DriveClientError("No valid Google Drive credentials found (File or Info)")
    
    def list_files(
        self,
        folder_id: str,
        page_size: int = 100,
        mime_type: Optional[str] = None
    ) -> List[Dict]:
        """
        List files in a Google Drive folder
        
        Args:
            folder_id: Google Drive folder ID
            page_size: Number of files per page (max 1000)
            mime_type: Optional MIME type filter (e.g., 'application/pdf')
        
        Returns:
            List of file metadata dictionaries
        
        Raises:
            DriveClientError: If listing fails
        """
        try:
            query = f"'{folder_id}' in parents and trashed=false"
            if mime_type:
                query += f" and mimeType='{mime_type}'"
            
            results = []
            page_token = None
            
            while True:
                response = self.service.files().list(
                    q=query,
                    pageSize=page_size,
                    fields="nextPageToken, files(id, name, mimeType, size, modifiedTime, md5Checksum)",
                    pageToken=page_token
                ).execute()
                
                files = response.get('files', [])
                results.extend(files)
                
                page_token = response.get('nextPageToken')
                if not page_token:
                    break
            
            return results
            
        except HttpError as e:
            raise DriveClientError(f"Failed to list files in folder {folder_id}: {str(e)}")
        except Exception as e:
            raise DriveClientError(f"Unexpected error listing files: {str(e)}")
    
    def get_file_metadata(self, file_id: str) -> Dict:
        """
        Get metadata for a specific file
        
        Args:
            file_id: Google Drive file ID
        
        Returns:
            File metadata dictionary
        
        Raises:
            DriveClientError: If metadata retrieval fails
        """
        try:
            file = self.service.files().get(
                fileId=file_id,
                fields="id, name, mimeType, size, modifiedTime, md5Checksum, parents"
            ).execute()
            return file
            
        except HttpError as e:
            raise DriveClientError(f"Failed to get metadata for file {file_id}: {str(e)}")
        except Exception as e:
            raise DriveClientError(f"Unexpected error getting file metadata: {str(e)}")
    
    def download_file(self, file_id: str, output_stream: BinaryIO) -> int:
        """
        Download a file from Google Drive
        
        Args:
            file_id: Google Drive file ID
            output_stream: Binary stream to write file content to
        
        Returns:
            Number of bytes downloaded
        
        Raises:
            DriveClientError: If download fails
        """
        try:
            request = self.service.files().get_media(fileId=file_id)
            downloader = MediaIoBaseDownload(output_stream, request)
            
            done = False
            bytes_downloaded = 0
            
            while not done:
                status, done = downloader.next_chunk()
                if status:
                    bytes_downloaded = int(status.resumable_progress)
            
            return bytes_downloaded
            
        except HttpError as e:
            raise DriveClientError(f"Failed to download file {file_id}: {str(e)}")
        except Exception as e:
            raise DriveClientError(f"Unexpected error downloading file: {str(e)}")
    
    def download_file_to_path(self, file_id: str, output_path: str) -> int:
        """
        Download a file from Google Drive to a local path
        
        Args:
            file_id: Google Drive file ID
            output_path: Local file path to save to
        
        Returns:
            Number of bytes downloaded
        
        Raises:
            DriveClientError: If download fails
        """
        try:
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'wb') as f:
                return self.download_file(file_id, f)
                
        except Exception as e:
            raise DriveClientError(f"Failed to download file to {output_path}: {str(e)}")
    
    def get_folder_name(self, folder_id: str) -> str:
        """
        Get the name of a folder
        
        Args:
            folder_id: Google Drive folder ID
        
        Returns:
            Folder name
        
        Raises:
            DriveClientError: If folder not found
        """
        try:
            folder = self.service.files().get(
                fileId=folder_id,
                fields="name"
            ).execute()
            return folder.get('name', 'Unknown Folder')
            
        except HttpError as e:
            raise DriveClientError(f"Failed to get folder name for {folder_id}: {str(e)}")
        except Exception as e:
            raise DriveClientError(f"Unexpected error getting folder name: {str(e)}")
    
    def verify_folder_access(self, folder_id: str) -> bool:
        """
        Verify that the service account has access to a folder
        
        Args:
            folder_id: Google Drive folder ID
        
        Returns:
            True if accessible, False otherwise
        """
        try:
            self.service.files().get(
                fileId=folder_id,
                fields="id"
            ).execute()
            return True
        except:
            return False
    
    def list_pdf_files(self, folder_id: str) -> List[Dict]:
        """
        List only PDF files in a folder
        
        Args:
            folder_id: Google Drive folder ID
        
        Returns:
            List of PDF file metadata
        """
        return self.list_files(folder_id, mime_type='application/pdf')

    def list_subfolders(self, folder_id: str) -> List[Dict]:
        """
        List only subfolders in a folder
        
        Args:
            folder_id: Google Drive folder ID
        
        Returns:
            List of subfolder metadata
        """
        return self.list_files(folder_id, mime_type='application/vnd.google-apps.folder')


# Utility function for easy access
def get_drive_client() -> GoogleDriveClient:
    """
    Get a configured Google Drive client instance
    
    Returns:
        GoogleDriveClient instance
    """
    return GoogleDriveClient()
