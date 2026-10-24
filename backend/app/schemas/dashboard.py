from decimal import Decimal
from typing import List, Dict, Optional
from pydantic import BaseModel

class DashboardSummaryResponse(BaseModel):
    total_expenses: Decimal
    total_taxable: Decimal
    total_gst: Decimal
    total_cgst: Decimal
    total_sgst: Decimal
    total_igst: Decimal
    total_invoices: int
    pending_reviews: int
    confirmed_invoices: int
    average_invoice_value: Decimal

class MonthlyExpenseItem(BaseModel):
    month: str # e.g. "2025-01" or "Jan 2025"
    total_amount: Decimal
    taxable_amount: Decimal
    gst_amount: Decimal
    invoice_count: int

class GSTBreakdownResponse(BaseModel):
    total_cgst: Decimal
    total_sgst: Decimal
    total_igst: Decimal
    total_gst: Decimal
    cgst_percentage: Decimal
    sgst_percentage: Decimal
    igst_percentage: Decimal
    slabs: List[Dict[str, Decimal]] # e.g. [{"rate": 18, "taxable": ..., "tax": ...}]

class VendorExpenseItem(BaseModel):
    vendor_name: str
    gstin: Optional[str] = None
    total_amount: Decimal
    invoice_count: int
    percentage: Decimal

class CategoryExpenseItem(BaseModel):
    category: str
    total_amount: Decimal
    invoice_count: int
    percentage: Decimal
