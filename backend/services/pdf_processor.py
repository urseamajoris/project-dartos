import PyPDF2
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
import os
import tempfile
import logging
import time
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self, max_retries: int = 3, retry_delay: float = 1.0):
        self.temp_dir = tempfile.gettempdir()
        self.max_retries = max_retries
        self.retry_delay = retry_delay
    
    def extract_text(self, pdf_path: str) -> str:
        """Extract text from PDF using PyPDF2, fallback to OCR if needed"""
        if not os.path.exists(pdf_path):
            logger.error(f"PDF file does not exist: {pdf_path}")
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        try:
            # First try to extract text directly
            text = self._extract_text_direct(pdf_path)
            logger.info(f"Direct text extraction yielded {len(text)} characters")
            
            # If text is too short or empty, use OCR
            if len(text.strip()) < 100:
                logger.info("Text too short, falling back to OCR")
                ocr_text = self._extract_text_ocr_with_retries(pdf_path)
                if ocr_text:
                    text = ocr_text
                    logger.info(f"OCR extraction successful, {len(text)} characters")
                else:
                    logger.warning("OCR extraction failed, using direct text")
            
            return text
        
        except Exception as e:
            logger.error(f"Error extracting text from PDF {pdf_path}: {e}")
            raise RuntimeError(f"Failed to extract text from PDF: {str(e)}")
    
    def _extract_text_direct(self, pdf_path: str) -> str:
        """Extract text directly from PDF"""
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for i, page in enumerate(pdf_reader.pages):
                    page_text = page.extract_text()
                    text += page_text + "\n"
                    logger.debug(f"Extracted text from page {i+1}: {len(page_text)} chars")
        except Exception as e:
            logger.warning(f"Direct text extraction failed: {e}")
            raise
        return text
    
    def _extract_text_ocr_with_retries(self, pdf_path: str) -> Optional[str]:
        """Extract text using OCR from PDF images with retries"""
        for attempt in range(self.max_retries):
            try:
                text = self._extract_text_ocr(pdf_path)
                if text.strip():
                    return text
            except Exception as e:
                logger.warning(f"OCR attempt {attempt+1} failed: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
        logger.error("All OCR attempts failed")
        return None
    
    def _extract_text_ocr(self, pdf_path: str) -> str:
        """Extract text using OCR from PDF images"""
        text = ""
        try:
            # Check if tesseract is available
            pytesseract.get_tesseract_version()
        except Exception as e:
            logger.error(f"Tesseract not available: {e}")
            raise RuntimeError("Tesseract OCR is not installed or not accessible")
        
        try:
            # Convert PDF to images
            images = convert_from_path(pdf_path, dpi=300)  # Higher DPI for better OCR
            logger.info(f"Converted PDF to {len(images)} images")
            
            # Extract text from each image using OCR
            for i, image in enumerate(images):
                page_text = pytesseract.image_to_string(image, lang='eng')
                text += page_text + "\n"
                logger.debug(f"OCR on page {i+1}: {len(page_text)} chars")
            
        except Exception as e:
            logger.error(f"OCR extraction failed: {e}")
            raise
        
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
                logger.debug(f"Saved image {i+1} to {image_path}")
        except Exception as e:
            logger.error(f"Error extracting images: {e}")
            raise
        return images