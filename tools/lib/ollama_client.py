"""
ollama_client.py
================
Minimaler Chat-Completion-Client fuer lokale Ollama-Instanz.

Lauscht auf http://localhost:11434/api/chat (Ollama-Standard).
Struktur weitgehend analog zu openrouter_client.py, aber ohne
API-Key, ohne .env und ohne Retry-Logik (Ollama laeuft lokal,
Netzwerkfehler sind unwahrscheinlich).

Verwendung:
    from lib.ollama_client import OllamaClient, OllamaError

    client = OllamaClient(model="gemma4:2b")
    text = client.chat(
        system="Du bist ein Uebersetzer.",
        user="Uebersetze: ...",
        temperature=0.4,
        max_tokens=2000,
    )
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Optional

import httpx


OLLAMA_API_BASE = "http://localhost:11434"


class OllamaError(RuntimeError):
    """Allgemeiner Ollama-Fehler (HTTP, Parsing, etc.)."""


@dataclass
class OllamaClient:
    model: str
    api_base: str = OLLAMA_API_BASE
    timeout_sec: float = 180.0
    max_retries: int = 2
    backoff_sec: float = 3.0
    last_usage: dict = field(default_factory=dict)
    usage_totals: dict = field(default_factory=dict)
    last_response_model: str = ""
    last_response_done: bool = False
    last_eval_count: int = 0

    def _headers(self) -> dict[str, str]:
        return {"Content-Type": "application/json"}

    def chat(
        self,
        system: str,
        user: str,
        temperature: float = 0.4,
        max_tokens: int = 4000,
        model: Optional[str] = None,
    ) -> str:
        """
        Chat-Completion-Call an Ollama `/api/chat`.
        Baut die Messages und gibt den `content` der Antwort zurueck.
        """
        url = f"{self.api_base.rstrip('/')}/api/chat"
        payload = {
            "model": model or self.model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": False,
        }

        last_err: Optional[Exception] = None
        last_body: str = "(keine Antwort)"
        for attempt in range(self.max_retries + 1):
            try:
                with httpx.Client(timeout=self.timeout_sec) as client:
                    r = client.post(url, headers=self._headers(), json=payload)
                if r.status_code >= 500:
                    last_body = r.text[:300]
                    last_err = OllamaError(
                        f"Ollama 5xx: {r.status_code} — {r.text[:300]}"
                    )
                    if attempt < self.max_retries:
                        time.sleep(self.backoff_sec)
                        continue
                    raise last_err
                if r.status_code >= 400:
                    raise OllamaError(
                        f"Ollama {r.status_code}: {r.text[:500]}"
                    )

                # JSON parsen
                try:
                    data = r.json()
                except json.JSONDecodeError as e:
                    last_body = r.text[:500]
                    last_err = e
                    if attempt < self.max_retries:
                        time.sleep(self.backoff_sec)
                        continue
                    raise OllamaError(
                        f"Ollama-Antwort ist kein gueltiges JSON "
                        f"(Status {r.status_code}): {r.text[:500]}"
                    ) from e

                self._record_response_meta(data)
                return self._extract_content(data)

            except httpx.TimeoutException as e:
                last_err = e
                if attempt < self.max_retries:
                    time.sleep(self.backoff_sec)
                    continue
            except httpx.HTTPError as e:
                last_err = e
                if attempt < self.max_retries:
                    time.sleep(self.backoff_sec)
                    continue
            except OllamaError:
                raise
            except Exception as e:
                raise OllamaError(f"Unerwarteter Fehler: {e}") from e

        raise OllamaError(
            f"Ollama-Call endgueltig fehlgeschlagen "
            f"({self.max_retries + 1} Versuche). "
            f"Letzter Fehler: {last_err}. Body: {last_body[:200]}"
        )

    @staticmethod
    def _extract_content(data: dict) -> str:
        try:
            msg = data["message"]
        except (KeyError, TypeError) as e:
            raise OllamaError(
                f"Unerwartete Ollama-Antwort: 'message' fehlt. "
                f"Body: {json.dumps(data)[:500]}"
            ) from e
        content = msg.get("content")
        if not isinstance(content, str) or not content.strip():
            raise OllamaError(
                f"Ollama-Antwort ohne Text-Content. "
                f"Body: {json.dumps(data)[:500]}"
            )
        return content

    def _record_response_meta(self, data: dict) -> None:
        model = data.get("model")
        self.last_response_model = model if isinstance(model, str) else ""
        done = data.get("done", False)
        self.last_response_done = bool(done)
        self.last_eval_count = data.get("eval_count", 0)
        # Ollama liefert kein Usage-Objekt wie OpenRouter, aber
        # eval_count ist die Token-Anzahl.
        self.last_usage = {"eval_count": self.last_eval_count}
        self.usage_totals["eval_count"] = (
            self.usage_totals.get("eval_count", 0) + self.last_eval_count
        )

    def usage_summary(self) -> str:
        parts = []
        if self.usage_totals.get("eval_count"):
            parts.append(f"eval_count={self.usage_totals['eval_count']}")
        if self.last_response_model:
            parts.append(f"Modell={self.last_response_model}")
        if self.last_response_done:
            parts.append("done=yes")
        return "Tokens: " + ", ".join(parts) if parts else "Tokens: keine Daten"

    def response_meta_summary(self) -> str:
        parts = []
        if self.last_response_model:
            parts.append(f"Modell={self.last_response_model}")
        if self.last_eval_count:
            parts.append(f"eval_count={self.last_eval_count}")
        return ", ".join(parts)


# ---------------------------------------------------------------------------
# Mini-Self-Test (nur bei direktem Aufruf)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("OllamaClient-Self-Test")
    try:
        c = OllamaClient(model="gemma4:2b")
        print(f"  model:    {c.model}")
        print(f"  api_base: {c.api_base}")
    except Exception as e:
        print(f"  FEHLER: {e}")
