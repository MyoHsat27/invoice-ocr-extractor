from __future__ import annotations

from typing import Any

import httpx

from invoice_agent.settings import Settings


class ProviderConfigurationError(RuntimeError):
    pass


class ProviderRequestError(RuntimeError):
    pass


class OpenRouterClient:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def chat_json(self, system_prompt: str, user_prompt: str) -> dict[str, Any]:
        if not self.settings.openrouter_api_key:
            raise ProviderConfigurationError("OPENROUTER_API_KEY is not configured.")

        payload = {
            "model": self.settings.openrouter_model,
            "temperature": 0,
            "response_format": {"type": "json_object"},
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        }
        headers = {
            "Authorization": f"Bearer {self.settings.openrouter_api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": self.settings.openrouter_referer,
            "X-Title": "Invoice Review Agent",
        }

        async with httpx.AsyncClient(timeout=45) as client:
            try:
                response = await client.post(self.settings.openrouter_chat_url, json=payload, headers=headers)
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as exc:
                detail = _provider_error_detail(exc.response)
                raise ProviderRequestError(
                    f"OpenRouter request failed with {exc.response.status_code}: {detail}"
                ) from exc
            except httpx.HTTPError as exc:
                raise ProviderRequestError(f"OpenRouter request failed: {exc}") from exc


def _provider_error_detail(response: httpx.Response) -> str:
    try:
        payload = response.json()
    except ValueError:
        return response.text[:500]

    if isinstance(payload, dict):
        error = payload.get("error")
        if isinstance(error, dict):
            message = error.get("message")
            if message:
                return str(message)
        if payload.get("message"):
            return str(payload["message"])
    return str(payload)[:500]
