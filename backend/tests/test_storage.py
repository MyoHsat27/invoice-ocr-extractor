import sqlite3
import tempfile
import unittest
from pathlib import Path

from invoice_agent.models import ExtractedInvoice, InvoiceDraft, InvoiceStatus
from invoice_agent.repositories.invoice_repository import InvoiceRepository


class InvoiceRepositoryTests(unittest.TestCase):
    def test_save_and_get_invoice_round_trip(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            db_path = Path(temp_dir) / "invoices.db"
            repository = InvoiceRepository(db_path)
            draft = InvoiceDraft(
                id="invoice-1",
                filename="sample.txt",
                raw_text="Invoice total 107.00",
                extracted=ExtractedInvoice(vendor_name="Acme", total=107.0),
            )

            repository.save(draft)
            loaded = repository.get("invoice-1")

            self.assertEqual(loaded.filename, "sample.txt")
            self.assertEqual(loaded.extracted.vendor_name, "Acme")

            with sqlite3.connect(db_path) as connection:
                count = connection.execute("select count(*) from invoices").fetchone()[0]

            self.assertEqual(count, 1)

    def test_list_summaries_returns_latest_updated_first(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            repository = InvoiceRepository(Path(temp_dir) / "invoices.db")
            first = InvoiceDraft(
                id="invoice-1",
                filename="first.txt",
                raw_text="First",
                extracted=ExtractedInvoice(vendor_name="First Vendor"),
            )
            second = InvoiceDraft(
                id="invoice-2",
                filename="second.txt",
                raw_text="Second",
                extracted=ExtractedInvoice(vendor_name="Second Vendor"),
                status=InvoiceStatus.reviewed,
            )

            repository.save(first)
            repository.save(second)
            summaries = repository.list_summaries()

            self.assertEqual([summary.id for summary in summaries], ["invoice-2", "invoice-1"])
            self.assertEqual(summaries[0].status, InvoiceStatus.reviewed)

    def test_update_review_keeps_validation_warnings_accurate(self) -> None:
        from invoice_agent.services.invoice_service import InvoiceService
        from invoice_agent.models import UpdateInvoiceRequest
        from invoice_agent.settings import Settings

        with tempfile.TemporaryDirectory() as temp_dir:
            repository = InvoiceRepository(Path(temp_dir) / "invoices.db")
            service = InvoiceService(repository=repository, settings=Settings())
            draft = InvoiceDraft(
                id="invoice-1",
                filename="sample.txt",
                raw_text="Invoice total 120.00",
                extracted=ExtractedInvoice(vendor_name="Acme", total=120.0),
            )
            repository.save(draft)

            updated = service.update_invoice(
                "invoice-1",
                UpdateInvoiceRequest(
                    extracted=ExtractedInvoice(
                        vendor_name="Acme",
                        invoice_number="INV-1001",
                        subtotal=100.0,
                        tax=10.0,
                        total=120.0,
                    )
                ),
            )

            self.assertIn("Total does not match subtotal plus tax.", updated.warnings)


if __name__ == "__main__":
    unittest.main()
