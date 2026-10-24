import React from 'react';
import { Loader2 } from 'lucide-react';

export default function LoadingState({ message = 'Loading data...', rows = 4 }) {
  return (
    <div className="w-full p-8 flex flex-col items-center justify-center space-y-4">
      <Loader2 className="w-8 h-8 text-indigo-600 animate-spin" />
      <p className="text-sm font-medium text-slate-500">{message}</p>
      
      {/* Skeletons */}
      <div className="w-full max-w-2xl space-y-3 mt-4">
        {[...Array(rows)].map((_, i) => (
          <div key={i} className="h-10 bg-slate-100 rounded-lg animate-pulse w-full" />
        ))}
      </div>
    </div>
  );
}
