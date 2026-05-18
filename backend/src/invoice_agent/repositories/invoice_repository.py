from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from pathlib import Path

from invoice_agent.models import InvoiceDraft, InvoiceSummary


class InvoiceNotFoundError(KeyError):
    pass


class InvoiceRepository:
    def __init__(self, path: Path) -> None:
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def save(self, draft: InvoiceDraft) -> InvoiceDraft:
        draft.updated_at = datetime.utcnow()
        payload = json.dumps(draft.model_dump(mode="json"))

        with self._connect() as connection:
            connection.execute(
                """
                insert into invoices (id, payload, updated_at)
                values (?, ?, ?)
                on conflict(id) do update set
                    payload = excluded.payload,
                    updated_at = excluded.updated_at
                """,
                (draft.id, payload, draft.updated_at.isoformat()),
            )

        return draft

    def get(self, invoice_id: str) -> InvoiceDraft:
        with self._connect() as connection:
            row = connection.execute(
                "select payload from invoices where id = ?",
                (invoice_id,),
            ).fetchone()

        if row is None:
            raise InvoiceNotFoundError(invoice_id)

        return InvoiceDraft.model_validate(json.loads(row["payload"]))

    def list_summaries(self) -> list[InvoiceSummary]:
        with self._connect() as connection:
            rows = connection.execute(
                "select payload from invoices order by updated_at desc"
            ).fetchall()

        drafts = [InvoiceDraft.model_validate(json.loads(row["payload"])) for row in rows]
        return [
            InvoiceSummary(
                id=draft.id,
                filename=draft.filename,
                vendor_name=draft.extracted.vendor_name,
                invoice_number=draft.extracted.invoice_number,
                total=draft.extracted.total,
                currency=draft.extracted.currency,
                status=draft.status,
                updated_at=draft.updated_at,
            )
            for draft in drafts
        ]

    def _ensure_schema(self) -> None:
        with self._connect() as connection:
            connection.execute(
                """
                create table if not exists invoices (
                    id text primary key,
                    payload text not null,
                    updated_at text not null
                )
                """
            )
            connection.execute(
                "create index if not exists idx_invoices_updated_at on invoices(updated_at desc)"
            )

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

