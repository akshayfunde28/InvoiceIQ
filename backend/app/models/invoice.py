from datetime import datetime, date
from decimal import Decimal
from typing import List, Optional, Any
from sqlalchemy import (
    String, Text, Numeric, Integer, Boolean, Date, DateTime, 
    ForeignKey, JSON, func, Index
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base

class Invoice(Base):
    __tablename__ = "invoices"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), 
        index=True, 
        nullable=True
    )
    vendor_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("vendors.id", ondelete="SET NULL"), 
        index=True, 
        nullable=True
    )
    
    # Core invoice identifiers
    invoice_number: Mapped[str] = mapped_column(String(100), index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(100), default="General Expenses", index=True, nullable=False)
    invoice_date: Mapped[Optional[date]] = mapped_column(Date, index=True, nullable=True)
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    
    # Vendor & Buyer snapshot details
    vendor_name_raw: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    vendor_gstin: Mapped[Optional[str]] = mapped_column(String(15), index=True, nullable=True)
    vendor_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    
    buyer_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    buyer_gstin: Mapped[Optional[str]] = mapped_column(String(15), nullable=True)
    buyer_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    place_of_supply: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Financial breakdown (Strict Decimal / Numeric precision)
    taxable_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"), nullable=False)
    cgst_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"), nullable=False)
    sgst_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"), nullable=False)
    igst_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"), nullable=False)
    total_tax: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"), nullable=False)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"), nullable=False)
    additional_charges: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"), nullable=False)
    round_off: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"), nullable=False)
    total_amount: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"), index=True, nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="INR", nullable=False)
    
    # Payment status
    amount_paid: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"), nullable=False)
    balance_due: Mapped[Decimal] = mapped_column(Numeric(14, 2), default=Decimal("0.00"), nullable=False)
    payment_status: Mapped[str] = mapped_column(String(50), default="unpaid", nullable=False) # unpaid, paid, partially_paid
    
    # Processing & review statuses
    processing_status: Mapped[str] = mapped_column(String(50), default="extracted", nullable=False) # extracted, confirmed, failed
    review_status: Mapped[str] = mapped_column(String(50), default="auto_verified", nullable=False) # auto_verified, needs_review, manually_confirmed
    validation_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("100.00"), nullable=False)
    discrepancy_flags: Mapped[Optional[Any]] = mapped_column(JSON, default=list, nullable=True)
    is_duplicate: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # File storage references
    original_filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_path: Mapped[str] = mapped_column(String(500), nullable=False)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    mime_type: Mapped[str] = mapped_column(String(100), default="application/pdf", nullable=False)
    ocr_used: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Raw extraction traces (for debugging & manual review verification)
    raw_extracted_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    ai_raw_response: Mapped[Optional[Any]] = mapped_column(JSON, nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        index=True,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        onupdate=func.now(), 
        nullable=False
    )

    # Relationships
    user: Mapped[Optional["User"]] = relationship("User", back_populates="invoices")
    vendor: Mapped[Optional["Vendor"]] = relationship("Vendor", back_populates="invoices")
    line_items: Mapped[List["InvoiceLineItem"]] = relationship(
        "InvoiceLineItem", 
        back_populates="invoice", 
        cascade="all, delete-orphan",
        order_by="InvoiceLineItem.item_index"
    )

    __table_args__ = (
        Index("ix_invoices_vendor_number", "vendor_name_raw", "invoice_number"),
    )
