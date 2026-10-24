import React from 'react';
import { formatCurrency, formatPercentage } from '../../utils/formatters';

export default function GSTBreakdown({ breakdown }) {
  if (!breakdown || Number(breakdown.total_gst) === 0) {
    return (
      <div className="h-72 flex items-center justify-center text-slate-400 text-sm">
        No GST data available yet.
      </div>
    );
  }

  const {
    total_cgst = 0,
    total_sgst = 0,
    total_igst = 0,
    total_gst = 0,
    cgst_percentage = 0,
    sgst_percentage = 0,
    igst_percentage = 0,
    slabs = [],
  } = breakdown;

  return (
    <div className="space-y-6">
      {/* Total GST pill banner */}
      <div className="bg-slate-50 border border-slate-200/80 rounded-xl p-4 flex items-center justify-between">
        <span className="text-xs font-semibold uppercase text-slate-500">Cumulative Tax</span>
        <span className="text-xl font-bold text-slate-900">{formatCurrency(total_gst)}</span>
      </div>

      {/* Tax Component Progress Bars */}
      <div className="space-y-4">
        <div>
          <div className="flex justify-between text-xs font-medium text-slate-600 mb-1.5">
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-indigo-500" />
              CGST (Central Tax)
            </span>
            <span className="font-semibold text-slate-900">
              {formatCurrency(total_cgst)} ({formatPercentage(cgst_percentage)})
            </span>
          </div>
          <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
            <div
              className="bg-indigo-500 h-2 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(100, Math.max(0, cgst_percentage))}%` }}
            />
          </div>
        </div>

        <div>
          <div className="flex justify-between text-xs font-medium text-slate-600 mb-1.5">
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-emerald-500" />
              SGST (State Tax)
            </span>
            <span className="font-semibold text-slate-900">
              {formatCurrency(total_sgst)} ({formatPercentage(sgst_percentage)})
            </span>
          </div>
          <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
            <div
              className="bg-emerald-500 h-2 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(100, Math.max(0, sgst_percentage))}%` }}
            />
          </div>
        </div>

        <div>
          <div className="flex justify-between text-xs font-medium text-slate-600 mb-1.5">
            <span className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full bg-amber-500" />
              IGST (Integrated Tax)
            </span>
            <span className="font-semibold text-slate-900">
              {formatCurrency(total_igst)} ({formatPercentage(igst_percentage)})
            </span>
          </div>
          <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
            <div
              className="bg-amber-500 h-2 rounded-full transition-all duration-500"
              style={{ width: `${Math.min(100, Math.max(0, igst_percentage))}%` }}
            />
          </div>
        </div>
      </div>

      {/* Tax Slabs breakdown */}
      {slabs && slabs.length > 0 && (
        <div className="pt-2 border-t border-slate-100">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block mb-3">
            Active GST Slabs
          </span>
          <div className="grid grid-cols-2 gap-2">
            {slabs.map((slab, i) => (
              <div
                key={i}
                className="bg-white border border-slate-200/80 rounded-xl p-3 text-xs flex flex-col justify-between"
              >
                <div className="flex items-center justify-between mb-1">
                  <span className="font-bold text-slate-800">{slab.rate}% Slab</span>
                  <span className="text-[10px] text-slate-400">Tax</span>
                </div>
                <div className="font-semibold text-emerald-600">
                  {formatCurrency(slab.tax)}
                </div>
                <div className="text-[11px] text-slate-500 mt-1">
                  On {formatCurrency(slab.taxable)} taxable
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
