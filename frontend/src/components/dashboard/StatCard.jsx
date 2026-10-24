import React from 'react';

export default function StatCard({
  title,
  value,
  subtitle,
  icon: Icon,
  variant = 'indigo', // indigo, emerald, amber, blue, purple
  badge,
}) {
  const variantStyles = {
    indigo: {
      iconBg: 'bg-indigo-50 text-indigo-600 border border-indigo-100',
      badgeBg: 'bg-indigo-50 text-indigo-700 border border-indigo-100',
    },
    emerald: {
      iconBg: 'bg-emerald-50 text-emerald-600 border border-emerald-100',
      badgeBg: 'bg-emerald-50 text-emerald-700 border border-emerald-100',
    },
    amber: {
      iconBg: 'bg-amber-50 text-amber-600 border border-amber-100',
      badgeBg: 'bg-amber-50 text-amber-700 border border-amber-100',
    },
    blue: {
      iconBg: 'bg-blue-50 text-blue-600 border border-blue-100',
      badgeBg: 'bg-blue-50 text-blue-700 border border-blue-100',
    },
    purple: {
      iconBg: 'bg-purple-50 text-purple-600 border border-purple-100',
      badgeBg: 'bg-purple-50 text-purple-700 border border-purple-100',
    },
  };

  const style = variantStyles[variant] || variantStyles.indigo;

  return (
    <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs hover:shadow-md transition-shadow">
      <div className="flex items-center justify-between mb-4">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
          {title}
        </span>
        {Icon && (
          <div className={`w-10 h-10 rounded-xl flex items-center justify-center ${style.iconBg}`}>
            <Icon className="w-5 h-5" />
          </div>
        )}
      </div>

      <div className="flex items-baseline justify-between gap-2">
        <div className="text-2xl font-bold text-slate-900 tracking-tight">
          {value}
        </div>
        {badge && (
          <span className={`text-xs font-semibold px-2.5 py-0.5 rounded-full ${style.badgeBg}`}>
            {badge}
          </span>
        )}
      </div>

      {subtitle && (
        <div className="mt-2 text-xs text-slate-500 font-medium">
          {subtitle}
        </div>
      )}
    </div>
  );
}
