import React, { useState } from 'react';
import {
  FileText,
  Download,
  Building2,
  Calendar,
  CreditCard,
  ShieldCheck,
  AlertTriangle,
  RotateCw,
  Check,
  Trash2,
  ExternalLink,
} from 'lucide-react';
import { formatCurrency, formatDate } from '../../utils/formatters';
import StatusBadge from './StatusBadge';
import DiscrepancyBadge from './DiscrepancyBadge';
import ConfirmDialog from '../common/ConfirmDialog';
import { apiClient } from '../../api/client';

export default function InvoiceDetails({
  invoice,
  onUpdateSuccess,
  onDeleteSuccess,
}) {
  const [isReprocessing, setIsReprocessing] = useState(false);
  const [isConfirming, setIsConfirming] = useState(false);
  const [showDeleteDialog, setShowDeleteDialog] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleReprocess = async () => {
    setIsReprocessing(true);
    try {
      const updated = await apiClient.reprocessInvoice(invoice.id);
      if (onUpdateSuccess) onUpdateSuccess(updated);
    } catch (err) {
      alert(`Reprocessing failed: ${err.message}`);
    } finally {
      setIsReprocessing(false);
    }
  };

  const handleConfirmInvoice = async () => {
    setIsConfirming(true);
    try {
      const updated = await apiClient.updateInvoice(invoice.id, {
        processing_status: 'confirmed',
        review_status: 'manually_confirmed',
      });
      if (onUpdateSuccess) onUpdateSuccess(updated);
    } catch (err) {
      alert(`Confirmation failed: ${err.message}`);
    } finally {
      setIsConfirming(false);
    }
  };

  const handleDelete = async () => {
    setIsDeleting(true);
    try {
      await apiClient.deleteInvoice(invoice.id);
      if (onDeleteSuccess) onDeleteSuccess();
    } catch (err) {
      alert(`Delete failed: ${err.message}`);
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Top Action Bar */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="w-12 h-12 rounded-2xl bg-indigo-50 text-indigo-600 flex items-center justify-center shrink-0 border border-indigo-100">
            <FileText className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center gap-2.5">
              <h2 className="text-xl font-bold text-slate-900 tracking-tight">
                {invoice.invoice_number}
              </h2>
              <StatusBadge type="review" status={invoice.review_status} />
              <StatusBadge type="payment" status={invoice.payment_status} />
            </div>
            <p className="text-xs text-slate-500 mt-1">
              Uploaded on {formatDate(invoice.created_at)} • File: {invoice.original_filename}
            </p>
          </div>
        </div>

        {/* Action buttons */}
        <div className="flex items-center gap-2.5 flex-wrap">
          <a
            href={apiClient.getInvoiceFileUrl(invoice.id)}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 transition-colors"
          >
            <Download className="w-3.5 h-3.5" />
            Download PDF
          </a>

          <button
            type="button"
            disabled={isReprocessing}
            onClick={handleReprocess}
            className="inline-flex items-center gap-1.5 px-3.5 py-2 rounded-xl text-xs font-semibold text-slate-700 bg-slate-100 hover:bg-slate-200 transition-colors cursor-pointer"
          >
            <RotateCw className={`w-3.5 h-3.5 ${isReprocessing ? 'animate-spin' : ''}`} />
            {isReprocessing ? 'Reprocessing...' : 'Reprocess AI'}
          </button>

          {invoice.processing_status !== 'confirmed' && (
            <button
              type="button"
              disabled={isConfirming}
              onClick={handleConfirmInvoice}
              className="inline-flex items-center gap-1.5 px-4 py-2 rounded-xl text-xs font-bold text-white bg-emerald-600 hover:bg-emerald-700 shadow-sm shadow-emerald-600/20 transition-all cursor-pointer"
            >
              <Check className="w-3.5 h-3.5" />
              {isConfirming ? 'Confirming...' : 'Confirm Invoice'}
            </button>
          )}

          <button
            type="button"
            onClick={() => setShowDeleteDialog(true)}
            className="p-2 rounded-xl text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors cursor-pointer"
            title="Delete invoice"
          >
            <Trash2 className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Discrepancy Warnings Alert Banner */}
      {invoice.discrepancy_flags && invoice.discrepancy_flags.length > 0 && (
        <div className="bg-amber-50 rounded-2xl p-5 border border-amber-200">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
            <div>
              <h4 className="text-xs font-bold uppercase text-amber-900 tracking-wider">
                Automated Validation Flags ({invoice.discrepancy_flags.length})
              </h4>
              <ul className="mt-2 space-y-1 text-xs text-amber-800 list-disc list-inside">
                {invoice.discrepancy_flags.map((msg, i) => (
                  <li key={i}>{msg}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Vendor & Buyer Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Vendor */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-400 mb-4">
            <Building2 className="w-4 h-4 text-indigo-500" />
            <span>Supplier (Vendor)</span>
          </div>
          <h3 className="text-base font-bold text-slate-900">{invoice.vendor_name_raw}</h3>
          <div className="mt-3 space-y-2 text-xs text-slate-600">
            <p className="flex justify-between">
              <span className="text-slate-400">GSTIN:</span>
              <span className="font-mono font-bold text-slate-800">
                {invoice.vendor_gstin || 'Not Specified'}
              </span>
            </p>
            {invoice.vendor_address && (
              <p className="flex justify-between">
                <span className="text-slate-400">Address:</span>
                <span className="text-right max-w-xs">{invoice.vendor_address}</span>
              </p>
            )}
          </div>
        </div>

        {/* Buyer */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs">
          <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-slate-400 mb-4">
            <Building2 className="w-4 h-4 text-emerald-500" />
            <span>Customer (Buyer)</span>
          </div>
          <h3 className="text-base font-bold text-slate-900">{invoice.buyer_name || 'Direct Customer'}</h3>
          <div className="mt-3 space-y-2 text-xs text-slate-600">
            <p className="flex justify-between">
              <span className="text-slate-400">GSTIN:</span>
              <span className="font-mono font-bold text-slate-800">
                {invoice.buyer_gstin || 'Not Specified'}
              </span>
            </p>
            {invoice.place_of_supply && (
              <p className="flex justify-between">
                <span className="text-slate-400">Place of Supply:</span>
                <span>{invoice.place_of_supply}</span>
              </p>
            )}
            {invoice.buyer_address && (
              <p className="flex justify-between">
                <span className="text-slate-400">Address:</span>
                <span className="text-right max-w-xs">{invoice.buyer_address}</span>
              </p>
            )}
          </div>
        </div>
      </div>

      {/* Line Items Table */}
      <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
        <div className="p-6 border-b border-slate-100 flex items-center justify-between">
          <h3 className="text-sm font-bold text-slate-900 uppercase tracking-wider">
            Line Items ({invoice.line_items?.length || 0})
          </h3>
          <span className="text-xs text-slate-500">
            Validated against GST statutory rules
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-600">
            <thead className="bg-slate-50 border-b border-slate-200 font-semibold text-slate-700">
              <tr>
                <th className="px-6 py-3.5">#</th>
                <th className="px-6 py-3.5">Description</th>
                <th className="px-6 py-3.5">HSN/SAC</th>
                <th className="px-6 py-3.5 text-right">Quantity</th>
                <th className="px-6 py-3.5 text-right">Unit Price</th>
                <th className="px-6 py-3.5 text-right">Taxable</th>
                <th className="px-6 py-3.5 text-right">Tax Rate</th>
                <th className="px-6 py-3.5 text-right">Tax Amount</th>
                <th className="px-6 py-3.5 text-right">Line Total</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {invoice.line_items && invoice.line_items.length > 0 ? (
                invoice.line_items.map((item, idx) => (
                  <tr key={item.id || idx} className="hover:bg-slate-50/50">
                    <td className="px-6 py-4 font-mono text-slate-400">{idx + 1}</td>
                    <td className="px-6 py-4 font-medium text-slate-900">{item.description}</td>
                    <td className="px-6 py-4 font-mono text-slate-500">{item.hsn_sac || '—'}</td>
                    <td className="px-6 py-4 text-right font-medium">
                      {Number(item.quantity).toFixed(2)} {item.unit || ''}
                    </td>
                    <td className="px-6 py-4 text-right">{formatCurrency(item.unit_price, invoice.currency)}</td>
                    <td className="px-6 py-4 text-right font-medium">{formatCurrency(item.taxable_amount, invoice.currency)}</td>
                    <td className="px-6 py-4 text-right font-semibold text-indigo-600">{Number(item.tax_rate).toFixed(1)}%</td>
                    <td className="px-6 py-4 text-right">{formatCurrency(item.tax_amount, invoice.currency)}</td>
                    <td className="px-6 py-4 text-right font-bold text-slate-900">{formatCurrency(item.total_amount, invoice.currency)}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan={9} className="px-6 py-8 text-center text-slate-400">
                    No individual line items parsed. Summary total stored.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Financial Summary & Breakdown */}
      <div className="flex flex-col md:flex-row justify-end gap-6">
        <div className="w-full max-w-md bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs space-y-3">
          <div className="flex justify-between text-xs text-slate-600">
            <span>Taxable Amount:</span>
            <span className="font-semibold text-slate-900">{formatCurrency(invoice.taxable_amount, invoice.currency)}</span>
          </div>

          {Number(invoice.cgst_amount) > 0 && (
            <div className="flex justify-between text-xs text-slate-600">
              <span>CGST:</span>
              <span className="font-semibold text-slate-900">{formatCurrency(invoice.cgst_amount, invoice.currency)}</span>
            </div>
          )}

          {Number(invoice.sgst_amount) > 0 && (
            <div className="flex justify-between text-xs text-slate-600">
              <span>SGST:</span>
              <span className="font-semibold text-slate-900">{formatCurrency(invoice.sgst_amount, invoice.currency)}</span>
            </div>
          )}

          {Number(invoice.igst_amount) > 0 && (
            <div className="flex justify-between text-xs text-slate-600">
              <span>IGST:</span>
              <span className="font-semibold text-slate-900">{formatCurrency(invoice.igst_amount, invoice.currency)}</span>
            </div>
          )}

          <div className="flex justify-between text-xs font-semibold text-emerald-700 pt-2 border-t border-slate-100">
            <span>Total GST:</span>
            <span>{formatCurrency(invoice.total_tax, invoice.currency)}</span>
          </div>

          {Number(invoice.round_off) !== 0 && (
            <div className="flex justify-between text-xs text-slate-500">
              <span>Round Off:</span>
              <span>{formatCurrency(invoice.round_off, invoice.currency)}</span>
            </div>
          )}

          <div className="flex justify-between text-lg font-bold text-slate-900 pt-3 border-t-2 border-slate-200">
            <span>Grand Total:</span>
            <span className="text-indigo-600">{formatCurrency(invoice.total_amount, invoice.currency)}</span>
          </div>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      <ConfirmDialog
        isOpen={showDeleteDialog}
        title="Delete Invoice"
        message={`Are you sure you want to delete invoice ${invoice.invoice_number}? This cannot be undone.`}
        confirmLabel="Delete"
        isDestructive={true}
        isLoading={isDeleting}
        onConfirm={handleDelete}
        onCancel={() => setShowDeleteDialog(false)}
      />
    </div>
  );
}
