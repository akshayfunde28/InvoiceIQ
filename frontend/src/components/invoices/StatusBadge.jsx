import React from 'react';
import { PROCESSING_STATUSES, REVIEW_STATUSES, PAYMENT_STATUSES } from '../../utils/constants';

export default function StatusBadge({ type = 'review', status }) {
  let config = { label: status, bg: 'bg-slate-100', text: 'text-slate-700', border: 'border-slate-200' };

  if (type === 'review' && REVIEW_STATUSES[status]) {
    config = REVIEW_STATUSES[status];
  } else if (type === 'processing' && PROCESSING_STATUSES[status]) {
    config = PROCESSING_STATUSES[status];
  } else if (type === 'payment' && PAYMENT_STATUSES[status]) {
    config = PAYMENT_STATUSES[status];
  }

  return (
    <span
      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${config.bg} ${config.text} ${config.border}`}
    >
      {config.label}
    </span>
  );
}
