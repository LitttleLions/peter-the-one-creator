"""repetition.py - Stil-Wiederholungsdetektor fuer DE-Szenen (report-only).

Erkennt gehaeufte literarische Wiederholungen in selbst erstellten
deutschen Originaltexten (z. B. "Die dritte Chronik"). Der bisherige
deterministische Regelcheck (long_sentence > 180/300,
degeneration-Loops) ist blind fuer variierte Wiederholung: Anaphern
("Er las ... Er las ..."), Wort-Echos ("schwerer ... schweres") und
Konjunktions-Stapelung ("bevor ... bevor ... bevor ...").

Sechs Signale, alle rein deterministisch und kostenlos:
1. Anapher, 2. Trigramm-Cluster, 3. Wort-Echo, 4. Stapelung,
5. TTR-Wortschatzarmut, 6. Leerformel "immer wieder".

Schwere: INFO default, WARNING erst bei starken Haeufungen,
niemals ERROR (kein Release-Gate-Effekt). Das Modul aendert nie
Texte und importiert nie aus review_checks (kein Zyklus): es liefert
reine Dicts, die review_checks in Findings wrappt.
"""

from __future__ import annotations

import re
from collections import Counter
from typing import Any

CATEGORY = "repetition_style"

WORD_RE = re.compile(r"[^\W\d_]+", re.UNICODE)
PARA_SPLIT_RE = re.compile(r"\n\s*\n")
SENT_END_RE = re.compile(r"[.!?;:\n]+")
FORMULA_RE = re.compile(r"\bimmer\s+wieder\b", re.IGNORECASE)

STOP = frozenset({
    "der", "die", "das", "den", "dem", "des", "ein", "eine", "einer",
    "einem", "einen", "eines", "und", "oder", "aber", "denn", "doch",
    "nur", "auch", "noch", "schon", "sehr", "als", "wie", "so", "zu",
    "zum", "zur", "im", "in", "am", "an", "auf", "aus", "bei", "mit",
    "von", "vor", "nach", "ueber", "unter", "durch", "fuer", "ohne",
    "gegen", "um", "ist", "sind", "war", "waren", "wird", "werden",
    "wurde", "wurden", "hat", "hatte", "hatten", "haben", "sein",
    "bin", "bist", "warst", "seid", "nicht", "kein", "keine",
    "keinen", "keiner", "keines", "ich", "du", "er", "sie", "es",
    "wir", "ihr", "mich", "dich", "sich", "uns", "euch", "mir",
    "dir", "ihm", "ihnen", "mein", "dein", "unser", "euer", "dass",
    "weil", "wenn", "bevor", "wer", "wen", "wem", "was", "wo",
    "dort", "hier", "da", "dann", "nun", "wieder", "immer", "nie",
    "nichts", "alles", "jeder", "jede", "jedes", "jedem", "jeden",
    "man", "etwas",
})

STACKING = frozenset({
    "bevor", "wenn", "weil", "wer", "wen", "wem", "dass", "denn",
    "oder", "als", "wie", "immer", "wieder", "nie", "nichts",
    "alles", "jeder", "jede", "jedes", "ohne", "ausser",
    "sondern", "bis",
})

ANAPHORA_INFO_MIN_RUN = 4
ANAPHORA_WARN_MIN_RUN = 7
TRIGRAM_WINDOW = 500
TRIGRAM_INFO_MIN = 5
TRIGRAM_PARA_MIN = 4
MAIN_CONTENT_MIN_LEN = 6
ECHO_WINDOW = 30
ECHO_STEP = 15
ECHO_INFO_MIN = 4
ECHO_WARN_MIN = 6
STACKING_INFO_MIN = 8
STACKING_WARN_MIN = 12
TTR_CHAPTER_MIN_WORDS = 200
TTR_CHAPTER_INFO = 0.25
TTR_PARA_MIN_WORDS = 80
TTR_PARA_INFO = 0.35
TTR_PARA_MAX_REPORTS = 2
FORMULA_INFO_MIN = 3
FORMULA_WARN_MIN = 6
MAX_FINDINGS_PER_SCENE = 6


def tokenize(text: str) -> list[str]:
    """Wort-Token (Original-Schreibung) eines Texts."""
    return WORD_RE.findall(text)


def normalize_key(word: str) -> str:
    """Vergleichsform: kleingeschrieben, eine Flexionsendung gestrippt."""
    low = word.lower()
    if len(low) >= 6:
        if low.endswith(("erem", "eren")):
            return low[:-4]
        if low.endswith(("ern", "em", "en", "er", "es")):
            return low[:-2]
        if low.endswith("e"):
            return low[:-1]
    return low


# Verbfamilien, deren Echo gewollt-liturgisch sein kann ("enthalten
# ... enthalten ... enthalten" im Inventar-Stil von Kap. 008). Diese
# Staemme melden wir nur als INFO und nur bei starker Haeufung.
# "word" faengt word/Worte/Worten/worden-Gemisch (Stemmer trennt
# Umlautformen nicht) — gleiche Behandlung: nur INFO, nie WARNING.
LITANY_VERBS = frozenset({
    "enthalt", "word", "worte", "wort", "sein", "hab", "hatt",
    "werd", "wurd", "wird", "mach", "getan", "gegang", "gekomm",
    "geblieb", "geword", "nehm", "genomm", "geb", "gegeb",
    "geseh", "gewusst", "gedacht", "gesagt", "gesproch",
    "gefragt",
})


def paragraphs(text: str) -> list[str]:
    """Nicht-leere Absaetze ohne reine Markdown-Headings."""
    out = []
    for part in PARA_SPLIT_RE.split(text.strip()):
        stripped = part.strip()
        if not stripped:
            continue
        if all(
            line.strip().startswith("#") or not line.strip()
            for line in stripped.splitlines()
        ):
            continue
        out.append(stripped)
    return out


def head_words(para: str, count: int = 2) -> str:
    """Erste Vergleichswoerter eines Absatzes (Satzzeichen frei)."""
    found = [w.lower() for w in tokenize(para) if len(w) >= 2]
    return " ".join(found[:count])


def anaphora_findings(text: str) -> list[dict[str, Any]]:
    """Gleiche Absatzanfaenge in Folge: 4-6x INFO, >= 7x WARNING."""
    paras = paragraphs(text)
    heads = [head_words(p) for p in paras]
    findings: list[dict[str, Any]] = []
    idx = 0
    while idx < len(heads):
        if not heads[idx]:
            idx += 1
            continue
        end = idx + 1
        while end < len(heads) and heads[end] == heads[idx]:
            end += 1
        run = end - idx
        if run >= ANAPHORA_INFO_MIN_RUN:
            sev = "WARNING" if run >= ANAPHORA_WARN_MIN_RUN else "INFO"
            advice = (
                "Anapher stark gehaeuft: kuerzen oder variieren."
                if sev == "WARNING"
                else "Anapher pruefen: Stilmittel oder variieren."
            )
            findings.append({
                "severity": sev,
                "message": (
                    f"Anapher '{heads[idx]}' {run}x hintereinander "
                    f"(Absaetze {idx + 1}-{end})."
                ),
                "evidence": " / ".join(
                    p.replace("\n", " ")[:120] for p in paras[idx:end]
                )[:500],
                "recommendation": advice,
            })
        idx = end
    return findings


def trigram_findings(
    all_words: list[str],
    paras: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Gleiches Inhaltswort-Tripel >= 4x im Absatz, ungleich verteilt.

    Absatzlokal + alle 3 Woerter >= 5 Zeichen/nicht STOP (sonst zaehlt
    jeder Standard-Satzanfang). Zusaetzlich ungleiche Verteilung ueber
    die Absatzdrittel: Bei Test-Loops ("Satz X Nummer N" 65x) steht in
    jedem Drittel gleich viel; echte Leitmotive clustern. Kriterium:
    max(Drittel) >= 2 * min(Drittel) oder min == 0.
    """
    sources = paras if paras is not None else [" ".join(all_words)]
    seen: dict[str, int] = {}
    order: list[str] = []
    for para in sources:
        low = [w.lower() for w in tokenize(para)]
        if len(low) < 12:
            continue
        thirds = [0, len(low) // 3, 2 * len(low) // 3, len(low)]
        positions: dict[str, list[int]] = {}
        for k in range(len(low) - 2):
            tri = tuple(low[k:k + 3])
            if not all(
                t not in STOP and len(t) >= 5 for t in tri
            ):
                continue
            positions.setdefault(" ".join(tri), []).append(k)
        for key, pos in positions.items():
            if len(pos) < 4 or key in seen:
                continue
            per_third = [
                sum(1 for p in pos if thirds[i] <= p < thirds[i + 1])
                for i in range(3)
            ]
            hi, lo = max(per_third), min(per_third)
            if lo > 0 and hi < 2 * lo:
                continue
            seen[key] = len(pos)
            order.append(key)
    findings: list[dict[str, Any]] = []
    for key in sorted(order, key=lambda k: -seen[k])[:3]:
        findings.append({
            "severity": "INFO",
            "message": (
                f"Leitmotiv-Tripel '{key}' {seen[key]}x in einem Absatz."
            ),
            "evidence": f"'{key}' {seen[key]}x",
            "recommendation": (
                "Formulierung streuen oder als Leitmotiv markieren."
            ),
        })
    return findings

def is_main_content(word: str) -> bool:
    """Echte Inhaltswoerter: lang, nicht STOP, keine Zaehlnummern.

    Testsaetze wie "Deutscher Satz der Uebersetzung Nummer 12" bestehen
    aus solchen Woertern und wuerden jeden Detektor triggern — sie
    werden ueber die Unverteiltheit (Echo-Spread, Trigramm-Drittel)
    ausgeschlossen, nicht ueber die Wortliste.
    """
    low = word.lower()
    return (
        low not in STOP and len(low) >= MAIN_CONTENT_MIN_LEN
        and not low.isdigit()
    )


def echo_findings(all_words: list[str]) -> list[dict[str, Any]]:
    """Gleicher Stamm in 30 Woertern: >= 5x INFO, >= 8x WARNING.

    Nur Haupt-Inhaltswoerter (>= 6 Zeichen) + Verteilung ueber
    >= 4 Fenster: uniforme Testsaetze ("deutsch/satz/uebersetzung"
    in jedem Fenster) erreichen Spread 20, aber echte Szenen haben
    variierende Fensterinhalte — dort clustert ein Echo auf wenige
    Fenster. Zusaetzlich: Die Top-Fenster muessen sich inhaltlich
    unterscheiden (sonst Loop). Vereinfacht: max. 1 Echo-Meldung,
    nur wenn der Stamm NICHT in jedem Fenster gleich oft steht
    (Std-Abweichung der Fenster-Zaehler > 0).
    """
    low = [w.lower() for w in all_words]
    keys = [normalize_key(w) if is_main_content(w) else "" for w in low]
    counts_per_window: dict[str, list[int]] = {}
    step = 15
    size = 30
    for start in range(0, max(1, len(keys) - size + 1), step):
        window = [k for k in keys[start:start + size] if k]
        for key, count in Counter(window).items():
            if count >= 5:
                counts_per_window.setdefault(key, []).append(count)
    findings: list[dict[str, Any]] = []
    for key, series in sorted(
        counts_per_window.items(), key=lambda i: -max(i[1])
    ):
        if len(series) < 2:
            continue
        mean = sum(series) / len(series)
        var = sum((c - mean) ** 2 for c in series) / len(series)
        if var == 0:
            continue
        top = max(series)
        if key in LITANY_VERBS:
            if top < 10 or len(series) < 4:
                continue
            findings.append({
                "severity": "INFO",
                "message": (
                    f"Inventar-Echo '{key}' {top}x in 30 Woertern "
                    f"({len(series)}x verteilt) — Litanei-Stil, Hinweis."
                ),
                "evidence": (
                    f"'{key}' {top}x / 30 Woerter "
                    f"(Inventar-Stil, Kap. 008: 'enthalten ... enthalten')"
                ),
                "recommendation": "Inventar-Stil: nur Hinweis.",
            })
            if len(findings) >= 3:
                break
            continue
        sev = "WARNING" if top >= 8 else "INFO"
        findings.append({
            "severity": sev,
            "message": (
                f"Wort-Echo '{key}' {top}x in 30 Woertern "
                f"({len(series)}x verteilt)."
            ),
            "evidence": f"'{key}' {top}x / 30 Woerter",
            "recommendation": "Wort-Echo pruefen: variieren.",
        })
        if len(findings) >= 3:
            break
    return findings


def stacking_findings(text: str) -> list[dict[str, Any]]:
    """Bindewort-Stapelung pro Satzsegment: >= 8x INFO, >= 12x WARNING."""
    findings: list[dict[str, Any]] = []
    for segment in SENT_END_RE.split(text):
        low = [w.lower() for w in tokenize(segment)]
        if len(low) < 10:
            continue
        hits = [w for w in low if w in STACKING]
        if len(hits) < 8:
            continue
        sev = "WARNING" if len(hits) >= 12 else "INFO"
        top = Counter(hits).most_common(3)
        findings.append({
            "severity": sev,
            "message": (
                f"Stapelung ({len(hits)}x: "
                f"{', '.join(f'{w} {n}x' for w, n in top)}) "
                f"in {len(low)} Woertern ohne Satzende."
            ),
            "evidence": " ".join(segment.split())[:500],
            "recommendation": "Schachtelsatz gliedern.",
        })
    findings.sort(key=lambda item: item["severity"] != "WARNING")
    return findings[:3]


def ttr_findings(text: str) -> list[dict[str, Any]]:
    """Wortschatzarmut: Kapitel-TTR < 0.25, Absatz-TTR < 0.35 -> INFO.

    Nur fuer echte Prosa: min. 15 verschiedene Inhaltswoerter
    (>= 6 Zeichen) und min. 3 verschiedene Saetze (sonst meldet
    jeder uniforme Test-Loop "Wortschatzarmut").
    """
    findings: list[dict[str, Any]] = []
    words = [w.lower() for w in tokenize(text)]
    content_types = {w.lower() for w in words if is_main_content(w)}
    sentences = [s for s in SENT_END_RE.split(text) if s.strip()]
    if (
        len(words) >= 200
        and len(content_types) >= 15
        and len(sentences) >= 3
    ):
        ttr = len(set(words)) / len(words)
        if ttr < 0.25:
            findings.append({
                "severity": "INFO",
                "message": (
                    f"Kapitel-TTR {ttr:.2f} bei {len(words)} Woertern."
                ),
                "evidence": f"TTR={ttr:.2f}, Woerter={len(words)}",
                "recommendation": "Wortschatzarmut pruefen.",
            })
    reported = 0
    for idx, para in enumerate(paragraphs(text)):
        para_words = [w.lower() for w in tokenize(para)]
        if len(para_words) < 80:
            continue
        para_content = {w for w in para_words if is_main_content(w)}
        para_sentences = [s for s in SENT_END_RE.split(para) if s.strip()]
        if len(para_content) < 12 or len(para_sentences) < 2:
            continue
        ttr = len(set(para_words)) / len(para_words)
        if ttr < 0.35:
            findings.append({
                "severity": "INFO",
                "message": (
                    f"Absatz {idx + 1}: TTR {ttr:.2f} bei "
                    f"{len(para_words)} Woertern."
                ),
                "evidence": para.replace("\n", " ")[:500],
                "recommendation": "Wortschatzarmut pruefen.",
            })
            reported += 1
            if reported >= 2:
                break
    return findings


def formula_findings(text: str) -> list[dict[str, Any]]:
    """Leerformel 'immer wieder': >= 3x INFO, >= 6x WARNING."""
    count = len(FORMULA_RE.findall(text))
    if count < 3:
        return []
    sev = "WARNING" if count >= 6 else "INFO"
    return [{
        "severity": sev,
        "message": f"Leerformel 'immer wieder' {count}x in einer Szene.",
        "evidence": f"'immer wieder' {count}x",
        "recommendation": "Leerformel dosieren.",
    }]

def text_without_headings(text: str) -> str:
    """Szenentext ohne Markdown-Headings (verfaelschen Statistik)."""
    lines = [
        line for line in text.splitlines()
        if not line.strip().startswith("#")
    ]
    return "\n".join(lines).strip()


def repetition_scene_findings(
    chapter_id: str,
    scene_num: int,
    de_text: str,
) -> list[dict[str, Any]]:
    """Alle sechs Signale fuer eine DE-Szene, WARNING zuerst, max. 6.

    Erlaubt ist auch de_text="" (Test-/Import-Kontext): dann leer.
    Niemals ERROR.
    """
    _ = (chapter_id, scene_num)
    clean = text_without_headings(de_text)
    words = tokenize(clean)
    if len(words) < 30:
        return []
    out: list[dict[str, Any]] = []
    paras = paragraphs(clean)
    out.extend(anaphora_findings(clean))
    out.extend(trigram_findings(words, paras))
    out.extend(echo_findings(words))
    out.extend(stacking_findings(clean))
    out.extend(ttr_findings(clean))
    out.extend(formula_findings(clean))
    out.sort(key=lambda item: item["severity"] != "WARNING")
    return out[:6]
