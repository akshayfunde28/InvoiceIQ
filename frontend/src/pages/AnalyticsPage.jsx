import React, { useEffect, useState } from 'react';
import {
  BarChart3,
  Percent,
  Wallet,
  Building2,
  Calendar,
  Layers,
} from 'lucide-react';
import PageHeader from '../components/layout/PageHeader';
import StatCard from '../components/dashboard/StatCard';
import ExpenseChart from '../components/dashboard/ExpenseChart';
import GSTBreakdown from '../components/dashboard/GSTBreakdown';
import VendorExpenseList from '../components/dashboard/VendorExpenseList';
import LoadingState from '../components/common/LoadingState';
import ErrorMessage from '../components/common/ErrorMessage';
import { apiClient } from '../api/client';
import { formatCurrency, formatPercentage } from '../utils/formatters';

export default function AnalyticsPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [summary, setSummary] = useState(null);
  const [monthlyData, setMonthlyData] = useState([]);
  const [gstData, setGstData] = useState(null);
  const [vendorData, setVendorData] = useState([]);

  const fetchAnalytics = async () => {
    setLoading(true);
    setError(null);
    try {
      const [sumRes, monthRes, gstRes, vendorRes] = await Promise.all([
        apiClient.getDashboardSummary(),
        apiClient.getMonthlyExpenses(24),
        apiClient.getGSTBreakdown(),
        apiClient.getVendorExpenses(10),
      ]);

      setSummary(sumRes);
      setMonthlyData(monthRes);
      setGstData(gstRes);
      setVendorData(vendorRes);
    } catch (err) {
      setError(err.message || 'Failed to fetch analytics');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  if (loading) {
    return <LoadingState message="Computing statutory GST aggregations & expense trends..." rows={6} />;
  }

  if (error) {
    return (
      <ErrorMessage
        title="Failed to Load Analytics"
        message={error}
        onRetry={fetchAnalytics}
      />
    );
  }

  const gstRatio = summary?.total_expenses > 0
    ? (Number(summary.total_gst) / Number(summary.total_expenses)) * 100
    : 0;

  return (
    <div className="space-y-8 animate-fade-in">
      <PageHeader
        title="Expense & GST Analytics"
        subtitle="In-depth audit of expenditures, vendor concentration, and Indian GST tax slabs."
      />

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard
          title="Total Expenditure"
          value={formatCurrency(summary?.total_expenses || 0)}
          subtitle="All confirmed & tracked invoices"
          icon={Wallet}
          variant="indigo"
        />

        <StatCard
          title="Effective Tax Rate"
          value={formatPercentage(gstRatio)}
          subtitle="Tax share of total invoice spend"
          icon={Percent}
          variant="emerald"
        />

        <StatCard
          title="Average Invoice Value"
          value={formatCurrency(summary?.average_invoice_value || 0)}
          subtitle={`Across ${summary?.total_invoices || 0} processed invoices`}
          icon={BarChart3}
          variant="blue"
        />

        <StatCard
          title="Confirmed Invoices"
          value={summary?.confirmed_invoices || 0}
          subtitle={`${summary?.pending_reviews || 0} invoices awaiting sign-off`}
          icon={Layers}
          variant="purple"
        />
      </div>

      {/* Monthly Expense Chart */}
      <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs">
        <div className="mb-6">
          <h2 className="text-base font-bold text-slate-900 tracking-tight">
            Historical Expenditure Trends (Monthly)
          </h2>
          <p className="text-xs text-slate-500">
            Monthly gross spend, taxable base amount, and total GST.
          </p>
        </div>
        <ExpenseChart data={monthlyData} />
      </div>

      {/* Bottom Grid: GST Breakdown & Top 10 Vendors */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs">
          <div className="mb-6">
            <h2 className="text-base font-bold text-slate-900 tracking-tight">
              GST Tax Breakdown & Slabs
            </h2>
            <p className="text-xs text-slate-500">
              Tax components and slab distribution.
            </p>
          </div>
          <GSTBreakdown breakdown={gstData} />
        </div>

        <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs">
          <div className="mb-6">
            <h2 className="text-base font-bold text-slate-900 tracking-tight">
              Vendor Concentration (Top 10)
            </h2>
            <p className="text-xs text-slate-500">
              Breakdown of expenses by supplier.
            </p>
          </div>
          <VendorExpenseList vendors={vendorData} />
        </div>
      </div>
    </div>
  );
}
