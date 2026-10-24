import React, { useState } from 'react';
import { AlertTriangle, CheckCircle, HelpCircle } from 'lucide-react';

export default function DiscrepancyBadge({ score, discrepancies = [], isDuplicate = false }) {
  const [showTooltip, setShowTooltip] = useState(false);
  const numScore = Number(score) || 0;
  const issues = Array.isArray(discrepancies) ? discrepancies : [];

  let badgeColor = 'bg-emerald-50 text-emerald-700 border-emerald-200';
  let Icon = CheckCircle;

  if (isDuplicate || issues.length > 0 || numScore < 90) {
    badgeColor = 'bg-amber-50 text-amber-700 border-amber-200';
    Icon = AlertTriangle;
  }

  return (
    <div className="relative inline-block">
      <button
        type="button"
        onMouseEnter={() => setShowTooltip(true)}
        onMouseLeave={() => setShowTooltip(false)}
        onClick={() => setShowTooltip(!showTooltip)}
        className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-semibold border ${badgeColor} cursor-pointer transition-colors`}
      >
        <Icon className="w-3.5 h-3.5" />
        <span>{numScore.toFixed(0)}%</span>
        {issues.length > 0 && (
          <span className="w-4 h-4 rounded-full bg-amber-200/70 text-amber-900 text-[10px] flex items-center justify-center font-bold">
            {issues.length}
          </span>
        )}
      </button>

      {/* Issues Tooltip Popover */}
      {showTooltip && (issues.length > 0 || isDuplicate) && (
        <div className="absolute left-0 top-full mt-1.5 z-40 w-72 p-3 bg-slate-900 text-white rounded-xl shadow-xl text-xs border border-slate-800 animate-fade-in pointer-events-none">
          <p className="font-semibold text-amber-400 mb-1.5 flex items-center gap-1">
            <AlertTriangle className="w-3.5 h-3.5" />
            Detected Discrepancies ({issues.length})
          </p>
          <ul className="space-y-1 list-disc list-inside text-slate-300">
            {isDuplicate && (
              <li className="text-rose-300 font-medium">Duplicate invoice number for this vendor</li>
            )}
            {issues.map((iss, idx) => (
              <li key={idx} className="leading-snug">
                {iss}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
