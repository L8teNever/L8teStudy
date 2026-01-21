"""
OCR Service für L8teStudy Drive Integration
Extrahiert Text aus PDF-Dateien für die Volltextsuche
"""

import os
import io
from typing import Optional, Tuple
import pdfplumber
import PyPDF2
from PIL import Image


class OCRError(Exception):
    """Custom exception for OCR errors"""
    pass


class PDFTextExtractor:
    """
    PDF Text Extraction Service
    
    Features:
    - Extract text from PDF files
    - Support for both text-based and scanned PDFs
    - Page counting
    - Error handling
    """
    
    def __init__(self):
        """Initialize the PDF text extractor"""
        pass
    
    def extract_text_from_pdf(self, pdf_path: str) -> Tuple[str, int]:
        """
        Extract text from a PDF file
        
        Args:
            pdf_path: Path to the PDF file
        
        Returns:
            Tuple of (extracted_text, page_count)
        
        Raises:
            OCRError: If extraction fails
        """
        if not os.path.exists(pdf_path):
            raise OCRError(f"PDF file not found: {pdf_path}")
        
        # Try pdfplumber first (better for text-based PDFs)
        try:
            return self._extract_with_pdfplumber(pdf_path)
        except Exception as e:
            # Fallback to PyPDF2
            try:
                return self._extract_with_pypdf2(pdf_path)
            except Exception as e2:
                raise OCRError(
                    f"Failed to extract text from PDF: pdfplumber error: {str(e)}, "
                    f"PyPDF2 error: {str(e2)}"
                )
    
    def _extract_with_pdfplumber(self, pdf_path: str) -> Tuple[str, int]:
        """
        Extract text using pdfplumber
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            Tuple of (text, page_count)
        """
        text_parts = []
        page_count = 0
        
        with pdfplumber.open(pdf_path) as pdf:
            page_count = len(pdf.pages)
            
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        
        return '\n\n'.join(text_parts), page_count
    
    def _extract_with_pypdf2(self, pdf_path: str) -> Tuple[str, int]:
        """
        Extract text using PyPDF2 (fallback)
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            Tuple of (text, page_count)
        """
        text_parts = []
        
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            page_count = len(pdf_reader.pages)
            
            for page in pdf_reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)
        
        return '\n\n'.join(text_parts), page_count
    
    def extract_text_from_bytes(self, pdf_bytes: bytes) -> Tuple[str, int]:
        """
        Extract text from PDF bytes (in-memory)
        
        Args:
            pdf_bytes: PDF file as bytes
        
        Returns:
            Tuple of (extracted_text, page_count)
        
        Raises:
            OCRError: If extraction fails
        """
        try:
            # Try pdfplumber first
            text_parts = []
            page_count = 0
            
            with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
                page_count = len(pdf.pages)
                
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
            
            return '\n\n'.join(text_parts), page_count
            
        except Exception as e:
            # Fallback to PyPDF2
            try:
                text_parts = []
                pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
                page_count = len(pdf_reader.pages)
                
                for page in pdf_reader.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
                
                return '\n\n'.join(text_parts), page_count
                
            except Exception as e2:
                raise OCRError(
                    f"Failed to extract text from PDF bytes: {str(e)}, {str(e2)}"
                )
    
    def get_page_count(self, pdf_path: str) -> int:
        """
        Get the number of pages in a PDF
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            Number of pages
        
        Raises:
            OCRError: If reading fails
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                return len(pdf.pages)
        except:
            try:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    return len(pdf_reader.pages)
            except Exception as e:
                raise OCRError(f"Failed to get page count: {str(e)}")
    
    def is_text_based_pdf(self, pdf_path: str) -> bool:
        """
        Check if a PDF contains extractable text
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            True if PDF contains text, False if it's likely scanned
        """
        try:
            text, _ = self.extract_text_from_pdf(pdf_path)
            # If we got at least 50 characters, consider it text-based
            return len(text.strip()) > 50
        except:
            return False


class OCRService:
    """
    High-level OCR service for Drive Integration
    
    Handles PDF text extraction and indexing
    """
    
    def __init__(self):
        """Initialize OCR service"""
        self.extractor = PDFTextExtractor()
    
    def process_pdf_file(self, file_path: str) -> Tuple[str, int, bool]:
        """
        Process a PDF file and extract text
        
        Args:
            file_path: Path to PDF file
        
        Returns:
            Tuple of (extracted_text, page_count, success)
        """
        try:
            text, page_count = self.extractor.extract_text_from_pdf(file_path)
            return text, page_count, True
        except OCRError as e:
            return "", 0, False
        except Exception as e:
            return "", 0, False
    
    def process_pdf_bytes(self, pdf_bytes: bytes) -> Tuple[str, int, bool]:
        """
        Process PDF bytes and extract text
        
        Args:
            pdf_bytes: PDF file as bytes
        
        Returns:
            Tuple of (extracted_text, page_count, success)
        """
        try:
            text, page_count = self.extractor.extract_text_from_bytes(pdf_bytes)
            return text, page_count, True
        except OCRError as e:
            return "", 0, False
        except Exception as e:
            return "", 0, False
    
    def clean_text(self, text: str) -> str:
        """
        Clean extracted text for better search results
        
        Args:
            text: Raw extracted text
        
        Returns:
            Cleaned text
        """
        # Remove excessive whitespace
        lines = [line.strip() for line in text.split('\n')]
        lines = [line for line in lines if line]
        
        # Join with single newlines
        cleaned = '\n'.join(lines)
        
        # Remove multiple spaces
        import re
        cleaned = re.sub(r' +', ' ', cleaned)
        
        return cleaned


# Utility function
def get_ocr_service() -> OCRService:
    """
    Get an OCR service instance
    
    Returns:
        OCRService instance
    """
    return OCRService()
