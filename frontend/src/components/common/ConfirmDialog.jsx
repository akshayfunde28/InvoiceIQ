import React from 'react';
import { AlertTriangle } from 'lucide-react';

export default function ConfirmDialog({
  isOpen,
  title = 'Confirm Action',
  message = 'Are you sure you want to proceed? This action cannot be undone.',
  confirmLabel = 'Confirm',
  cancelLabel = 'Cancel',
  isDestructive = false,
  isLoading = false,
  onConfirm,
  onCancel,
}) {
  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto bg-slate-900/50 backdrop-blur-xs flex items-center justify-center p-4">
      <div className="relative bg-white rounded-2xl max-w-md w-full p-6 shadow-2xl border border-slate-100 transform transition-all animate-fade-in">
        <div className="flex items-start gap-4">
          <div className={`shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${isDestructive ? 'bg-rose-100 text-rose-600' : 'bg-indigo-100 text-indigo-600'}`}>
            <AlertTriangle className="w-5 h-5" />
          </div>
          <div className="flex-1">
            <h3 className="text-base font-semibold text-slate-900">{title}</h3>
            <p className="mt-2 text-sm text-slate-600 leading-relaxed">{message}</p>
          </div>
        </div>

        <div className="mt-6 flex items-center justify-end gap-3">
          <button
            type="button"
            disabled={isLoading}
            onClick={onCancel}
            className="px-4 py-2 rounded-lg border border-slate-200 text-sm font-medium text-slate-700 bg-white hover:bg-slate-50 transition-colors cursor-pointer"
          >
            {cancelLabel}
          </button>
          <button
            type="button"
            disabled={isLoading}
            onClick={onConfirm}
            className={`px-4 py-2 rounded-lg text-sm font-medium text-white transition-colors cursor-pointer shadow-sm ${
              isDestructive
                ? 'bg-rose-600 hover:bg-rose-700 focus:ring-rose-500'
                : 'bg-indigo-600 hover:bg-indigo-700 focus:ring-indigo-500'
            }`}
          >
            {isLoading ? 'Processing...' : confirmLabel}
          </button>
        </div>
      </div>
    </div>
  );
}
