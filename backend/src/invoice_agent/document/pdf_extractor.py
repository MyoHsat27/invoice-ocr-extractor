from __future__ import annotations

from io import BytesIO

from invoice_agent.document.errors import TextExtractionError
from invoice_agent.document.image_extractor import run_tesseract_ocr
from invoice_agent.document.models import DocumentEvidence, DocumentSourceType, ExtractedTable


def extract_pdf_document(filename: str, content: bytes) -> DocumentEvidence:
    embedded = extract_pdf_embedded_evidence(filename, content)
    if embedded.raw_text.strip() or embedded.tables:
        return embedded

    return extract_scanned_pdf_evidence(filename, content)


def extract_pdf_embedded_evidence(filename: str, content: bytes) -> DocumentEvidence:
    try:
        import pdfplumber
    except ModuleNotFoundError as exc:
        raise TextExtractionError(
            "PDF text/table extraction requires pdfplumber. Run `backend/.venv/bin/pip install -e backend`."
        ) from exc

    try:
        text_pages: list[str] = []
        tables: list[ExtractedTable] = []
        with pdfplumber.open(BytesIO(content)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                if page_text.strip():
                    text_pages.append(page_text.strip())

                for table in page.extract_tables():
                    rows = [
                        [cell.strip() if cell else "" for cell in row]
                        for row in table
                    ]
                    if rows:
                        tables.append(ExtractedTable(rows=rows))
    except Exception as exc:
        raise TextExtractionError("PDF text/table extraction failed.") from exc

    notes = ["PDF embedded text/table extraction was performed with pdfplumber."]
    if not text_pages and not tables:
        notes.append("No embedded PDF text or tables were detected; scanned OCR fallback is required.")

    return DocumentEvidence(
        filename=filename,
        source_type=DocumentSourceType.pdf,
        raw_text="\n\n".join(text_pages),
        tables=tables,
        extraction_notes=notes,
    )


def extract_scanned_pdf_evidence(filename: str, content: bytes) -> DocumentEvidence:
    try:
        import fitz
        from PIL import Image
    except ModuleNotFoundError as exc:
        raise TextExtractionError(
            "Scanned PDF OCR requires PyMuPDF, Pillow, and pytesseract. Run `backend/.venv/bin/pip install -e backend`."
        ) from exc

    try:
        document = fitz.open(stream=content, filetype="pdf")
        page_text: list[str] = []
        for page in document:
            pixmap = page.get_pixmap(matrix=fitz.Matrix(2, 2), alpha=False)
            image = Image.open(BytesIO(pixmap.tobytes("png")))
            text = run_tesseract_ocr(image)
            if text:
                page_text.append(text)
    except TextExtractionError:
        raise
    except Exception as exc:
        raise TextExtractionError("Scanned PDF OCR failed.") from exc

    raw_text = "\n\n".join(page_text)
    if not raw_text.strip():
        raise TextExtractionError("No text found in scanned PDF.")

    return DocumentEvidence(
        filename=filename,
        source_type=DocumentSourceType.scanned_pdf,
        raw_text=raw_text,
        extraction_notes=["PDF was rendered to images with PyMuPDF and OCR was performed with Tesseract."],
    )
