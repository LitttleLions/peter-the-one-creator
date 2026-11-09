"""HTTP-Client für den unveränderten amazon-kdp-skill.

Phase 1 darf nur Session, Katalog und einen Einzel-Metadaten-Sync aufrufen.
Update, Preis, Upload, Publish, Löschen und Reports sind hier gesperrt.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Callable


DEFAULT_PORT = 3001
HEALTH_PATH = "/api/kdp/health"
ALLOWED_GET = {
    "/api/kdp/health",
    "/api/kdp/status",
    "/api/kdp/bookshelf",
    "/api/kdp/catalog",
    "/api/kdp/account",
    "/api/kdp/metadata",
}
LOGIN_PATH = "/api/kdp/login/start"

Transport = Callable[[str, str, dict[str, Any] | None], Any]


class KdpClientError(Exception):
    pass


class KdpClient:
    def __init__(
        self,
        base_url: str | None = None,
        *,
        transport: Transport | None = None,
        timeout: float = 120,
    ):
        port = os.environ.get("KDP_SERVER_PORT", str(DEFAULT_PORT))
        self.base_url = (base_url or os.environ.get("KDP_API_URL") or f"http://127.0.0.1:{port}").rstrip("/")
        self.transport = transport
        self.timeout = timeout

    def get_json(self, path: str) -> Any:
        self._check_allowed("GET", path)
        return self._request("GET", path, None)

    def post_json(self, path: str, body: dict[str, Any] | None = None) -> Any:
        self._check_allowed("POST", path)
        return self._request("POST", path, body)

    def status(self) -> dict[str, Any]:
        payload = self.get_json("/api/kdp/status")
        if not isinstance(payload, dict):
            raise KdpClientError("Status-Antwort ist kein Objekt")
        return payload

    def start_login(self) -> dict[str, Any]:
        payload = self.post_json(LOGIN_PATH, {})
        if not isinstance(payload, dict):
            raise KdpClientError("Login-Antwort ist kein Objekt")
        return payload

    def sync_format(self, title_id: str, fmt: str) -> dict[str, Any]:
        payload = self.post_json(f"/api/kdp/metadata/sync/{title_id}/{fmt}", {})
        if not isinstance(payload, dict) or not isinstance(payload.get("book"), dict):
            raise KdpClientError("Metadata-Sync ohne book-Objekt")
        return payload["book"]

    def _check_allowed(self, method: str, path: str) -> None:
        if method == "GET" and path in ALLOWED_GET:
            return
        if method == "POST" and path == LOGIN_PATH:
            return
        if method == "POST" and _sync_path(path):
            return
        raise KdpClientError(
            f"Phase 1 ruft {method} {path} nicht auf. "
            "Update, Preis, Upload, Publish und Reports bleiben gesperrt."
        )

    def _request(self, method: str, path: str, body: dict[str, Any] | None) -> Any:
        if self.transport is not None:
            return self.transport(method, path, body)
        data = None if body is None else json.dumps(body).encode("utf-8")
        request = urllib.request.Request(
            self.base_url + path,
            data=data,
            method=method,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8")
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise KdpClientError(f"{method} {path} -> HTTP {exc.code}: {detail}") from exc
        except urllib.error.URLError as exc:
            raise KdpClientError(f"{method} {path} nicht erreichbar: {exc.reason}") from exc
        if not raw:
            return {}
        try:
            return json.loads(raw)
        except json.JSONDecodeError as exc:
            raise KdpClientError(f"{method} {path} lieferte kein JSON") from exc


def ensure_kdp_server(
    repo_root: Path,
    *,
    client: KdpClient | None = None,
    starter: Callable[[], None] | None = None,
    attempts: int = 40,
    pause_seconds: float = 0.5,
) -> KdpClient:
    active = client or KdpClient()
    if _health_ok(active):
        return active
    if active.transport is not None:
        raise KdpClientError("KDP-Server antwortet nicht")
    if starter is None:
        starter = lambda: start_kdp_server(repo_root)
    starter()
    for _ in range(attempts):
        if _health_ok(active):
            return active
        time.sleep(pause_seconds)
    raise KdpClientError(
        "amazon-kdp-skill antwortet nicht auf "
        f"{active.base_url}{HEALTH_PATH}. Im Vendor-Ordner `npm install` ausführen."
    )


def start_kdp_server(repo_root: Path) -> None:
    vendor = repo_root / "tools" / "vendor" / "amazon-kdp-skill"
    if not (vendor / "package.json").is_file():
        raise KdpClientError(
            "Submodule fehlt: tools/vendor/amazon-kdp-skill. "
            "`git submodule update --init tools/vendor/amazon-kdp-skill`"
        )
    if not (vendor / "node_modules").is_dir():
        raise KdpClientError(
            "Abhängigkeiten fehlen. Im Ordner tools/vendor/amazon-kdp-skill `npm install` ausführen "
            "(installiert auch Playwright-Chromium)."
        )
    npm = shutil.which("npm")
    if not npm:
        raise KdpClientError("npm ist nicht im PATH")
    session_dir = repo_root / ".kdp-session"
    session_dir.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env["KDP_SESSION_DIR"] = str(session_dir)
    env.setdefault("KDP_SERVER_PORT", os.environ.get("KDP_SERVER_PORT", str(DEFAULT_PORT)))
    env.setdefault("KDP_REQUEST_DELAY_MS", os.environ.get("KDP_REQUEST_DELAY_MS", "4000"))
    log_path = session_dir / "server.log"
    log_handle = log_path.open("a", encoding="utf-8")
    subprocess.Popen(
        [npm, "run", "server:start"],
        cwd=vendor,
        env=env,
        stdout=log_handle,
        stderr=subprocess.STDOUT,
    )


def _health_ok(client: KdpClient) -> bool:
    try:
        payload = client.get_json(HEALTH_PATH)
    except KdpClientError:
        return False
    return isinstance(payload, dict) and payload.get("ok") is True


def _sync_path(path: str) -> bool:
    parts = path.strip("/").split("/")
    if parts[:4] != ["api", "kdp", "metadata", "sync"]:
        return False
    if len(parts) != 6:
        return False
    title_id, fmt = parts[4], parts[5]
    if fmt not in {"kindle", "paperback", "hardcover"}:
        return False
    return bool(title_id) and title_id.isalnum() and title_id.upper() == title_id and 10 <= len(title_id) <= 14
