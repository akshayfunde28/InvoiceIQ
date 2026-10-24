from decimal import Decimal
from app.services.financial_validator import financial_validator, to_decimal
from app.schemas.invoice import ExtractedInvoiceData
from app.schemas.line_item import InvoiceLineItemBase

def test_financial_validator_perfect_intra_state_invoice():
    data = ExtractedInvoiceData(
        invoice_number="INV-2025-001",
        vendor_name="Acme Tech Solutions Pvt Ltd",
        vendor_gstin="29ABCDE1234F1Z5", # Valid 15-char Karnataka GSTIN
        buyer_name="Client Corp India",
        buyer_gstin="29XYZAB5678C1Z2",
        taxable_amount=Decimal("1000.00"),
        cgst_amount=Decimal("90.00"),
        sgst_amount=Decimal("90.00"),
        igst_amount=Decimal("0.00"),
        total_tax=Decimal("180.00"),
        discount_amount=Decimal("0.00"),
        additional_charges=Decimal("0.00"),
        round_off=Decimal("0.00"),
        total_amount=Decimal("1180.00"),
        line_items=[
            InvoiceLineItemBase(
                description="Software consulting services",
                taxable_amount=Decimal("1000.00"),
                tax_amount=Decimal("180.00"),
                total_amount=Decimal("1180.00")
            )
        ]
    )

    result = financial_validator.validate(data)
    assert result["score"] == Decimal("100.00")
    assert result["review_status"] == "auto_verified"
    assert len(result["discrepancies"]) == 0

def test_financial_validator_cgst_sgst_mismatch():
    data = ExtractedInvoiceData(
        invoice_number="INV-2025-002",
        vendor_name="Acme Tech",
        vendor_gstin="29ABCDE1234F1Z5",
        taxable_amount=Decimal("1000.00"),
        cgst_amount=Decimal("90.00"),
        sgst_amount=Decimal("100.00"), # Mismatched SGST
        total_tax=Decimal("190.00"),
        total_amount=Decimal("1190.00")
    )

    result = financial_validator.validate(data)
    assert result["review_status"] == "needs_review"
    assert any("CGST" in d and "SGST" in d for d in result["discrepancies"])

def test_financial_validator_invalid_gstin_flagged():
    data = ExtractedInvoiceData(
        invoice_number="INV-2025-003",
        vendor_name="Acme Tech",
        vendor_gstin="INVALID_GSTIN_123", # Invalid GSTIN
        taxable_amount=Decimal("500.00"),
        igst_amount=Decimal("90.00"),
        total_tax=Decimal("90.00"),
        total_amount=Decimal("590.00")
    )

    result = financial_validator.validate(data)
    assert result["review_status"] == "needs_review"
    assert any("GSTIN" in d for d in result["discrepancies"])

def test_financial_validator_total_calculation_discrepancy():
    data = ExtractedInvoiceData(
        invoice_number="INV-2025-004",
        vendor_name="Acme Tech",
        taxable_amount=Decimal("1000.00"),
        total_tax=Decimal("180.00"),
        total_amount=Decimal("1500.00") # False total
    )

    result = financial_validator.validate(data)
    assert result["review_status"] == "needs_review"
    assert any("Calculated total" in d for d in result["discrepancies"])
