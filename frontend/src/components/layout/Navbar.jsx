import React, { useEffect, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { UploadCloud, CheckCircle2, AlertCircle } from 'lucide-react';
import { apiClient } from '../../api/client';

export default function Navbar() {
  const location = useLocation();
  const [isHealthy, setIsHealthy] = useState(true);

  useEffect(() => {
    apiClient.checkHealth()
      .then(() => setIsHealthy(true))
      .catch(() => setIsHealthy(false));
  }, []);

  const todayStr = new Date().toLocaleDateString('en-IN', {
    weekday: 'short',
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });

  return (
    <header className="h-16 bg-white border-b border-slate-200 px-8 flex items-center justify-between sticky top-0 z-30 shadow-xs">
      {/* Current Date & System Status */}
      <div className="flex items-center gap-4">
        <span className="text-xs font-medium text-slate-500 bg-slate-100 px-3 py-1.5 rounded-lg border border-slate-200/60">
          {todayStr}
        </span>
        <div className="flex items-center gap-1.5 text-xs font-medium">
          {isHealthy ? (
            <span className="inline-flex items-center gap-1 text-emerald-700 bg-emerald-50 px-2.5 py-1 rounded-full border border-emerald-200">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
              API Connected
            </span>
          ) : (
            <span className="inline-flex items-center gap-1 text-rose-700 bg-rose-50 px-2.5 py-1 rounded-full border border-rose-200">
              <AlertCircle className="w-3 h-3" />
              API Offline
            </span>
          )}
        </div>
      </div>

      {/* Action CTA */}
      <div className="flex items-center gap-3">
        {location.pathname !== '/upload' && (
          <Link
            to="/upload"
            className="inline-flex items-center gap-2 px-3.5 py-2 rounded-xl text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 shadow-sm shadow-indigo-600/20 transition-all cursor-pointer"
          >
            <UploadCloud className="w-4 h-4" />
            <span>Upload Invoice</span>
          </Link>
        )}
      </div>
    </header>
  );
}
