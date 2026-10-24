from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Any
from pydantic import BaseModel, ConfigDict, Field
from app.schemas.line_item import (
    InvoiceLineItemBase, 
    InvoiceLineItemCreate, 
    InvoiceLineItemUpdate, 
    InvoiceLineItemResponse
)
from app.schemas.vendor import VendorResponse

class InvoiceBase(BaseModel):
    invoice_number: str
    category: str = "General Expenses"
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    
    vendor_name_raw: str
    vendor_gstin: Optional[str] = None
    vendor_address: Optional[str] = None
    
    buyer_name: Optional[str] = None
    buyer_gstin: Optional[str] = None
    buyer_address: Optional[str] = None
    place_of_supply: Optional[str] = None
    
    taxable_amount: Decimal = Decimal("0.00")
    cgst_amount: Decimal = Decimal("0.00")
    sgst_amount: Decimal = Decimal("0.00")
    igst_amount: Decimal = Decimal("0.00")
    total_tax: Decimal = Decimal("0.00")
    discount_amount: Decimal = Decimal("0.00")
    additional_charges: Decimal = Decimal("0.00")
    round_off: Decimal = Decimal("0.00")
    total_amount: Decimal = Decimal("0.00")
    currency: str = "INR"
    
    amount_paid: Decimal = Decimal("0.00")
    balance_due: Decimal = Decimal("0.00")
    payment_status: str = "unpaid"
    
    processing_status: str = "extracted"
    review_status: str = "auto_verified"

class ExtractedInvoiceData(BaseModel):
    invoice_number: Optional[str] = None
    invoice_date: Optional[str] = None # raw date string from AI
    due_date: Optional[str] = None
    
    vendor_name: Optional[str] = None
    vendor_gstin: Optional[str] = None
    vendor_address: Optional[str] = None
    vendor_pan: Optional[str] = None
    vendor_phone: Optional[str] = None
    vendor_email: Optional[str] = None
    
    buyer_name: Optional[str] = None
    buyer_gstin: Optional[str] = None
    buyer_address: Optional[str] = None
    place_of_supply: Optional[str] = None
    
    line_items: List[InvoiceLineItemBase] = Field(default_factory=list)
    
    taxable_amount: Optional[Decimal] = None
    cgst_amount: Optional[Decimal] = None
    sgst_amount: Optional[Decimal] = None
    igst_amount: Optional[Decimal] = None
    total_tax: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    additional_charges: Optional[Decimal] = None
    round_off: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None
    currency: Optional[str] = "INR"
    category: Optional[str] = "General Expenses"
    
    amount_paid: Optional[Decimal] = None
    balance_due: Optional[Decimal] = None
    payment_status: Optional[str] = "unpaid"

class InvoiceCreate(InvoiceBase):
    line_items: List[InvoiceLineItemCreate] = Field(default_factory=list)
    validation_score: Decimal = Decimal("100.00")
    discrepancy_flags: List[str] = Field(default_factory=list)
    is_duplicate: bool = False
    original_filename: str
    file_path: str
    file_size: Optional[int] = None
    mime_type: str = "application/pdf"
    ocr_used: bool = False
    raw_extracted_text: Optional[str] = None
    ai_raw_response: Optional[Any] = None

class InvoiceUpdate(BaseModel):
    invoice_number: Optional[str] = None
    category: Optional[str] = None
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    vendor_name_raw: Optional[str] = None
    vendor_gstin: Optional[str] = None
    vendor_address: Optional[str] = None
    buyer_name: Optional[str] = None
    buyer_gstin: Optional[str] = None
    buyer_address: Optional[str] = None
    place_of_supply: Optional[str] = None
    taxable_amount: Optional[Decimal] = None
    cgst_amount: Optional[Decimal] = None
    sgst_amount: Optional[Decimal] = None
    igst_amount: Optional[Decimal] = None
    total_tax: Optional[Decimal] = None
    discount_amount: Optional[Decimal] = None
    additional_charges: Optional[Decimal] = None
    round_off: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None
    currency: Optional[str] = None
    amount_paid: Optional[Decimal] = None
    balance_due: Optional[Decimal] = None
    payment_status: Optional[str] = None
    processing_status: Optional[str] = None
    review_status: Optional[str] = None
    line_items: Optional[List[InvoiceLineItemUpdate]] = None

class InvoiceResponse(InvoiceBase):
    id: int
    user_id: Optional[int] = None
    vendor_id: Optional[int] = None
    validation_score: Decimal
    discrepancy_flags: Optional[Any] = None
    is_duplicate: bool
    original_filename: str
    file_size: Optional[int] = None
    mime_type: str
    ocr_used: bool
    created_at: datetime
    updated_at: datetime
    line_items: List[InvoiceLineItemResponse] = Field(default_factory=list)
    vendor: Optional[VendorResponse] = None

    model_config = ConfigDict(from_attributes=True)

class InvoiceListResponse(BaseModel):
    items: List[InvoiceResponse]
    total: int
    page: int
    limit: int
    total_pages: int
