import React from 'react';
import { FolderOpen } from 'lucide-react';

export default function EmptyState({
  icon: Icon = FolderOpen,
  title = 'No records found',
  description = 'There are no items matching your criteria at this moment.',
  actionLabel,
  onAction,
}) {
  return (
    <div className="w-full py-16 px-4 flex flex-col items-center justify-center text-center bg-white rounded-xl border border-dashed border-slate-200">
      <div className="w-14 h-14 rounded-full bg-slate-50 flex items-center justify-center text-slate-400 mb-4 ring-8 ring-slate-50/50">
        <Icon className="w-7 h-7" />
      </div>
      <h3 className="text-base font-semibold text-slate-900">{title}</h3>
      <p className="mt-1 text-sm text-slate-500 max-w-sm">{description}</p>
      {actionLabel && onAction && (
        <button
          onClick={onAction}
          className="mt-6 inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-lg shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors cursor-pointer"
        >
          {actionLabel}
        </button>
      )}
    </div>
  );
}
