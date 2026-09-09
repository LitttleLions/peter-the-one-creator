"""Small Ollama chat client for local review and translation runs."""

from __future__ import annotations

import shutil
import subprocess
import sys
import time
from dataclasses import dataclass

import httpx


class OllamaError(RuntimeError):
    """Raised when the local Ollama API cannot return a chat response."""


def list_ollama_models(api_base: str = "http://localhost:11434", timeout_sec: float = 2.0) -> list[dict]:
    """Return locally installed Ollama models as [{"id": ..., "name": ...}, ...]."""
    try:
        with httpx.Client(timeout=timeout_sec) as client:
            resp = client.get(f"{api_base.rstrip('/')}/api/tags")
            if resp.status_code >= 400:
                return []
            data = resp.json()
            models = data.get("models") or []
            # Embedding-Modelle (z. B. qwen3-embedding, nomic-embed-text) können kein Chat
            EMBEDDING_KEYWORDS = {"embed", "embedding", "nomic-embed"}
            return [
                {"id": m.get("name", m.get("model", "")), "name": m.get("name", m.get("model", ""))}
                for m in models
                if not any(
                    kw in (m.get("name", "") or "").lower() for kw in EMBEDDING_KEYWORDS
                )
            ]
    except Exception:
        return []


def _ollama_health(api_base: str, timeout_sec: float = 2.0) -> bool:
    try:
        with httpx.Client(timeout=timeout_sec) as client:
            resp = client.get(f"{api_base.rstrip('/')}/api/tags")
            return resp.status_code < 500
    except Exception:
        return False


def _start_ollama() -> bool:
    """Start Ollama in the background. Returns True if the binary was found and launched."""
    ollama_exe = shutil.which("ollama")
    if ollama_exe is None:
        return False
    creationflags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0  # type: ignore[attr-defined]
    try:
        subprocess.Popen(
            [ollama_exe, "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            creationflags=creationflags,
        )
        return True
    except Exception:
        return False


@dataclass
class OllamaClient:
    model: str
    api_base: str = "http://localhost:11434"
    timeout_sec: float = 600.0
    _auto_start_attempted: bool = False

    def _ensure_ollama(self) -> None:
        if self._auto_start_attempted:
            if not _ollama_health(self.api_base):
                raise OllamaError(
                    f"Ollama laeuft nicht unter {self.api_base}. "
                    "Bitte `ollama serve` manuell starten."
                )
            return
        self._auto_start_attempted = True
        if _ollama_health(self.api_base):
            return
        print("Ollama laeuft nicht, versuche automatischen Start ...", flush=True)
        if not _start_ollama():
            raise OllamaError(
                f"Ollama-Binary nicht gefunden. Bitte installieren: https://ollama.ai/"
            )
        for _ in range(10):
            time.sleep(1.5)
            if _ollama_health(self.api_base):
                print("Ollama gestartet.", flush=True)
                return
        raise OllamaError(
            f"Ollama konnte nicht gestartet werden. "
            "Bitte `ollama serve` manuell starten und erneut versuchen."
        )

    def chat(
        self,
        system: str,
        user: str,
        temperature: float = 0.1,
        max_tokens: int = 2000,
        json_mode: bool = False,
        num_ctx: int = 32768,
    ) -> str:
        self._ensure_ollama()
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
                "num_ctx": num_ctx,
            },
        }
        if json_mode:
            payload["format"] = "json"
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
