from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from lib.ollama_client import OllamaClient  # noqa: E402


class FakeResponse:
    status_code = 200
    text = '{"message":{"content":"{\\"findings\\":[]}"}}'

    def json(self) -> dict:
        return {"message": {"content": '{"findings":[]}'}}


class FakeHttpClient:
    last_payload: dict | None = None

    def __init__(self, *args, **kwargs) -> None:
        pass

    def __enter__(self) -> "FakeHttpClient":
        return self

    def __exit__(self, *args) -> None:
        return None

    def post(self, _url: str, json: dict) -> FakeResponse:
        FakeHttpClient.last_payload = json
        return FakeResponse()


class OllamaClientTests(unittest.TestCase):
    def test_json_mode_sets_ollama_format_json(self) -> None:
        client = OllamaClient(model="qwen3:8b")
        with (
            patch("lib.ollama_client._ollama_health", return_value=True),
            patch("lib.ollama_client.httpx.Client", FakeHttpClient),
        ):
            content = client.chat("system", "user", json_mode=True)

        self.assertEqual(content, '{"findings":[]}')
        self.assertEqual(FakeHttpClient.last_payload["format"], "json")


if __name__ == "__main__":
    unittest.main()
