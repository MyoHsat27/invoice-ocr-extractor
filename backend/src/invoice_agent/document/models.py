from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


class DocumentSourceType(str, Enum):
    text = "text"
    pdf = "pdf"
    scanned_pdf = "scanned_pdf"
    image = "image"


class ExtractedTable(BaseModel):
    rows: list[list[str]] = Field(default_factory=list)


class DocumentEvidence(BaseModel):
    filename: str
    source_type: DocumentSourceType
    raw_text: str
    tables: list[ExtractedTable] = Field(default_factory=list)
    extraction_notes: list[str] = Field(default_factory=list)

    def to_prompt_context(self) -> str:
        table_sections = []
        for index, table in enumerate(self.tables, start=1):
            rendered_rows = [" | ".join(cell for cell in row) for row in table.rows if row]
            if rendered_rows:
                table_sections.append(f"Table {index}:\n" + "\n".join(rendered_rows))

        sections = [
            f"FILENAME: {self.filename}",
            f"SOURCE TYPE: {self.source_type.value}",
            "RAW TEXT:",
            self.raw_text,
        ]
        if table_sections:
            sections.extend(["TABLES:", "\n\n".join(table_sections)])
        if self.extraction_notes:
            sections.extend(["EXTRACTION NOTES:", "\n".join(f"- {note}" for note in self.extraction_notes)])
        return "\n\n".join(sections)

