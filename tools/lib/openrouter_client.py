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
- Bei 5xx und Timeouts wird automatisch retryt (max_retries,
  backoff in Sekunden).
"""

from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass
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
        for attempt in range(self.max_retries + 1):
            try:
                with httpx.Client(timeout=self.timeout_sec) as client:
                    r = client.post(url, headers=self._headers(),
                                    json=payload)
                if r.status_code >= 500:
                    raise OpenRouterError(
                        f"OpenRouter 5xx: {r.status_code} — "
                        f"{r.text[:300]}"
                    )
                if r.status_code == 429:
                    # Rate limit — etwas länger warten
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
                data = r.json()
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
            f"OpenRouter-Call endgültig fehlgeschlagen "
            f"({self.max_retries + 1} Versuche): {last_err}"
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
            raise OpenRouterError(
                f"OpenRouter-Antwort ohne Text-Content. "
                f"Body: {json.dumps(data)[:500]}"
            )
        return content


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
