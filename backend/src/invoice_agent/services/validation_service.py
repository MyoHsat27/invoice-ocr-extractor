from __future__ import annotations

from invoice_agent.models import ExtractedInvoice


def build_validation_warnings(invoice: ExtractedInvoice) -> list[str]:
    warnings: list[str] = []

    if not invoice.vendor_name:
        warnings.append("Vendor name is missing.")
    if not invoice.invoice_number:
        warnings.append("Invoice number is missing.")
    if invoice.total is None:
        warnings.append("Total is missing.")

    if invoice.subtotal is not None and invoice.tax is not None and invoice.total is not None:
        expected_total = round(invoice.subtotal + invoice.tax, 2)
        actual_total = round(invoice.total, 2)
        if abs(expected_total - actual_total) > 0.01:
            warnings.append("Total does not match subtotal plus tax.")

    for index, item in enumerate(invoice.line_items, start=1):
        if item.quantity is not None and item.unit_price is not None and item.amount is not None:
            expected_amount = round(item.quantity * item.unit_price, 2)
            actual_amount = round(item.amount, 2)
            if abs(expected_amount - actual_amount) > 0.01:
                warnings.append(f"Line item {index} amount does not match quantity times unit price.")

    return warnings

