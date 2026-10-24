import pymupdf
from datetime import datetime
from decimal import Decimal
from typing import List
from app.models.invoice import Invoice

class PDFReportService:
    @staticmethod
    def generate_expense_report(invoices: List[Invoice], company_name: str = "My Company") -> bytes:
        doc = pymupdf.open()
        
        # Calculate summary metrics
        total_spend = sum((inv.total_amount for inv in invoices), Decimal("0.00"))
        total_taxable = sum((inv.taxable_amount for inv in invoices), Decimal("0.00"))
        total_gst = sum((inv.total_tax for inv in invoices), Decimal("0.00"))
        total_cgst = sum((inv.cgst_amount for inv in invoices), Decimal("0.00"))
        total_sgst = sum((inv.sgst_amount for inv in invoices), Decimal("0.00"))
        total_igst = sum((inv.igst_amount for inv in invoices), Decimal("0.00"))

        rows_per_page = 14
        total_invoices = len(invoices)
        total_pages = max(1, (total_invoices + rows_per_page - 1) // rows_per_page)

        # Palette
        c_primary = (0.06, 0.09, 0.16)     # Slate 900
        c_indigo = (0.39, 0.40, 0.95)      # Indigo 600
        c_slate = (0.40, 0.45, 0.55)       # Slate 500
        c_border = (0.88, 0.91, 0.94)      # Slate 200
        c_bg = (0.97, 0.98, 0.99)          # Slate 50

        for page_idx in range(total_pages):
            page = doc.new_page(width=595, height=842) # A4
            
            # 1. Top Header Banner
            page.draw_rect(pymupdf.Rect(40, 35, 555, 95), color=c_border, fill=c_bg, width=0.8)
            page.insert_text((55, 62), "InvoiceIQ — Expense & GST Audit Report", fontsize=15, fontname="helv", color=c_indigo)
            page.insert_text((55, 80), f"Company: {company_name}  |  Generated on: {datetime.now().strftime('%d %b %Y, %I:%M %p')}", fontsize=9, fontname="helv", color=c_slate)

            # 2. Executive Summary Metrics (Page 1 only)
            y_start = 110
            if page_idx == 0:
                # 3 Metric Cards
                card_w = 150
                gap = 12.5
                
                # Card 1: Total Spend
                x1 = 40
                page.draw_rect(pymupdf.Rect(x1, y_start, x1 + card_w, y_start + 55), color=c_border, fill=(1, 1, 1), width=0.8)
                page.insert_text((x1 + 12, y_start + 20), "TOTAL EXPENDITURE", fontsize=7.5, fontname="helv", color=c_slate)
                page.insert_text((x1 + 12, y_start + 42), f"INR {total_spend:,.2f}", fontsize=12, fontname="helv", color=c_primary)

                # Card 2: Taxable Base
                x2 = x1 + card_w + gap
                page.draw_rect(pymupdf.Rect(x2, y_start, x2 + card_w, y_start + 55), color=c_border, fill=(1, 1, 1), width=0.8)
                page.insert_text((x2 + 12, y_start + 20), "TAXABLE BASE AMOUNT", fontsize=7.5, fontname="helv", color=c_slate)
                page.insert_text((x2 + 12, y_start + 42), f"INR {total_taxable:,.2f}", fontsize=12, fontname="helv", color=c_primary)

                # Card 3: Total GST
                x3 = x2 + card_w + gap
                page.draw_rect(pymupdf.Rect(x3, y_start, x3 + card_w, y_start + 55), color=c_border, fill=(1, 1, 1), width=0.8)
                page.insert_text((x3 + 12, y_start + 20), "TOTAL GST RECONCILED", fontsize=7.5, fontname="helv", color=c_slate)
                page.insert_text((x3 + 12, y_start + 42), f"INR {total_gst:,.2f}", fontsize=12, fontname="helv", color=c_indigo)

                y_table_header = y_start + 75
            else:
                y_table_header = y_start

            # 3. Invoices Table Header
            page.draw_rect(pymupdf.Rect(40, y_table_header, 555, y_table_header + 22), color=c_primary, fill=c_primary, width=0)
            page.insert_text((45, y_table_header + 15), "#", fontsize=8, fontname="helv", color=(1, 1, 1))
            page.insert_text((65, y_table_header + 15), "Invoice #", fontsize=8, fontname="helv", color=(1, 1, 1))
            page.insert_text((140, y_table_header + 15), "Date", fontsize=8, fontname="helv", color=(1, 1, 1))
            page.insert_text((200, y_table_header + 15), "Vendor Name", fontsize=8, fontname="helv", color=(1, 1, 1))
            page.insert_text((340, y_table_header + 15), "Category", fontsize=8, fontname="helv", color=(1, 1, 1))
            page.insert_text((420, y_table_header + 15), "GST (INR)", fontsize=8, fontname="helv", color=(1, 1, 1))
            page.insert_text((490, y_table_header + 15), "Total (INR)", fontsize=8, fontname="helv", color=(1, 1, 1))

            # 4. Invoices Table Rows
            start_i = page_idx * rows_per_page
            end_i = min(start_i + rows_per_page, total_invoices)
            curr_y = y_table_header + 24

            for r_idx in range(start_i, end_i):
                inv = invoices[r_idx]
                row_h = 32
                bg_color = (0.98, 0.99, 1.0) if (r_idx % 2 == 1) else (1, 1, 1)
                page.draw_rect(pymupdf.Rect(40, curr_y, 555, curr_y + row_h), color=c_border, fill=bg_color, width=0.5)

                inv_num = inv.invoice_number[:12]
                inv_date = inv.invoice_date.strftime("%d/%m/%Y") if inv.invoice_date else "—"
                vendor = (inv.vendor_name_raw or "Unknown")[:22]
                cat = (inv.category or "General")[:14]
                gst_val = f"{inv.total_tax:,.2f}"
                tot_val = f"{inv.total_amount:,.2f}"

                page.insert_text((45, curr_y + 19), str(r_idx + 1), fontsize=8, fontname="helv", color=c_slate)
                page.insert_text((65, curr_y + 19), inv_num, fontsize=8, fontname="helv", color=c_primary)
                page.insert_text((140, curr_y + 19), inv_date, fontsize=8, fontname="helv", color=c_slate)
                page.insert_text((200, curr_y + 19), vendor, fontsize=8, fontname="helv", color=c_primary)
                page.insert_text((340, curr_y + 19), cat, fontsize=8, fontname="helv", color=c_slate)
                page.insert_text((420, curr_y + 19), gst_val, fontsize=8, fontname="helv", color=c_slate)
                page.insert_text((490, curr_y + 19), tot_val, fontsize=8, fontname="helv", color=c_indigo)

                curr_y += row_h

            # 5. Footer
            page.draw_line(pymupdf.Point(40, 800), pymupdf.Point(555, 800), color=c_border, width=0.8)
            page.insert_text((40, 815), "Confidential • Official Expense & GST Audit Report generated by InvoiceIQ AI", fontsize=7.5, fontname="helv", color=c_slate)
            page.insert_text((500, 815), f"Page {page_idx + 1} of {total_pages}", fontsize=7.5, fontname="helv", color=c_slate)

        pdf_bytes = doc.tobytes()
        doc.close()
        return pdf_bytes

pdf_report_service = PDFReportService()
