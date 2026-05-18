from __future__ import annotations

from io import BytesIO

from invoice_agent.document.errors import TextExtractionError
from invoice_agent.document.models import DocumentEvidence, DocumentSourceType


def extract_image_document(filename: str, content: bytes) -> DocumentEvidence:
    text = run_tesseract_ocr_from_bytes(content)
    return DocumentEvidence(
        filename=filename,
        source_type=DocumentSourceType.image,
        raw_text=text,
        extraction_notes=["Image OCR was performed with Tesseract."],
    )


def run_tesseract_ocr_from_bytes(content: bytes) -> str:
    try:
        from PIL import Image

        image = Image.open(BytesIO(content))
        return run_tesseract_ocr(image)
    except ModuleNotFoundError as exc:
        raise TextExtractionError(
            "Image OCR requires optional dependencies. Run `backend/.venv/bin/pip install -e backend`."
        ) from exc
    except TextExtractionError:
        raise
    except Exception as exc:
        if exc.__class__.__name__ == "TesseractNotFoundError":
            raise TextExtractionError(
                "Image OCR requires the Tesseract binary. Install it with `brew install tesseract`."
            ) from exc
        raise TextExtractionError("Image OCR failed.") from exc


def run_tesseract_ocr(image: object) -> str:
    try:
        import pytesseract

        text = pytesseract.image_to_string(image).strip()
    except ModuleNotFoundError as exc:
        raise TextExtractionError(
            "Tesseract OCR requires optional dependencies. Run `backend/.venv/bin/pip install -e backend`."
        ) from exc
    except Exception as exc:
        if exc.__class__.__name__ == "TesseractNotFoundError":
            raise TextExtractionError(
                "Image OCR requires the Tesseract binary. Install it with `brew install tesseract`."
            ) from exc
        raise

    if not text:
        raise TextExtractionError("No text found in image.")
    return text
