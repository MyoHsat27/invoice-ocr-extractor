import unittest
from io import BytesIO
from unittest.mock import patch

from invoice_agent.document.errors import TextExtractionError, UnsupportedFileTypeError
from invoice_agent.document.loader import extract_document_evidence

try:
    from PIL import Image
except ModuleNotFoundError:
    Image = None


class OcrTests(unittest.TestCase):
    def test_extract_text_from_txt_upload(self) -> None:
        result = extract_document_evidence("invoice.txt", b"Vendor: Acme\nTotal: 107.00").raw_text

        self.assertEqual(result, "Vendor: Acme\nTotal: 107.00")

    def test_extract_text_from_text_based_pdf_upload(self) -> None:
        result = extract_document_evidence("invoice.pdf", _minimal_text_pdf()).raw_text

        self.assertIn("Invoice INV-1001", result)

    def test_extract_text_from_pdf_uses_tesseract_when_embedded_text_is_empty(self) -> None:
        with patch("invoice_agent.document.pdf_extractor.extract_pdf_embedded_evidence") as embedded:
            embedded.return_value.raw_text = ""
            embedded.return_value.tables = []
            with patch("invoice_agent.document.pdf_extractor.extract_scanned_pdf_evidence") as scanned:
                scanned.return_value.raw_text = "Scanned invoice total 88"
                result = extract_document_evidence("scan.pdf", b"%PDF-1.4 fake scanned pdf").raw_text

        self.assertEqual(result, "Scanned invoice total 88")

    def test_extract_text_from_image_upload_uses_tesseract(self) -> None:
        if Image is None:
            self.skipTest("Pillow is not installed.")

        with patch("invoice_agent.document.image_extractor.run_tesseract_ocr", return_value="Image invoice total 42"):
            result = extract_document_evidence("invoice.png", _minimal_png()).raw_text

        self.assertEqual(result, "Image invoice total 42")

    def test_image_upload_preserves_tesseract_install_error(self) -> None:
        if Image is None:
            self.skipTest("Pillow is not installed.")

        with patch(
            "invoice_agent.document.image_extractor.run_tesseract_ocr",
            side_effect=TextExtractionError("Image OCR requires the Tesseract binary."),
        ):
            with self.assertRaisesRegex(TextExtractionError, "Tesseract binary"):
                extract_document_evidence("invoice.png", _minimal_png())

    def test_extract_text_rejects_unsupported_file_type(self) -> None:
        with self.assertRaises(UnsupportedFileTypeError):
            extract_document_evidence("invoice.xlsx", b"not supported")


def _minimal_text_pdf() -> bytes:
    stream = b"BT\n/F1 24 Tf\n72 720 Td\n(Invoice INV-1001 Total 107.00) Tj\nET"
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    chunks = [b"%PDF-1.4\n"]
    offsets = [0]
    for index, body in enumerate(objects, start=1):
        offsets.append(sum(len(chunk) for chunk in chunks))
        chunks.append(f"{index} 0 obj\n".encode("ascii") + body + b"\nendobj\n")

    xref_offset = sum(len(chunk) for chunk in chunks)
    xref = [b"xref\n0 6\n", b"0000000000 65535 f \n"]
    xref.extend(f"{offset:010d} 00000 n \n".encode("ascii") for offset in offsets[1:])
    chunks.extend(
        [
            *xref,
            b"trailer\n<< /Root 1 0 R /Size 6 >>\n",
            f"startxref\n{xref_offset}\n%%EOF\n".encode("ascii"),
        ]
    )
    return b"".join(chunks)


def _minimal_png() -> bytes:
    if Image is None:
        raise RuntimeError("Pillow is not installed.")

    buffer = BytesIO()
    Image.new("RGB", (8, 8), "white").save(buffer, format="PNG")
    return buffer.getvalue()


if __name__ == "__main__":
    unittest.main()
