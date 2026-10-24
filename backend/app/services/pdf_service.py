import pymupdf
from pathlib import Path
from typing import Tuple, List
from app.core.logging import logger

SUPPORTED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".webp"}

class PDFService:
    @staticmethod
    def validate_file(file_bytes: bytes, filename: str, max_size_mb: int = 15) -> Tuple[bool, str]:
        # Validate size
        max_bytes = max_size_mb * 1024 * 1024
        if len(file_bytes) > max_bytes:
            return False, f"File size exceeds maximum limit of {max_size_mb} MB"
            
        ext = Path(filename).suffix.lower()
        if ext not in SUPPORTED_EXTENSIONS:
            return False, f"Unsupported file format '{ext}'. Supported: PDF, PNG, JPG, JPEG, WEBP."

        # Check signatures
        if ext == ".pdf" and not file_bytes.startswith(b"%PDF-"):
            return False, "Corrupted or invalid PDF header signature."

        return True, ""

    @classmethod
    def validate_pdf(cls, file_bytes: bytes, max_size_mb: int = 15) -> Tuple[bool, str]:
        max_bytes = max_size_mb * 1024 * 1024
        if len(file_bytes) > max_bytes:
            return False, f"File size exceeds maximum limit of {max_size_mb} MB"
        if not file_bytes.startswith(b"%PDF-"):
            return False, "Corrupted or invalid PDF signature."
        return True, ""


    @staticmethod
    def extract_text(file_path: Path) -> Tuple[str, bool]:
        """
        Extracts text from PDF or Image using PyMuPDF.
        Returns: (extracted_text, needs_ocr)
        """
        try:
            doc = pymupdf.open(str(file_path))
            total_pages = len(doc)
            extracted_pages: List[str] = []
            total_chars = 0
            
            for page_num in range(total_pages):
                page = doc[page_num]
                text = page.get_text("text").strip()
                extracted_pages.append(text)
                total_chars += len(text)
                
            doc.close()
            
            combined_text = "\n\n--- Page Break ---\n\n".join(extracted_pages).strip()
            
            # If image or sparse text, flag for OCR
            ext = file_path.suffix.lower()
            if ext in {".png", ".jpg", ".jpeg", ".webp"}:
                needs_ocr = len(combined_text) < 30
            else:
                avg_chars = total_chars / max(total_pages, 1)
                needs_ocr = avg_chars < 40 or total_chars < 50
            
            logger.info(f"Extracted {total_chars} characters from {file_path.name}. Needs OCR: {needs_ocr}")
            return combined_text, needs_ocr
            
        except Exception as e:
            logger.error(f"Error extracting text with PyMuPDF: {str(e)}")
            return "", True

pdf_service = PDFService()
