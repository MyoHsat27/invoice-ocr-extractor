INVOICE_EXTRACTION_SYSTEM_PROMPT = """You extract invoice data for a human review workflow.
Return only JSON. Do not include markdown or explanations.
Use empty strings or null for unknown values.
Amounts must be numbers, not strings.
The JSON object must use these keys:
vendor_name, invoice_number, invoice_date, due_date, currency, subtotal, tax, total, line_items.
Each line item must use: description, quantity, unit_price, amount."""


def build_invoice_extraction_user_prompt(document_context: str) -> str:
    return f"""Extract structured invoice data from this document evidence.

The evidence may include raw OCR text, embedded PDF text, table rows, and extraction notes.
Prefer explicit values from tables when line items are present.

{document_context}"""

