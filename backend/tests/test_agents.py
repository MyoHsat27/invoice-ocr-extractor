import json
import unittest

from invoice_agent.agents import build_validation_warnings, extract_invoice_from_model_payload, parse_model_json
from invoice_agent.models import ExtractedInvoice, InvoiceLineItem


class AgentParsingTests(unittest.TestCase):
    def test_parse_model_json_accepts_clean_json_object(self) -> None:
        payload = {
            "vendor_name": "Acme Supplies",
            "invoice_number": "INV-1001",
            "invoice_date": "2026-05-01",
            "due_date": "2026-05-31",
            "currency": "USD",
            "subtotal": 100.0,
            "tax": 7.0,
            "total": 107.0,
            "line_items": [
                {
                    "description": "Paper",
                    "quantity": 2,
                    "unit_price": 50.0,
                    "amount": 100.0,
                }
            ],
        }

        result = parse_model_json(json.dumps(payload))

        self.assertEqual(result["vendor_name"], "Acme Supplies")
        self.assertEqual(result["line_items"][0]["amount"], 100.0)

    def test_parse_model_json_extracts_json_from_wrapped_text(self) -> None:
        result = parse_model_json('Here is the result:\n{"vendor_name":"Acme","total":42}\nDone.')

        self.assertEqual(result["vendor_name"], "Acme")
        self.assertEqual(result["total"], 42)

    def test_parse_model_json_repairs_common_model_json_errors(self) -> None:
        result = parse_model_json(
            """
            ```json
            {
              "vendor_name": "Acme Supplies",
              "invoice_number": "INV-1001",
              "total": 107.00,
              "line_items": [
                {"description": "Paper", "quantity": 2, "unit_price": 50, "amount": 100,},
              ],
            }
            ```
            """
        )

        self.assertEqual(result["vendor_name"], "Acme Supplies")
        self.assertEqual(result["line_items"][0]["amount"], 100)

    def test_validation_warns_when_total_does_not_match_subtotal_and_tax(self) -> None:
        invoice = ExtractedInvoice(
            vendor_name="Acme Supplies",
            invoice_number="INV-1001",
            invoice_date="2026-05-01",
            due_date="2026-05-31",
            currency="USD",
            subtotal=100.0,
            tax=10.0,
            total=120.0,
            line_items=[
                InvoiceLineItem(
                    description="Paper",
                    quantity=2,
                    unit_price=50.0,
                    amount=100.0,
                )
            ],
        )

        warnings = build_validation_warnings(invoice)

        self.assertIn("Total does not match subtotal plus tax.", warnings)

    def test_extract_invoice_from_model_payload_returns_invoice_and_metadata(self) -> None:
        payload = {
            "choices": [
                {
                    "message": {
                        "content": json.dumps(
                            {
                                "vendor_name": "Acme Supplies",
                                "invoice_number": "INV-1001",
                                "currency": "USD",
                                "total": 107.0,
                                "line_items": [],
                            }
                        )
                    }
                }
            ],
            "model": "deepseek/deepseek-v4-flash",
            "usage": {
                "prompt_tokens": 100,
                "completion_tokens": 50,
                "total_tokens": 150,
            },
        }

        invoice, warnings, metadata = extract_invoice_from_model_payload(payload)

        self.assertEqual(invoice.vendor_name, "Acme Supplies")
        self.assertEqual(metadata.model, "deepseek/deepseek-v4-flash")
        self.assertEqual(metadata.total_tokens, 150)
        self.assertEqual(warnings, [])


if __name__ == "__main__":
    unittest.main()
