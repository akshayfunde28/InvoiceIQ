import uuid
import re
import csv
import io
from pathlib import Path
from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List, Tuple
from fastapi import UploadFile, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging import logger
from app.models.invoice import Invoice
from app.models.line_item import InvoiceLineItem
from app.repositories.vendor_repo import VendorRepository
from app.repositories.invoice_repo import InvoiceRepository
from app.services.pdf_service import pdf_service
from app.services.ocr_service import ocr_service
from app.services.grok_service import grok_service
from app.services.financial_validator import financial_validator, to_decimal
from app.schemas.invoice import InvoiceUpdate, ExtractedInvoiceData

from app.models.user import User
from app.services.pdf_report_service import pdf_report_service

def infer_category(vendor_name: str, items_text: str) -> str:
    combined = f"{vendor_name} {items_text}".lower()
    if any(k in combined for k in ["cloud", "software", "aws", "azure", "google", "saas", "license", "api", "hosting", "domain"]):
        return "Software & Cloud"
    elif any(k in combined for k in ["laptop", "computer", "server", "hardware", "chair", "desk", "printer", "equipment"]):
        return "Hardware & IT Equipment"
    elif any(k in combined for k in ["consulting", "legal", "audit", "advisory", "professional", "freelance"]):
        return "Professional Services"
    elif any(k in combined for k in ["office", "stationery", "paper", "supplies", "pen"]):
        return "Office Supplies"
    elif any(k in combined for k in ["travel", "hotel", "flight", "taxi", "cab", "fuel"]):
        return "Travel & Transport"
    elif any(k in combined for k in ["marketing", "ad", "advertising", "seo", "branding"]):
        return "Marketing & Sales"
    return "General Expenses"

def parse_date_safely(date_str: Optional[str]) -> Optional[date]:
    if not date_str or not str(date_str).strip():
        return None
    clean = str(date_str).strip()
    # Try common formats
    formats = ["%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%Y/%m/%d", "%d %b %Y", "%d %B %Y"]
    for fmt in formats:
        try:
            return datetime.strptime(clean, fmt).date()
        except ValueError:
            continue
    # Extract YYYY-MM-DD via regex if mixed with text
    match = re.search(r"(\d{4})[-/.](\d{2})[-/.](\d{2})", clean)
    if match:
        try:
            return date(int(match.group(1)), int(match.group(2)), int(match.group(3)))
        except ValueError:
            pass
    return None

class InvoiceService:
    @staticmethod
    def _save_file(file: UploadFile) -> Tuple[Path, str, int]:
        file_bytes = file.file.read()
        file_size = len(file_bytes)
        
        # Validate File (PDF or Image)
        is_valid, err_msg = pdf_service.validate_file(file_bytes, file.filename or "invoice.pdf", settings.MAX_UPLOAD_SIZE_MB)
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=err_msg
            )
            
        safe_filename = re.sub(r"[^a-zA-Z0-9_.-]", "_", file.filename or "invoice.pdf")
        unique_name = f"{uuid.uuid4().hex}_{safe_filename}"
        dest_path = settings.upload_path / unique_name
        
        with open(dest_path, "wb") as f:
            f.write(file_bytes)
            
        return dest_path, safe_filename, file_size

    @classmethod
    def process_upload(cls, db: Session, file: UploadFile, user: Optional[User] = None) -> Invoice:
        # 1. Save file safely
        dest_path, original_filename, file_size = cls._save_file(file)
        
        # 2. Extract text using PyMuPDF / Image OCR
        extracted_text, needs_ocr = pdf_service.extract_text(dest_path)
        ocr_used = False
        
        # 3. Fallback to OCR if text is sparse/scanned
        if needs_ocr and ocr_service.is_available():
            logger.info(f"Triggering OCR fallback for {original_filename}")
            ocr_text = ocr_service.extract_text_from_pdf(dest_path)
            if ocr_text:
                extracted_text = f"{extracted_text}\n\n{ocr_text}".strip()
                ocr_used = True

        if not extracted_text:
            logger.warning(f"Could not extract readable text from {original_filename}")

        # 4. Grok AI extraction
        ai_data: ExtractedInvoiceData
        try:
            ai_data = grok_service.extract_invoice(extracted_text)
        except Exception as e:
            logger.error(f"AI extraction failed: {str(e)}")
            ai_data = ExtractedInvoiceData(invoice_number=f"INV-{uuid.uuid4().hex[:8].upper()}")

        # 5. Financial Validation
        val_result = financial_validator.validate(ai_data)
        score = val_result["score"]
        review_status = val_result["review_status"]
        discrepancies = val_result["discrepancies"]

        # 6. Duplicate Detection (scoped to user)
        invoice_repo = InvoiceRepository(db)
        vendor_repo = VendorRepository(db)
        
        vendor_name = ai_data.vendor_name or "Unknown Vendor"
        inv_number = ai_data.invoice_number or f"INV-{uuid.uuid4().hex[:8].upper()}"
        user_id = user.id if user else None
        
        is_dup = invoice_repo.check_duplicate(vendor_name, inv_number, user_id=user_id)
        if is_dup:
            discrepancies.append(
                f"Potential duplicate invoice: Number '{inv_number}' already exists for vendor '{vendor_name}'"
            )
            review_status = "needs_review"
            score = max(Decimal("0.00"), score - Decimal("15.00"))

        # 7. Create or link Vendor
        vendor = vendor_repo.find_or_create(
            name=vendor_name,
            gstin=ai_data.vendor_gstin,
            address=ai_data.vendor_address,
            pan=ai_data.vendor_pan,
            phone=ai_data.vendor_phone,
            email=ai_data.vendor_email
        )

        # 8. Infer Category
        items_summary = " ".join([item.description for item in ai_data.line_items])
        category = ai_data.category or infer_category(vendor_name, items_summary)

        # 9. Create Invoice Model
        inv_date = parse_date_safely(ai_data.invoice_date)
        due_date = parse_date_safely(ai_data.due_date)

        new_invoice = Invoice(
            user_id=user_id,
            vendor_id=vendor.id,
            invoice_number=inv_number,
            category=category,
            invoice_date=inv_date,
            due_date=due_date,
            vendor_name_raw=vendor_name,
            vendor_gstin=ai_data.vendor_gstin.upper() if ai_data.vendor_gstin else None,
            vendor_address=ai_data.vendor_address,
            buyer_name=ai_data.buyer_name,
            buyer_gstin=ai_data.buyer_gstin.upper() if ai_data.buyer_gstin else None,
            buyer_address=ai_data.buyer_address,
            place_of_supply=ai_data.place_of_supply,
            taxable_amount=to_decimal(ai_data.taxable_amount),
            cgst_amount=to_decimal(ai_data.cgst_amount),
            sgst_amount=to_decimal(ai_data.sgst_amount),
            igst_amount=to_decimal(ai_data.igst_amount),
            total_tax=to_decimal(ai_data.total_tax),
            discount_amount=to_decimal(ai_data.discount_amount),
            additional_charges=to_decimal(ai_data.additional_charges),
            round_off=to_decimal(ai_data.round_off),
            total_amount=to_decimal(ai_data.total_amount),
            currency=ai_data.currency or "INR",
            amount_paid=to_decimal(ai_data.amount_paid),
            balance_due=to_decimal(ai_data.balance_due),
            payment_status=ai_data.payment_status or "unpaid",
            processing_status="extracted",
            review_status=review_status,
            validation_score=score,
            discrepancy_flags=discrepancies,
            is_duplicate=is_dup,
            original_filename=original_filename,
            file_path=str(dest_path),
            file_size=file_size,
            mime_type=file.content_type or "application/pdf",
            ocr_used=ocr_used,
            raw_extracted_text=extracted_text[:10000] if extracted_text else None,
            ai_raw_response=ai_data.model_dump(mode="json")
        )

        db.add(new_invoice)
        db.flush()

        # 9. Line Items
        for idx, item in enumerate(ai_data.line_items):
            db_item = InvoiceLineItem(
                invoice_id=new_invoice.id,
                item_index=idx,
                description=item.description or f"Item {idx+1}",
                hsn_sac=item.hsn_sac,
                quantity=to_decimal(item.quantity) or Decimal("1.000"),
                unit=item.unit or "UNIT",
                unit_price=to_decimal(item.unit_price),
                discount=to_decimal(item.discount),
                taxable_amount=to_decimal(item.taxable_amount),
                tax_rate=to_decimal(item.tax_rate),
                cgst_rate=to_decimal(item.cgst_rate),
                sgst_rate=to_decimal(item.sgst_rate),
                igst_rate=to_decimal(item.igst_rate),
                tax_amount=to_decimal(item.tax_amount),
                total_amount=to_decimal(item.total_amount)
            )
            db.add(db_item)

        db.commit()
        db.refresh(new_invoice)
        return invoice_repo.get_by_id(new_invoice.id) # loads relationships cleanly

    @classmethod
    def update_invoice(cls, db: Session, invoice: Invoice, data: InvoiceUpdate) -> Invoice:
        invoice_repo = InvoiceRepository(db)
        vendor_repo = VendorRepository(db)

        # Update core invoice fields
        update_dict = data.model_dump(exclude_unset=True, exclude={"line_items"})
        for field, value in update_dict.items():
            setattr(invoice, field, value)

        # If vendor name or gstin updated, update or find vendor
        if data.vendor_name_raw or data.vendor_gstin:
            v_name = invoice.vendor_name_raw
            v_gstin = invoice.vendor_gstin
            vendor = vendor_repo.find_or_create(name=v_name, gstin=v_gstin)
            invoice.vendor_id = vendor.id

        # Update line items if provided
        if data.line_items is not None:
            # Clear existing line items
            invoice.line_items.clear()
            for idx, item in enumerate(data.line_items):
                db_item = InvoiceLineItem(
                    invoice_id=invoice.id,
                    item_index=item.item_index if item.item_index is not None else idx,
                    description=item.description or f"Item {idx+1}",
                    hsn_sac=item.hsn_sac,
                    quantity=item.quantity if item.quantity is not None else Decimal("1.000"),
                    unit=item.unit or "UNIT",
                    unit_price=item.unit_price or Decimal("0.00"),
                    discount=item.discount or Decimal("0.00"),
                    taxable_amount=item.taxable_amount or Decimal("0.00"),
                    tax_rate=item.tax_rate or Decimal("0.00"),
                    cgst_rate=item.cgst_rate or Decimal("0.00"),
                    sgst_rate=item.sgst_rate or Decimal("0.00"),
                    igst_rate=item.igst_rate or Decimal("0.00"),
                    tax_amount=item.tax_amount or Decimal("0.00"),
                    total_amount=item.total_amount or Decimal("0.00")
                )
                invoice.line_items.append(db_item)

        # Re-run validation on updated values
        temp_data = ExtractedInvoiceData(
            invoice_number=invoice.invoice_number,
            vendor_name=invoice.vendor_name_raw,
            vendor_gstin=invoice.vendor_gstin,
            buyer_name=invoice.buyer_name,
            buyer_gstin=invoice.buyer_gstin,
            taxable_amount=invoice.taxable_amount,
            cgst_amount=invoice.cgst_amount,
            sgst_amount=invoice.sgst_amount,
            igst_amount=invoice.igst_amount,
            total_tax=invoice.total_tax,
            discount_amount=invoice.discount_amount,
            additional_charges=invoice.additional_charges,
            round_off=invoice.round_off,
            total_amount=invoice.total_amount
        )
        val_result = financial_validator.validate(temp_data)
        
        # If user explicitly confirms, set processing_status = "confirmed" and review_status = "manually_confirmed"
        if data.processing_status == "confirmed":
            invoice.processing_status = "confirmed"
            invoice.review_status = "manually_confirmed"
            invoice.validation_score = Decimal("100.00")
            invoice.discrepancy_flags = []
        else:
            invoice.validation_score = val_result["score"]
            invoice.discrepancy_flags = val_result["discrepancies"]

        db.commit()
        db.refresh(invoice)
        return invoice_repo.get_by_id(invoice.id)

    @classmethod
    def reprocess_invoice(cls, db: Session, invoice: Invoice) -> Invoice:
        file_path = Path(invoice.file_path)
        if not file_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Original invoice PDF file not found on disk"
            )

        extracted_text, needs_ocr = pdf_service.extract_text(file_path)
        ocr_used = False
        if needs_ocr and ocr_service.is_available():
            ocr_text = ocr_service.extract_text_from_pdf(file_path)
            if ocr_text:
                extracted_text = f"{extracted_text}\n\n{ocr_text}".strip()
                ocr_used = True

        ai_data = grok_service.extract_invoice(extracted_text)
        val_result = financial_validator.validate(ai_data)

        # Update metadata & raw content
        invoice.raw_extracted_text = extracted_text[:10000]
        invoice.ocr_used = ocr_used
        invoice.ai_raw_response = ai_data.model_dump(mode="json")

        # Update identifiers & vendor/buyer
        if ai_data.invoice_number:
            invoice.invoice_number = ai_data.invoice_number
        if ai_data.invoice_date:
            invoice.invoice_date = parse_date_safely(ai_data.invoice_date)
        if ai_data.due_date:
            invoice.due_date = parse_date_safely(ai_data.due_date)
        if ai_data.vendor_name:
            invoice.vendor_name_raw = ai_data.vendor_name
        if ai_data.vendor_gstin:
            invoice.vendor_gstin = ai_data.vendor_gstin.upper()
        if ai_data.vendor_address:
            invoice.vendor_address = ai_data.vendor_address
        if ai_data.buyer_name:
            invoice.buyer_name = ai_data.buyer_name
        if ai_data.buyer_gstin:
            invoice.buyer_gstin = ai_data.buyer_gstin.upper()
        if ai_data.buyer_address:
            invoice.buyer_address = ai_data.buyer_address
        if ai_data.place_of_supply:
            invoice.place_of_supply = ai_data.place_of_supply

        # Link/update vendor
        if invoice.vendor_name_raw:
            vendor_repo = VendorRepository(db)
            vendor = vendor_repo.find_or_create(
                name=invoice.vendor_name_raw,
                gstin=invoice.vendor_gstin,
                address=invoice.vendor_address
            )
            invoice.vendor_id = vendor.id

        # Update line items if extracted
        if ai_data.line_items:
            invoice.line_items.clear()
            for idx, item in enumerate(ai_data.line_items):
                db_item = InvoiceLineItem(
                    invoice_id=invoice.id,
                    item_index=idx,
                    description=item.description or f"Item {idx+1}",
                    hsn_sac=item.hsn_sac,
                    quantity=to_decimal(item.quantity) or Decimal("1.000"),
                    unit=item.unit or "UNIT",
                    unit_price=to_decimal(item.unit_price),
                    discount=to_decimal(item.discount),
                    taxable_amount=to_decimal(item.taxable_amount),
                    tax_rate=to_decimal(item.tax_rate),
                    cgst_rate=to_decimal(item.cgst_rate),
                    sgst_rate=to_decimal(item.sgst_rate),
                    igst_rate=to_decimal(item.igst_rate),
                    tax_amount=to_decimal(item.tax_amount),
                    total_amount=to_decimal(item.total_amount)
                )
                invoice.line_items.append(db_item)

        # Update financial totals
        invoice.taxable_amount = to_decimal(ai_data.taxable_amount)
        invoice.cgst_amount = to_decimal(ai_data.cgst_amount)
        invoice.sgst_amount = to_decimal(ai_data.sgst_amount)
        invoice.igst_amount = to_decimal(ai_data.igst_amount)
        invoice.total_tax = to_decimal(ai_data.total_tax)
        invoice.total_amount = to_decimal(ai_data.total_amount)
        invoice.discount_amount = to_decimal(ai_data.discount_amount)
        invoice.additional_charges = to_decimal(ai_data.additional_charges)
        invoice.round_off = to_decimal(ai_data.round_off)
        invoice.amount_paid = to_decimal(ai_data.amount_paid)
        invoice.balance_due = to_decimal(ai_data.balance_due)
        if ai_data.currency:
            invoice.currency = ai_data.currency

        # Update scores & review status
        invoice.validation_score = val_result["score"]
        invoice.discrepancy_flags = val_result["discrepancies"]
        invoice.review_status = val_result["review_status"]

        db.commit()
        db.refresh(invoice)
        return InvoiceRepository(db).get_by_id(invoice.id)

    @classmethod
    def export_csv(cls, invoices: List[Invoice]) -> str:
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Headers
        writer.writerow([
            "Invoice ID", "Invoice Number", "Date", "Due Date",
            "Vendor Name", "Vendor GSTIN", "Buyer Name", "Buyer GSTIN",
            "Taxable Amount", "CGST", "SGST", "IGST", "Total GST",
            "Discount", "Charges", "Total Amount", "Currency",
            "Payment Status", "Processing Status", "Review Status",
            "Validation Score", "Created At"
        ])
        
        for inv in invoices:
            writer.writerow([
                inv.id,
                inv.invoice_number,
                inv.invoice_date.strftime("%Y-%m-%d") if inv.invoice_date else "",
                inv.due_date.strftime("%Y-%m-%d") if inv.due_date else "",
                inv.vendor_name_raw,
                inv.vendor_gstin or "",
                inv.buyer_name or "",
                inv.buyer_gstin or "",
                f"{inv.taxable_amount:.2f}",
                f"{inv.cgst_amount:.2f}",
                f"{inv.sgst_amount:.2f}",
                f"{inv.igst_amount:.2f}",
                f"{inv.total_tax:.2f}",
                f"{inv.discount_amount:.2f}",
                f"{inv.additional_charges:.2f}",
                f"{inv.total_amount:.2f}",
                inv.currency,
                inv.payment_status,
                inv.processing_status,
                inv.review_status,
                f"{inv.validation_score:.1f}%",
                inv.created_at.strftime("%Y-%m-%d %H:%M:%S") if inv.created_at else ""
            ])
            
        return output.getvalue()

    @classmethod
    def export_pdf(cls, invoices: List[Invoice], company_name: str = "My Company") -> bytes:
        return pdf_report_service.generate_expense_report(invoices, company_name)

invoice_service = InvoiceService()
