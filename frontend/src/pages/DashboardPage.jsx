import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import {
  Wallet,
  Receipt,
  FileCheck2,
  Clock,
  ArrowRight,
  TrendingUp,
  Percent,
} from 'lucide-react';
import PageHeader from '../components/layout/PageHeader';
import StatCard from '../components/dashboard/StatCard';
import ExpenseChart from '../components/dashboard/ExpenseChart';
import GSTBreakdown from '../components/dashboard/GSTBreakdown';
import VendorExpenseList from '../components/dashboard/VendorExpenseList';
import InvoiceTable from '../components/invoices/InvoiceTable';
import LoadingState from '../components/common/LoadingState';
import ErrorMessage from '../components/common/ErrorMessage';
import EmptyState from '../components/common/EmptyState';
import { apiClient } from '../api/client';
import { formatCurrency } from '../utils/formatters';

export default function DashboardPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [summary, setSummary] = useState(null);
  const [monthlyData, setMonthlyData] = useState([]);
  const [gstData, setGstData] = useState(null);
  const [vendorData, setVendorData] = useState([]);
  const [recentInvoices, setRecentInvoices] = useState([]);

  const fetchData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [sumRes, monthRes, gstRes, vendorRes, invRes] = await Promise.all([
        apiClient.getDashboardSummary(),
        apiClient.getMonthlyExpenses(),
        apiClient.getGSTBreakdown(),
        apiClient.getVendorExpenses(5),
        apiClient.getInvoices({ limit: 5, sort_by: 'created_at', sort_order: 'desc' }),
      ]);

      setSummary(sumRes);
      setMonthlyData(monthRes);
      setGstData(gstRes);
      setVendorData(vendorRes);
      setRecentInvoices(invRes.items || []);
    } catch (err) {
      setError(err.message || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  if (loading) {
    return <LoadingState message="Fetching live financial metrics from PostgreSQL..." rows={5} />;
  }

  if (error) {
    return (
      <ErrorMessage
        title="Failed to Load Dashboard"
        message={error}
        onRetry={fetchData}
      />
    );
  }

  return (
    <div className="space-y-8 animate-fade-in">
      {/* Page Title & Quick Actions */}
      <PageHeader
        title="Expense & GST Dashboard"
        subtitle="Real-time financial summary, automated GST reconciliation, and invoice processing."
      >
        <Link
          to="/upload"
          className="px-4 py-2 rounded-xl text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 shadow-sm shadow-indigo-600/20 transition-all"
        >
          Upload New Invoice
        </Link>
      </PageHeader>

      {/* Primary Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5">
        <StatCard
          title="Total Expenses"
          value={formatCurrency(summary?.total_expenses || 0)}
          subtitle="Cumulative verified expenses"
          icon={Wallet}
          variant="indigo"
        />

        <StatCard
          title="Total Taxable"
          value={formatCurrency(summary?.total_taxable || 0)}
          subtitle="Pre-tax expense base"
          icon={TrendingUp}
          variant="blue"
        />

        <StatCard
          title="Total GST Reconciled"
          value={formatCurrency(summary?.total_gst || 0)}
          subtitle={`CGST: ${formatCurrency(summary?.total_cgst || 0)} | SGST: ${formatCurrency(summary?.total_sgst || 0)}`}
          icon={Percent}
          variant="emerald"
        />

        <StatCard
          title="Total Invoices"
          value={summary?.total_invoices || 0}
          subtitle={`${summary?.pending_reviews || 0} pending review`}
          badge={summary?.pending_reviews > 0 ? `${summary.pending_reviews} review` : 'All cleared'}
          icon={Receipt}
          variant={summary?.pending_reviews > 0 ? 'amber' : 'purple'}
        />
      </div>

      {/* Charts Row: Monthly Expenses & GST Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="text-base font-bold text-slate-900 tracking-tight">
                Monthly Expense Trend
              </h2>
              <p className="text-xs text-slate-500">
                Monthly expense totals, taxable amounts, and GST components.
              </p>
            </div>
          </div>
          <ExpenseChart data={monthlyData} />
        </div>

        {/* GST Breakdown Card */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs">
          <div className="mb-6">
            <h2 className="text-base font-bold text-slate-900 tracking-tight">
              GST Distribution
            </h2>
            <p className="text-xs text-slate-500">
              Tax allocation across CGST, SGST, and IGST.
            </p>
          </div>
          <GSTBreakdown breakdown={gstData} />
        </div>
      </div>

      {/* Row: Top Vendors & Recent Invoices Preview */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Top Vendors */}
        <div className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h2 className="text-base font-bold text-slate-900 tracking-tight">
                Top Vendors by Spend
              </h2>
              <p className="text-xs text-slate-500">
                Highest expenditure suppliers.
              </p>
            </div>
            <Link
              to="/vendors"
              className="text-xs font-semibold text-indigo-600 hover:text-indigo-700 flex items-center gap-1"
            >
              All Vendors <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
          <VendorExpenseList vendors={vendorData} />
        </div>

        {/* Recent Invoices Preview */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-base font-bold text-slate-900 tracking-tight">
                Recent Invoices
              </h2>
              <p className="text-xs text-slate-500">
                Latest extracted and processed invoices.
              </p>
            </div>
            <Link
              to="/invoices"
              className="text-xs font-semibold text-indigo-600 hover:text-indigo-700 flex items-center gap-1"
            >
              View All Invoices <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>

          {recentInvoices.length > 0 ? (
            <InvoiceTable
              invoices={recentInvoices}
              total={summary?.total_invoices || recentInvoices.length}
              page={1}
              totalPages={1}
              onPageChange={() => {}}
              onSortChange={() => {}}
              onDeleteSuccess={fetchData}
            />
          ) : (
            <EmptyState
              title="No invoices yet"
              description="Upload your first invoice PDF to start automated financial tracking."
              actionLabel="Upload First Invoice"
              onAction={() => window.location.href = '/upload'}
            />
          )}
        </div>
      </div>
    </div>
  );
}
