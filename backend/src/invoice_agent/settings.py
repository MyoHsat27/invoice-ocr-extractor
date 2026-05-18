from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv


class Settings:
    def __init__(self, dotenv_path: Path | None = None) -> None:
        self.backend_root = self._find_backend_root()
        load_dotenv(dotenv_path or self.backend_root / ".env")
        self.openrouter_api_key = os.getenv("OPENROUTER_API_KEY", "")
        self.openrouter_model = os.getenv("OPENROUTER_MODEL", "deepseek/deepseek-v4-flash")
        self.openrouter_base_url = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
        self.openrouter_referer = os.getenv("OPENROUTER_REFERER", "http://localhost:5173")
        self.data_path = self._resolve_backend_path(os.getenv("INVOICE_DATA_PATH", "data/invoices.db"))
        self.allowed_origins = self._parse_csv_env(
            "FRONTEND_ORIGINS",
            os.getenv("FRONTEND_ORIGIN", "http://localhost:5173"),
        )
        self.max_upload_bytes = self._parse_positive_int_env("MAX_UPLOAD_BYTES", 10 * 1024 * 1024)

    @property
    def openrouter_chat_url(self) -> str:
        return f"{self.openrouter_base_url.rstrip('/')}/chat/completions"

    def _resolve_backend_path(self, path_value: str) -> Path:
        path = Path(path_value)
        if path.is_absolute():
            return path
        return self.backend_root / path

    def _parse_csv_env(self, name: str, default_value: str) -> list[str]:
        value = os.getenv(name, default_value)
        values = [item.strip() for item in value.split(",") if item.strip()]
        return values or [default_value]

    def _parse_positive_int_env(self, name: str, default_value: int) -> int:
        value = os.getenv(name)
        if value is None:
            return default_value

        try:
            parsed = int(value)
        except ValueError:
            return default_value

        return parsed if parsed > 0 else default_value

    def _find_backend_root(self) -> Path:
        configured_root = os.getenv("BACKEND_ROOT")
        if configured_root:
            return Path(configured_root)

        source_root = Path(__file__).resolve().parents[2]
        if source_root.name == "backend" and (source_root / "pyproject.toml").exists():
            return source_root

        cwd = Path.cwd()
        if cwd.name == "backend" and (cwd / "pyproject.toml").exists():
            return cwd

        cwd_backend = cwd / "backend"
        if (cwd_backend / "pyproject.toml").exists():
            return cwd_backend

        return cwd
