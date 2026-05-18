from __future__ import annotations

from litestar import Litestar
from litestar.config.cors import CORSConfig

from invoice_agent.repositories.invoice_repository import InvoiceRepository
from invoice_agent.routes.health import health
from invoice_agent.routes.invoices import (
    get_invoice,
    list_invoices,
    reprocess_invoice,
    update_invoice,
    upload_invoice,
)
from invoice_agent.services.invoice_service import InvoiceService
from invoice_agent.settings import Settings


def create_app(settings: Settings | None = None) -> Litestar:
    resolved_settings = settings or Settings()
    repository = InvoiceRepository(resolved_settings.data_path)
    invoice_service = InvoiceService(repository=repository, settings=resolved_settings)
    cors_config = CORSConfig(allow_origins=resolved_settings.allowed_origins)

    app = Litestar(
        route_handlers=[
            health,
            list_invoices,
            get_invoice,
            upload_invoice,
            update_invoice,
            reprocess_invoice,
        ],
        cors_config=cors_config,
    )
    app.state.settings = resolved_settings
    app.state.invoice_repository = repository
    app.state.invoice_service = invoice_service
    return app


app = create_app()
