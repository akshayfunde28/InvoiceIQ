import React from 'react';
import { NavLink } from 'react-router-dom';
import {
  LayoutDashboard,
  FileText,
  UploadCloud,
  BarChart3,
  Building2,
  Receipt,
  Sparkles
} from 'lucide-react';

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard },
  { name: 'Invoices', href: '/invoices', icon: FileText },
  { name: 'Upload Invoice', href: '/upload', icon: UploadCloud },
  { name: 'Expense Analytics', href: '/analytics', icon: BarChart3 },
  { name: 'Vendors', href: '/vendors', icon: Building2 },
];

export default function Sidebar() {
  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 text-slate-300 flex flex-col shrink-0 h-screen sticky top-0">
      {/* Brand Logo */}
      <div className="h-16 flex items-center px-6 gap-3 border-b border-slate-800/80">
        <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center text-white shadow-lg shadow-indigo-500/25">
          <Receipt className="w-5 h-5" />
        </div>
        <div>
          <span className="text-lg font-bold text-white tracking-tight flex items-center gap-1.5">
            Invoice<span className="text-indigo-400">IQ</span>
          </span>
          <span className="text-[10px] uppercase font-semibold tracking-wider text-slate-400 block -mt-1">
            AI Expense Hub
          </span>
        </div>
      </div>

      {/* Navigation links */}
      <nav className="flex-1 px-3 py-6 space-y-1.5 overflow-y-auto">
        {navigation.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.name}
              to={item.href}
              end={item.href === '/'}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3.5 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  isActive
                    ? 'bg-indigo-600 text-white shadow-md shadow-indigo-600/30'
                    : 'text-slate-400 hover:text-slate-100 hover:bg-slate-800/60'
                }`
              }
            >
              <Icon className="w-4 h-4 shrink-0" />
              <span>{item.name}</span>
            </NavLink>
          );
        })}
      </nav>

      {/* Indian GST AI Badge info card */}
      <div className="p-4 border-t border-slate-800/80">
        <div className="p-3.5 rounded-xl bg-gradient-to-br from-indigo-950/60 to-slate-800/70 border border-indigo-500/20 text-xs">
          <div className="flex items-center gap-1.5 text-indigo-400 font-semibold mb-1">
            <Sparkles className="w-3.5 h-3.5" />
            <span>Smart GST Engine</span>
          </div>
          <p className="text-slate-400 leading-relaxed text-[11px]">
            PyMuPDF + Grok AI with automated CGST/SGST/IGST reconciliation.
          </p>
        </div>
      </div>
    </aside>
  );
}
