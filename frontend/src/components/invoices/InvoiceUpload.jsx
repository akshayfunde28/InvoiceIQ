import React, { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  UploadCloud,
  FileCheck,
  AlertCircle,
  Sparkles,
  Check,
  RotateCcw,
  Plus,
  Trash2,
  AlertTriangle,
  ArrowRight,
  ShieldCheck,
} from 'lucide-react';
import { apiClient } from '../../api/client';
import { formatFileSize } from '../../utils/formatters';

const ALLOWED_EXTENSIONS = ['.pdf', '.png', '.jpg', '.jpeg', '.webp'];
const ALLOWED_MIME_TYPES = ['application/pdf', 'image/png', 'image/jpeg', 'image/webp'];

export default function InvoiceUpload({ onUploadSuccess }) {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);

  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [fileError, setFileError] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [processingStage, setProcessingStage] = useState('');

  // Extracted Invoice Review State
  const [extractedInvoice, setExtractedInvoice] = useState(null);
  const [editableInvoice, setEditableInvoice] = useState(null);
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // File Validation
  const validateFile = (file) => {
    setFileError(null);
    if (!file) return false;
    const ext = '.' + file.name.split('.').pop().toLowerCase();
    const isAllowedExt = ALLOWED_EXTENSIONS.includes(ext);
    const isAllowedMime = ALLOWED_MIME_TYPES.includes(file.type) || file.type.startsWith('image/');
    if (!isAllowedExt && !isAllowedMime) {
      setFileError('Unsupported file format. Please upload a PDF or image (.pdf, .png, .jpg, .jpeg, .webp).');
      return false;
    }
    const maxBytes = 15 * 1024 * 1024; // 15MB
    if (file.size > maxBytes) {
      setFileError(`File size exceeds 15MB limit (${formatFileSize(file.size)}).`);
      return false;
    }
    return true;
  };

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true);
    } else if (e.type === 'dragleave') {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      const file = e.dataTransfer.files[0];
      if (validateFile(file)) {
        setSelectedFile(file);
        handleUploadAndExtract(file);
      }
    }
  };

  const handleFileInputChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      if (validateFile(file)) {
        setSelectedFile(file);
        handleUploadAndExtract(file);
      }
    }
  };

  const handleUploadAndExtract = async (file) => {
    setIsProcessing(true);
    setUploadProgress(10);
    const isImage = file.type?.startsWith('image/') || /\.(png|jpe?g|webp)$/i.test(file.name);
    setProcessingStage(isImage ? 'Uploading invoice image...' : 'Uploading invoice document...');
    setSaveSuccess(false);

    try {
      setProcessingStage(
        isImage
          ? 'Analyzing invoice image with PyMuPDF OCR & Grok AI...'
          : 'Analyzing document with PyMuPDF & Grok AI...'
      );
      const response = await apiClient.uploadInvoice(file, (progress) => {
        setUploadProgress(progress);
        if (progress >= 100) {
          setProcessingStage('Grok AI extracting structured invoice and GST fields...');
        }
      });

      setUploadProgress(100);
      setExtractedInvoice(response);
      setEditableInvoice(JSON.parse(JSON.stringify(response)));
      setProcessingStage('');
    } catch (err) {
      setFileError(err.message || 'Invoice extraction failed. Please try again.');
    } finally {
      setIsProcessing(false);
    }
  };

  const handleFieldChange = (field, value) => {
    setEditableInvoice((prev) => ({
      ...prev,
      [field]: value,
    }));
  };

  const handleLineItemChange = (index, field, value) => {
    setEditableInvoice((prev) => {
      const items = [...(prev.line_items || [])];
      items[index] = { ...items[index], [field]: value };
      return { ...prev, line_items: items };
    });
  };

  const addLineItem = () => {
    setEditableInvoice((prev) => ({
      ...prev,
      line_items: [
        ...(prev.line_items || []),
        {
          item_index: (prev.line_items?.length || 0),
          description: '',
          hsn_sac: '',
          quantity: 1,
          unit: 'UNIT',
          unit_price: 0,
          taxable_amount: 0,
          tax_rate: 18,
          tax_amount: 0,
          total_amount: 0,
        },
      ],
    }));
  };

  const removeLineItem = (index) => {
    setEditableInvoice((prev) => ({
      ...prev,
      line_items: prev.line_items.filter((_, i) => i !== index),
    }));
  };

  const handleConfirmAndSave = async () => {
    if (!editableInvoice?.id) return;
    setIsSaving(true);
    try {
      const payload = {
        invoice_number: editableInvoice.invoice_number,
        invoice_date: editableInvoice.invoice_date,
        due_date: editableInvoice.due_date,
        vendor_name_raw: editableInvoice.vendor_name_raw,
        vendor_gstin: editableInvoice.vendor_gstin,
        vendor_address: editableInvoice.vendor_address,
        buyer_name: editableInvoice.buyer_name,
        buyer_gstin: editableInvoice.buyer_gstin,
        buyer_address: editableInvoice.buyer_address,
        place_of_supply: editableInvoice.place_of_supply,
        taxable_amount: Number(editableInvoice.taxable_amount) || 0,
        cgst_amount: Number(editableInvoice.cgst_amount) || 0,
        sgst_amount: Number(editableInvoice.sgst_amount) || 0,
        igst_amount: Number(editableInvoice.igst_amount) || 0,
        total_tax: Number(editableInvoice.total_tax) || 0,
        discount_amount: Number(editableInvoice.discount_amount) || 0,
        additional_charges: Number(editableInvoice.additional_charges) || 0,
        round_off: Number(editableInvoice.round_off) || 0,
        total_amount: Number(editableInvoice.total_amount) || 0,
        payment_status: editableInvoice.payment_status || 'unpaid',
        processing_status: 'confirmed', // Confirmed by user!
        review_status: 'manually_confirmed',
        line_items: editableInvoice.line_items || [],
      };

      const updated = await apiClient.updateInvoice(editableInvoice.id, payload);
      setExtractedInvoice(updated);
      setEditableInvoice(updated);
      setSaveSuccess(true);
      if (onUploadSuccess) onUploadSuccess(updated);
    } catch (err) {
      alert(`Failed to save invoice: ${err.message}`);
    } finally {
      setIsSaving(false);
    }
  };

  const resetUpload = () => {
    setSelectedFile(null);
    setExtractedInvoice(null);
    setEditableInvoice(null);
    setFileError(null);
    setUploadProgress(0);
    setSaveSuccess(false);
  };

  return (
    <div className="space-y-8">
      {/* Upload Drop Zone Card */}
      {!editableInvoice && (
        <div
          onDragEnter={handleDrag}
          onDragLeave={handleDrag}
          onDragOver={handleDrag}
          onDrop={handleDrop}
          onClick={() => fileInputRef.current?.click()}
          className={`border-2 border-dashed rounded-3xl p-12 text-center transition-all cursor-pointer ${
            dragActive
              ? 'border-indigo-600 bg-indigo-50/50 scale-[1.01]'
              : 'border-slate-300 bg-white hover:border-indigo-400 hover:bg-slate-50/50'
          }`}
        >
          <input
            ref={fileInputRef}
            type="file"
            accept=".pdf,application/pdf,image/png,image/jpeg,image/webp,.png,.jpg,.jpeg,.webp"
            onChange={handleFileInputChange}
            className="hidden"
          />

          <div className="w-16 h-16 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center mx-auto mb-4 shadow-sm">
            <UploadCloud className="w-8 h-8" />
          </div>

          <h3 className="text-lg font-bold text-slate-900">
            {isProcessing ? 'Processing Invoice...' : 'Drag and drop your invoice PDF or image here'}
          </h3>
          <p className="mt-1 text-sm text-slate-500 max-w-md mx-auto">
            Supports PDF, PNG, JPG, and WEBP formats up to 15MB. Automatic OCR & Indian GST parsing.
          </p>

          <button
            type="button"
            className="mt-6 inline-flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-semibold text-white bg-indigo-600 hover:bg-indigo-700 shadow-md shadow-indigo-600/25 transition-all"
          >
            Browse Files
          </button>

          {/* Processing Indicator */}
          {isProcessing && (
            <div className="mt-8 max-w-md mx-auto space-y-3">
              <div className="flex justify-between text-xs font-semibold text-slate-600">
                <span>{processingStage || 'Analyzing document...'}</span>
                <span>{uploadProgress}%</span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-2.5 overflow-hidden">
                <div
                  className="bg-indigo-600 h-2.5 rounded-full transition-all duration-300 animate-pulse"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
            </div>
          )}

          {/* Error Message */}
          {fileError && (
            <div className="mt-6 inline-flex items-center gap-2 p-3 rounded-xl bg-rose-50 border border-rose-200 text-xs font-medium text-rose-700 max-w-md">
              <AlertCircle className="w-4 h-4 shrink-0" />
              <span>{fileError}</span>
            </div>
          )}
        </div>
      )}

      {/* Extracted Invoice Review & Confirmation Panel */}
      {editableInvoice && (
        <div className="bg-white rounded-3xl border border-slate-200 shadow-sm overflow-hidden animate-fade-in">
          {/* Header Banner */}
          <div className="bg-slate-900 text-white p-6 flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-indigo-600 flex items-center justify-center text-white shrink-0">
                <Sparkles className="w-5 h-5" />
              </div>
              <div>
                <div className="flex items-center gap-2.5 flex-wrap">
                  <h2 className="text-lg font-bold">Review Extracted Invoice</h2>
                  {/* Confidence Score Badge */}
                  {editableInvoice.validation_score !== undefined && editableInvoice.validation_score !== null && (
                    <div
                      className={`inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-xs font-bold border transition-colors shadow-xs ${
                        Number(editableInvoice.validation_score) >= 90
                          ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30'
                          : Number(editableInvoice.validation_score) >= 70
                          ? 'bg-amber-500/20 text-amber-300 border-amber-500/30'
                          : 'bg-rose-500/20 text-rose-300 border-rose-500/30'
                      }`}
                      title={`AI validation & extraction confidence: ${Number(editableInvoice.validation_score).toFixed(0)}%`}
                    >
                      <ShieldCheck className="w-3.5 h-3.5" />
                      <span>{Number(editableInvoice.validation_score).toFixed(0)}% Confidence Score</span>
                    </div>
                  )}
                  {editableInvoice.ocr_used && (
                    <span className="inline-flex items-center px-2 py-0.5 rounded-md text-[11px] font-semibold bg-indigo-500/20 text-indigo-300 border border-indigo-500/30">
                      OCR Fallback
                    </span>
                  )}
                </div>
                <p className="text-xs text-slate-400 mt-1">
                  Verify or edit extracted figures before final confirmation.
                </p>
              </div>
            </div>

            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={resetUpload}
                className="px-3.5 py-2 rounded-xl text-xs font-semibold text-slate-300 hover:text-white bg-slate-800 hover:bg-slate-700 transition-colors flex items-center gap-1.5 cursor-pointer"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                Upload Another
              </button>
              <button
                type="button"
                disabled={isSaving || saveSuccess}
                onClick={handleConfirmAndSave}
                className={`px-5 py-2 rounded-xl text-xs font-bold transition-all flex items-center gap-2 cursor-pointer shadow-md ${
                  saveSuccess
                    ? 'bg-emerald-600 text-white'
                    : 'bg-indigo-600 hover:bg-indigo-500 text-white shadow-indigo-600/30'
                }`}
              >
                {saveSuccess ? (
                  <>
                    <Check className="w-4 h-4" />
                    <span>Saved & Confirmed</span>
                  </>
                ) : (
                  <>
                    <FileCheck className="w-4 h-4" />
                    <span>{isSaving ? 'Saving...' : 'Confirm & Save Invoice'}</span>
                  </>
                )}
              </button>
            </div>
          </div>

          {/* Discrepancies and Warnings */}
          {editableInvoice.discrepancy_flags && editableInvoice.discrepancy_flags.length > 0 && (
            <div className="p-5 bg-amber-50 border-b border-amber-200">
              <div className="flex items-start gap-3">
                <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
                <div>
                  <h4 className="text-xs font-bold uppercase text-amber-900 tracking-wider">
                    Validation Warnings ({editableInvoice.discrepancy_flags.length})
                  </h4>
                  <ul className="mt-1 space-y-1 text-xs text-amber-800 list-disc list-inside">
                    {editableInvoice.discrepancy_flags.map((msg, i) => (
                      <li key={i}>{msg}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          )}

          {/* Success Banner */}
          {saveSuccess && (
            <div className="p-5 bg-emerald-50 border-b border-emerald-200 flex items-center justify-between">
              <div className="flex items-center gap-2 text-emerald-800 text-sm font-semibold">
                <Check className="w-5 h-5 text-emerald-600" />
                <span>Invoice confirmed and permanently recorded in PostgreSQL!</span>
              </div>
              <button
                type="button"
                onClick={() => navigate(`/invoices/${editableInvoice.id}`)}
                className="text-xs font-bold text-emerald-900 hover:underline flex items-center gap-1 cursor-pointer"
              >
                View Full Details <ArrowRight className="w-3.5 h-3.5" />
              </button>
            </div>
          )}

          <div className="p-8 space-y-8">
            {/* Core Invoice Details */}
            <div>
              <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider mb-4">
                1. Invoice Identifiers
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
                <div>
                  <label className="block text-xs font-medium text-slate-600 mb-1">Invoice Number *</label>
                  <input
                    type="text"
                    value={editableInvoice.invoice_number || ''}
                    onChange={(e) => handleFieldChange('invoice_number', e.target.value)}
                    className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20 font-semibold"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-600 mb-1">Invoice Date</label>
                  <input
                    type="date"
                    value={editableInvoice.invoice_date || ''}
                    onChange={(e) => handleFieldChange('invoice_date', e.target.value)}
                    className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-600 mb-1">Due Date</label>
                  <input
                    type="date"
                    value={editableInvoice.due_date || ''}
                    onChange={(e) => handleFieldChange('due_date', e.target.value)}
                    className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                  />
                </div>
              </div>
            </div>

            {/* Vendor & Buyer Details */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 pt-4 border-t border-slate-100">
              {/* Vendor */}
              <div className="space-y-4">
                <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
                  2. Vendor (Supplier)
                </h3>
                <div>
                  <label className="block text-xs font-medium text-slate-600 mb-1">Vendor Name *</label>
                  <input
                    type="text"
                    value={editableInvoice.vendor_name_raw || ''}
                    onChange={(e) => handleFieldChange('vendor_name_raw', e.target.value)}
                    className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20 font-medium"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-600 mb-1">Vendor GSTIN (15 Digits)</label>
                  <input
                    type="text"
                    maxLength={15}
                    value={editableInvoice.vendor_gstin || ''}
                    onChange={(e) => handleFieldChange('vendor_gstin', e.target.value.toUpperCase())}
                    className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm font-mono focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-600 mb-1">Address</label>
                  <textarea
                    rows={2}
                    value={editableInvoice.vendor_address || ''}
                    onChange={(e) => handleFieldChange('vendor_address', e.target.value)}
                    className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-xs focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                  />
                </div>
              </div>

              {/* Buyer */}
              <div className="space-y-4">
                <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
                  3. Buyer (Customer)
                </h3>
                <div>
                  <label className="block text-xs font-medium text-slate-600 mb-1">Buyer Name</label>
                  <input
                    type="text"
                    value={editableInvoice.buyer_name || ''}
                    onChange={(e) => handleFieldChange('buyer_name', e.target.value)}
                    className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20 font-medium"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-600 mb-1">Buyer GSTIN</label>
                  <input
                    type="text"
                    maxLength={15}
                    value={editableInvoice.buyer_gstin || ''}
                    onChange={(e) => handleFieldChange('buyer_gstin', e.target.value.toUpperCase())}
                    className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm font-mono focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-slate-600 mb-1">Place of Supply</label>
                  <input
                    type="text"
                    value={editableInvoice.place_of_supply || ''}
                    onChange={(e) => handleFieldChange('place_of_supply', e.target.value)}
                    className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20"
                  />
                </div>
              </div>
            </div>

            {/* Line Items */}
            <div className="pt-4 border-t border-slate-100">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
                  4. Line Items ({editableInvoice.line_items?.length || 0})
                </h3>
                <button
                  type="button"
                  onClick={addLineItem}
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-semibold text-indigo-700 bg-indigo-50 hover:bg-indigo-100 cursor-pointer transition-colors"
                >
                  <Plus className="w-3.5 h-3.5" />
                  Add Line Item
                </button>
              </div>

              <div className="overflow-x-auto border border-slate-200 rounded-xl">
                <table className="w-full text-left text-xs text-slate-600">
                  <thead className="bg-slate-50 border-b border-slate-200 font-semibold text-slate-700">
                    <tr>
                      <th className="p-3">Description</th>
                      <th className="p-3 w-24">HSN/SAC</th>
                      <th className="p-3 w-20 text-right">Qty</th>
                      <th className="p-3 w-28 text-right">Rate</th>
                      <th className="p-3 w-28 text-right">Taxable</th>
                      <th className="p-3 w-20 text-right">GST %</th>
                      <th className="p-3 w-28 text-right">Tax Amt</th>
                      <th className="p-3 w-32 text-right">Line Total</th>
                      <th className="p-3 w-12 text-center"></th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {editableInvoice.line_items?.map((item, idx) => (
                      <tr key={idx} className="hover:bg-slate-50/50">
                        <td className="p-2">
                          <input
                            type="text"
                            value={item.description || ''}
                            onChange={(e) => handleLineItemChange(idx, 'description', e.target.value)}
                            className="w-full px-2 py-1 bg-transparent border border-transparent hover:border-slate-300 focus:border-indigo-500 focus:bg-white rounded"
                          />
                        </td>
                        <td className="p-2">
                          <input
                            type="text"
                            value={item.hsn_sac || ''}
                            onChange={(e) => handleLineItemChange(idx, 'hsn_sac', e.target.value)}
                            className="w-full px-2 py-1 bg-transparent border border-transparent hover:border-slate-300 focus:border-indigo-500 focus:bg-white rounded font-mono"
                          />
                        </td>
                        <td className="p-2 text-right">
                          <input
                            type="number"
                            step="0.01"
                            value={item.quantity || 1}
                            onChange={(e) => handleLineItemChange(idx, 'quantity', parseFloat(e.target.value) || 0)}
                            className="w-full px-2 py-1 text-right bg-transparent border border-transparent hover:border-slate-300 focus:border-indigo-500 focus:bg-white rounded"
                          />
                        </td>
                        <td className="p-2 text-right">
                          <input
                            type="number"
                            step="0.01"
                            value={item.unit_price || 0}
                            onChange={(e) => handleLineItemChange(idx, 'unit_price', parseFloat(e.target.value) || 0)}
                            className="w-full px-2 py-1 text-right bg-transparent border border-transparent hover:border-slate-300 focus:border-indigo-500 focus:bg-white rounded"
                          />
                        </td>
                        <td className="p-2 text-right">
                          <input
                            type="number"
                            step="0.01"
                            value={item.taxable_amount || 0}
                            onChange={(e) => handleLineItemChange(idx, 'taxable_amount', parseFloat(e.target.value) || 0)}
                            className="w-full px-2 py-1 text-right bg-transparent border border-transparent hover:border-slate-300 focus:border-indigo-500 focus:bg-white rounded font-medium"
                          />
                        </td>
                        <td className="p-2 text-right">
                          <input
                            type="number"
                            step="0.1"
                            value={item.tax_rate || 0}
                            onChange={(e) => handleLineItemChange(idx, 'tax_rate', parseFloat(e.target.value) || 0)}
                            className="w-full px-2 py-1 text-right bg-transparent border border-transparent hover:border-slate-300 focus:border-indigo-500 focus:bg-white rounded"
                          />
                        </td>
                        <td className="p-2 text-right">
                          <input
                            type="number"
                            step="0.01"
                            value={item.tax_amount || 0}
                            onChange={(e) => handleLineItemChange(idx, 'tax_amount', parseFloat(e.target.value) || 0)}
                            className="w-full px-2 py-1 text-right bg-transparent border border-transparent hover:border-slate-300 focus:border-indigo-500 focus:bg-white rounded"
                          />
                        </td>
                        <td className="p-2 text-right">
                          <input
                            type="number"
                            step="0.01"
                            value={item.total_amount || 0}
                            onChange={(e) => handleLineItemChange(idx, 'total_amount', parseFloat(e.target.value) || 0)}
                            className="w-full px-2 py-1 text-right bg-transparent border border-transparent hover:border-slate-300 focus:border-indigo-500 focus:bg-white rounded font-bold text-slate-900"
                          />
                        </td>
                        <td className="p-2 text-center">
                          <button
                            type="button"
                            onClick={() => removeLineItem(idx)}
                            className="p-1 rounded text-slate-400 hover:text-rose-600 transition-colors cursor-pointer"
                          >
                            <Trash2 className="w-3.5 h-3.5" />
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Financial Totals Reconciliation */}
            <div className="pt-4 border-t border-slate-100 flex flex-col md:flex-row justify-between gap-8">
              <div className="space-y-4 max-w-sm">
                <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
                  Payment & Status
                </h3>
                <div>
                  <label className="block text-xs font-medium text-slate-600 mb-1">Payment Status</label>
                  <select
                    value={editableInvoice.payment_status || 'unpaid'}
                    onChange={(e) => handleFieldChange('payment_status', e.target.value)}
                    className="w-full px-3.5 py-2 bg-slate-50 border border-slate-200 rounded-xl text-sm"
                  >
                    <option value="unpaid">Unpaid</option>
                    <option value="paid">Paid</option>
                    <option value="partially_paid">Partially Paid</option>
                  </select>
                </div>
              </div>

              {/* Financial Totals Breakdown Box */}
              <div className="w-full max-w-md bg-slate-50 rounded-2xl p-6 border border-slate-200 space-y-3">
                <div className="flex justify-between text-xs">
                  <span className="text-slate-600">Taxable Amount:</span>
                  <input
                    type="number"
                    step="0.01"
                    value={editableInvoice.taxable_amount || 0}
                    onChange={(e) => handleFieldChange('taxable_amount', parseFloat(e.target.value) || 0)}
                    className="w-32 px-2 py-1 bg-white border border-slate-200 rounded text-right font-medium text-xs"
                  />
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-slate-600">CGST Amount:</span>
                  <input
                    type="number"
                    step="0.01"
                    value={editableInvoice.cgst_amount || 0}
                    onChange={(e) => handleFieldChange('cgst_amount', parseFloat(e.target.value) || 0)}
                    className="w-32 px-2 py-1 bg-white border border-slate-200 rounded text-right text-xs"
                  />
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-slate-600">SGST Amount:</span>
                  <input
                    type="number"
                    step="0.01"
                    value={editableInvoice.sgst_amount || 0}
                    onChange={(e) => handleFieldChange('sgst_amount', parseFloat(e.target.value) || 0)}
                    className="w-32 px-2 py-1 bg-white border border-slate-200 rounded text-right text-xs"
                  />
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-slate-600">IGST Amount:</span>
                  <input
                    type="number"
                    step="0.01"
                    value={editableInvoice.igst_amount || 0}
                    onChange={(e) => handleFieldChange('igst_amount', parseFloat(e.target.value) || 0)}
                    className="w-32 px-2 py-1 bg-white border border-slate-200 rounded text-right text-xs"
                  />
                </div>
                <div className="flex justify-between text-xs font-semibold pt-2 border-t border-slate-200">
                  <span className="text-slate-700">Total GST:</span>
                  <input
                    type="number"
                    step="0.01"
                    value={editableInvoice.total_tax || 0}
                    onChange={(e) => handleFieldChange('total_tax', parseFloat(e.target.value) || 0)}
                    className="w-32 px-2 py-1 bg-white border border-slate-200 rounded text-right font-bold text-xs"
                  />
                </div>
                <div className="flex justify-between text-base font-bold pt-3 border-t-2 border-slate-300 text-slate-900">
                  <span>Grand Total:</span>
                  <input
                    type="number"
                    step="0.01"
                    value={editableInvoice.total_amount || 0}
                    onChange={(e) => handleFieldChange('total_amount', parseFloat(e.target.value) || 0)}
                    className="w-36 px-2.5 py-1 bg-white border-2 border-indigo-500 rounded text-right font-extrabold text-indigo-700 text-sm"
                  />
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
