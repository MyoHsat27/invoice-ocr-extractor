import type { InvoiceDraft, InvoiceSummary } from '$lib/types/invoice';
import { PUBLIC_API_BASE_URL } from '$env/static/public';

const apiBase = PUBLIC_API_BASE_URL || 'http://localhost:8000';

async function requestJson<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${apiBase}${path}`, init);
  const text = await response.text();
  const payload = text ? JSON.parse(text) : null;

  if (!response.ok) {
    throw new Error(payload?.detail || `Request failed with ${response.status}`);
  }

  return payload as T;
}

export function listInvoices(): Promise<InvoiceSummary[]> {
  return requestJson<InvoiceSummary[]>('/api/invoices');
}

export function getInvoice(id: string): Promise<InvoiceDraft> {
  return requestJson<InvoiceDraft>(`/api/invoices/${id}`);
}

export function uploadInvoice(file: File): Promise<InvoiceDraft> {
  const form = new FormData();
  form.append('data', file);
  return requestJson<InvoiceDraft>('/api/invoices/upload', {
    method: 'POST',
    body: form
  });
}

export function saveInvoice(draft: InvoiceDraft): Promise<InvoiceDraft> {
  return requestJson<InvoiceDraft>(`/api/invoices/${draft.id}`, {
    method: 'PATCH',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      extracted: draft.extracted,
      status: 'reviewed'
    })
  });
}

export function reprocessInvoice(id: string): Promise<InvoiceDraft> {
  return requestJson<InvoiceDraft>(`/api/invoices/${id}/reprocess`, {
    method: 'POST'
  });
}
