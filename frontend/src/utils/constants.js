export const PROCESSING_STATUSES = {
  extracted: { label: 'Extracted', bg: 'bg-blue-50', text: 'text-blue-700', border: 'border-blue-200' },
  confirmed: { label: 'Confirmed', bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200' },
  failed: { label: 'Failed', bg: 'bg-rose-50', text: 'text-rose-700', border: 'border-rose-200' },
};

export const REVIEW_STATUSES = {
  auto_verified: { label: 'Auto Verified', bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200' },
  needs_review: { label: 'Needs Review', bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200' },
  manually_confirmed: { label: 'Manually Confirmed', bg: 'bg-indigo-50', text: 'text-indigo-700', border: 'border-indigo-200' },
};

export const PAYMENT_STATUSES = {
  paid: { label: 'Paid', bg: 'bg-emerald-50', text: 'text-emerald-700', border: 'border-emerald-200' },
  unpaid: { label: 'Unpaid', bg: 'bg-rose-50', text: 'text-rose-700', border: 'border-rose-200' },
  partially_paid: { label: 'Partial', bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200' },
};
