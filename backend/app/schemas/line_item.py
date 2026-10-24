from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class InvoiceLineItemBase(BaseModel):
    item_index: int = 0
    description: str
    hsn_sac: Optional[str] = None
    quantity: Decimal = Decimal("1.000")
    unit: Optional[str] = "UNIT"
    unit_price: Decimal = Decimal("0.00")
    discount: Decimal = Decimal("0.00")
    taxable_amount: Decimal = Decimal("0.00")
    tax_rate: Decimal = Decimal("0.00")
    cgst_rate: Decimal = Decimal("0.00")
    sgst_rate: Decimal = Decimal("0.00")
    igst_rate: Decimal = Decimal("0.00")
    tax_amount: Decimal = Decimal("0.00")
    total_amount: Decimal = Decimal("0.00")

class InvoiceLineItemCreate(InvoiceLineItemBase):
    pass

class InvoiceLineItemUpdate(BaseModel):
    id: Optional[int] = None
    item_index: Optional[int] = None
    description: Optional[str] = None
    hsn_sac: Optional[str] = None
    quantity: Optional[Decimal] = None
    unit: Optional[str] = None
    unit_price: Optional[Decimal] = None
    discount: Optional[Decimal] = None
    taxable_amount: Optional[Decimal] = None
    tax_rate: Optional[Decimal] = None
    cgst_rate: Optional[Decimal] = None
    sgst_rate: Optional[Decimal] = None
    igst_rate: Optional[Decimal] = None
    tax_amount: Optional[Decimal] = None
    total_amount: Optional[Decimal] = None

class InvoiceLineItemResponse(InvoiceLineItemBase):
    id: int
    invoice_id: int

    model_config = ConfigDict(from_attributes=True)
