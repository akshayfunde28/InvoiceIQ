from datetime import date, datetime
from decimal import Decimal
from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy import select, func, and_, or_, desc, asc
from sqlalchemy.orm import Session, joinedload
from app.models.invoice import Invoice
from app.models.line_item import InvoiceLineItem
from app.models.vendor import Vendor
from app.schemas.invoice import InvoiceUpdate

class InvoiceRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_id(self, invoice_id: int, user_id: Optional[int] = None) -> Optional[Invoice]:
        stmt = select(Invoice).options(
            joinedload(Invoice.line_items), 
            joinedload(Invoice.vendor)
        ).where(Invoice.id == invoice_id)

        if user_id is not None:
            stmt = stmt.where(or_(Invoice.user_id == user_id, Invoice.user_id.is_(None)))

        return self.db.execute(stmt).unique().scalar_one_or_none()

    def check_duplicate(
        self, 
        vendor_name: str, 
        invoice_number: str, 
        user_id: Optional[int] = None,
        exclude_id: Optional[int] = None
    ) -> bool:
        if not vendor_name or not invoice_number:
            return False
            
        filters = [
            func.lower(Invoice.vendor_name_raw) == vendor_name.strip().lower(),
            func.lower(Invoice.invoice_number) == invoice_number.strip().lower()
        ]
        if user_id is not None:
            filters.append(or_(Invoice.user_id == user_id, Invoice.user_id.is_(None)))
        if exclude_id is not None:
            filters.append(Invoice.id != exclude_id)
            
        stmt = select(func.count(Invoice.id)).where(and_(*filters))
        count = self.db.execute(stmt).scalar() or 0
        return count > 0

    def list_invoices(
        self,
        user_id: Optional[int] = None,
        page: int = 1,
        limit: int = 10,
        search: Optional[str] = None,
        vendor_id: Optional[int] = None,
        category: Optional[str] = None,
        review_status: Optional[str] = None,
        processing_status: Optional[str] = None,
        payment_status: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        min_amount: Optional[Decimal] = None,
        max_amount: Optional[Decimal] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc"
    ) -> Tuple[List[Invoice], int]:
        stmt = select(Invoice).options(
            joinedload(Invoice.line_items), 
            joinedload(Invoice.vendor)
        )
        
        filters = []
        if user_id is not None:
            filters.append(or_(Invoice.user_id == user_id, Invoice.user_id.is_(None)))
        if search:
            s = f"%{search.strip().lower()}%"
            filters.append(
                or_(
                    func.lower(Invoice.invoice_number).like(s),
                    func.lower(Invoice.vendor_name_raw).like(s),
                    func.lower(Invoice.vendor_gstin).like(s),
                    func.lower(Invoice.buyer_name).like(s),
                )
            )
        if vendor_id:
            filters.append(Invoice.vendor_id == vendor_id)
        if category:
            filters.append(Invoice.category == category)
        if review_status:
            filters.append(Invoice.review_status == review_status)
        if processing_status:
            filters.append(Invoice.processing_status == processing_status)
        if payment_status:
            filters.append(Invoice.payment_status == payment_status)
        if from_date:
            filters.append(Invoice.invoice_date >= from_date)
        if to_date:
            filters.append(Invoice.invoice_date <= to_date)
        if min_amount is not None:
            filters.append(Invoice.total_amount >= min_amount)
        if max_amount is not None:
            filters.append(Invoice.total_amount <= max_amount)

        if filters:
            stmt = stmt.where(and_(*filters))

        # Count total
        count_stmt = select(func.count(func.distinct(Invoice.id)))
        if filters:
            count_stmt = count_stmt.where(and_(*filters))
        total = self.db.execute(count_stmt).scalar() or 0

        # Sorting
        sort_col = getattr(Invoice, sort_by, Invoice.created_at)
        if sort_order.lower() == "asc":
            stmt = stmt.order_by(asc(sort_col))
        else:
            stmt = stmt.order_by(desc(sort_col))

        # Pagination
        offset = (page - 1) * limit
        stmt = stmt.offset(offset).limit(limit)

        results = list(self.db.execute(stmt).unique().scalars().all())
        return results, total

    def delete(self, invoice: Invoice) -> None:
        vendor_id = invoice.vendor_id
        self.db.delete(invoice)
        self.db.commit()

        # If the vendor has no other invoices left, auto-delete the orphaned vendor
        if vendor_id is not None:
            remaining = self.db.execute(
                select(func.count(Invoice.id)).where(Invoice.vendor_id == vendor_id)
            ).scalar() or 0
            if remaining == 0:
                orphaned_vendor = self.db.execute(
                    select(Vendor).where(Vendor.id == vendor_id)
                ).scalar_one_or_none()
                if orphaned_vendor:
                    self.db.delete(orphaned_vendor)
                    self.db.commit()

    # Dashboard Aggregations (User-scoped)
    def get_dashboard_summary(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        stmt = select(
            func.coalesce(func.sum(Invoice.total_amount), 0).label("total_expenses"),
            func.coalesce(func.sum(Invoice.taxable_amount), 0).label("total_taxable"),
            func.coalesce(func.sum(Invoice.total_tax), 0).label("total_gst"),
            func.coalesce(func.sum(Invoice.cgst_amount), 0).label("total_cgst"),
            func.coalesce(func.sum(Invoice.sgst_amount), 0).label("total_sgst"),
            func.coalesce(func.sum(Invoice.igst_amount), 0).label("total_igst"),
            func.count(Invoice.id).label("total_invoices"),
            func.count(func.nullif(Invoice.review_status != "needs_review", True)).label("pending_reviews"),
            func.count(func.nullif(Invoice.processing_status != "confirmed", True)).label("confirmed_invoices"),
            func.coalesce(func.avg(Invoice.total_amount), 0).label("avg_invoice_value")
        )
        if user_id is not None:
            stmt = stmt.where(or_(Invoice.user_id == user_id, Invoice.user_id.is_(None)))

        row = self.db.execute(stmt).one()
        return {
            "total_expenses": Decimal(str(row.total_expenses)),
            "total_taxable": Decimal(str(row.total_taxable)),
            "total_gst": Decimal(str(row.total_gst)),
            "total_cgst": Decimal(str(row.total_cgst)),
            "total_sgst": Decimal(str(row.total_sgst)),
            "total_igst": Decimal(str(row.total_igst)),
            "total_invoices": int(row.total_invoices),
            "pending_reviews": int(row.pending_reviews),
            "confirmed_invoices": int(row.confirmed_invoices),
            "average_invoice_value": Decimal(str(row.avg_invoice_value)).quantize(Decimal("0.01")),
        }

    def get_monthly_expenses(self, user_id: Optional[int] = None, limit: int = 12) -> List[Dict[str, Any]]:
        month_expr = func.to_char(
            func.coalesce(Invoice.invoice_date, Invoice.created_at), 
            "YYYY-MM"
        )
        stmt = select(
            month_expr.label("month"),
            func.coalesce(func.sum(Invoice.total_amount), 0).label("total_amount"),
            func.coalesce(func.sum(Invoice.taxable_amount), 0).label("taxable_amount"),
            func.coalesce(func.sum(Invoice.total_tax), 0).label("gst_amount"),
            func.count(Invoice.id).label("invoice_count")
        )
        if user_id is not None:
            stmt = stmt.where(or_(Invoice.user_id == user_id, Invoice.user_id.is_(None)))

        stmt = stmt.group_by(month_expr).order_by(month_expr.asc()).limit(limit)

        rows = self.db.execute(stmt).all()
        return [
            {
                "month": r.month,
                "total_amount": Decimal(str(r.total_amount)),
                "taxable_amount": Decimal(str(r.taxable_amount)),
                "gst_amount": Decimal(str(r.gst_amount)),
                "invoice_count": int(r.invoice_count)
            }
            for r in rows if r.month
        ]

    def get_gst_breakdown(self, user_id: Optional[int] = None) -> Dict[str, Any]:
        stmt = select(
            func.coalesce(func.sum(Invoice.cgst_amount), 0).label("cgst"),
            func.coalesce(func.sum(Invoice.sgst_amount), 0).label("sgst"),
            func.coalesce(func.sum(Invoice.igst_amount), 0).label("igst"),
            func.coalesce(func.sum(Invoice.total_tax), 0).label("total")
        )
        if user_id is not None:
            stmt = stmt.where(or_(Invoice.user_id == user_id, Invoice.user_id.is_(None)))

        row = self.db.execute(stmt).one()
        cgst = Decimal(str(row.cgst))
        sgst = Decimal(str(row.sgst))
        igst = Decimal(str(row.igst))
        total = Decimal(str(row.total))

        cgst_pct = (cgst / total * 100).quantize(Decimal("0.1")) if total > 0 else Decimal("0.0")
        sgst_pct = (sgst / total * 100).quantize(Decimal("0.1")) if total > 0 else Decimal("0.0")
        igst_pct = (igst / total * 100).quantize(Decimal("0.1")) if total > 0 else Decimal("0.0")

        # Tax slabs from line items
        slab_stmt = select(
            InvoiceLineItem.tax_rate,
            func.coalesce(func.sum(InvoiceLineItem.taxable_amount), 0).label("taxable"),
            func.coalesce(func.sum(InvoiceLineItem.tax_amount), 0).label("tax")
        ).join(Invoice, InvoiceLineItem.invoice_id == Invoice.id)

        if user_id is not None:
            slab_stmt = slab_stmt.where(or_(Invoice.user_id == user_id, Invoice.user_id.is_(None)))

        slab_stmt = slab_stmt.group_by(InvoiceLineItem.tax_rate).order_by(InvoiceLineItem.tax_rate.asc())

        slab_rows = self.db.execute(slab_stmt).all()
        slabs = [
            {
                "rate": Decimal(str(s.tax_rate)),
                "taxable": Decimal(str(s.taxable)),
                "tax": Decimal(str(s.tax))
            }
            for s in slab_rows if s.tax_rate > 0
        ]

        return {
            "total_cgst": cgst,
            "total_sgst": sgst,
            "total_igst": igst,
            "total_gst": total,
            "cgst_percentage": cgst_pct,
            "sgst_percentage": sgst_pct,
            "igst_percentage": igst_pct,
            "slabs": slabs
        }

    def get_vendor_expenses(self, user_id: Optional[int] = None, limit: int = 5) -> List[Dict[str, Any]]:
        total_stmt = select(func.coalesce(func.sum(Invoice.total_amount), 0))
        if user_id is not None:
            total_stmt = total_stmt.where(or_(Invoice.user_id == user_id, Invoice.user_id.is_(None)))
        grand_total = Decimal(str(self.db.execute(total_stmt).scalar() or 0))

        stmt = select(
            Invoice.vendor_name_raw.label("vendor_name"),
            Invoice.vendor_gstin.label("gstin"),
            func.coalesce(func.sum(Invoice.total_amount), 0).label("total_amount"),
            func.count(Invoice.id).label("invoice_count")
        )
        if user_id is not None:
            stmt = stmt.where(or_(Invoice.user_id == user_id, Invoice.user_id.is_(None)))

        stmt = stmt.group_by(Invoice.vendor_name_raw, Invoice.vendor_gstin)\
         .order_by(desc("total_amount"))\
         .limit(limit)

        rows = self.db.execute(stmt).all()
        return [
            {
                "vendor_name": r.vendor_name,
                "gstin": r.gstin,
                "total_amount": Decimal(str(r.total_amount)),
                "invoice_count": int(r.invoice_count),
                "percentage": (
                    (Decimal(str(r.total_amount)) / grand_total * 100).quantize(Decimal("0.1"))
                    if grand_total > 0 else Decimal("0.0")
                )
            }
            for r in rows
        ]

    def get_category_expenses(self, user_id: Optional[int] = None) -> List[Dict[str, Any]]:
        total_stmt = select(func.coalesce(func.sum(Invoice.total_amount), 0))
        if user_id is not None:
            total_stmt = total_stmt.where(or_(Invoice.user_id == user_id, Invoice.user_id.is_(None)))
        grand_total = Decimal(str(self.db.execute(total_stmt).scalar() or 0))

        stmt = select(
            Invoice.category.label("category"),
            func.coalesce(func.sum(Invoice.total_amount), 0).label("total_amount"),
            func.count(Invoice.id).label("invoice_count")
        )
        if user_id is not None:
            stmt = stmt.where(or_(Invoice.user_id == user_id, Invoice.user_id.is_(None)))

        stmt = stmt.group_by(Invoice.category).order_by(desc("total_amount"))
        rows = self.db.execute(stmt).all()

        return [
            {
                "category": r.category or "General Expenses",
                "total_amount": Decimal(str(r.total_amount)),
                "invoice_count": int(r.invoice_count),
                "percentage": (
                    (Decimal(str(r.total_amount)) / grand_total * 100).quantize(Decimal("0.1"))
                    if grand_total > 0 else Decimal("0.0")
                )
            }
            for r in rows
        ]
