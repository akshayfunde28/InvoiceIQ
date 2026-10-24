import pymupdf
from pathlib import Path
from PIL import Image
import io
import pytesseract
import shutil
from app.core.config import settings
from app.core.logging import logger

class OCRService:
    def __init__(self):
        if settings.TESSERACT_CMD:
            pytesseract.pytesseract.tesseract_cmd = settings.TESSERACT_CMD

    def is_available(self) -> bool:
        if settings.TESSERACT_CMD and Path(settings.TESSERACT_CMD).exists():
            return True
        return shutil.which("tesseract") is not None

    def extract_text_from_pdf(self, file_path: Path) -> str:
        if not self.is_available():
            logger.warning("Tesseract OCR is not installed or not in PATH. Skipping OCR step.")
            return ""

        try:
            doc = pymupdf.open(str(file_path))
            ocr_pages = []
            
            for page_index in range(len(doc)):
                page = doc[page_index]
                # Render page at 200 DPI for high OCR accuracy
                pix = page.get_pixmap(dpi=200)
                img = Image.open(io.BytesIO(pix.tobytes("png")))
                
                page_text = pytesseract.image_to_string(img)
                if page_text.strip():
                    ocr_pages.append(page_text.strip())
                    
            doc.close()
            combined_ocr = "\n\n--- OCR Page Break ---\n\n".join(ocr_pages)
            logger.info(f"OCR completed successfully for {len(ocr_pages)} pages.")
            return combined_ocr
            
        except Exception as e:
            logger.error(f"Failed to perform OCR on {file_path}: {str(e)}")
            return ""

ocr_service = OCRService()
