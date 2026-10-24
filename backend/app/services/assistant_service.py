import json
from decimal import Decimal
from typing import Dict, Any, List
from openai import OpenAI
from sqlalchemy.orm import Session
from sqlalchemy import select, func, desc

from app.core.config import settings
from app.core.logging import logger
from app.models.invoice import Invoice
from app.models.vendor import Vendor
from app.models.user import User

ASSISTANT_SYSTEM_PROMPT = """You are InvoiceIQ's AI Expense & Tax Auditor Assistant.
Your job is to answer the user's financial questions accurately based ONLY on the provided verified database context.

Rules:
1. Ground your answers strictly in the provided database figures. Never make up numbers, vendors, or invoices.
2. Present monetary numbers cleanly in Indian Rupees (₹) with appropriate commas and two decimals (e.g. ₹1,47,500.00).
3. If asked about GST, break down CGST, SGST, and IGST where applicable.
4. Keep answers concise, executive, friendly, and easy to read using markdown bullet points and bold highlights.
5. If the database context does not contain the answer, politely state what is currently recorded in their system.
"""

class AssistantService:
    @staticmethod
    def answer_query(db: Session, user: User, question: str) -> str:
        # 1. Fetch live metrics from database for this user
        invoices = db.execute(
            select(Invoice).where(Invoice.user_id == user.id)
        ).scalars().all()

        if not invoices:
            # Check if there are unassigned invoices to assist the user
            invoices = db.execute(select(Invoice)).scalars().all()

        total_spend = sum((inv.total_amount for inv in invoices), Decimal("0.00"))
        total_taxable = sum((inv.taxable_amount for inv in invoices), Decimal("0.00"))
        total_gst = sum((inv.total_tax for inv in invoices), Decimal("0.00"))
        total_cgst = sum((inv.cgst_amount for inv in invoices), Decimal("0.00"))
        total_sgst = sum((inv.sgst_amount for inv in invoices), Decimal("0.00"))
        total_igst = sum((inv.igst_amount for inv in invoices), Decimal("0.00"))

        # Vendor totals
        vendor_totals: Dict[str, Decimal] = {}
        category_totals: Dict[str, Decimal] = {}
        monthly_totals: Dict[str, Decimal] = {}
        pending_review_count = 0

        for inv in invoices:
            v_name = inv.vendor_name_raw or "Unknown"
            vendor_totals[v_name] = vendor_totals.get(v_name, Decimal("0.00")) + inv.total_amount

            cat = inv.category or "General Expenses"
            category_totals[cat] = category_totals.get(cat, Decimal("0.00")) + inv.total_amount

            m_key = inv.invoice_date.strftime("%B %Y") if inv.invoice_date else "Unknown Date"
            monthly_totals[m_key] = monthly_totals.get(m_key, Decimal("0.00")) + inv.total_amount

            if inv.review_status == "needs_review":
                pending_review_count += 1

        top_vendors = sorted(vendor_totals.items(), key=lambda x: x[1], reverse=True)[:5]
        top_categories = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
        monthly_sorted = sorted(monthly_totals.items(), key=lambda x: x[1], reverse=True)

        recent_invoices_sample = [
            {
                "invoice_number": inv.invoice_number,
                "date": str(inv.invoice_date),
                "vendor": inv.vendor_name_raw,
                "total": float(inv.total_amount),
                "gst": float(inv.total_tax),
                "status": inv.processing_status,
                "review_status": inv.review_status,
                "category": inv.category
            }
            for inv in invoices[:10]
        ]

        context_data = {
            "user_name": user.name,
            "company_name": user.company_name,
            "total_invoices_count": len(invoices),
            "pending_review_count": pending_review_count,
            "total_expenditure_inr": float(total_spend),
            "total_taxable_amount_inr": float(total_taxable),
            "total_gst_paid_inr": float(total_gst),
            "cgst_inr": float(total_cgst),
            "sgst_inr": float(total_sgst),
            "igst_inr": float(total_igst),
            "monthly_expenditure_ranking": [
                {"month": m, "amount_inr": float(a)} for m, a in monthly_sorted
            ],
            "top_vendors_by_spend": [
                {"vendor": v, "amount_inr": float(a)} for v, a in top_vendors
            ],
            "category_breakdown": [
                {"category": c, "amount_inr": float(a)} for c, a in top_categories
            ],
            "recent_invoices": recent_invoices_sample
        }

        user_prompt = f"""User Question: "{question}"

Verified Database Context:
{json.dumps(context_data, indent=2)}

Please answer the user's question clearly and accurately using the numbers in the context above."""

        try:
            client = OpenAI(
                api_key=settings.XAI_API_KEY,
                base_url=settings.XAI_BASE_URL,
                timeout=45.0,
            )

            response = client.chat.completions.create(
                model=settings.XAI_MODEL,
                messages=[
                    {"role": "system", "content": ASSISTANT_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,
            )

            answer = response.choices[0].message.content.strip()
            return answer

        except Exception as e:
            logger.error(f"Assistant LLM call failed: {str(e)}")
            # Fallback deterministic answer generator
            q_lower = question.lower()
            if "highest" in q_lower or "which month" in q_lower:
                if monthly_sorted:
                    top_m, top_a = monthly_sorted[0]
                    return f"Based on your database records, **{top_m}** had the highest expenses at **₹{top_a:,.2f}**."
                return "No monthly expense records are currently stored."
            elif "how much gst" in q_lower or "total gst" in q_lower:
                return (
                    f"You have paid a total of **₹{total_gst:,.2f}** in GST across {len(invoices)} invoices.\n\n"
                    f"- **CGST**: ₹{total_cgst:,.2f}\n"
                    f"- **SGST**: ₹{total_sgst:,.2f}\n"
                    f"- **IGST**: ₹{total_igst:,.2f}"
                )
            elif "vendor" in q_lower:
                if top_vendors:
                    top_v, top_va = top_vendors[0]
                    return f"Your top spending vendor is **{top_v}** with a cumulative spend of **₹{top_va:,.2f}**."
                return "No vendor records are currently stored."
            else:
                return (
                    f"Here is your financial summary across **{len(invoices)} invoices**:\n\n"
                    f"- **Total Spend**: ₹{total_spend:,.2f}\n"
                    f"- **Total Taxable Base**: ₹{total_taxable:,.2f}\n"
                    f"- **Total GST Paid**: ₹{total_gst:,.2f}\n"
                    f"- **Pending Reviews**: {pending_review_count} invoice(s)"
                )

assistant_service = AssistantService()
