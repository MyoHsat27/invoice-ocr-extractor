from __future__ import annotations

from invoice_agent.llm.invoice_extractor import (
    ModelOutputError,
    extract_invoice_from_model_payload,
    parse_model_json,
)
from invoice_agent.llm.openrouter_client import OpenRouterClient, ProviderConfigurationError, ProviderRequestError
from invoice_agent.services.validation_service import build_validation_warnings
from invoice_agent.settings import Settings


async def extract_invoice_with_openrouter(raw_text: str, settings: Settings):
    extractor = InvoiceLlmExtractor(OpenRouterClient(settings))
    return await extractor.extract(raw_text)


from invoice_agent.llm.invoice_extractor import InvoiceLlmExtractor  # noqa: E402

__all__ = [
    "ModelOutputError",
    "ProviderConfigurationError",
    "ProviderRequestError",
    "build_validation_warnings",
    "extract_invoice_from_model_payload",
    "extract_invoice_with_openrouter",
    "parse_model_json",
]
