import React from 'react';
import { AlertCircle, RotateCcw } from 'lucide-react';

export default function ErrorMessage({
  title = 'An error occurred',
  message,
  onRetry,
}) {
  return (
    <div className="rounded-xl bg-rose-50 border border-rose-200 p-5 my-4">
      <div className="flex items-start">
        <div className="shrink-0 text-rose-500 mt-0.5">
          <AlertCircle className="w-5 h-5" />
        </div>
        <div className="ml-3 flex-1">
          <h3 className="text-sm font-semibold text-rose-800">{title}</h3>
          <div className="mt-1 text-sm text-rose-700">
            {message || 'Unable to complete the requested operation.'}
          </div>
          {onRetry && (
            <div className="mt-4">
              <button
                type="button"
                onClick={onRetry}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-md bg-rose-100 hover:bg-rose-200 text-rose-800 text-xs font-medium transition-colors cursor-pointer"
              >
                <RotateCcw className="w-3.5 h-3.5" />
                Retry Operation
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
