import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import {
  FileText,
  Download,
  Eye,
  Trash2,
  ChevronLeft,
  ChevronRight,
  ArrowUpDown,
  Building2,
} from 'lucide-react';
import { formatCurrency, formatDate } from '../../utils/formatters';
import StatusBadge from './StatusBadge';
import DiscrepancyBadge from './DiscrepancyBadge';
import ConfirmDialog from '../common/ConfirmDialog';
import { apiClient } from '../../api/client';

export default function InvoiceTable({
  invoices = [],
  total = 0,
  page = 1,
  limit = 10,
  totalPages = 1,
  onPageChange,
  onSortChange,
  sortBy = 'created_at',
  sortOrder = 'desc',
  onDeleteSuccess,
}) {
  const [deleteTarget, setDeleteTarget] = useState(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleDelete = async () => {
    if (!deleteTarget) return;
    setIsDeleting(true);
    try {
      await apiClient.deleteInvoice(deleteTarget.id);
      setDeleteTarget(null);
      if (onDeleteSuccess) onDeleteSuccess();
    } catch (err) {
      alert(`Failed to delete invoice: ${err.message}`);
    } finally {
      setIsDeleting(false);
    }
  };

  const renderSortHeader = (label, columnKey) => {
    const isSorted = sortBy === columnKey;
    return (
      <button
        type="button"
        onClick={() => {
          const nextOrder = isSorted && sortOrder === 'asc' ? 'desc' : 'asc';
          onSortChange(columnKey, nextOrder);
        }}
        className="inline-flex items-center gap-1.5 uppercase font-semibold text-xs tracking-wider text-slate-500 hover:text-slate-900 cursor-pointer"
      >
        <span>{label}</span>
        <ArrowUpDown className={`w-3.5 h-3.5 ${isSorted ? 'text-indigo-600' : 'text-slate-300'}`} />
      </button>
    );
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200/80 shadow-xs overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-slate-600">
          <thead className="bg-slate-50/80 border-b border-slate-200/80 text-xs">
            <tr>
              <th className="px-6 py-4">{renderSortHeader('Invoice #', 'invoice_number')}</th>
              <th className="px-6 py-4">{renderSortHeader('Date', 'invoice_date')}</th>
              <th className="px-6 py-4">{renderSortHeader('Vendor', 'vendor_name_raw')}</th>
              <th className="px-6 py-4 text-right">{renderSortHeader('Total Amount', 'total_amount')}</th>
              <th className="px-6 py-4">Total GST</th>
              <th className="px-6 py-4 text-center">Score / Check</th>
              <th className="px-6 py-4">Review Status</th>
              <th className="px-6 py-4">Payment</th>
              <th className="px-6 py-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {invoices.map((inv) => (
              <tr key={inv.id} className="hover:bg-slate-50/80 transition-colors">
                {/* Invoice # */}
                <td className="px-6 py-4 font-semibold text-slate-900 whitespace-nowrap">
                  <Link
                    to={`/invoices/${inv.id}`}
                    className="flex items-center gap-2 hover:text-indigo-600 transition-colors"
                  >
                    <FileText className="w-4 h-4 text-indigo-500 shrink-0" />
                    <span>{inv.invoice_number}</span>
                  </Link>
                </td>

                {/* Date */}
                <td className="px-6 py-4 whitespace-nowrap text-xs text-slate-500">
                  {formatDate(inv.invoice_date)}
                </td>

                {/* Vendor */}
                <td className="px-6 py-4 max-w-xs truncate">
                  <div className="flex items-center gap-2">
                    <Building2 className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                    <span className="font-medium text-slate-900 truncate">
                      {inv.vendor_name_raw}
                    </span>
                  </div>
                  {inv.vendor_gstin && (
                    <span className="text-[11px] text-slate-400 block font-mono pl-5">
                      {inv.vendor_gstin}
                    </span>
                  )}
                </td>

                {/* Total Amount */}
                <td className="px-6 py-4 text-right font-bold text-slate-900 whitespace-nowrap">
                  {formatCurrency(inv.total_amount, inv.currency)}
                </td>

                {/* Total GST */}
                <td className="px-6 py-4 text-xs font-medium text-slate-600 whitespace-nowrap">
                  {formatCurrency(inv.total_tax, inv.currency)}
                </td>

                {/* Validation Score & Discrepancies */}
                <td className="px-6 py-4 text-center whitespace-nowrap">
                  <DiscrepancyBadge
                    score={inv.validation_score}
                    discrepancies={inv.discrepancy_flags}
                    isDuplicate={inv.is_duplicate}
                  />
                </td>

                {/* Review Status */}
                <td className="px-6 py-4 whitespace-nowrap">
                  <StatusBadge type="review" status={inv.review_status} />
                </td>

                {/* Payment Status */}
                <td className="px-6 py-4 whitespace-nowrap">
                  <StatusBadge type="payment" status={inv.payment_status} />
                </td>

                {/* Actions */}
                <td className="px-6 py-4 text-right whitespace-nowrap">
                  <div className="flex items-center justify-end gap-1.5">
                    <Link
                      to={`/invoices/${inv.id}`}
                      className="p-1.5 rounded-lg text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 transition-colors"
                      title="View details"
                    >
                      <Eye className="w-4 h-4" />
                    </Link>
                    <a
                      href={apiClient.getInvoiceFileUrl(inv.id)}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="p-1.5 rounded-lg text-slate-400 hover:text-emerald-600 hover:bg-emerald-50 transition-colors"
                      title="Download PDF"
                    >
                      <Download className="w-4 h-4" />
                    </a>
                    <button
                      type="button"
                      onClick={() => setDeleteTarget(inv)}
                      className="p-1.5 rounded-lg text-slate-400 hover:text-rose-600 hover:bg-rose-50 transition-colors cursor-pointer"
                      title="Delete invoice"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination Bar */}
      <div className="px-6 py-4 bg-slate-50/60 border-t border-slate-200/80 flex items-center justify-between text-xs text-slate-500">
        <div>
          Showing <span className="font-semibold text-slate-900">{invoices.length}</span> of{' '}
          <span className="font-semibold text-slate-900">{total}</span> total invoices
        </div>

        <div className="flex items-center gap-2">
          <button
            type="button"
            disabled={page <= 1}
            onClick={() => onPageChange(page - 1)}
            className="p-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors cursor-pointer"
            title="Previous page"
          >
            <ChevronLeft className="w-4 h-4" />
          </button>
          <span className="font-medium text-slate-700 px-2">
            Page {page} of {totalPages || 1}
          </span>
          <button
            type="button"
            disabled={page >= totalPages}
            onClick={() => onPageChange(page + 1)}
            className="p-1.5 rounded-lg border border-slate-200 bg-white hover:bg-slate-50 disabled:opacity-40 disabled:cursor-not-allowed transition-colors cursor-pointer"
            title="Next page"
          >
            <ChevronRight className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Delete Confirmation Modal */}
      <ConfirmDialog
        isOpen={Boolean(deleteTarget)}
        title="Delete Invoice"
        message={`Are you sure you want to permanently delete invoice ${deleteTarget?.invoice_number}? This will remove all associated line items and financial records.`}
        confirmLabel="Delete Invoice"
        isDestructive={true}
        isLoading={isDeleting}
        onConfirm={handleDelete}
        onCancel={() => setDeleteTarget(null)}
      />
    </div>
  );
}
