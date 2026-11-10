"""Begleiteter Browser-Fahrer fuer den KDP-Content-Manager (A+ Content).

Amazon hat keine A+-Schnittstelle; das Formular ist eine Webseite. Dieser
Fahrer bedient sie, aber nie blind: erst ein Schnappschuss der sichtbaren
Felder, dann ein Plan mit Pruefsummen, dann die Ausfuehrung mit Journal.

Sicherheitsregeln, die im Code stehen und nicht umgangen werden:

- nur Amazon-Hosts als Ziel (``assert_allowed_url``),
- Passwort-, Steuer-, Bank-, Telefon- und E-Mail-Felder werden nie gefuellt,
- Klicks auf Speichern/Veroeffentlichen brauchen ``--allow-submit``,
- Uploads muessen dieselbe SHA-256 haben wie beim Planen,
- jede Aktion landet im Journal (JSONL), ohne Werte sensibler Felder.

Befehle::

    python tools/aplus_drive.py login
    python tools/aplus_drive.py snapshot --url https://kdp.amazon.com/en_US/bookshelf
    python tools/aplus_drive.py plan --actions actions.json --out plan.json
    python tools/aplus_drive.py execute --plan plan.json --journal journal.jsonl
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_STATE = REPO_ROOT / ".kdp-session" / "amazon-kdp.json"
ALLOWED_SUFFIXES = (".amazon.com", ".amazon.de")
ALLOWED_ACTIONS = ("fill", "select", "upload", "click")
SENSITIVE = re.compile(
    r"passwor|kennwort|steuer|tax|bank|iban|bic|konto|credit.?card|kreditkarte|"
    r"telefon|phone|handy|e-?mail|sms|otp|einmal|verification|bestaetigungscode|"
    r"sozialversicherung|ausweis|passport",
    re.I,
)
SUBMIT_HINT = re.compile(r"speicher|veroeffentlich|veröffentlich|publish|submit|absenden|freigeben", re.I)

SNAPSHOT_JS = r"""() => {
  const visible = el => !!(el.getClientRects().length && getComputedStyle(el).visibility !== 'hidden');
  const labelOf = el => (el.labels && el.labels[0] ? el.labels[0].innerText
      : el.getAttribute('aria-label') || el.getAttribute('placeholder')
      || el.getAttribute('name') || el.innerText || '').trim().slice(0, 200);
  const nodes = Array.from(document.querySelectorAll('input,textarea,select,button,[role=button]'))
      .filter(el => (visible(el) || el.matches('input[type=file]')))
      .filter(el => !['hidden', 'password'].includes((el.type || '').toLowerCase()));
  return nodes.map((el, index) => {
    el.setAttribute('data-drive-control', String(index));
    return {
      index: index,
      tag: el.tagName.toLowerCase(),
      type: (el.type || '').toLowerCase(),
      label: labelOf(el),
      href: el.tagName === 'A' ? (el.getAttribute('href') || '') : '',
      disabled: !!el.disabled,
      options: el.tagName === 'SELECT' ? Array.from(el.options).map(o => o.label) : []
    };
  });
}"""


def now() -> str:
    return datetime.now().isoformat(timespec="seconds")


def assert_allowed_url(url: str) -> None:
    parsed = urlparse(str(url or "").strip())
    host = (parsed.hostname or "").lower()
    if parsed.scheme not in ("http", "https"):
        raise SystemExit(f"Nur http(s) erlaubt: {url}")
    if not any(host == suffix.lstrip(".") or host.endswith(suffix) for suffix in ALLOWED_SUFFIXES):
        raise SystemExit(f"Kein Amazon-Host: {host or url}")


def normalize_label(text: str) -> str:
    return " ".join(str(text or "").split()).casefold()


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_sensitive(label: str) -> bool:
    return bool(SENSITIVE.search(label or ""))


def requires_submit_confirmation(label: str) -> bool:
    return bool(SUBMIT_HINT.search(label or ""))


def resolve_step(controls: list[dict[str, Any]], step: dict[str, Any]) -> tuple[dict[str, Any] | None, str]:
    """Ziel-Control ueber die Beschriftung finden (exakt, ohne Gross/klein)."""
    wanted = normalize_label(step.get("label"))
    if not wanted:
        return None, "Schritt ohne label"
    matches = [control for control in controls if normalize_label(control.get("label")) == wanted]
    if not matches:
        return None, f"kein Feld mit label={step.get('label')!r}"
    if len(matches) > 1:
        return None, f"label={step.get('label')!r} ist mehrdeutig ({len(matches)} Treffer)"
    return matches[0], ""


def validate_steps(
    controls: list[dict[str, Any]],
    steps: list[dict[str, Any]],
    base_dir: Path,
) -> tuple[list[dict[str, Any]], list[str]]:
    """Aktionsliste gegen den Schnappschuss pruefen und aufloesen."""
    resolved: list[dict[str, Any]] = []
    problems: list[str] = []
    for position, step in enumerate(steps, start=1):
        action = str(step.get("action") or "").strip().lower()
        label = str(step.get("label") or "")
        if action not in ALLOWED_ACTIONS:
            problems.append(f"Schritt {position}: unbekannte Aktion {action!r}")
            continue
        control, problem = resolve_step(controls, step)
        if problem:
            problems.append(f"Schritt {position}: {problem}")
            continue
        assert control is not None
        if control.get("disabled"):
            problems.append(f"Schritt {position}: Feld {label!r} ist deaktiviert")
            continue
        if action in ("fill", "select") and is_sensitive(label):
            problems.append(f"Schritt {position}: {label!r} ist ein sensibles Feld und wird nicht gefuellt")
            continue
        entry: dict[str, Any] = {
            "position": position,
            "action": action,
            "label": label,
            "control_index": control["index"],
            "needs_confirmation": action == "click" and requires_submit_confirmation(label),
        }
        if action in ("fill", "select"):
            value = str(step.get("value") or "")
            if not value:
                problems.append(f"Schritt {position}: value fehlt")
                continue
            entry["value"] = value
        if action == "upload":
            source = Path(str(step.get("path") or ""))
            if not source.is_absolute():
                source = (base_dir / source).resolve()
            if not source.is_file():
                problems.append(f"Schritt {position}: Datei fehlt: {source}")
                continue
            entry["path"] = source.as_posix()
            entry["size"] = source.stat().st_size
            entry["sha256"] = sha256_of(source)
        resolved.append(entry)
    return resolved, problems


@contextmanager
def open_browser(state_path: Path, headless: bool):
    """Playwright starten; Sitzung aus ``state_path`` laden, wenn vorhanden."""
    from playwright.sync_api import sync_playwright  # lokal, damit Tests ohne Playwright laufen

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=headless)
        context_args: dict[str, Any] = {}
        if state_path.is_file():
            context_args["storage_state"] = str(state_path)
        context = browser.new_context(**context_args)
        page = context.new_page()
        try:
            yield page, context
        finally:
            context.close()
            browser.close()


def snapshot_page(page) -> list[dict[str, Any]]:
    return page.evaluate(SNAPSHOT_JS)


def append_journal(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")


def execute_plan(
    page,
    plan: dict[str, Any],
    journal_path: Path,
    *,
    allow_submit: bool = False,
    pause: float = 0.3,
) -> list[dict[str, Any]]:
    """Plan abspielen; jeder Schritt wird erneut gegen die Seite aufgeloest."""
    records: list[dict[str, Any]] = []
    for step in plan.get("steps") or []:
        label = str(step.get("label") or "")
        action = str(step.get("action") or "")
        record: dict[str, Any] = {
            "ts": now(),
            "position": step.get("position"),
            "action": action,
            "label": label,
            "outcome": "pending",
        }
        try:
            controls = snapshot_page(page)
            control, problem = resolve_step(controls, step)
            if problem:
                record.update(outcome="failed", detail=problem)
                records.append(record)
                append_journal(journal_path, record)
                raise SystemExit(f"Schritt {step.get('position')}: {problem}")
            assert control is not None
            selector = f"[data-drive-control='{control['index']}']"
            if action == "fill":
                if is_sensitive(label):
                    record.update(outcome="blocked", detail="sensibles Feld")
                    records.append(record)
                    append_journal(journal_path, record)
                    continue
                page.fill(selector, str(step.get("value") or ""))
            elif action == "select":
                page.select_option(selector, label=str(step.get("value") or ""))
            elif action == "upload":
                source = Path(str(step.get("path") or ""))
                if not source.is_file():
                    record.update(outcome="failed", detail="Datei fehlt")
                    records.append(record)
                    append_journal(journal_path, record)
                    continue
                if sha256_of(source) != step.get("sha256"):
                    record.update(outcome="failed", detail="Datei hat sich seit dem Plan geaendert")
                    records.append(record)
                    append_journal(journal_path, record)
                    continue
                page.set_input_files(selector, str(source))
            elif action == "click":
                if requires_submit_confirmation(label) and not allow_submit:
                    record.update(outcome="blocked", detail="bestaetigung noetig (--allow-submit)")
                    records.append(record)
                    append_journal(journal_path, record)
                    continue
                page.click(selector)
            record["outcome"] = "ok"
            page.wait_for_timeout(int(pause * 1000))
        except SystemExit:
            raise
        except Exception as error:  # Playwright-/DOM-Fehler protokollieren, nicht verschweigen
            record.update(outcome="failed", detail=f"{type(error).__name__}: {error}")
        records.append(record)
        append_journal(journal_path, record)
    return records


LOGIN_URL = "https://kdp.amazon.de/aplus"
LOGIN_FALLBACKS = (
    "https://kdp.amazon.de/aplus",
    "https://www.amazon.de/",
    "https://kdp.amazon.com/en_US/bookshelf",
)
LOGIN_HINTS = ("e-mail", "mobiltelefon", "passwort", "password", "anmelden", "sign in")


def open_login_page(page, url: str) -> str:
    """Erste erreichbare Anmeldeseite oeffnen (Amazon resettet einzelne Hosts)."""
    candidates = [url] + [candidate for candidate in LOGIN_FALLBACKS if candidate != url]
    for candidate in candidates:
        try:
            page.goto(candidate, wait_until="domcontentloaded", timeout=30000)
            return candidate
        except Exception as error:
            print(f"  {candidate} nicht erreichbar ({type(error).__name__}), naechster Versuch")
    raise SystemExit("Keine KDP-/Amazon-Seite erreichbar")


def looks_like_login(controls: list[dict[str, Any]]) -> bool:
    """Anmeldeseite erkennen: sie zeigt genau die Konto-Felder, keine Formulare."""
    labels = " ".join(normalize_label(control.get("label")) for control in controls)
    return any(hint in labels for hint in LOGIN_HINTS)


def authenticated_on_kdp(page, controls: list[dict[str, Any]]) -> bool:
    """Nur zaehlt eine echte KDP-Seite - der Storefront ohne Login reicht nicht."""
    url = page.url or ""
    return (
        "kdp.amazon." in url
        and "signin" not in url
        and "/ap/" not in url
        and not looks_like_login(controls)
    )


def cmd_login(args: argparse.Namespace) -> int:
    state = Path(args.storage_state)
    url = getattr(args, "url", None) or LOGIN_URL
    assert_allowed_url(url)
    with open_browser(state, headless=False) as (page, context):
        opened = open_login_page(page, url)
        print(f"Browser offen auf {opened}")
        print("Bitte im Fenster anmelden (inkl. Zwei-Faktor). Ich warte und speichere dann.")
        deadline = int(getattr(args, "timeout", 300))
        waited = 0
        while waited < deadline:
            try:
                page.wait_for_timeout(5000)
                controls = snapshot_page(page)
            except Exception as error:  # Fenster geschlossen oder Verbindung weg
                print(f"Fenster weg ({type(error).__name__}); nichts gespeichert.", flush=True)
                return 2
            waited += 5
            if authenticated_on_kdp(page, controls):
                state.parent.mkdir(parents=True, exist_ok=True)
                context.storage_state(path=str(state))
                print(f"Anmeldung erkannt nach {waited} s auf {page.url}. Sitzung gespeichert: {state}", flush=True)
                return 0
            if waited % 30 == 0:
                print(f"  warte ... {waited} s (Seite: {page.url[:70]})", flush=True)
        print("Zeitlimit erreicht, keine Anmeldung erkannt. Sitzung unveraendert.")
        return 1


def cmd_snapshot(args: argparse.Namespace) -> int:
    assert_allowed_url(args.url)
    with open_browser(Path(args.storage_state), headless=args.headless) as (page, _context):
        page.goto(args.url)
        page.wait_for_timeout(1500)
        controls = snapshot_page(page)
    payload = {"url": args.url, "captured_at": now(), "controls": controls}
    if args.out:
        Path(args.out).write_text(
            json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
        )
    print(f"{len(controls)} Felder auf {args.url}")
    for control in controls:
        print(f"  [{control['index']:>2}] {control['tag']:<8} {control['label'][:70]}")
    if args.out:
        print(f"geschrieben: {args.out}")
    return 0


def cmd_plan(args: argparse.Namespace) -> int:
    actions_path = Path(args.actions)
    document = json.loads(actions_path.read_text(encoding="utf-8"))
    url = str(document.get("url") or "")
    assert_allowed_url(url)
    steps = document.get("steps") or []
    with open_browser(Path(args.storage_state), headless=args.headless) as (page, _context):
        page.goto(url)
        page.wait_for_timeout(1500)
        controls = snapshot_page(page)
    resolved, problems = validate_steps(controls, steps, actions_path.parent)
    plan = {
        "url": url,
        "created_at": now(),
        "source_actions": actions_path.as_posix(),
        "steps": resolved,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Plan: {len(resolved)} von {len(steps)} Schritten aufgeloest -> {out}")
    for step in resolved:
        flag = " [bestaetigung]" if step.get("needs_confirmation") else ""
        print(f"  {step['position']:>2}. {step['action']:<6} {step['label'][:60]}{flag}")
    if problems:
        print("Probleme:")
        for problem in problems:
            print(f"  - {problem}")
        return 1
    return 0


def cmd_execute(args: argparse.Namespace) -> int:
    plan_path = Path(args.plan)
    plan = json.loads(plan_path.read_text(encoding="utf-8"))
    assert_allowed_url(str(plan.get("url") or ""))
    journal = Path(args.journal)
    with open_browser(Path(args.storage_state), headless=args.headless) as (page, _context):
        page.goto(str(plan["url"]))
        page.wait_for_timeout(1500)
        records = execute_plan(page, plan, journal, allow_submit=args.allow_submit)
    ok = sum(1 for record in records if record["outcome"] == "ok")
    blocked = sum(1 for record in records if record["outcome"] == "blocked")
    failed = sum(1 for record in records if record["outcome"] == "failed")
    print(f"Ausgefuehrt: {ok} ok, {blocked} blockiert, {failed} fehlgeschlagen")
    for record in records:
        if record["outcome"] != "ok":
            print(f"  {record['position']}. {record['label'][:50]}: {record['outcome']} - {record.get('detail', '')}")
    print(f"Journal: {journal}")
    return 0 if failed == 0 else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Begleiteter KDP-Browser-Fahrer (A+ Content)")
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--storage-state", default=str(DEFAULT_STATE), help="Sitzungsdatei (Cookies)")
    common.add_argument("--headless", action="store_true", help="ohne Fenster (nur Snapshot/Tests)")
    parser.add_argument("--storage-state", default=str(DEFAULT_STATE), help=argparse.SUPPRESS)
    parser.add_argument("--headless", action="store_true", help=argparse.SUPPRESS)
    sub = parser.add_subparsers(dest="command", required=True)

    login = sub.add_parser("login", parents=[common], help="Browser oeffnen und Anmeldung speichern")
    login.add_argument("--url", default=LOGIN_URL, help="Startseite (Default: deutsches KDP)")
    login.add_argument("--timeout", type=int, default=300, help="Sekunden warten (Default 300)")
    login.set_defaults(func=cmd_login)

    snapshot = sub.add_parser("snapshot", parents=[common], help="sichtbare Felder einer Seite auflisten")
    snapshot.add_argument("--url", required=True)
    snapshot.add_argument("--out")
    snapshot.set_defaults(func=cmd_snapshot)

    plan = sub.add_parser("plan", parents=[common], help="Aktionsliste gegen die Seite aufloesen")
    plan.add_argument("--actions", required=True)
    plan.add_argument("--out", required=True)
    plan.set_defaults(func=cmd_plan)

    execute = sub.add_parser("execute", parents=[common], help="Plan ausfuehren")
    execute.add_argument("--plan", required=True)
    execute.add_argument("--journal", required=True)
    execute.add_argument("--allow-submit", action="store_true", help="Klicks auf Speichern/Veroeffentlichen erlauben")
    execute.set_defaults(func=cmd_execute)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
