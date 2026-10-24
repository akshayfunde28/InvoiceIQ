import React, { useEffect, useState } from 'react';
import { Building2, Search, MapPin, Mail, Phone, Calendar, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import PageHeader from '../components/layout/PageHeader';
import LoadingState from '../components/common/LoadingState';
import ErrorMessage from '../components/common/ErrorMessage';
import EmptyState from '../components/common/EmptyState';
import { apiClient } from '../api/client';
import { formatDate } from '../utils/formatters';

export default function VendorsPage() {
  const [vendors, setVendors] = useState([]);
  const [search, setSearch] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchVendors = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await apiClient.getVendors({ limit: 100 });
      setVendors(data || []);
    } catch (err) {
      setError(err.message || 'Failed to fetch vendor directory');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchVendors();
  }, []);

  const filteredVendors = vendors.filter((v) => {
    if (!search.trim()) return true;
    const q = search.toLowerCase();
    return (
      v.name?.toLowerCase().includes(q) ||
      v.gstin?.toLowerCase().includes(q) ||
      v.address?.toLowerCase().includes(q)
    );
  });

  return (
    <div className="space-y-6 animate-fade-in">
      <PageHeader
        title="Vendor Directory"
        subtitle={`Directory of ${vendors.length} suppliers parsed and recorded from invoices.`}
      />

      {/* Search Input */}
      <div className="bg-white rounded-2xl p-4 border border-slate-200/80 shadow-xs max-w-md">
        <div className="relative">
          <Search className="w-4 h-4 text-slate-400 absolute left-3.5 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search vendor name, GSTIN, city..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9.5 pr-4 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
          />
        </div>
      </div>

      {loading ? (
        <LoadingState message="Loading registered vendors..." rows={4} />
      ) : error ? (
        <ErrorMessage
          title="Failed to Load Vendors"
          message={error}
          onRetry={fetchVendors}
        />
      ) : filteredVendors.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredVendors.map((vendor) => (
            <div
              key={vendor.id}
              className="bg-white rounded-2xl p-6 border border-slate-200/80 shadow-xs hover:shadow-md transition-shadow flex flex-col justify-between"
            >
              <div>
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center font-bold text-base shrink-0 border border-indigo-100">
                    <Building2 className="w-5 h-5" />
                  </div>
                  <div className="min-w-0">
                    <h3 className="text-sm font-bold text-slate-900 truncate">
                      {vendor.name}
                    </h3>
                    <p className="text-[11px] font-mono text-slate-400 truncate">
                      {vendor.gstin ? `GSTIN: ${vendor.gstin}` : 'No GSTIN recorded'}
                    </p>
                  </div>
                </div>

                <div className="space-y-2 text-xs text-slate-600 pt-3 border-t border-slate-100">
                  {vendor.address && (
                    <div className="flex items-start gap-2">
                      <MapPin className="w-3.5 h-3.5 text-slate-400 shrink-0 mt-0.5" />
                      <span className="line-clamp-2">{vendor.address}</span>
                    </div>
                  )}

                  {vendor.phone && (
                    <div className="flex items-center gap-2">
                      <Phone className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                      <span>{vendor.phone}</span>
                    </div>
                  )}

                  {vendor.email && (
                    <div className="flex items-center gap-2">
                      <Mail className="w-3.5 h-3.5 text-slate-400 shrink-0" />
                      <span className="truncate">{vendor.email}</span>
                    </div>
                  )}
                </div>
              </div>

              <div className="mt-6 pt-4 border-t border-slate-100 flex items-center justify-between text-xs text-slate-400">
                <span className="flex items-center gap-1">
                  <Calendar className="w-3 h-3" />
                  Added {formatDate(vendor.created_at)}
                </span>
                <Link
                  to={`/invoices?search=${encodeURIComponent(vendor.name)}`}
                  className="font-semibold text-indigo-600 hover:text-indigo-700 flex items-center gap-1"
                >
                  View Invoices <ArrowRight className="w-3.5 h-3.5" />
                </Link>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <EmptyState
          icon={Building2}
          title="No vendors found"
          description={
            search
              ? 'No vendors match your search keyword. Try a different query.'
              : 'Vendors will automatically be recorded here as invoices are uploaded and processed.'
          }
          actionLabel={search ? 'Clear Search' : 'Upload Invoice'}
          onAction={search ? () => setSearch('') : () => window.location.href = '/upload'}
        />
      )}
    </div>
  );
}
