import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { ArrowLeft } from 'lucide-react';
import InvoiceDetails from '../components/invoices/InvoiceDetails';
import LoadingState from '../components/common/LoadingState';
import ErrorMessage from '../components/common/ErrorMessage';
import { apiClient } from '../api/client';

export default function InvoiceDetailPage() {
  const { id } = useParams();
  const navigate = useNavigate();

  const [invoice, setInvoice] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchInvoice = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiClient.getInvoice(id);
      setInvoice(data);
    } catch (err) {
      setError(err.message || `Failed to load invoice #${id}`);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchInvoice();
  }, [id]);

  if (loading) {
    return <LoadingState message="Loading invoice records..." rows={6} />;
  }

  if (error || !invoice) {
    return (
      <div className="space-y-4">
        <Link
          to="/invoices"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-indigo-600 hover:text-indigo-700"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Invoices
        </Link>
        <ErrorMessage
          title="Invoice Not Found"
          message={error || 'The requested invoice does not exist.'}
          onRetry={fetchInvoice}
        />
      </div>
    );
  }

  return (
    <div className="space-y-6 animate-fade-in max-w-6xl mx-auto">
      <div className="flex items-center gap-2">
        <Link
          to="/invoices"
          className="inline-flex items-center gap-1.5 text-xs font-semibold text-slate-500 hover:text-slate-900 bg-white border border-slate-200/80 px-3 py-1.5 rounded-lg shadow-2xs transition-colors"
        >
          <ArrowLeft className="w-3.5 h-3.5" /> Back to Invoices
        </Link>
      </div>

      <InvoiceDetails
        invoice={invoice}
        onUpdateSuccess={(updated) => setInvoice(updated)}
        onDeleteSuccess={() => navigate('/invoices')}
      />
    </div>
  );
}
