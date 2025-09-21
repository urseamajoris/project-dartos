import PyPDF2
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import os
import tempfile

class PDFProcessor:
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
    
    def extract_text(self, pdf_path: str) -> str:
        """Extract text from PDF using PyPDF2, fallback to OCR if needed"""
        try:
            # First try to extract text directly
            text = self._extract_text_direct(pdf_path)
            
            # If text is too short or empty, use OCR
            if len(text.strip()) < 100:
                text = self._extract_text_ocr(pdf_path)
            
            return text
        
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""
    
    def _extract_text_direct(self, pdf_path: str) -> str:
        """Extract text directly from PDF"""
        text = ""
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    
    def _extract_text_ocr(self, pdf_path: str) -> str:
        """Extract text using OCR from PDF images"""
        text = ""
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path)
            
            # Extract text from each image using OCR
            for image in images:
                page_text = pytesseract.image_to_string(image)
                text += page_text + "\n"
            
        except Exception as e:
            print(f"OCR extraction failed: {e}")
        
        return text
    
    def extract_images(self, pdf_path: str) -> list:
        """Extract images from PDF for analysis"""
        images = []
        try:
            pdf_images = convert_from_path(pdf_path)
            for i, image in enumerate(pdf_images):
                image_path = os.path.join(self.temp_dir, f"page_{i}.png")
                image.save(image_path, "PNG")
                images.append(image_path)
        except Exception as e:
            print(f"Error extracting images: {e}")
        
        return images