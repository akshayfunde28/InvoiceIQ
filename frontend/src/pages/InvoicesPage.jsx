import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { UploadCloud, FileText } from 'lucide-react';
import PageHeader from '../components/layout/PageHeader';
import InvoiceFilters from '../components/invoices/InvoiceFilters';
import InvoiceTable from '../components/invoices/InvoiceTable';
import LoadingState from '../components/common/LoadingState';
import ErrorMessage from '../components/common/ErrorMessage';
import EmptyState from '../components/common/EmptyState';
import { apiClient } from '../api/client';

export default function InvoicesPage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const [invoices, setInvoices] = useState([]);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(1);

  const [filters, setFilters] = useState({
    page: 1,
    limit: 10,
    search: '',
    category: '',
    review_status: '',
    payment_status: '',
    from_date: '',
    to_date: '',
    min_amount: '',
    max_amount: '',
    sort_by: 'created_at',
    sort_order: 'desc',
  });

  const fetchInvoices = async () => {
    setLoading(true);
    setError(null);
    try {
      const cleanParams = {};
      Object.entries(filters).forEach(([k, v]) => {
        if (v !== '' && v !== null && v !== undefined) {
          cleanParams[k] = v;
        }
      });

      const response = await apiClient.getInvoices(cleanParams);
      setInvoices(response.items || []);
      setTotal(response.total || 0);
      setTotalPages(response.total_pages || 1);
    } catch (err) {
      setError(err.message || 'Failed to fetch invoices');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInvoices();
  }, [filters]);

  const handlePageChange = (newPage) => {
    setFilters((prev) => ({ ...prev, page: newPage }));
  };

  const handleSortChange = (sortBy, sortOrder) => {
    setFilters((prev) => ({ ...prev, sort_by: sortBy, sort_order: sortOrder, page: 1 }));
  };

  const hasFiltersApplied = Boolean(
    filters.search ||
    filters.category ||
    filters.review_status ||
    filters.payment_status ||
    filters.from_date ||
    filters.to_date ||
    filters.min_amount ||
    filters.max_amount
  );

  const handleResetFilters = () => {
    setFilters({
      page: 1,
      limit: 10,
      search: '',
      category: '',
      review_status: '',
      payment_status: '',
      from_date: '',
      to_date: '',
      min_amount: '',
      max_amount: '',
      sort_by: 'created_at',
      sort_order: 'desc',
    });
  };

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader
        title="Invoices Management"
        subtitle={`Total of ${total} invoices processed and tracked in database.`}
      >
        <Link
          to="/upload"
          className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-xs font-semibold text-white bg-indigo-600 hover:bg-indigo-700 shadow-sm shadow-indigo-600/20 transition-all cursor-pointer"
        >
          <UploadCloud className="w-4 h-4" />
          <span>Upload Invoice</span>
        </Link>
      </PageHeader>

      {/* Filters */}
      <InvoiceFilters
        filters={filters}
        onChange={setFilters}
        onReset={handleResetFilters}
      />

      {/* Error state */}
      {error && (
        <ErrorMessage
          title="Failed to Load Invoices"
          message={error}
          onRetry={fetchInvoices}
        />
      )}

      {/* Loading state */}
      {loading ? (
        <LoadingState message="Loading invoices from database..." rows={6} />
      ) : invoices.length > 0 ? (
        <InvoiceTable
          invoices={invoices}
          total={total}
          page={filters.page}
          limit={filters.limit}
          totalPages={totalPages}
          onPageChange={handlePageChange}
          onSortChange={handleSortChange}
          sortBy={filters.sort_by}
          sortOrder={filters.sort_order}
          onDeleteSuccess={fetchInvoices}
        />
      ) : (
        <EmptyState
          icon={FileText}
          title="No invoices found"
          description={
            hasFiltersApplied
              ? 'No invoices match your current filter parameters. Try clearing your filters.'
              : 'You have not uploaded any invoices yet. Click below to process your first invoice.'
          }
          actionLabel={
            hasFiltersApplied
              ? 'Clear Filters'
              : 'Upload Invoice'
          }
          onAction={
            hasFiltersApplied
              ? handleResetFilters
              : () => window.location.href = '/upload'
          }
        />
      )}
    </div>
  );
}
