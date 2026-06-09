"""
openrouter_client.py
====================
Minimaler OpenRouter-Chat-Completion-Client.

Lädt die Konfiguration aus `.env` (über python-dotenv) und
stellt eine kleine, robuste `OpenRouterClient`-Klasse bereit.

Verwendung:
    from lib.openrouter_client import OpenRouterClient, OpenRouterError

    client = OpenRouterClient.from_env()
    text = client.chat(
        system="Du bist ein Übersetzer.",
        user="Übersetze: ...",
        temperature=0.4,
        max_tokens=2000,
    )

Hinweise:
- Der Client ist bewusst klein gehalten. Kein Streaming, keine
  Async-API in dieser Version — das holen wir nach, sobald
  die Grundpipeline steht.
- HTTP-Fehler werden in OpenRouterError verpackt, mit Statuscode
  und Body-Auszug, damit man im Logfile sehen kann, was
  schiefging.
- Bei 5xx, Timeouts und JSON-Parse-Fehlern wird automatisch
  retryt (max_retries, backoff in Sekunden).
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import httpx
from dotenv import load_dotenv


DEFAULT_API_BASE = "https://openrouter.ai/api/v1"
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
DOTENV_PATH = REPO_ROOT / ".env"


class OpenRouterError(RuntimeError):
    """Allgemeiner OpenRouter-Fehler (HTTP, Parsing, Auth, etc.)."""


@dataclass
class OpenRouterClient:
    api_key: str
    model: str
    api_base: str = DEFAULT_API_BASE
    app_name: str = "peter-the-one"
    app_url: str = ""
    timeout_sec: float = 180.0
    max_retries: int = 2
    backoff_sec: float = 3.0
    last_usage: dict = field(default_factory=dict)
    usage_totals: dict = field(default_factory=dict)
    last_response_model: str = ""
    last_response_id: str = ""
    last_response_provider: str = ""
    last_response_created: int | None = None

    @classmethod
    def from_env(
        cls,
        model_override: Optional[str] = None,
        dotenv_path: Path | str = DOTENV_PATH,
    ) -> "OpenRouterClient":
        """Lädt .env (falls vorhanden) und baut einen Client
        aus den Umgebungsvariablen. `model_override` schlägt
        OPENROUTER_MODEL."""
        p = Path(dotenv_path)
        if p.exists():
            load_dotenv(p, override=False)

        api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        if not api_key or api_key.startswith("sk-or-v1-DEIN_KEY"):
            raise OpenRouterError(
                "OPENROUTER_API_KEY fehlt oder ist noch der Platzhalter. "
                "Bitte `.env` anlegen (siehe `.env.example`) und "
                "den echten Key eintragen."
            )

        model = (
            model_override
            or os.getenv("OPENROUTER_MODEL")
            or "anthropic/claude-3.5-sonnet"
        )
        api_base = os.getenv("OPENROUTER_API_BASE", DEFAULT_API_BASE)
        app_name = os.getenv("OPENROUTER_APP_NAME", "peter-the-one")
        app_url = os.getenv("OPENROUTER_APP_URL", "")
        return cls(
            api_key=api_key,
            model=model,
            api_base=api_base,
            app_name=app_name,
            app_url=app_url,
        )

    def _headers(self) -> dict[str, str]:
        h = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Title": self.app_name,
        }
        if self.app_url:
            h["HTTP-Referer"] = self.app_url
        return h

    def chat(
        self,
        system: str,
        user: str,
        temperature: float = 0.4,
        max_tokens: int = 4000,
        model: Optional[str] = None,
    ) -> str:
        """
        Einfacher Chat-Completion-Call. Gibt den `content` der
        ersten Choice zurück.
        """
        url = f"{self.api_base.rstrip('/')}/chat/completions"
        payload = {
            "model": model or self.model,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        }

        last_err: Optional[Exception] = None
        last_body: str = "(keine Antwort)"
        for attempt in range(self.max_retries + 1):
            try:
                with httpx.Client(timeout=self.timeout_sec) as client:
                    r = client.post(url, headers=self._headers(),
                                    json=payload)
                if r.status_code >= 500:
                    last_body = r.text[:300]
                    last_err = OpenRouterError(
                        f"OpenRouter 5xx: {r.status_code} — "
                        f"{r.text[:300]}"
                    )
                    if attempt < self.max_retries:
                        time.sleep(self.backoff_sec)
                        continue
                    raise last_err
                if r.status_code == 429:
                    last_body = r.text[:300]
                    if attempt < self.max_retries:
                        time.sleep(self.backoff_sec * 2)
                        continue
                    raise OpenRouterError(
                        f"OpenRouter 429 (Rate Limit): {r.text[:300]}"
                    )
                if r.status_code >= 400:
                    # 4xx — kein Retry, sondern harter Fehler
                    raise OpenRouterError(
                        f"OpenRouter {r.status_code}: {r.text[:500]}"
                    )

                # JSON parsen – mit Retry bei Parse-Fehlern
                try:
                    data = r.json()
                except json.JSONDecodeError as e:
                    last_body = r.text[:500]
                    last_err = e
                    if attempt < self.max_retries:
                        time.sleep(self.backoff_sec)
                        continue
                    raise OpenRouterError(
                        f"OpenRouter-Antwort ist kein gueltiges JSON "
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
            except OpenRouterError:
                raise
            except Exception as e:
                # Unerwarteter Fehler — nicht retryen
                raise OpenRouterError(f"Unerwarteter Fehler: {e}") from e

        raise OpenRouterError(
            f"OpenRouter-Call endgueltig fehlgeschlagen "
            f"({self.max_retries + 1} Versuche). "
            f"Letzter Fehler: {last_err}. Body: {last_body[:200]}"
        )

    @staticmethod
    def _extract_content(data: dict) -> str:
        try:
            choices = data["choices"]
        except (KeyError, TypeError) as e:
            raise OpenRouterError(
                f"Unerwartete OpenRouter-Antwort: "
                f"'choices' fehlt. Body: {json.dumps(data)[:500]}"
            ) from e
        if not choices:
            raise OpenRouterError(
                f"OpenRouter-Antwort ohne choices. "
                f"Body: {json.dumps(data)[:500]}"
            )
        msg = choices[0].get("message") or {}
        content = msg.get("content")
        if not isinstance(content, str) or not content.strip():
            reason = choices[0].get("finish_reason", "unbekannt")
            thinking = msg.get("reasoning") or msg.get("thinking") or "(kein reasoning)"
            raise OpenRouterError(
                f"OpenRouter-Antwort ohne Text-Content. "
                f"finish_reason={reason}. "
                f"Reasoning/Thinking (erste 300 Zeichen): "
                f"{str(thinking)[:300]}"
            )
        return content

    def _record_response_meta(self, data: dict) -> None:
        model = data.get("model")
        self.last_response_model = model if isinstance(model, str) else ""
        response_id = data.get("id")
        self.last_response_id = response_id if isinstance(response_id, str) else ""
        response_provider = data.get("provider")
        self.last_response_provider = (
            response_provider if isinstance(response_provider, str) else ""
        )
        response_created = data.get("created")
        self.last_response_created = (
            response_created if isinstance(response_created, int) else None
        )
        usage = data.get("usage") or {}
        if not isinstance(usage, dict):
            usage = {}
        self.last_usage = usage
        for key, value in usage.items():
            if isinstance(value, int):
                self.usage_totals[key] = self.usage_totals.get(key, 0) + value

    def usage_summary(self) -> str:
        if not self.usage_totals:
            meta = self.response_meta_summary()
            if meta:
                return f"Tokens: keine Usage-Daten vom Provider erhalten; {meta}"
            return "Tokens: keine Usage-Daten vom Provider erhalten"
        preferred = [
            "prompt_tokens",
            "completion_tokens",
            "total_tokens",
            "reasoning_tokens",
        ]
        parts = []
        for key in preferred:
            if key in self.usage_totals:
                parts.append(f"{key}={self.usage_totals[key]}")
        for key in sorted(self.usage_totals):
            if key not in preferred:
                parts.append(f"{key}={self.usage_totals[key]}")
        if self.last_response_model:
            parts.append(f"Antwort-Modell={self.last_response_model}")
        if self.last_response_provider:
            parts.append(f"Antwort-Provider={self.last_response_provider}")
        if self.last_response_id:
            parts.append(f"Response-ID={self.last_response_id}")
        return "Tokens: " + ", ".join(parts)

    def response_meta_summary(self) -> str:
        parts = []
        if self.last_response_model:
            parts.append(f"Antwort-Modell={self.last_response_model}")
        if self.last_response_provider:
            parts.append(f"Antwort-Provider={self.last_response_provider}")
        if self.last_response_id:
            parts.append(f"Response-ID={self.last_response_id}")
        if self.last_response_created is not None:
            parts.append(f"Response-Created={self.last_response_created}")
        return ", ".join(parts)


# ---------------------------------------------------------------------------
# Mini-Self-Test (nur bei direktem Aufruf)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("OpenRouterClient-Self-Test")
    try:
        c = OpenRouterClient.from_env()
        print(f"  model:    {c.model}")
        print(f"  api_base: {c.api_base}")
        print("  API-Key vorhanden (nicht angezeigt).")
    except OpenRouterError as e:
        print(f"  FEHLER: {e}")
