from __future__ import annotations

from invoice_agent.document.errors import TextExtractionError
from invoice_agent.document.models import DocumentEvidence, DocumentSourceType


def extract_text_document(filename: str, content: bytes) -> DocumentEvidence:
    try:
        raw_text = content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise TextExtractionError("Text upload must be UTF-8 encoded.") from exc

    return DocumentEvidence(
        filename=filename,
        source_type=DocumentSourceType.text,
        raw_text=raw_text,
    )

