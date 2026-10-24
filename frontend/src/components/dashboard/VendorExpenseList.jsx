import React from 'react';
import { Building2 } from 'lucide-react';
import { formatCurrency, formatPercentage } from '../../utils/formatters';

export default function VendorExpenseList({ vendors = [] }) {
  if (!vendors || vendors.length === 0) {
    return (
      <div className="h-64 flex items-center justify-center text-slate-400 text-sm">
        No vendor expenses recorded yet.
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {vendors.map((v, i) => (
        <div key={i} className="flex items-center justify-between p-3.5 rounded-xl bg-slate-50/70 hover:bg-slate-50 transition-colors border border-slate-100">
          <div className="flex items-center gap-3 min-w-0">
            <div className="w-9 h-9 rounded-xl bg-white border border-slate-200 flex items-center justify-center text-slate-500 shrink-0">
              <Building2 className="w-4 h-4" />
            </div>
            <div className="min-w-0">
              <p className="text-sm font-semibold text-slate-900 truncate">
                {v.vendor_name}
              </p>
              <p className="text-xs text-slate-400 truncate">
                {v.gstin ? `GSTIN: ${v.gstin}` : `${v.invoice_count} invoice(s)`}
              </p>
            </div>
          </div>

          <div className="text-right shrink-0 ml-4">
            <p className="text-sm font-bold text-slate-900">
              {formatCurrency(v.total_amount)}
            </p>
            <p className="text-xs font-medium text-indigo-600">
              {formatPercentage(v.percentage)} of total
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}
