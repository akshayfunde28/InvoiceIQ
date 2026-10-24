import pymupdf
from pathlib import Path

def create_sample_pdf():
    out_dir = Path("sample_invoices")
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "sample_gst_invoice.pdf"

    doc = pymupdf.open()
    page = doc.new_page(width=595, height=842) # A4 format

    # Colors
    c_primary = (0.09, 0.09, 0.16)
    c_indigo = (0.39, 0.40, 0.95)
    c_slate = (0.40, 0.45, 0.55)

    # Header
    page.insert_text((50, 60), "TAX INVOICE", fontsize=18, fontname="helv", color=c_indigo)
    page.insert_text((50, 80), "Original for Recipient", fontsize=9, fontname="helv", color=c_slate)

    # Supplier Box
    page.draw_rect(pymupdf.Rect(50, 100, 300, 200), color=(0.85, 0.88, 0.92), width=1)
    page.insert_text((60, 118), "SUPPLIER (VENDOR):", fontsize=9, fontname="helv", color=c_slate)
    page.insert_text((60, 135), "Zenith Cloud Services India Pvt Ltd", fontsize=11, fontname="helv", color=c_primary)
    page.insert_text((60, 150), "Tower B, Prestige Tech Park, Marathahalli", fontsize=9, fontname="helv", color=c_slate)
    page.insert_text((60, 165), "Bangalore, Karnataka - 560103", fontsize=9, fontname="helv", color=c_slate)
    page.insert_text((60, 185), "GSTIN: 29AABCZ9988F1Z4", fontsize=10, fontname="helv", color=c_primary)

    # Invoice Details Box
    page.draw_rect(pymupdf.Rect(320, 100, 545, 200), color=(0.85, 0.88, 0.92), width=1)
    page.insert_text((330, 118), "INVOICE DETAILS:", fontsize=9, fontname="helv", color=c_slate)
    page.insert_text((330, 138), "Invoice Number: ZCS-2025-0982", fontsize=10, fontname="helv", color=c_primary)
    page.insert_text((330, 155), "Invoice Date: 2025-02-18", fontsize=10, fontname="helv", color=c_primary)
    page.insert_text((330, 172), "Due Date: 2025-03-18", fontsize=10, fontname="helv", color=c_primary)
    page.insert_text((330, 189), "Place of Supply: Karnataka (29)", fontsize=9, fontname="helv", color=c_slate)

    # Buyer Box
    page.draw_rect(pymupdf.Rect(50, 215, 545, 285), color=(0.85, 0.88, 0.92), width=1)
    page.insert_text((60, 233), "BILL TO (BUYER):", fontsize=9, fontname="helv", color=c_slate)
    page.insert_text((60, 250), "InvoiceIQ Global Technologies", fontsize=11, fontname="helv", color=c_primary)
    page.insert_text((60, 265), "100 Feet Road, Indiranagar, Bangalore - 560038 | GSTIN: 29AABCB9999M1Z3", fontsize=9, fontname="helv", color=c_slate)

    # Table Header
    y = 310
    page.draw_rect(pymupdf.Rect(50, y, 545, y + 24), color=(0.24, 0.27, 0.35), fill=(0.95, 0.96, 0.98), width=0.5)
    page.insert_text((55, y + 16), "Item Description", fontsize=9, fontname="helv", color=c_primary)
    page.insert_text((250, y + 16), "HSN/SAC", fontsize=9, fontname="helv", color=c_primary)
    page.insert_text((320, y + 16), "Qty", fontsize=9, fontname="helv", color=c_primary)
    page.insert_text((360, y + 16), "Rate", fontsize=9, fontname="helv", color=c_primary)
    page.insert_text((420, y + 16), "GST %", fontsize=9, fontname="helv", color=c_primary)
    page.insert_text((480, y + 16), "Total", fontsize=9, fontname="helv", color=c_primary)

    # Item 1
    y = 340
    page.insert_text((55, y), "Enterprise Kubernetes Cluster Hosting (Standard Tier)", fontsize=9, fontname="helv", color=c_primary)
    page.insert_text((250, y), "998315", fontsize=9, fontname="helv", color=c_slate)
    page.insert_text((320, y), "1.00", fontsize=9, fontname="helv", color=c_slate)
    page.insert_text((360, y), "50,000.00", fontsize=9, fontname="helv", color=c_slate)
    page.insert_text((420, y), "18.0%", fontsize=9, fontname="helv", color=c_slate)
    page.insert_text((480, y), "50,000.00", fontsize=9, fontname="helv", color=c_primary)

    # Item 2
    y = 365
    page.insert_text((55, y), "24x7 Priority Infrastructure Support & SLA", fontsize=9, fontname="helv", color=c_primary)
    page.insert_text((250, y), "998313", fontsize=9, fontname="helv", color=c_slate)
    page.insert_text((320, y), "1.00", fontsize=9, fontname="helv", color=c_slate)
    page.insert_text((360, y), "15,000.00", fontsize=9, fontname="helv", color=c_slate)
    page.insert_text((420, y), "18.0%", fontsize=9, fontname="helv", color=c_slate)
    page.insert_text((480, y), "15,000.00", fontsize=9, fontname="helv", color=c_primary)

    # Totals Box
    y_box = 420
    page.draw_rect(pymupdf.Rect(320, y_box, 545, y_box + 140), color=(0.85, 0.88, 0.92), width=1)
    page.insert_text((330, y_box + 25), "Taxable Amount:", fontsize=10, fontname="helv", color=c_slate)
    page.insert_text((465, y_box + 25), "INR 65,000.00", fontsize=10, fontname="helv", color=c_primary)

    page.insert_text((330, y_box + 48), "CGST (9.0%):", fontsize=10, fontname="helv", color=c_slate)
    page.insert_text((465, y_box + 48), "INR 5,850.00", fontsize=10, fontname="helv", color=c_primary)

    page.insert_text((330, y_box + 71), "SGST (9.0%):", fontsize=10, fontname="helv", color=c_slate)
    page.insert_text((465, y_box + 71), "INR 5,850.00", fontsize=10, fontname="helv", color=c_primary)

    page.insert_text((330, y_box + 94), "Total GST (18.0%):", fontsize=10, fontname="helv", color=c_slate)
    page.insert_text((465, y_box + 94), "INR 11,700.00", fontsize=10, fontname="helv", color=c_primary)

    page.draw_line(pymupdf.Point(325, y_box + 105), pymupdf.Point(540, y_box + 105), color=(0.85, 0.88, 0.92), width=1)
    page.insert_text((330, y_box + 125), "Grand Total:", fontsize=12, fontname="helv", color=c_indigo)
    page.insert_text((460, y_box + 125), "INR 76,700.00", fontsize=12, fontname="helv", color=c_indigo)

    # Footer
    page.insert_text((50, 780), "This is a computer generated invoice and requires no physical signature.", fontsize=8, fontname="helv", color=c_slate)
    page.insert_text((50, 795), "Zenith Cloud Services India Pvt Ltd • Indiranagar, Bangalore", fontsize=8, fontname="helv", color=c_slate)

    doc.save(str(out_path))
    doc.close()
    print(f"Sample PDF created at {out_path}")

if __name__ == "__main__":
    create_sample_pdf()
