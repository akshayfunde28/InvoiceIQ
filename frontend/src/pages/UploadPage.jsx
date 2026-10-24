import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, FileText, CheckCircle2, ShieldCheck } from 'lucide-react';
import PageHeader from '../components/layout/PageHeader';
import InvoiceUpload from '../components/invoices/InvoiceUpload';

export default function UploadPage() {
  const navigate = useNavigate();

  const handleSuccess = (savedInvoice) => {
    // Optionally redirect or keep on screen
  };

  return (
    <div className="space-y-8 animate-fade-in max-w-5xl mx-auto">
      <PageHeader
        title="Upload & Process Invoice"
        subtitle="Automatic multi-page PDF & Image text extraction, OCR fallback, Grok AI parsing, and statutory Indian GST validation."
      />

      {/* Pipeline Explanation Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs flex items-start gap-3">
          <div className="w-8 h-8 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center shrink-0">
            <FileText className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-slate-900">1. Text & OCR Extraction</h4>
            <p className="text-[11px] text-slate-500 mt-0.5 leading-snug">
              PyMuPDF digital extraction with automatic Tesseract OCR fallback for scanned receipts.
            </p>
          </div>
        </div>

        <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs flex items-start gap-3">
          <div className="w-8 h-8 rounded-xl bg-purple-50 text-purple-600 flex items-center justify-center shrink-0">
            <Sparkles className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-slate-900">2. Grok AI Model</h4>
            <p className="text-[11px] text-slate-500 mt-0.5 leading-snug">
              Extracts GSTINs, HSN codes, tax components, and line items into strict JSON.
            </p>
          </div>
        </div>

        <div className="bg-white p-4 rounded-2xl border border-slate-200/80 shadow-xs flex items-start gap-3">
          <div className="w-8 h-8 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0">
            <ShieldCheck className="w-4 h-4" />
          </div>
          <div>
            <h4 className="text-xs font-bold text-slate-900">3. GST Math Audit</h4>
            <p className="text-[11px] text-slate-500 mt-0.5 leading-snug">
              Reconciles CGST/SGST/IGST, line item sums, and flags discrepancies for human review.
            </p>
          </div>
        </div>
      </div>

      {/* Main Upload and Preview Component */}
      <InvoiceUpload onUploadSuccess={handleSuccess} />
    </div>
  );
}
