import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from invoice_agent.settings import Settings


class SettingsTests(unittest.TestCase):
    def test_settings_loads_openrouter_key_from_dotenv_file(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            dotenv_path = Path(temp_dir) / ".env"
            dotenv_path.write_text("OPENROUTER_API_KEY=test-key-from-file\n", encoding="utf-8")

            with patch.dict(os.environ, {}, clear=True):
                settings = Settings(dotenv_path=dotenv_path)

        self.assertEqual(settings.openrouter_api_key, "test-key-from-file")

    def test_settings_parses_frontend_origins_and_upload_limit(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            dotenv_path = Path(temp_dir) / ".env"
            dotenv_path.write_text(
                "\n".join(
                    [
                        "FRONTEND_ORIGINS=http://localhost:5173, http://127.0.0.1:5173",
                        "MAX_UPLOAD_BYTES=2048",
                        "OPENROUTER_REFERER=https://demo.example.com",
                    ]
                ),
                encoding="utf-8",
            )

            with patch.dict(os.environ, {}, clear=True):
                settings = Settings(dotenv_path=dotenv_path)

        self.assertEqual(settings.allowed_origins, ["http://localhost:5173", "http://127.0.0.1:5173"])
        self.assertEqual(settings.max_upload_bytes, 2048)
        self.assertEqual(settings.openrouter_referer, "https://demo.example.com")


if __name__ == "__main__":
    unittest.main()
