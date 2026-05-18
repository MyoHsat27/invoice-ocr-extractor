from __future__ import annotations

from litestar import MediaType, Request, get, patch, post
from litestar.datastructures import UploadFile
from litestar.enums import RequestEncodingType
from litestar.exceptions import HTTPException, NotFoundException
from litestar.params import Body
from litestar.status_codes import HTTP_400_BAD_REQUEST, HTTP_413_REQUEST_ENTITY_TOO_LARGE, HTTP_502_BAD_GATEWAY

from invoice_agent.models import InvoiceDraft, InvoiceSummary, UpdateInvoiceRequest
from invoice_agent.repositories.invoice_repository import InvoiceNotFoundError
from invoice_agent.services.invoice_service import (
    InvoiceExtractionProviderError,
    InvoiceProcessingError,
    InvoiceService,
)


def _service(request: Request) -> InvoiceService:
    return request.app.state.invoice_service


async def _read_upload_content(request: Request, data: UploadFile) -> bytes:
    max_upload_bytes = request.app.state.settings.max_upload_bytes
    max_multipart_overhead_bytes = 64 * 1024
    content_length = request.headers.get("content-length")

    if content_length:
        try:
            request_size = int(content_length)
        except ValueError:
            request_size = 0

        if request_size > max_upload_bytes + max_multipart_overhead_bytes:
            raise HTTPException(
                status_code=HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Upload is too large. Maximum file size is {max_upload_bytes} bytes.",
            )

    chunks = bytearray()
    while True:
        chunk = await data.read(1024 * 1024)
        if not chunk:
            break

        chunks.extend(chunk)
        if len(chunks) > max_upload_bytes:
            raise HTTPException(
                status_code=HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"Upload is too large. Maximum file size is {max_upload_bytes} bytes.",
            )

    return bytes(chunks)


@get("/api/invoices")
async def list_invoices(request: Request) -> list[InvoiceSummary]:
    return _service(request).list_invoices()


@get("/api/invoices/{invoice_id:str}")
async def get_invoice(request: Request, invoice_id: str) -> InvoiceDraft:
    try:
        return _service(request).get_invoice(invoice_id)
    except InvoiceNotFoundError as exc:
        raise NotFoundException(detail="Invoice not found.") from exc


@post("/api/invoices/upload", media_type=MediaType.JSON)
async def upload_invoice(
    request: Request,
    data: UploadFile = Body(media_type=RequestEncodingType.MULTI_PART),
) -> InvoiceDraft:
    filename = data.filename or "invoice"
    content = await _read_upload_content(request, data)
    try:
        return await _service(request).upload_invoice(filename, content)
    except InvoiceProcessingError as exc:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except InvoiceExtractionProviderError as exc:
        raise HTTPException(status_code=HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc


@patch("/api/invoices/{invoice_id:str}", media_type=MediaType.JSON)
async def update_invoice(
    request: Request,
    invoice_id: str,
    data: UpdateInvoiceRequest,
) -> InvoiceDraft:
    try:
        return _service(request).update_invoice(invoice_id, data)
    except InvoiceNotFoundError as exc:
        raise NotFoundException(detail="Invoice not found.") from exc


@post("/api/invoices/{invoice_id:str}/reprocess", media_type=MediaType.JSON)
async def reprocess_invoice(request: Request, invoice_id: str) -> InvoiceDraft:
    try:
        return await _service(request).reprocess_invoice(invoice_id)
    except InvoiceNotFoundError as exc:
        raise NotFoundException(detail="Invoice not found.") from exc
    except InvoiceProcessingError as exc:
        raise HTTPException(status_code=HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except InvoiceExtractionProviderError as exc:
        raise HTTPException(status_code=HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc
