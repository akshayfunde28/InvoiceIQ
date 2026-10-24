import pymupdf
from pathlib import Path
from app.services.pdf_service import pdf_service

def test_pdf_validation_header():
    valid_pdf_bytes = b"%PDF-1.4 sample content"
    is_valid, msg = pdf_service.validate_pdf(valid_pdf_bytes)
    assert is_valid is True
    assert msg == ""

    invalid_bytes = b"NOT_A_PDF_FILE"
    is_valid, msg = pdf_service.validate_pdf(invalid_bytes)
    assert is_valid is False
    assert "PDF signature" in msg

def test_pdf_validation_size():
    huge_bytes = b"%PDF-" + (b"0" * (16 * 1024 * 1024))
    is_valid, msg = pdf_service.validate_pdf(huge_bytes, max_size_mb=15)
    assert is_valid is False
    assert "exceeds maximum limit" in msg

def test_pdf_text_extraction(tmp_path: Path):
    # Generate a temporary PDF with PyMuPDF
    test_pdf_path = tmp_path / "sample_invoice.pdf"
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((50, 72), "TAX INVOICE\nInvoice No: INV-TEST-99\nVendor: Alpha Corp", fontsize=12)
    doc.save(str(test_pdf_path))
    doc.close()

    text, needs_ocr = pdf_service.extract_text(test_pdf_path)
    assert "TAX INVOICE" in text
    assert "INV-TEST-99" in text
    assert "Alpha Corp" in text
    assert needs_ocr is False
