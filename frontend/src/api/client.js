import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '/api',
  timeout: 120000, // 2 minutes for large PDF processing
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    let message = 'An unexpected error occurred. Please try again.';
    if (error.response?.data?.detail) {
      if (typeof error.response.data.detail === 'string') {
        message = error.response.data.detail;
      } else if (Array.isArray(error.response.data.detail)) {
        message = error.response.data.detail.map((d) => d.msg || JSON.stringify(d)).join(', ');
      }
    } else if (error.message) {
      message = error.message;
    }
    return Promise.reject(new Error(message));
  }
);

export const apiClient = {
  // Dashboard APIs
  getDashboardSummary: () => api.get('/dashboard/summary').then((r) => r.data),
  getMonthlyExpenses: (limit = 12) => api.get(`/dashboard/monthly-expenses?limit=${limit}`).then((r) => r.data),
  getGSTBreakdown: () => api.get('/dashboard/gst-breakdown').then((r) => r.data),
  getVendorExpenses: (limit = 5) => api.get(`/dashboard/vendor-expenses?limit=${limit}`).then((r) => r.data),

  // Invoice APIs
  getInvoices: (params = {}) => api.get('/invoices', { params }).then((r) => r.data),
  getInvoice: (id) => api.get(`/invoices/${id}`).then((r) => r.data),
  uploadInvoice: (file, onProgress) => {
    const formData = new FormData();
    formData.append('file', file);
    return api.post('/invoices/upload', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      onUploadProgress: (progressEvent) => {
        if (onProgress && progressEvent.total) {
          const percentCompleted = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(percentCompleted);
        }
      },
    }).then((r) => r.data);
  },
  updateInvoice: (id, data) => api.put(`/invoices/${id}`, data).then((r) => r.data),
  deleteInvoice: (id) => api.delete(`/invoices/${id}`).then((r) => r.data),
  reprocessInvoice: (id) => api.post(`/invoices/${id}/reprocess`).then((r) => r.data),
  getInvoiceFileUrl: (id) => `/api/invoices/${id}/file`,
  exportCsvUrl: (params = {}) => {
    const clean = {};
    Object.entries(params).forEach(([k, v]) => {
      if (k === 'page' || k === 'limit') return;
      if (v !== '' && v !== null && v !== undefined) clean[k] = v;
    });
    const query = new URLSearchParams(clean).toString();
    return `/api/invoices/export/csv${query ? '?' + query : ''}`;
  },
  exportPdfUrl: (params = {}) => {
    const clean = {};
    Object.entries(params).forEach(([k, v]) => {
      if (k === 'page' || k === 'limit') return;
      if (v !== '' && v !== null && v !== undefined) clean[k] = v;
    });
    const query = new URLSearchParams(clean).toString();
    return `/api/invoices/export/pdf${query ? '?' + query : ''}`;
  },

  // Vendors
  getVendors: (params = {}) => api.get('/vendors', { params }).then((r) => r.data),
  getVendor: (id) => api.get(`/vendors/${id}`).then((r) => r.data),

  // Health
  checkHealth: () => api.get('/health').then((r) => r.data),

  // AI Assistant
  askAssistant: (question) => api.post('/assistant/chat', { question }).then((r) => r.data),
};

export default api;
