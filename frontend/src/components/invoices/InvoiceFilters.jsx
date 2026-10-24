import React from 'react';
import { Search, Filter, X, Download, FileText } from 'lucide-react';
import { apiClient } from '../../api/client';

export default function InvoiceFilters({
  filters,
  onChange,
  onReset,
}) {
  const handleChange = (key, value) => {
    onChange({ ...filters, [key]: value, page: 1 });
  };

  const hasActiveFilters = Boolean(
    filters.search ||
    filters.category ||
    filters.review_status ||
    filters.payment_status ||
    filters.from_date ||
    filters.to_date ||
    filters.min_amount ||
    filters.max_amount
  );

  return (
    <div className="bg-white rounded-2xl p-5 border border-slate-200/80 shadow-xs space-y-4 mb-6">
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-6 gap-3">
        {/* Search */}
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search invoice #, vendor..."
            value={filters.search || ''}
            onChange={(e) => handleChange('search', e.target.value)}
            className="w-full pl-9.5 pr-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all placeholder:text-slate-400"
          />
        </div>

        {/* Category */}
        <div>
          <select
            value={filters.category || ''}
            onChange={(e) => handleChange('category', e.target.value)}
            className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all text-slate-700"
          >
            <option value="">All Categories</option>
            <option value="Software & Cloud">Software & Cloud</option>
            <option value="Hardware & IT Equipment">Hardware & IT Equipment</option>
            <option value="Professional Services">Professional Services</option>
            <option value="Office Supplies">Office Supplies</option>
            <option value="Travel & Transport">Travel & Transport</option>
            <option value="Marketing & Sales">Marketing & Sales</option>
            <option value="General Expenses">General Expenses</option>
          </select>
        </div>

        {/* Review Status */}
        <div>
          <select
            value={filters.review_status || ''}
            onChange={(e) => handleChange('review_status', e.target.value)}
            className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all text-slate-700"
          >
            <option value="">All Review Statuses</option>
            <option value="auto_verified">Auto Verified</option>
            <option value="needs_review">Needs Review</option>
            <option value="manually_confirmed">Manually Confirmed</option>
          </select>
        </div>

        {/* Payment Status */}
        <div>
          <select
            value={filters.payment_status || ''}
            onChange={(e) => handleChange('payment_status', e.target.value)}
            className="w-full px-3 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all text-slate-700"
          >
            <option value="">All Payment Statuses</option>
            <option value="paid">Paid</option>
            <option value="unpaid">Unpaid</option>
            <option value="partially_paid">Partial</option>
          </select>
        </div>

        {/* Date Range: From & To */}
        <div className="flex items-center gap-1.5" title="Date Range (From - To)">
          <input
            type="date"
            value={filters.from_date || ''}
            onChange={(e) => handleChange('from_date', e.target.value)}
            className="w-1/2 px-2 py-2 text-[11px] bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 text-slate-700"
            title="From date"
          />
          <span className="text-slate-400 text-xs shrink-0">-</span>
          <input
            type="date"
            value={filters.to_date || ''}
            onChange={(e) => handleChange('to_date', e.target.value)}
            className="w-1/2 px-2 py-2 text-[11px] bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 text-slate-700"
            title="To date"
          />
        </div>

        {/* Amount Range: Min & Max */}
        <div className="flex items-center gap-1.5" title="Amount Range in INR (Min - Max)">
          <input
            type="number"
            min="0"
            step="any"
            placeholder="Min ₹"
            value={filters.min_amount || ''}
            onChange={(e) => handleChange('min_amount', e.target.value)}
            className="w-1/2 px-2.5 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 text-slate-700"
            title="Minimum amount (₹)"
          />
          <span className="text-slate-400 text-xs shrink-0">-</span>
          <input
            type="number"
            min="0"
            step="any"
            placeholder="Max ₹"
            value={filters.max_amount || ''}
            onChange={(e) => handleChange('max_amount', e.target.value)}
            className="w-1/2 px-2.5 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 text-slate-700"
            title="Maximum amount (₹)"
          />
        </div>
      </div>

      {/* Filter actions */}
      <div className="flex items-center justify-between pt-2 border-t border-slate-100 text-xs">
        <div className="flex items-center gap-2">
          {hasActiveFilters && (
            <button
              type="button"
              onClick={onReset}
              className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-slate-600 bg-slate-100 hover:bg-slate-200 font-medium transition-colors cursor-pointer"
            >
              <X className="w-3.5 h-3.5" />
              Reset Filters
            </button>
          )}
        </div>

        <div className="flex items-center gap-2">
          <a
            href={apiClient.exportPdfUrl(filters)}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-rose-700 bg-rose-50 hover:bg-rose-100 font-semibold border border-rose-200/80 transition-colors cursor-pointer shadow-xs"
            title="Export filtered invoices as PDF report"
          >
            <FileText className="w-3.5 h-3.5" />
            Export PDF
          </a>
          <a
            href={apiClient.exportCsvUrl(filters)}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-indigo-700 bg-indigo-50 hover:bg-indigo-100 font-semibold border border-indigo-200/80 transition-colors cursor-pointer shadow-xs"
            title="Export filtered invoices as CSV"
          >
            <Download className="w-3.5 h-3.5" />
            Export CSV
          </a>
        </div>
      </div>
    </div>
  );
}
