"""Small Ollama chat client for local review runs."""

from __future__ import annotations

from dataclasses import dataclass

import httpx


class OllamaError(RuntimeError):
    """Raised when the local Ollama API cannot return a chat response."""


@dataclass
class OllamaClient:
    model: str
    api_base: str = "http://localhost:11434"
    timeout_sec: float = 180.0

    def chat(
        self,
        system: str,
        user: str,
        temperature: float = 0.1,
        max_tokens: int = 2000,
    ) -> str:
        url = f"{self.api_base.rstrip('/')}/api/chat"
        payload = {
            "model": self.model,
            "stream": False,
            "think": False,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            },
        }
        try:
            with httpx.Client(timeout=self.timeout_sec) as client:
                response = client.post(url, json=payload)
        except httpx.HTTPError as exc:
            raise OllamaError(
                f"Ollama nicht erreichbar unter {self.api_base}: {exc}"
            ) from exc
        if response.status_code >= 400:
            raise OllamaError(
                f"Ollama {response.status_code}: {response.text[:500]}"
            )
        try:
            data = response.json()
        except ValueError as exc:
            raise OllamaError(
                f"Ollama-Antwort ist kein gueltiges JSON: {response.text[:500]}"
            ) from exc
        message = data.get("message") or {}
        content = message.get("content")
        if not isinstance(content, str) or not content.strip():
            raise OllamaError(
                f"Ollama-Antwort ohne Textinhalt: {str(data)[:500]}"
            )
        return content
