import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/layout/Layout';
import DashboardPage from './pages/DashboardPage';
import InvoicesPage from './pages/InvoicesPage';
import InvoiceDetailPage from './pages/InvoiceDetailPage';
import UploadPage from './pages/UploadPage';
import AnalyticsPage from './pages/AnalyticsPage';
import VendorsPage from './pages/VendorsPage';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<DashboardPage />} />
          <Route path="invoices" element={<InvoicesPage />} />
          <Route path="invoices/:id" element={<InvoiceDetailPage />} />
          <Route path="upload" element={<UploadPage />} />
          <Route path="analytics" element={<AnalyticsPage />} />
          <Route path="vendors" element={<VendorsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
