# InvoiceIQ — AI-Based Smart Invoice Processing & Expense Management System

InvoiceIQ is an enterprise-grade full-stack accounting application designed to automate the intake, extraction, mathematical reconciliation, and financial reporting of commercial invoices with specialized support for the **Indian Goods and Services Tax (GST)** system.

---

## 🌟 Key Features

1. **AI-Powered Invoice Extraction**:
   - **Multi-page PDF parsing** using high-performance `PyMuPDF`.
   - **Tesseract OCR fallback** for scanned receipts and image-heavy documents.
   - **Structured AI extraction** powered by Grok/Groq LLMs (`openai/gpt-oss-120b` or `grok-2-latest`) via OpenAI-compatible endpoints.
   - Zero fabrication policy (`null` for omitted data).

2. **Automated Indian GST & Financial Reconciliation**:
   - Dual-structure tax auditing: Intra-state (`CGST` + `SGST`) and Inter-state (`IGST`).
   - Rate consistency checks: verifies `CGST rate == SGST rate`.
   - Statutory 15-character GSTIN format validation (`^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$`).
   - Multi-tier decimal reconciliation:
     $$\text{Line Items Taxable Sum} \leftrightarrow \text{Invoice Taxable Amount}$$
     $$\text{Taxable} + \text{Total GST} - \text{Discount} + \text{Charges} \pm \text{Round Off} == \text{Grand Total}$$
   - Objective validation scoring (0–100%) and automated discrepancy flag generation.

3. **Vendor Management & Deduplication**:
   - Automated vendor identification, deduplication, and record linking.
   - Duplicate invoice number detection across vendor records.

4. **Interactive Review & Manual Sign-off**:
   - Live drag-and-drop upload zone with progress indication.
   - Editable extraction preview allowing accountants to review or adjust figures before confirming.
   - Real-time audit feedback and discrepancy warnings.

5. **Financial Analytics & Dashboard**:
   - Live summary metrics: Total Spend, Taxable Base, Total GST, Invoices count.
   - Recharts visual monthly expenditure trends.
   - GST distribution and active tax slab analysis (5%, 12%, 18%, 28%).
   - Top suppliers by expenditure concentration.
   - Paginated invoice table with multi-attribute filtering, sorting, and CSV export.

---

## 🏗️ Project Architecture

```text
InvoiceIQ Project/
├── frontend/                     # React 19 + Vite + Tailwind CSS v4
│   ├── src/
│   │   ├── api/
│   │   │   └── client.js         # Axios API client
│   │   ├── components/
│   │   │   ├── common/           # LoadingState, EmptyState, ErrorMessage, ConfirmDialog
│   │   │   ├── layout/           # Sidebar, Navbar, PageHeader, Layout
│   │   │   ├── dashboard/        # StatCard, ExpenseChart, GSTBreakdown, VendorExpenseList
│   │   │   └── invoices/         # InvoiceTable, InvoiceFilters, InvoiceUpload, InvoiceDetails
│   │   ├── pages/                # DashboardPage, InvoicesPage, UploadPage, InvoiceDetailPage, etc.
│   │   ├── utils/                # formatters.js (INR currency, dates), constants.js
│   │   ├── App.jsx               # React Router routes
│   │   ├── index.css             # Tailwind CSS tokens & styling
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
├── backend/                      # FastAPI + SQLAlchemy 2.x + Alembic + PyMuPDF
│   ├── alembic/                  # Database migration versions and env
│   ├── app/
│   │   ├── api/                  # FastAPI routers (invoices, dashboard, vendors, health)
│   │   ├── core/                 # Config (Pydantic settings) and logging
│   │   ├── db/                   # Session, Base, seed data
│   │   ├── models/               # SQLAlchemy models (Vendor, Invoice, InvoiceLineItem)
│   │   ├── repositories/         # Database queries and aggregations
│   │   ├── schemas/              # Pydantic v2 validation models
│   │   ├── services/             # PDF extraction, OCR, Grok LLM, Financial Validator
│   │   └── main.py               # FastAPI entrypoint
│   ├── tests/                    # Automated pytest suite (100% passing)
│   ├── requirements.txt
│   ├── alembic.ini
│   ├── .env                      # Active credentials
│   └── .env.example
├── sample_invoices/              # Pre-generated realistic sample GST invoice for testing
├── docker-compose.yml
└── README.md
```

---

## 🚀 Quickstart Guide

### 1. Prerequisites
- **Python 3.11+**
- **Node.js v20+**
- **PostgreSQL 15+** running locally on port `5432`

---

### 2. Database Setup

Ensure PostgreSQL is running. Connect to PostgreSQL and create the application database:
```sql
CREATE DATABASE invoiceiq_db OWNER root;
```

---

### 3. Backend Setup & Run

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Activate the virtual environment:
   - **Windows PowerShell**:
     ```powershell
     .\.venv\Scripts\Activate.ps1
     ```
   - **Linux / macOS**:
     ```bash
     source .venv/bin/activate
     ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Verify your environment variables in `.env`:
   ```ini
   DATABASE_URL=postgresql+psycopg2://root:root@localhost:5432/invoiceiq_db
   XAI_API_KEY=your_groq_or_xai_api_key_here
   XAI_BASE_URL=https://api.groq.com/openai/v1
   XAI_MODEL=openai/gpt-oss-120b
   UPLOAD_DIR=uploads/invoices
   MAX_UPLOAD_SIZE_MB=15
   ```

5. Apply database migrations:
   ```bash
   alembic upgrade head
   ```

6. Seed initial realistic Indian GST invoices (optional):
   ```bash
   python app/db/seed.py
   ```

7. Start the FastAPI development server:
   ```bash
   uvicorn app.main:app --reload --port 8000
   ```
   - Interactive Swagger API docs: [http://localhost:8000/docs](http://localhost:8000/docs)
   - Health Check: [http://localhost:8000/api/health](http://localhost:8000/api/health)

---

### 4. Frontend Setup & Run

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install npm dependencies:
   ```bash
   npm install
   ```

3. Start Vite dev server:
   ```bash
   npm run dev
   ```
   The UI will be available at [http://localhost:5173](http://localhost:5173).

---

## 🧪 Automated Testing

InvoiceIQ includes an automated test suite verifying financial mathematics, GST rules, PDF text extraction, OCR fallback, and API CRUD endpoints.

Run tests:
```bash
pytest backend/tests -v
```

Output:
```text
backend/tests/test_dashboard_api.py::test_dashboard_endpoints PASSED
backend/tests/test_financial_validator.py::test_financial_validator_perfect_intra_state_invoice PASSED
backend/tests/test_financial_validator.py::test_financial_validator_cgst_sgst_mismatch PASSED
backend/tests/test_financial_validator.py::test_financial_validator_invalid_gstin_flagged PASSED
backend/tests/test_financial_validator.py::test_financial_validator_total_calculation_discrepancy PASSED
backend/tests/test_invoices_api.py::test_health_endpoint PASSED
backend/tests/test_invoices_api.py::test_invoice_upload_and_crud_workflow PASSED
backend/tests/test_pdf_extraction.py::test_pdf_validation_header PASSED
backend/tests/test_pdf_extraction.py::test_pdf_validation_size PASSED
backend/tests/test_pdf_extraction.py::test_pdf_text_extraction PASSED

10 passed in 1.63s
```

---

## 📄 Sample Testing Document

A pre-generated sample GST invoice is included:
`sample_invoices/sample_gst_invoice.pdf`

You can drag and drop this file directly into the **Upload Invoice** page in the UI to see the live extraction and GST reconciliation in action!

---

## 🔒 Security Best Practices

- **Zero Client-side Key Exposure**: All AI API keys and database credentials remain strictly within the backend `.env`.
- **Upload Hardening**: File header magic bytes verification (`%PDF-`), safe UUID-based filenames, storage outside public web roots, and strict size enforcement.
- **Financial Precision**: All calculations use Python's `Decimal` with `ROUND_HALF_UP` to prevent IEEE 754 floating-point errors.
- **Sanitized Error Responses**: Internal database errors and stack traces are suppressed from client responses.
