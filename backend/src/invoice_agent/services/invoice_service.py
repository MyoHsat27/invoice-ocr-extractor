from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from invoice_agent.agents import (
    ModelOutputError,
    ProviderConfigurationError,
    ProviderRequestError,
    extract_invoice_with_openrouter,
)
from invoice_agent.document.errors import TextExtractionError, UnsupportedFileTypeError
from invoice_agent.document.loader import extract_document_evidence
from invoice_agent.models import InvoiceDraft, InvoiceStatus, InvoiceSummary, UpdateInvoiceRequest
from invoice_agent.repositories.invoice_repository import InvoiceNotFoundError, InvoiceRepository
from invoice_agent.settings import Settings
from invoice_agent.services.validation_service import build_validation_warnings


class InvoiceProcessingError(ValueError):
    pass


class InvoiceExtractionProviderError(RuntimeError):
    pass


class InvoiceService:
    def __init__(self, repository: InvoiceRepository, settings: Settings) -> None:
        self.repository = repository
        self.settings = settings

    def list_invoices(self) -> list[InvoiceSummary]:
        return self.repository.list_summaries()

    def get_invoice(self, invoice_id: str) -> InvoiceDraft:
        return self.repository.get(invoice_id)

    async def upload_invoice(self, filename: str, content: bytes) -> InvoiceDraft:
        try:
            evidence = extract_document_evidence(filename, content)
        except (TextExtractionError, UnsupportedFileTypeError) as exc:
            raise InvoiceProcessingError(str(exc)) from exc

        draft = await self._create_draft_from_evidence(
            filename=filename,
            raw_text=evidence.to_prompt_context(),
        )
        return self.repository.save(draft)

    def update_invoice(self, invoice_id: str, data: UpdateInvoiceRequest) -> InvoiceDraft:
        draft = self.repository.get(invoice_id)
        draft.extracted = data.extracted
        draft.status = data.status
        draft.updated_at = datetime.utcnow()
        draft.warnings = build_validation_warnings(data.extracted)
        return self.repository.save(draft)

    async def reprocess_invoice(self, invoice_id: str) -> InvoiceDraft:
        existing = self.repository.get(invoice_id)
        draft = await self._create_draft_from_evidence(
            filename=existing.filename,
            raw_text=existing.raw_text,
            invoice_id=existing.id,
        )
        draft.created_at = existing.created_at
        draft.status = InvoiceStatus.draft
        return self.repository.save(draft)

    async def _create_draft_from_evidence(
        self,
        filename: str,
        raw_text: str,
        invoice_id: str | None = None,
    ) -> InvoiceDraft:
        if not raw_text.strip():
            raise InvoiceProcessingError("Invoice text is empty.")

        try:
            extracted, warnings, metadata = await extract_invoice_with_openrouter(
                raw_text=raw_text,
                settings=self.settings,
            )
        except ProviderConfigurationError as exc:
            raise InvoiceProcessingError(str(exc)) from exc
        except ProviderRequestError as exc:
            raise InvoiceExtractionProviderError(str(exc)) from exc
        except (ModelOutputError, ValueError) as exc:
            raise InvoiceExtractionProviderError(
                f"Model response could not be converted into invoice JSON: {exc}"
            ) from exc

        return InvoiceDraft(
            id=invoice_id or str(uuid4()),
            filename=filename,
            raw_text=raw_text,
            extracted=extracted,
            warnings=warnings,
            provider=metadata,
        )
