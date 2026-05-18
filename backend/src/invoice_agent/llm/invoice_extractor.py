from __future__ import annotations

import json
from json import JSONDecodeError
from typing import Any

from invoice_agent.llm.openrouter_client import OpenRouterClient
from invoice_agent.llm.prompts import INVOICE_EXTRACTION_SYSTEM_PROMPT, build_invoice_extraction_user_prompt
from invoice_agent.models import ExtractedInvoice, ProviderMetadata
from invoice_agent.services.validation_service import build_validation_warnings


class ModelOutputError(ValueError):
    """Raised when a model response cannot be converted into an invoice object."""


class InvoiceLlmExtractor:
    def __init__(self, client: OpenRouterClient) -> None:
        self.client = client

    async def extract(
        self,
        document_context: str,
    ) -> tuple[ExtractedInvoice, list[str], ProviderMetadata]:
        payload = await self.client.chat_json(
            system_prompt=INVOICE_EXTRACTION_SYSTEM_PROMPT,
            user_prompt=build_invoice_extraction_user_prompt(document_context),
        )
        return extract_invoice_from_model_payload(payload)


def extract_invoice_from_model_payload(
    payload: dict[str, Any],
) -> tuple[ExtractedInvoice, list[str], ProviderMetadata]:
    try:
        content = payload["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError) as exc:
        raise ModelOutputError("Provider response did not include assistant content.") from exc

    invoice = ExtractedInvoice.model_validate(parse_model_json(content))
    warnings = build_validation_warnings(invoice)
    usage = payload.get("usage") or {}
    metadata = ProviderMetadata(
        model=str(payload.get("model") or ""),
        prompt_tokens=usage.get("prompt_tokens"),
        completion_tokens=usage.get("completion_tokens"),
        total_tokens=usage.get("total_tokens"),
    )
    return invoice, warnings, metadata


def parse_model_json(content: str) -> dict[str, Any]:
    stripped = content.strip()
    candidate = _strip_markdown_fence(stripped)

    parsed = _try_parse_json(candidate)
    if parsed is None:
        object_candidate = _extract_first_json_object_text(candidate)
        parsed = _try_parse_json(object_candidate)
    if parsed is None:
        parsed = _repair_json(candidate)

    if not isinstance(parsed, dict):
        raise ModelOutputError("Model response was valid JSON but not an object.")
    return parsed


def _try_parse_json(content: str) -> Any | None:
    try:
        return json.loads(content)
    except JSONDecodeError:
        return None


def _repair_json(content: str) -> Any:
    try:
        from json_repair import loads

        return loads(content)
    except Exception as exc:
        raise ModelOutputError(f"Model response was not valid repairable JSON: {exc}") from exc


def _strip_markdown_fence(content: str) -> str:
    if not content.startswith("```"):
        return content

    lines = content.splitlines()
    if lines and lines[0].startswith("```"):
        lines = lines[1:]
    if lines and lines[-1].strip() == "```":
        lines = lines[:-1]
    return "\n".join(lines).strip()


def _extract_first_json_object_text(content: str) -> str:
    start = content.find("{")
    if start == -1:
        raise ModelOutputError("Model response did not contain a JSON object.")

    depth = 0
    in_string = False
    escaped = False

    for index in range(start, len(content)):
        char = content[index]

        if in_string:
            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True
        elif char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return content[start : index + 1]

    raise ModelOutputError("Model response contained incomplete JSON.")
