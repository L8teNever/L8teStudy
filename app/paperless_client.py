"""
Paperless-NGX API Client
Handles all communication with Paperless-NGX instance
"""

import requests
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PaperlessAPIError(Exception):
    """Custom exception for Paperless API errors"""
    pass


class PaperlessClient:
    """Client for interacting with Paperless-NGX API"""
    
    def __init__(self, base_url: str, api_token: str):
        """
        Initialize Paperless client
        
        Args:
            base_url: Base URL of Paperless instance (e.g., https://paperless.example.com)
            api_token: API token from Paperless settings
        """
        self.base_url = base_url.rstrip('/')
        self.api_token = api_token
        self.headers = {
            'Authorization': f'Token {api_token}',
            'Accept': 'application/json',
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        Make HTTP request to Paperless API
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE, PATCH)
            endpoint: API endpoint (without base URL)
            **kwargs: Additional arguments for requests
            
        Returns:
            JSON response as dict
            
        Raises:
            PaperlessAPIError: If request fails
        """
        url = f"{self.base_url}/api{endpoint}"
        
        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()
            
            # Some endpoints return empty responses (e.g., DELETE)
            if response.status_code == 204:
                return {'success': True}
            
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            logger.error(f"Paperless API HTTP error: {e}")
            error_msg = f"HTTP {response.status_code}"
            try:
                error_data = response.json()
                error_msg = error_data.get('detail', str(error_data))
            except:
                error_msg = response.text or error_msg
            raise PaperlessAPIError(f"API Error: {error_msg}")
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Paperless API request error: {e}")
            raise PaperlessAPIError(f"Connection Error: {str(e)}")
    
    # --- Connection Test ---
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to Paperless instance
        
        Returns:
            Dict with connection status and info
        """
        try:
            # Try to get user info as connection test
            data = self._make_request('GET', '/ui_settings/')
            return {
                'success': True,
                'message': 'Connection successful',
                'user': data.get('user', {})
            }
        except PaperlessAPIError as e:
            return {
                'success': False,
                'message': str(e)
            }
    
    # --- Documents ---
    
    def get_documents(
        self,
        page: int = 1,
        page_size: int = 25,
        query: Optional[str] = None,
        tags: Optional[List[int]] = None,
        correspondent: Optional[int] = None,
        document_type: Optional[int] = None,
        ordering: str = '-created'
    ) -> Dict[str, Any]:
        """
        Get list of documents with pagination and filters
        
        Args:
            page: Page number (1-indexed)
            page_size: Number of documents per page
            query: Search query (full-text search)
            tags: List of tag IDs to filter by
            correspondent: Correspondent ID to filter by
            document_type: Document type ID to filter by
            ordering: Sort field (prefix with - for descending)
            
        Returns:
            Dict with 'count', 'next', 'previous', 'results'
        """
        params = {
            'page': page,
            'page_size': page_size,
            'ordering': ordering
        }
        
        if query:
            params['query'] = query
        if tags:
            params['tags__id__in'] = ','.join(map(str, tags))
        if correspondent:
            params['correspondent__id'] = correspondent
        if document_type:
            params['document_type__id'] = document_type
        
        return self._make_request('GET', '/documents/', params=params)
    
    def get_document(self, doc_id: int) -> Dict[str, Any]:
        """
        Get single document details
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document data
        """
        return self._make_request('GET', f'/documents/{doc_id}/')
    
    def download_document(self, doc_id: int, original: bool = False) -> bytes:
        """
        Download document file
        
        Args:
            doc_id: Document ID
            original: If True, download original file; if False, download archived (OCR'd) version
            
        Returns:
            File content as bytes
        """
        endpoint = f'/documents/{doc_id}/download/' if not original else f'/documents/{doc_id}/original/'
        url = f"{self.base_url}/api{endpoint}"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            logger.error(f"Error downloading document {doc_id}: {e}")
            raise PaperlessAPIError(f"Download failed: {str(e)}")
    
    def get_document_preview(self, doc_id: int) -> bytes:
        """
        Get document thumbnail/preview image
        
        Args:
            doc_id: Document ID
            
        Returns:
            Image content as bytes
        """
        url = f"{self.base_url}/api/documents/{doc_id}/thumb/"
        
        try:
            response = self.session.get(url)
            response.raise_for_status()
            return response.content
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting preview for document {doc_id}: {e}")
            raise PaperlessAPIError(f"Preview failed: {str(e)}")
    
    def upload_document(
        self,
        file_path: str = None,
        file_content: bytes = None,
        filename: str = None,
        title: Optional[str] = None,
        tags: Optional[List[int]] = None,
        correspondent: Optional[int] = None,
        document_type: Optional[int] = None,
        created: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Upload new document to Paperless
        
        Args:
            file_path: Path to file (if uploading from disk)
            file_content: File content as bytes (if uploading from memory)
            filename: Filename (required if using file_content)
            title: Document title
            tags: List of tag IDs
            correspondent: Correspondent ID
            document_type: Document type ID
            created: Document creation date
            
        Returns:
            Upload response with task ID
        """
        if file_path:
            with open(file_path, 'rb') as f:
                file_data = f.read()
            import os
            filename = os.path.basename(file_path)
        elif file_content and filename:
            file_data = file_content
        else:
            raise ValueError("Either file_path or (file_content + filename) must be provided")
        
        files = {
            'document': (filename, file_data)
        }
        
        data = {}
        if title:
            data['title'] = title
        if tags:
            data['tags'] = tags
        if correspondent:
            data['correspondent'] = correspondent
        if document_type:
            data['document_type'] = document_type
        if created:
            data['created'] = created.isoformat()
        
        # Remove Authorization header for multipart upload (will be added by session)
        headers = dict(self.headers)
        headers.pop('Content-Type', None)  # Let requests set it for multipart
        
        return self._make_request('POST', '/documents/post_document/', files=files, data=data)
    
    def update_document(
        self,
        doc_id: int,
        title: Optional[str] = None,
        tags: Optional[List[int]] = None,
        correspondent: Optional[int] = None,
        document_type: Optional[int] = None,
        created: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """
        Update document metadata
        
        Args:
            doc_id: Document ID
            title: New title
            tags: New list of tag IDs
            correspondent: New correspondent ID
            document_type: New document type ID
            created: New creation date
            
        Returns:
            Updated document data
        """
        data = {}
        if title is not None:
            data['title'] = title
        if tags is not None:
            data['tags'] = tags
        if correspondent is not None:
            data['correspondent'] = correspondent
        if document_type is not None:
            data['document_type'] = document_type
        if created is not None:
            data['created'] = created.isoformat()
        
        return self._make_request('PATCH', f'/documents/{doc_id}/', json=data)
    
    def delete_document(self, doc_id: int) -> Dict[str, Any]:
        """
        Delete document
        
        Args:
            doc_id: Document ID
            
        Returns:
            Success response
        """
        return self._make_request('DELETE', f'/documents/{doc_id}/')
    
    # --- Tags ---
    
    def get_tags(self) -> List[Dict[str, Any]]:
        """
        Get all tags
        
        Returns:
            List of tag objects
        """
        response = self._make_request('GET', '/tags/')
        return response.get('results', [])
    
    def create_tag(self, name: str, color: str = '#a6cee3', is_inbox_tag: bool = False) -> Dict[str, Any]:
        """
        Create new tag
        
        Args:
            name: Tag name
            color: Hex color code
            is_inbox_tag: Whether this is an inbox tag
            
        Returns:
            Created tag data
        """
        data = {
            'name': name,
            'color': color,
            'is_inbox_tag': is_inbox_tag
        }
        return self._make_request('POST', '/tags/', json=data)
    
    # --- Correspondents ---
    
    def get_correspondents(self) -> List[Dict[str, Any]]:
        """
        Get all correspondents
        
        Returns:
            List of correspondent objects
        """
        response = self._make_request('GET', '/correspondents/')
        return response.get('results', [])
    
    def create_correspondent(self, name: str) -> Dict[str, Any]:
        """
        Create new correspondent
        
        Args:
            name: Correspondent name
            
        Returns:
            Created correspondent data
        """
        data = {'name': name}
        return self._make_request('POST', '/correspondents/', json=data)
    
    # --- Document Types ---
    
    def get_document_types(self) -> List[Dict[str, Any]]:
        """
        Get all document types
        
        Returns:
            List of document type objects
        """
        response = self._make_request('GET', '/document_types/')
        return response.get('results', [])
    
    def create_document_type(self, name: str) -> Dict[str, Any]:
        """
        Create new document type
        
        Args:
            name: Document type name
            
        Returns:
            Created document type data
        """
        data = {'name': name}
        return self._make_request('POST', '/document_types/', json=data)
    
    # --- Search ---
    
    def search(self, query: str, page: int = 1, page_size: int = 25) -> Dict[str, Any]:
        """
        Full-text search across all documents
        
        Args:
            query: Search query
            page: Page number
            page_size: Results per page
            
        Returns:
            Search results with pagination
        """
        return self.get_documents(page=page, page_size=page_size, query=query)
    
    # --- Statistics ---
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get Paperless statistics
        
        Returns:
            Statistics data
        """
        return self._make_request('GET', '/statistics/')
