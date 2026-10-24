import io
from decimal import Decimal
import pymupdf
from unittest.mock import patch
from app.schemas.invoice import ExtractedInvoiceData
from app.schemas.line_item import InvoiceLineItemBase

def create_mock_pdf_bytes():
    doc = pymupdf.open()
    page = doc.new_page()
    page.insert_text((50, 72), "TAX INVOICE INV-8888 Vendor: Innovatech India", fontsize=12)
    pdf_bytes = doc.tobytes()
    doc.close()
    return pdf_bytes

def test_health_endpoint(client):
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["database"] == "healthy"

def test_invoice_upload_and_crud_workflow(client):
    pdf_bytes = create_mock_pdf_bytes()
    mock_extracted = ExtractedInvoiceData(
        invoice_number="INV-2025-500",
        invoice_date="2025-02-15",
        due_date="2025-03-15",
        vendor_name="Innovatech India Pvt Ltd",
        vendor_gstin="27ABCDE1234F1Z9",
        buyer_name="Client Solutions Ltd",
        buyer_gstin="27XYZAB5678C1Z3",
        taxable_amount=Decimal("2000.00"),
        cgst_amount=Decimal("180.00"),
        sgst_amount=Decimal("180.00"),
        igst_amount=Decimal("0.00"),
        total_tax=Decimal("360.00"),
        total_amount=Decimal("2360.00"),
        line_items=[
            InvoiceLineItemBase(
                description="Cloud Hosting Monthly Subscription",
                hsn_sac="998315",
                quantity=Decimal("1.000"),
                unit="UNIT",
                unit_price=Decimal("2000.00"),
                taxable_amount=Decimal("2000.00"),
                tax_rate=Decimal("18.00"),
                cgst_rate=Decimal("9.00"),
                sgst_rate=Decimal("9.00"),
                tax_amount=Decimal("360.00"),
                total_amount=Decimal("2360.00")
            )
        ]
    )

    # 1. Upload invoice with mocked Grok response
    with patch("app.services.grok_service.grok_service.extract_invoice", return_value=mock_extracted):
        files = {"file": ("innovatech_invoice.pdf", io.BytesIO(pdf_bytes), "application/pdf")}
        upload_resp = client.post("/api/invoices/upload", files=files)
        assert upload_resp.status_code == 201
        inv_data = upload_resp.json()
        assert inv_data["invoice_number"] == "INV-2025-500"
        assert inv_data["vendor_name_raw"] == "Innovatech India Pvt Ltd"
        assert float(inv_data["total_amount"]) == 2360.00
        inv_id = inv_data["id"]

    # 2. Get invoice by ID
    get_resp = client.get(f"/api/invoices/{inv_id}")
    assert get_resp.status_code == 200
    assert len(get_resp.json()["line_items"]) == 1

    # 3. Update invoice (e.g. mark as confirmed)
    update_payload = {
        "processing_status": "confirmed",
        "payment_status": "paid",
        "amount_paid": 2360.00
    }
    put_resp = client.put(f"/api/invoices/{inv_id}", json=update_payload)
    assert put_resp.status_code == 200
    assert put_resp.json()["processing_status"] == "confirmed"
    assert put_resp.json()["payment_status"] == "paid"

    # 4. List invoices with search
    list_resp = client.get("/api/invoices?search=Innovatech")
    assert list_resp.status_code == 200
    assert list_resp.json()["total"] >= 1

    # 5. CSV export
    csv_resp = client.get("/api/invoices/export/csv")
    assert csv_resp.status_code == 200
    assert "INV-2025-500" in csv_resp.text

    # 6. Delete invoice
    del_resp = client.delete(f"/api/invoices/{inv_id}")
    assert del_resp.status_code == 204

    # Verify deleted
    get_deleted = client.get(f"/api/invoices/{inv_id}")
    assert get_deleted.status_code == 404
