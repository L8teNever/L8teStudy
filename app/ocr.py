"""
OCR Service wrapper for Tesseract
"""
import pytesseract
from PIL import Image
from flask import current_app

class OCRService:
    def __init__(self):
        pass

    def extract_text_from_image(self, image_path):
        """Extract text from an image file"""
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image, lang='deu+eng')
            return text
        except Exception as e:
            current_app.logger.error(f"OCR failed: {e}")
            return None

def get_ocr_service():
    return OCRService()
