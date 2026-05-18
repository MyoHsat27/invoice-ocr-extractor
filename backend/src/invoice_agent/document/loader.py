from __future__ import annotations

from pathlib import Path

from invoice_agent.document.errors import UnsupportedFileTypeError
from invoice_agent.document.image_extractor import extract_image_document
from invoice_agent.document.models import DocumentEvidence
from invoice_agent.document.pdf_extractor import extract_pdf_document
from invoice_agent.document.text_extractor import extract_text_document


IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}
TEXT_SUFFIXES = {".txt", ".text"}


def extract_document_evidence(filename: str, content: bytes) -> DocumentEvidence:
    suffix = Path(filename).suffix.lower()

    if suffix in TEXT_SUFFIXES:
        return extract_text_document(filename, content)
    if suffix == ".pdf":
        return extract_pdf_document(filename, content)
    if suffix in IMAGE_SUFFIXES:
        return extract_image_document(filename, content)

    raise UnsupportedFileTypeError(
        "Supported uploads are .txt, .pdf, .png, .jpg, .jpeg, .tif, .tiff, and .bmp files."
    )
