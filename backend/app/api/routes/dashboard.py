from typing import List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.user import User
from app.repositories.invoice_repo import InvoiceRepository
from app.schemas.dashboard import (
    DashboardSummaryResponse, 
    MonthlyExpenseItem, 
    GSTBreakdownResponse, 
    VendorExpenseItem,
    CategoryExpenseItem
)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = InvoiceRepository(db)
    return repo.get_dashboard_summary(user_id=current_user.id)

@router.get("/monthly-expenses", response_model=List[MonthlyExpenseItem])
def get_monthly_expenses(
    limit: int = Query(12, ge=1, le=24),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = InvoiceRepository(db)
    return repo.get_monthly_expenses(user_id=current_user.id, limit=limit)

@router.get("/gst-breakdown", response_model=GSTBreakdownResponse)
def get_gst_breakdown(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = InvoiceRepository(db)
    return repo.get_gst_breakdown(user_id=current_user.id)

@router.get("/vendor-expenses", response_model=List[VendorExpenseItem])
def get_vendor_expenses(
    limit: int = Query(5, ge=1, le=20),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = InvoiceRepository(db)
    return repo.get_vendor_expenses(user_id=current_user.id, limit=limit)

@router.get("/category-expenses", response_model=List[CategoryExpenseItem])
def get_category_expenses(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    repo = InvoiceRepository(db)
    return repo.get_category_expenses(user_id=current_user.id)
