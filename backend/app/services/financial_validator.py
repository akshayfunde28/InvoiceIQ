import re
from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, List, Any, Optional, Tuple
from app.schemas.invoice import ExtractedInvoiceData
from app.schemas.line_item import InvoiceLineItemBase

GSTIN_REGEX = re.compile(r"^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$")

def to_decimal(val: Any) -> Decimal:
    if val is None:
        return Decimal("0.00")
    try:
        return Decimal(str(val)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    except Exception:
        return Decimal("0.00")

class FinancialValidator:
    ROUNDING_TOLERANCE = Decimal("0.10") # 10 paise tolerance for legitimate commercial rounding differences

    @classmethod
    def validate_gstin(cls, gstin: Optional[str]) -> Tuple[bool, str]:
        if not gstin or not gstin.strip():
            return True, ""
        clean_gstin = gstin.strip().upper()
        if len(clean_gstin) != 15:
            return False, f"GSTIN '{clean_gstin}' length is {len(clean_gstin)} characters (expected 15)"
        if not GSTIN_REGEX.match(clean_gstin):
            return False, f"GSTIN '{clean_gstin}' format does not match standard 15-character alphanumeric Indian GST pattern"
        return True, ""

    @classmethod
    def validate(cls, data: ExtractedInvoiceData) -> Dict[str, Any]:
        """
        Validates invoice financial figures, GST structure, and identifies discrepancies.
        Returns:
            {
                "score": Decimal (0 to 100),
                "review_status": "auto_verified" | "needs_review",
                "discrepancies": List[str]
            }
        """
        discrepancies: List[str] = []
        score = Decimal("100.00")

        # 1. Missing core identifiers
        if not data.invoice_number or not str(data.invoice_number).strip():
            discrepancies.append("Missing invoice number")
            score -= Decimal("25.00")

        if not data.vendor_name or not str(data.vendor_name).strip():
            discrepancies.append("Missing vendor name")
            score -= Decimal("20.00")

        # 2. GSTIN format validation
        if data.vendor_gstin:
            is_valid_v, v_msg = cls.validate_gstin(data.vendor_gstin)
            if not is_valid_v:
                discrepancies.append(f"Vendor {v_msg}")
                score -= Decimal("10.00")

        if data.buyer_gstin:
            is_valid_b, b_msg = cls.validate_gstin(data.buyer_gstin)
            if not is_valid_b:
                discrepancies.append(f"Buyer {b_msg}")
                score -= Decimal("5.00")

        # 3. Numeric values conversion
        taxable = to_decimal(data.taxable_amount)
        cgst = to_decimal(data.cgst_amount)
        sgst = to_decimal(data.sgst_amount)
        igst = to_decimal(data.igst_amount)
        total_tax = to_decimal(data.total_tax)
        discount = to_decimal(data.discount_amount)
        charges = to_decimal(data.additional_charges)
        round_off = to_decimal(data.round_off)
        grand_total = to_decimal(data.total_amount)

        # 4. GST Structure reconciliation (CGST + SGST vs IGST)
        calculated_tax = Decimal("0.00")
        has_intra_state = cgst > 0 or sgst > 0
        has_inter_state = igst > 0

        if has_intra_state and has_inter_state:
            discrepancies.append("Mixed GST structure: Both CGST/SGST and IGST are charged on the same invoice")
            score -= Decimal("15.00")

        if has_intra_state:
            # Under Indian GST, CGST and SGST rates and amounts must be equal
            cgst_sgst_diff = abs(cgst - sgst)
            if cgst_sgst_diff > cls.ROUNDING_TOLERANCE:
                discrepancies.append(f"CGST ({cgst}) and SGST ({sgst}) amounts do not match")
                score -= Decimal("10.00")
            calculated_tax = cgst + sgst

        elif has_inter_state:
            calculated_tax = igst

        # Compare tax sum with declared total tax
        if total_tax > 0 and calculated_tax > 0:
            tax_diff = abs(total_tax - calculated_tax)
            if tax_diff > cls.ROUNDING_TOLERANCE:
                discrepancies.append(
                    f"Tax components sum ({calculated_tax}) differs from total tax ({total_tax}) by {tax_diff}"
                )
                score -= Decimal("10.00")
        elif calculated_tax > 0 and total_tax == 0:
            total_tax = calculated_tax

        # 5. Grand Total equation: Taxable + Tax - Discount + Charges + RoundOff == Grand Total
        expected_total = (taxable + total_tax - discount + charges + round_off).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        if grand_total > 0 and taxable > 0:
            total_diff = abs(grand_total - expected_total)
            if total_diff > cls.ROUNDING_TOLERANCE:
                discrepancies.append(
                    f"Calculated total ({expected_total}) differs from declared total ({grand_total}) by {total_diff}"
                )
                score -= Decimal("20.00")

        # 6. Line Items validation
        if data.line_items:
            items_taxable_sum = sum((to_decimal(item.taxable_amount) for item in data.line_items), Decimal("0.00"))
            items_tax_sum = sum((to_decimal(item.tax_amount) for item in data.line_items), Decimal("0.00"))
            items_total_sum = sum((to_decimal(item.total_amount) for item in data.line_items), Decimal("0.00"))

            # Reconcile line items taxable sum with invoice taxable amount
            if taxable > 0 and items_taxable_sum > 0:
                line_taxable_diff = abs(taxable - items_taxable_sum)
                if line_taxable_diff > cls.ROUNDING_TOLERANCE:
                    discrepancies.append(
                        f"Line items taxable sum ({items_taxable_sum}) differs from invoice taxable amount ({taxable}) by {line_taxable_diff}"
                    )
                    score -= Decimal("10.00")

            # Reconcile line items tax sum with invoice total tax
            if total_tax > 0 and items_tax_sum > 0:
                line_tax_diff = abs(total_tax - items_tax_sum)
                if line_tax_diff > cls.ROUNDING_TOLERANCE:
                    discrepancies.append(
                        f"Line items tax sum ({items_tax_sum}) differs from invoice total tax ({total_tax}) by {line_tax_diff}"
                    )
                    score -= Decimal("10.00")

        # Clamp score between 0 and 100
        score = max(Decimal("0.00"), min(score, Decimal("100.00")))
        review_status = "auto_verified" if score >= Decimal("90.00") and len(discrepancies) == 0 else "needs_review"

        return {
            "score": score,
            "review_status": review_status,
            "discrepancies": discrepancies
        }
financial_validator = FinancialValidator()
