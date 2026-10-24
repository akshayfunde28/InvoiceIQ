import sys
from pathlib import Path
backend_dir = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(backend_dir))

from datetime import date, timedelta
from decimal import Decimal
from app.db.session import SessionLocal
from app.models.user import User
from app.models.vendor import Vendor
from app.models.invoice import Invoice
from app.models.line_item import InvoiceLineItem
from app.core.security import get_password_hash

def seed_data():
    db = SessionLocal()
    try:
        # 0. Ensure Demo User exists
        demo_user = db.query(User).filter(User.email == "demo@invoiceiq.com").first()
        if not demo_user:
            demo_user = User(
                email="demo@invoiceiq.com",
                name="Akshay Funde",
                hashed_password=get_password_hash("demo123"),
                company_name="InvoiceIQ Tech Enterprises"
            )
            db.add(demo_user)
            db.commit()
            db.refresh(demo_user)
            print(f"Created demo user: {demo_user.email} (ID: {demo_user.id})")
        else:
            print(f"Demo user exists: {demo_user.email} (ID: {demo_user.id})")

        # Check if already seeded
        existing_count = db.query(Invoice).count()
        if existing_count > 0:
            # Update any invoices with NULL user_id to demo_user.id
            db.query(Invoice).filter(Invoice.user_id.is_(None)).update({"user_id": demo_user.id})
            db.commit()
            print(f"Database already has {existing_count} invoices. Linked to demo user {demo_user.id}.")
            return

        print("Seeding initial Indian GST invoices...")

        # 1. Vendor 1: Intra-state (Karnataka: 29)
        v1 = Vendor(
            name="Infoscribe Digital Solutions Pvt Ltd",
            gstin="29AABCI1234F1Z5",
            pan="AABCI1234F",
            address="Level 4, Embassy Tech Village, Outer Ring Road, Bangalore - 560103",
            city="Bangalore",
            state="Karnataka",
            state_code="29",
            email="accounts@infoscribe.in",
            phone="+91 80 4123 4567"
        )
        db.add(v1)
        db.flush()

        # 2. Vendor 2: Inter-state (Maharashtra: 27)
        v2 = Vendor(
            name="Apex Cloud Infrastructure Ltd",
            gstin="27AAACA9876K1Z1",
            pan="AAACA9876K",
            address="Godrej One, 5th Floor, Pirojshanagar, Vikhroli East, Mumbai - 400079",
            city="Mumbai",
            state="Maharashtra",
            state_code="27",
            email="billing@apexcloud.co.in",
            phone="+91 22 6123 7890"
        )
        db.add(v2)
        db.flush()

        # 3. Vendor 3: Intra-state Office Supplies
        v3 = Vendor(
            name="Paramount Office Systems",
            gstin="29AAPFP4521P1Z8",
            pan="AAPFP4521P",
            address="12/A, Brigade Road, Ashok Nagar, Bangalore - 560025",
            city="Bangalore",
            state="Karnataka",
            state_code="29",
            email="sales@paramountoffice.in",
            phone="+91 80 2558 9988"
        )
        db.add(v3)
        db.flush()

        today = date.today()

        # Invoice 1: Intra-state 18% (9% CGST + 9% SGST)
        inv1 = Invoice(
            vendor_id=v1.id,
            invoice_number="INV-2025-0891",
            invoice_date=today - timedelta(days=28),
            due_date=today + timedelta(days=2),
            vendor_name_raw=v1.name,
            vendor_gstin=v1.gstin,
            vendor_address=v1.address,
            buyer_name="InvoiceIQ Enterprises Ltd",
            buyer_gstin="29AABCB9999M1Z3",
            buyer_address="Indiranagar 100ft Road, Bangalore - 560038",
            place_of_supply="Karnataka (29)",
            taxable_amount=Decimal("125000.00"),
            cgst_amount=Decimal("11250.00"),
            sgst_amount=Decimal("11250.00"),
            igst_amount=Decimal("0.00"),
            total_tax=Decimal("22500.00"),
            discount_amount=Decimal("0.00"),
            additional_charges=Decimal("0.00"),
            round_off=Decimal("0.00"),
            total_amount=Decimal("147500.00"),
            currency="INR",
            amount_paid=Decimal("147500.00"),
            balance_due=Decimal("0.00"),
            payment_status="paid",
            processing_status="confirmed",
            review_status="auto_verified",
            validation_score=Decimal("100.00"),
            discrepancy_flags=[],
            is_duplicate=False,
            original_filename="infoscribe_software_license.pdf",
            file_path="uploads/invoices/seed_infoscribe.pdf",
            file_size=245000,
            mime_type="application/pdf",
            ocr_used=False
        )
        db.add(inv1)
        db.flush()

        db.add_all([
            InvoiceLineItem(
                invoice_id=inv1.id,
                item_index=0,
                description="Annual SaaS Platform Enterprise License",
                hsn_sac="998314",
                quantity=Decimal("1.000"),
                unit="YEAR",
                unit_price=Decimal("100000.00"),
                taxable_amount=Decimal("100000.00"),
                tax_rate=Decimal("18.00"),
                cgst_rate=Decimal("9.00"),
                sgst_rate=Decimal("9.00"),
                tax_amount=Decimal("18000.00"),
                total_amount=Decimal("118000.00")
            ),
            InvoiceLineItem(
                invoice_id=inv1.id,
                item_index=1,
                description="Custom API Integration & Onboarding",
                hsn_sac="998315",
                quantity=Decimal("1.000"),
                unit="SVC",
                unit_price=Decimal("25000.00"),
                taxable_amount=Decimal("25000.00"),
                tax_rate=Decimal("18.00"),
                cgst_rate=Decimal("9.00"),
                sgst_rate=Decimal("9.00"),
                tax_amount=Decimal("4500.00"),
                total_amount=Decimal("29500.00")
            )
        ])

        # Invoice 2: Inter-state 18% (18% IGST)
        inv2 = Invoice(
            vendor_id=v2.id,
            invoice_number="APX-2025-4421",
            invoice_date=today - timedelta(days=12),
            due_date=today + timedelta(days=18),
            vendor_name_raw=v2.name,
            vendor_gstin=v2.gstin,
            vendor_address=v2.address,
            buyer_name="InvoiceIQ Enterprises Ltd",
            buyer_gstin="29AABCB9999M1Z3",
            buyer_address="Indiranagar 100ft Road, Bangalore - 560038",
            place_of_supply="Karnataka (29)",
            taxable_amount=Decimal("78400.00"),
            cgst_amount=Decimal("0.00"),
            sgst_amount=Decimal("0.00"),
            igst_amount=Decimal("14112.00"),
            total_tax=Decimal("14112.00"),
            discount_amount=Decimal("0.00"),
            additional_charges=Decimal("0.00"),
            round_off=Decimal("0.00"),
            total_amount=Decimal("92512.00"),
            currency="INR",
            amount_paid=Decimal("0.00"),
            balance_due=Decimal("92512.00"),
            payment_status="unpaid",
            processing_status="confirmed",
            review_status="auto_verified",
            validation_score=Decimal("100.00"),
            discrepancy_flags=[],
            is_duplicate=False,
            original_filename="apex_cloud_compute_nodes.pdf",
            file_path="uploads/invoices/seed_apex.pdf",
            file_size=198000,
            mime_type="application/pdf",
            ocr_used=False
        )
        db.add(inv2)
        db.flush()

        db.add_all([
            InvoiceLineItem(
                invoice_id=inv2.id,
                item_index=0,
                description="Dedicated GPU Compute Cluster (Monthly)",
                hsn_sac="998315",
                quantity=Decimal("2.000"),
                unit="NODE",
                unit_price=Decimal("39200.00"),
                taxable_amount=Decimal("78400.00"),
                tax_rate=Decimal("18.00"),
                igst_rate=Decimal("18.00"),
                tax_amount=Decimal("14112.00"),
                total_amount=Decimal("92512.00")
            )
        ])

        # Invoice 3: Hardware with 12% GST
        inv3 = Invoice(
            vendor_id=v3.id,
            invoice_number="POS-2025-0104",
            invoice_date=today - timedelta(days=5),
            due_date=today + timedelta(days=25),
            vendor_name_raw=v3.name,
            vendor_gstin=v3.gstin,
            vendor_address=v3.address,
            buyer_name="InvoiceIQ Enterprises Ltd",
            buyer_gstin="29AABCB9999M1Z3",
            buyer_address="Indiranagar 100ft Road, Bangalore - 560038",
            place_of_supply="Karnataka (29)",
            taxable_amount=Decimal("45000.00"),
            cgst_amount=Decimal("2700.00"),
            sgst_amount=Decimal("2700.00"),
            igst_amount=Decimal("0.00"),
            total_tax=Decimal("5400.00"),
            discount_amount=Decimal("0.00"),
            additional_charges=Decimal("0.00"),
            round_off=Decimal("0.00"),
            total_amount=Decimal("50400.00"),
            currency="INR",
            amount_paid=Decimal("25000.00"),
            balance_due=Decimal("25400.00"),
            payment_status="partially_paid",
            processing_status="confirmed",
            review_status="auto_verified",
            validation_score=Decimal("100.00"),
            discrepancy_flags=[],
            is_duplicate=False,
            original_filename="paramount_ergonomic_chairs.pdf",
            file_path="uploads/invoices/seed_paramount.pdf",
            file_size=154000,
            mime_type="application/pdf",
            ocr_used=False
        )
        db.add(inv3)
        db.flush()

        db.add_all([
            InvoiceLineItem(
                invoice_id=inv3.id,
                item_index=0,
                description="Ergonomic Executive Mesh Chairs",
                hsn_sac="940130",
                quantity=Decimal("5.000"),
                unit="PCS",
                unit_price=Decimal("9000.00"),
                taxable_amount=Decimal("45000.00"),
                tax_rate=Decimal("12.00"),
                cgst_rate=Decimal("6.00"),
                sgst_rate=Decimal("6.00"),
                tax_amount=Decimal("5400.00"),
                total_amount=Decimal("50400.00")
            )
        ])

        db.commit()
        print("Successfully seeded 3 realistic GST invoices into invoiceiq_db!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    seed_data()
