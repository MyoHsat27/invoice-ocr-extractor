from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class InvoiceStatus(str, Enum):
    draft = "draft"
    reviewed = "reviewed"


class InvoiceLineItem(BaseModel):
    description: str = ""
    quantity: Optional[float] = None
    unit_price: Optional[float] = None
    amount: Optional[float] = None

    @field_validator("description", mode="before")
    @classmethod
    def empty_string_for_null_text(cls, value: object) -> object:
        return "" if value is None else value


class ExtractedInvoice(BaseModel):
    vendor_name: str = ""
    invoice_number: str = ""
    invoice_date: str = ""
    due_date: str = ""
    currency: str = "USD"
    subtotal: Optional[float] = None
    tax: Optional[float] = None
    total: Optional[float] = None
    line_items: list[InvoiceLineItem] = Field(default_factory=list)

    @field_validator("vendor_name", "invoice_number", "invoice_date", "due_date", "currency", mode="before")
    @classmethod
    def empty_string_for_null_text(cls, value: object) -> object:
        return "" if value is None else value


class ProviderMetadata(BaseModel):
    provider: str = "openrouter"
    model: str = ""
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None


class InvoiceDraft(BaseModel):
    id: str
    filename: str
    raw_text: str
    extracted: ExtractedInvoice
    warnings: list[str] = Field(default_factory=list)
    status: InvoiceStatus = InvoiceStatus.draft
    provider: ProviderMetadata = Field(default_factory=ProviderMetadata)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class InvoiceSummary(BaseModel):
    id: str
    filename: str
    vendor_name: str = ""
    invoice_number: str = ""
    total: Optional[float] = None
    currency: str = "USD"
    status: InvoiceStatus = InvoiceStatus.draft
    updated_at: datetime


class UpdateInvoiceRequest(BaseModel):
    extracted: ExtractedInvoice
    status: InvoiceStatus = InvoiceStatus.reviewed
