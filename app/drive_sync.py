"""
Drive Sync Service für L8teStudy
Background Worker für automatische Synchronisation von Google Drive Ordnern
"""

import os
import tempfile
from datetime import datetime
from typing import List, Optional
from flask import current_app
from . import db
from .models import DriveFolder, DriveFile, DriveFileContent
from .drive_client import GoogleDriveClient, DriveClientError
from .drive_encryption import DriveEncryptionManager
from .ocr_service import OCRService
from .subject_mapper import SubjectMapper


class DriveSyncError(Exception):
    """Custom exception for sync errors"""
    pass


class DriveSyncService:
    """
    Drive Synchronization Service
    
    Features:
    - Sync all enabled folders
    - Download and encrypt new files
    - OCR text extraction
    - Subject mapping
    - Change detection via hash
    """
    
    def __init__(self):
        """Initialize sync service"""
        self.drive_client = None
        self.encryption_manager = None
        self.ocr_service = None
    
    def _init_services(self):
        """Lazy initialization of services"""
        if self.drive_client is None:
            try:
                self.drive_client = GoogleDriveClient()
            except Exception as e:
                current_app.logger.error(f"Failed to initialize Drive client: {e}")
                raise DriveSyncError(f"Drive client initialization failed: {e}")
        
        if self.encryption_manager is None:
            self.encryption_manager = DriveEncryptionManager()
        
        if self.ocr_service is None:
            self.ocr_service = OCRService()
    
    def sync_all_folders(self) -> dict:
        """
        Synchronisiert alle aktivierten Ordner
        
        Returns:
            Dictionary mit Sync-Statistiken
        """
        self._init_services()
        
        stats = {
            'total_folders': 0,
            'synced_folders': 0,
            'failed_folders': 0,
            'new_files': 0,
            'updated_files': 0,
            'errors': []
        }
        
        # Get all enabled folders
        folders = DriveFolder.query.filter_by(sync_enabled=True).all()
        stats['total_folders'] = len(folders)
        
        for folder in folders:
            try:
                result = self.sync_folder(folder.id)
                stats['synced_folders'] += 1
                stats['new_files'] += result.get('new_files', 0)
                stats['updated_files'] += result.get('updated_files', 0)
            except Exception as e:
                stats['failed_folders'] += 1
                stats['errors'].append({
                    'folder_id': folder.id,
                    'folder_name': folder.folder_name,
                    'error': str(e)
                })
                current_app.logger.error(f"Failed to sync folder {folder.id}: {e}")
        
        return stats
    
    def sync_folder(self, folder_db_id: int) -> dict:
        """
        Synchronisiert einen einzelnen Ordner
        
        Args:
            folder_db_id: Database ID des DriveFolder
        
        Returns:
            Dictionary mit Sync-Statistiken
        
        Raises:
            DriveSyncError: Bei Sync-Fehlern
        """
        self._init_services()
        
        folder = DriveFolder.query.get(folder_db_id)
        if not folder:
            raise DriveSyncError(f"Folder {folder_db_id} not found")
        
        if not folder.sync_enabled:
            raise DriveSyncError(f"Folder {folder_db_id} sync is disabled")
        
        stats = {
            'new_files': 0,
            'updated_files': 0,
            'skipped_files': 0,
            'errors': []
        }
        
        try:
            # Update folder status
            folder.sync_status = 'syncing'
            folder.sync_error = None
            db.session.commit()
            
            # List files in Google Drive folder
            drive_files = self.drive_client.list_pdf_files(folder.folder_id)
            
            # Process each file
            for drive_file in drive_files:
                try:
                    result = self._process_file(folder, drive_file)
                    if result == 'new':
                        stats['new_files'] += 1
                    elif result == 'updated':
                        stats['updated_files'] += 1
                    elif result == 'skipped':
                        stats['skipped_files'] += 1
                except Exception as e:
                    stats['errors'].append({
                        'file_id': drive_file.get('id'),
                        'file_name': drive_file.get('name'),
                        'error': str(e)
                    })
                    current_app.logger.error(
                        f"Failed to process file {drive_file.get('name')}: {e}"
                    )
            
            # Update folder status
            folder.sync_status = 'completed'
            folder.last_sync_at = datetime.utcnow()
            
            if stats['errors']:
                folder.sync_error = f"{len(stats['errors'])} files failed"
            
            db.session.commit()
            
        except Exception as e:
            folder.sync_status = 'error'
            folder.sync_error = str(e)
            db.session.commit()
            raise DriveSyncError(f"Folder sync failed: {e}")
        
        return stats
    
    def _process_file(self, folder: DriveFolder, drive_file: dict) -> str:
        """
        Verarbeitet eine einzelne Datei
        
        Args:
            folder: DriveFolder Objekt
            drive_file: Google Drive file metadata
        
        Returns:
            'new', 'updated', or 'skipped'
        """
        file_id = drive_file['id']
        file_name = drive_file['name']
        file_size = int(drive_file.get('size', 0))
        mime_type = drive_file.get('mimeType', 'application/pdf')
        
        # Check if file already exists
        existing_file = DriveFile.query.filter_by(
            drive_folder_id=folder.id,
            file_id=file_id
        ).first()
        
        # Download file to temp location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as temp_file:
            temp_path = temp_file.name
        
        try:
            # Download from Google Drive
            self.drive_client.download_file_to_path(file_id, temp_path)
            
            # Calculate hash
            file_hash = self.encryption_manager.calculate_file_hash(temp_path)
            
            # Check if file changed
            if existing_file and existing_file.file_hash == file_hash:
                return 'skipped'
            
            # Encrypt and store
            metadata = {
                'file_id': file_id,
                'filename': file_name,
                'user_id': folder.user_id,
                'folder_id': folder.folder_id
            }
            
            encrypted_path, _, _ = self.encryption_manager.encrypt_and_store_file(
                temp_path,
                file_id,
                metadata
            )
            
            # Extract text with OCR
            text, page_count, ocr_success = self.ocr_service.process_pdf_file(temp_path)
            
            if ocr_success:
                text = self.ocr_service.clean_text(text)
            
            # Map to subject
            subject_id = None
            auto_mapped = False
            
            if folder.user_id:
                mapper = SubjectMapper(
                    class_id=None,  # Will be determined from user
                    user_id=folder.user_id
                )
                
                # Try to extract subject from filename or parent folder
                subject = mapper.map_folder_to_subject(file_name, auto_create=True)
                if subject:
                    subject_id = subject.id
                    auto_mapped = True
            
            # Create or update database entry
            if existing_file:
                # Update existing
                existing_file.filename = file_name
                existing_file.encrypted_path = encrypted_path
                existing_file.file_hash = file_hash
                existing_file.file_size = file_size
                existing_file.mime_type = mime_type
                existing_file.subject_id = subject_id
                existing_file.auto_mapped = auto_mapped
                existing_file.ocr_completed = ocr_success
                existing_file.ocr_error = None if ocr_success else "OCR failed"
                existing_file.updated_at = datetime.utcnow()
                
                # Update content
                if existing_file.content:
                    existing_file.content.content_text = text
                    existing_file.content.page_count = page_count
                    existing_file.content.ocr_completed_at = datetime.utcnow()
                else:
                    content = DriveFileContent(
                        drive_file_id=existing_file.id,
                        content_text=text,
                        page_count=page_count
                    )
                    db.session.add(content)
                
                db.session.commit()
                return 'updated'
            else:
                # Create new
                new_file = DriveFile(
                    drive_folder_id=folder.id,
                    file_id=file_id,
                    filename=file_name,
                    encrypted_path=encrypted_path,
                    file_hash=file_hash,
                    file_size=file_size,
                    mime_type=mime_type,
                    subject_id=subject_id,
                    auto_mapped=auto_mapped,
                    ocr_completed=ocr_success,
                    ocr_error=None if ocr_success else "OCR failed"
                )
                
                db.session.add(new_file)
                db.session.flush()  # Get the ID
                
                # Add content
                content = DriveFileContent(
                    drive_file_id=new_file.id,
                    content_text=text,
                    page_count=page_count
                )
                db.session.add(content)
                
                db.session.commit()
                return 'new'
        
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.remove(temp_path)
    
    def add_folder(
        self,
        user_id: int,
        folder_id: str,
        privacy_level: str = 'private'
    ) -> DriveFolder:
        """
        Fügt einen neuen Ordner hinzu
        
        Args:
            user_id: Benutzer-ID
            folder_id: Google Drive Folder ID
            privacy_level: 'private' oder 'public'
        
        Returns:
            DriveFolder Objekt
        
        Raises:
            DriveSyncError: Bei Fehlern
        """
        self._init_services()
        
        # Verify folder access
        if not self.drive_client.verify_folder_access(folder_id):
            raise DriveSyncError("Cannot access folder. Please share it with the service account.")
        
        # Get folder name
        try:
            folder_name = self.drive_client.get_folder_name(folder_id)
        except:
            folder_name = "Unknown Folder"
        
        # Check if already exists
        existing = DriveFolder.query.filter_by(
            user_id=user_id,
            folder_id=folder_id
        ).first()
        
        if existing:
            raise DriveSyncError("Folder already added")
        
        # Create folder
        folder = DriveFolder(
            user_id=user_id,
            folder_id=folder_id,
            folder_name=folder_name,
            privacy_level=privacy_level,
            sync_enabled=True,
            sync_status='pending'
        )
        
        db.session.add(folder)
        db.session.commit()
        
        return folder


# Utility function
def get_drive_sync_service() -> DriveSyncService:
    """
    Get a Drive Sync Service instance
    
    Returns:
        DriveSyncService instance
    """
    return DriveSyncService()
