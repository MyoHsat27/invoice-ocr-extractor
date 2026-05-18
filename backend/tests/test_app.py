import tempfile
import unittest
from pathlib import Path

from litestar.status_codes import HTTP_200_OK, HTTP_413_REQUEST_ENTITY_TOO_LARGE
from litestar.testing import TestClient

from invoice_agent.app import create_app
from invoice_agent.settings import Settings


class AppRouteTests(unittest.TestCase):
    def test_health_route_returns_ok(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            settings = Settings()
            settings.data_path = Path(temp_dir) / "invoices.db"
            app = create_app(settings=settings)

            with TestClient(app=app) as client:
                response = client.get("/health")

            self.assertEqual(response.status_code, HTTP_200_OK)
            self.assertEqual(response.json()["status"], "ok")

    def test_invoice_list_starts_empty(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            settings = Settings()
            settings.data_path = Path(temp_dir) / "invoices.db"
            app = create_app(settings=settings)

            with TestClient(app=app) as client:
                response = client.get("/api/invoices")

            self.assertEqual(response.status_code, HTTP_200_OK)
            self.assertEqual(response.json(), [])

    def test_upload_rejects_oversized_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            settings = Settings()
            settings.data_path = Path(temp_dir) / "invoices.db"
            settings.max_upload_bytes = 8
            app = create_app(settings=settings)

            with TestClient(app=app) as client:
                response = client.post(
                    "/api/invoices/upload",
                    files={"data": ("invoice.txt", b"this is too large", "text/plain")},
                )

            self.assertEqual(response.status_code, HTTP_413_REQUEST_ENTITY_TOO_LARGE)


if __name__ == "__main__":
    unittest.main()
