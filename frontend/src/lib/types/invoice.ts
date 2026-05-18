export type InvoiceStatus = 'draft' | 'reviewed';

export type InvoiceLineItem = {
  description: string;
  quantity: number | null;
  unit_price: number | null;
  amount: number | null;
};

export type ExtractedInvoice = {
  vendor_name: string;
  invoice_number: string;
  invoice_date: string;
  due_date: string;
  currency: string;
  subtotal: number | null;
  tax: number | null;
  total: number | null;
  line_items: InvoiceLineItem[];
};

export type ProviderMetadata = {
  provider: string;
  model: string;
  prompt_tokens: number | null;
  completion_tokens: number | null;
  total_tokens: number | null;
};

export type InvoiceDraft = {
  id: string;
  filename: string;
  raw_text: string;
  extracted: ExtractedInvoice;
  warnings: string[];
  status: InvoiceStatus;
  provider: ProviderMetadata;
  updated_at: string;
};

export type InvoiceSummary = {
  id: string;
  filename: string;
  vendor_name: string;
  invoice_number: string;
  total: number | null;
  currency: string;
  status: InvoiceStatus;
  updated_at: string;
};

