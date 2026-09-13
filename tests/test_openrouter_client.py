from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import patch


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from lib.openrouter_client import (  # noqa: E402
    REASONING_EFFORTS,
    OpenRouterClient,
    build_chat_payload,
)


class FakeResponse:
    status_code = 200
    text = '{"choices":[{"message":{"content":"Hallo"}}]}'

    def json(self) -> dict:
        return {
            "id": "gen-test",
            "model": "test/model",
            "choices": [
                {"message": {"content": "Hallo"}, "finish_reason": "stop"}
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 5,
                "total_tokens": 15,
            },
        }


class FakeHttpClient:
    last_payload: dict | None = None

    def __init__(self, *args, **kwargs) -> None:
        pass

    def __enter__(self) -> "FakeHttpClient":
        return self

    def __exit__(self, *args) -> None:
        return None

    def post(self, _url: str, headers: dict, json: dict) -> FakeResponse:
        FakeHttpClient.last_payload = json
        return FakeResponse()


class BuildChatPayloadTests(unittest.TestCase):
    def test_reasoning_effort_becomes_reasoning_object(self) -> None:
        payload = build_chat_payload(
            model="deepseek/deepseek-v4.1-flash",
            system="sys",
            user="usr",
            temperature=0.2,
            max_tokens=10000,
            reasoning_effort="low",
        )

        self.assertEqual(payload["reasoning"], {"effort": "low"})
        self.assertEqual(payload["max_tokens"], 10000)
        self.assertEqual(payload["messages"][0]["role"], "system")
        self.assertIn("low", REASONING_EFFORTS)

    def test_payload_omits_reasoning_without_effort(self) -> None:
        payload = build_chat_payload(
            model="deepseek/deepseek-v4-flash",
            system="sys",
            user="usr",
            temperature=0.2,
            max_tokens=10000,
        )

        self.assertNotIn("reasoning", payload)


class OpenRouterClientReasoningTests(unittest.TestCase):
    def test_chat_forwards_configured_reasoning_effort(self) -> None:
        client = OpenRouterClient(
            api_key="dummy", model="test/model", reasoning_effort="low"
        )
        with patch("lib.openrouter_client.httpx.Client", FakeHttpClient):
            content = client.chat("system", "user", temperature=0.2,
                                  max_tokens=100)

        self.assertEqual(content, "Hallo")
        self.assertEqual(
            FakeHttpClient.last_payload["reasoning"], {"effort": "low"}
        )

    def test_chat_without_effort_sends_no_reasoning(self) -> None:
        client = OpenRouterClient(api_key="dummy", model="test/model")
        with patch("lib.openrouter_client.httpx.Client", FakeHttpClient):
            client.chat("system", "user", temperature=0.2, max_tokens=100)

        self.assertNotIn("reasoning", FakeHttpClient.last_payload)


if __name__ == "__main__":
    unittest.main()
