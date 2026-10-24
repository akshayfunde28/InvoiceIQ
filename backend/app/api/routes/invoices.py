from datetime import date
from decimal import Decimal
from pathlib import Path
from typing import Optional, List
from fastapi import (
    APIRouter, Depends, UploadFile, File, Query, 
    HTTPException, status, Response
)
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.repositories.invoice_repo import InvoiceRepository
from app.services.invoice_service import invoice_service
from app.schemas.invoice import (
    InvoiceResponse, 
    InvoiceListResponse, 
    InvoiceUpdate
)

router = APIRouter(prefix="/invoices", tags=["Invoices"])

SUPPORTED_EXTENSIONS = {".pdf", ".png", ".jpg", ".jpeg", ".webp"}

@router.post("/upload", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
def upload_invoice(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    ext = Path(file.filename or "").suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format '{ext}'. Allowed: PDF, PNG, JPG, JPEG, WEBP."
        )
    return invoice_service.process_upload(db, file, user=current_user)

@router.get("", response_model=InvoiceListResponse)
def list_invoices(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: Optional[str] = Query(None),
    vendor_id: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    review_status: Optional[str] = Query(None),
    processing_status: Optional[str] = Query(None),
    payment_status: Optional[str] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    min_amount: Optional[Decimal] = Query(None),
    max_amount: Optional[Decimal] = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = InvoiceRepository(db)
    items, total = repo.list_invoices(
        user_id=current_user.id,
        page=page,
        limit=limit,
        search=search,
        vendor_id=vendor_id,
        category=category,
        review_status=review_status,
        processing_status=processing_status,
        payment_status=payment_status,
        from_date=from_date,
        to_date=to_date,
        min_amount=min_amount,
        max_amount=max_amount,
        sort_by=sort_by,
        sort_order=sort_order
    )
    total_pages = (total + limit - 1) // limit if total > 0 else 1
    return {
        "items": items,
        "total": total,
        "page": page,
        "limit": limit,
        "total_pages": total_pages
    }

@router.get("/export/csv")
def export_invoices_csv(
    search: Optional[str] = Query(None),
    vendor_id: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    review_status: Optional[str] = Query(None),
    processing_status: Optional[str] = Query(None),
    payment_status: Optional[str] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    min_amount: Optional[Decimal] = Query(None),
    max_amount: Optional[Decimal] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = InvoiceRepository(db)
    items, _ = repo.list_invoices(
        user_id=current_user.id,
        page=1,
        limit=10000,
        search=search,
        vendor_id=vendor_id,
        category=category,
        review_status=review_status,
        processing_status=processing_status,
        payment_status=payment_status,
        from_date=from_date,
        to_date=to_date,
        min_amount=min_amount,
        max_amount=max_amount
    )
    csv_content = invoice_service.export_csv(items)
    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=InvoiceIQ_Expenses.csv"}
    )

@router.get("/export/pdf")
def export_invoices_pdf(
    invoice_ids: Optional[str] = Query(None), # Comma separated IDs if selected
    search: Optional[str] = Query(None),
    vendor_id: Optional[int] = Query(None),
    category: Optional[str] = Query(None),
    review_status: Optional[str] = Query(None),
    processing_status: Optional[str] = Query(None),
    payment_status: Optional[str] = Query(None),
    from_date: Optional[date] = Query(None),
    to_date: Optional[date] = Query(None),
    min_amount: Optional[Decimal] = Query(None),
    max_amount: Optional[Decimal] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = InvoiceRepository(db)
    if invoice_ids:
        id_list = [int(i.strip()) for i in invoice_ids.split(",") if i.strip().isdigit()]
        items = []
        for inv_id in id_list:
            inv = repo.get_by_id(inv_id, user_id=current_user.id)
            if inv:
                items.append(inv)
    else:
        items, _ = repo.list_invoices(
            user_id=current_user.id,
            page=1,
            limit=500,
            search=search,
            vendor_id=vendor_id,
            category=category,
            review_status=review_status,
            processing_status=processing_status,
            payment_status=payment_status,
            from_date=from_date,
            to_date=to_date,
            min_amount=min_amount,
            max_amount=max_amount
        )

    pdf_bytes = invoice_service.export_pdf(items, company_name=current_user.company_name or "InvoiceIQ")
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=InvoiceIQ_Expense_Report.pdf"}
    )

@router.get("/{invoice_id}", response_model=InvoiceResponse)
def get_invoice(
    invoice_id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = InvoiceRepository(db)
    invoice = repo.get_by_id(invoice_id, user_id=current_user.id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice with ID {invoice_id} not found"
        )
    return invoice

@router.put("/{invoice_id}", response_model=InvoiceResponse)
def update_invoice(
    invoice_id: int, 
    data: InvoiceUpdate, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = InvoiceRepository(db)
    invoice = repo.get_by_id(invoice_id, user_id=current_user.id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice with ID {invoice_id} not found"
        )
    return invoice_service.update_invoice(db, invoice, data)

@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_invoice(
    invoice_id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = InvoiceRepository(db)
    invoice = repo.get_by_id(invoice_id, user_id=current_user.id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice with ID {invoice_id} not found"
        )
    
    try:
        f_path = Path(invoice.file_path)
        if f_path.exists():
            f_path.unlink()
    except Exception:
        pass

    repo.delete(invoice)
    return None

@router.get("/{invoice_id}/file")
def get_invoice_file(
    invoice_id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = InvoiceRepository(db)
    invoice = repo.get_by_id(invoice_id, user_id=current_user.id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice with ID {invoice_id} not found"
        )
    
    file_path = Path(invoice.file_path)
    if not file_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice file does not exist on disk"
        )

    return FileResponse(
        path=str(file_path),
        media_type=invoice.mime_type or "application/pdf",
        filename=invoice.original_filename
    )

@router.post("/{invoice_id}/reprocess", response_model=InvoiceResponse)
def reprocess_invoice(
    invoice_id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = InvoiceRepository(db)
    invoice = repo.get_by_id(invoice_id, user_id=current_user.id)
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Invoice with ID {invoice_id} not found"
        )
    return invoice_service.reprocess_invoice(db, invoice)
