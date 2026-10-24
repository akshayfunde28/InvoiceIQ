import json
import re
from typing import Dict, Any, Optional
from openai import OpenAI
from app.core.config import settings
from app.core.logging import logger
from app.schemas.invoice import ExtractedInvoiceData

SYSTEM_PROMPT = """You are an expert AI accounting and Indian GST tax auditor specializing in invoice data extraction.
Extract all relevant invoice information from the provided document text into a single, clean JSON object.

Follow these strict rules:
1. Return ONLY a valid JSON object matching the requested schema. Do not include markdown preamble or conversational text.
2. If any field is missing, not mentioned, or cannot be determined with certainty, set it to null. NEVER make up or fabricate missing numbers or names.
3. Dates must be formatted as YYYY-MM-DD whenever possible. If only year or partial date is known, format what is clear.
4. For monetary numbers, provide pure numbers without currency symbols (e.g. 1500.50 instead of "₹1,500.50").
5. Handle Indian GST rules accurately:
   - Identify whether taxes are split into CGST + SGST (intra-state) or IGST (inter-state).
   - Extract 15-character GSTIN codes for vendor and buyer accurately.
   - Extract HSN/SAC codes for line items where present.
6. The JSON structure MUST contain:
{
  "invoice_number": "string or null",
  "invoice_date": "YYYY-MM-DD or null",
  "due_date": "YYYY-MM-DD or null",
  "vendor_name": "string or null",
  "vendor_gstin": "string (15 chars) or null",
  "vendor_pan": "string or null",
  "vendor_address": "string or null",
  "vendor_phone": "string or null",
  "vendor_email": "string or null",
  "buyer_name": "string or null",
  "buyer_gstin": "string (15 chars) or null",
  "buyer_address": "string or null",
  "place_of_supply": "string or null",
  "line_items": [
    {
      "item_index": 0,
      "description": "string",
      "hsn_sac": "string or null",
      "quantity": 1.0,
      "unit": "UNIT or PCS or KG or null",
      "unit_price": 0.0,
      "discount": 0.0,
      "taxable_amount": 0.0,
      "tax_rate": 0.0,
      "cgst_rate": 0.0,
      "sgst_rate": 0.0,
      "igst_rate": 0.0,
      "tax_amount": 0.0,
      "total_amount": 0.0
    }
  ],
  "taxable_amount": 0.0,
  "cgst_amount": 0.0,
  "sgst_amount": 0.0,
  "igst_amount": 0.0,
  "total_tax": 0.0,
  "discount_amount": 0.0,
  "additional_charges": 0.0,
  "round_off": 0.0,
  "total_amount": 0.0,
  "currency": "INR",
  "amount_paid": 0.0,
  "balance_due": 0.0,
  "payment_status": "unpaid or paid or partially_paid"
}
"""

class GrokService:
    def __init__(self):
        self._client: Optional[OpenAI] = None

    @property
    def client(self) -> OpenAI:
        if self._client is None:
            self._client = OpenAI(
                api_key=settings.XAI_API_KEY,
                base_url=settings.XAI_BASE_URL,
                timeout=60.0,
            )
        return self._client

    def extract_invoice(self, document_text: str) -> ExtractedInvoiceData:
        """
        Sends extracted document text to the LLM (Grok/Groq) and parses structured invoice data.
        """
        if not document_text or not document_text.strip():
            logger.warning("Empty document text provided to GrokService.")
            return ExtractedInvoiceData()

        # Truncate text if excessively long to stay safely within context limits
        max_chars = 30000
        truncated_text = document_text[:max_chars]

        user_prompt = f"Extract invoice information from the following document content:\n\n{truncated_text}"

        models_to_try = [settings.XAI_MODEL, "openai/gpt-oss-120b", "qwen/qwen3.8-27b"]
        seen = set()
        candidate_models = [m for m in models_to_try if not (m in seen or seen.add(m))]

        last_error = None
        for model in candidate_models:
            try:
                logger.info(f"Sending request to LLM ({model}) at {settings.XAI_BASE_URL}")
                response = self.client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt}
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.1,
                )

                raw_content = response.choices[0].message.content
                logger.info(f"Received raw response from LLM ({model}) successfully.")
                return self._parse_json_response(raw_content)

            except Exception as e:
                logger.warning(f"Model '{model}' failed: {str(e)}. Trying next candidate...")
                last_error = e

        logger.error(f"All LLM candidate models failed. Last error: {str(last_error)}")
        raise RuntimeError(f"AI extraction service failed: {str(last_error)}")

    def _parse_json_response(self, raw_content: str) -> ExtractedInvoiceData:
        if not raw_content:
            return ExtractedInvoiceData()

        cleaned = raw_content.strip()
        # Strip potential markdown fences if present
        if cleaned.startswith("```"):
            cleaned = re.sub(r"^```(?:json)?", "", cleaned).strip()
            cleaned = re.sub(r"```$", "", cleaned).strip()

        try:
            data = json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse error on LLM response: {str(e)}")
            # Try finding the first { and last }
            start = cleaned.find("{")
            end = cleaned.rfind("}")
            if start != -1 and end != -1:
                data = json.loads(cleaned[start:end+1])
            else:
                raise ValueError("Could not parse structured JSON from LLM response")

        return ExtractedInvoiceData.model_validate(data)

grok_service = GrokService()
