import React, { useState } from 'react';
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend,
} from 'recharts';
import { formatCurrency } from '../../utils/formatters';

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-slate-900 text-white p-3.5 rounded-xl shadow-xl border border-slate-800 text-xs space-y-1.5">
        <p className="font-semibold text-slate-300">{label}</p>
        {payload.map((entry, index) => (
          <div key={`tooltip-${index}`} className="flex items-center justify-between gap-4">
            <span className="flex items-center gap-1.5 text-slate-400">
              <span className="w-2 h-2 rounded-full" style={{ backgroundColor: entry.color }} />
              {entry.name}:
            </span>
            <span className="font-semibold text-white">
              {formatCurrency(entry.value)}
            </span>
          </div>
        ))}
      </div>
    );
  }
  return null;
};

export default function ExpenseChart({ data = [] }) {
  if (!data || data.length === 0) {
    return (
      <div className="h-72 flex items-center justify-center text-slate-400 text-sm">
        No monthly expense data recorded yet.
      </div>
    );
  }

  // Format data for chart
  const formattedData = data.map((d) => ({
    month: d.month,
    'Total Expense': Number(d.total_amount) || 0,
    'Taxable Amount': Number(d.taxable_amount) || 0,
    'Total GST': Number(d.gst_amount) || 0,
  }));

  return (
    <div className="w-full h-80">
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={formattedData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f1f5f9" vertical={false} />
          <XAxis
            dataKey="month"
            stroke="#94a3b8"
            fontSize={12}
            tickLine={false}
            axisLine={{ stroke: '#e2e8f0' }}
          />
          <YAxis
            stroke="#94a3b8"
            fontSize={11}
            tickLine={false}
            axisLine={false}
            tickFormatter={(val) => `₹${val >= 1000 ? `${(val / 1000).toFixed(0)}k` : val}`}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            verticalAlign="top"
            align="right"
            iconType="circle"
            wrapperStyle={{ paddingBottom: '16px', fontSize: '12px' }}
          />
          <Bar dataKey="Total Expense" fill="#6366f1" radius={[6, 6, 0, 0]} maxBarSize={45} />
          <Bar dataKey="Taxable Amount" fill="#93c5fd" radius={[6, 6, 0, 0]} maxBarSize={45} />
          <Bar dataKey="Total GST" fill="#10b981" radius={[6, 6, 0, 0]} maxBarSize={45} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
