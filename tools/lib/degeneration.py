"""
degeneration.py
===============
Erkennt "Degeneration" in LLM-Outputs - Symptome, die darauf hindeuten,
dass das Modell in eine kaputte Generierungs-Schleife geraeten ist:

1. Token-Loop: dasselbe Wort >= 10x hintereinander
2. Phrasen-Loop: gleiche Wortgruppe (2-5 Woerter) >= 7x hintereinander
3. Single-Token-Spam: ein einzelnes Wort macht > 25% des Texts aus
4. Mojibake-Cluster: nicht-druckbare Zeichen / Ersatzzeichen
5. Endlos-Satz: > 300 Woerter ohne Satzendzeichen
6. Sprach-Mismatch: erwartete Sprache (z. B. Deutsch) stimmt nicht
   mit Output ueberein (Modell driftet z. B. ins Englische ab)

Unicode-aware: nutzt \\p{L} statt \\w, damit deutsche Umlaute
(ae, oe, ue, ss) korrekt als Wortbestandteile erkannt werden.

Python-Port der JS-Funktion `detectDegeneration()` aus dem
OpenRouter-Snippet des Nutzers.

Verwendung:
    from lib.degeneration import detect_degeneration

    result = detect_degeneration(text, expected_language="deutsch")
    if not result["ok"]:
        print(f"Degeneration: {result['reason']}")
"""

from __future__ import annotations

import re
from typing import Optional, TypedDict, Union


# Sprach-Stoppwoerter-Tabelle (Funktionswoerter, die in normaler Prosa
# haeufig vorkommen). Genutzt fuer den Sprach-Mismatch-Check.
STOP_WORDS: dict[str, list[str]] = {
    "deutsch": [
        "der", "die", "das", "und", "ist", "nicht", "ein", "eine",
        "den", "dem", "des", "mit", "von", "auf", "fuer", "auch",
        "als", "war", "sich", "aber", "noch", "schon", "wenn", "wie",
        "nur", "doch", "ich", "sie", "er", "wir", "ihr",
    ],
    "english": [
        "the", "and", "is", "of", "to", "in", "that", "with", "for",
        "was", "are", "but", "not", "his", "her", "they", "this",
        "from", "have", "had", "she", "would", "could", "been", "were",
        "their", "which", "about",
    ],
    "francais": [
        "le", "la", "les", "une", "des", "que", "pas", "pour", "sur",
        "avec", "dans", "elle", "qui", "mais", "comme", "tout", "plus",
        "etait", "sont",
    ],
    "espanol": [
        "que", "los", "las", "una", "por", "con", "para", "como",
        "mas", "pero", "todo", "esta", "son", "este", "esta", "cuando",
    ],
    "italiano": [
        "che", "non", "per", "con", "una", "sono", "questo", "questa",
        "molto", "anche", "quando", "come", "tutto",
    ],
    "russisch": [
        # Cyrillic Stopwords (vereinfachte Auswahl)
        "\u0438", "\u0432", "\u043d\u0435", "\u043d\u0430", "\u044f",
        "\u0447\u0442\u043e", "\u043e\u043d", "\u0441", "\u043a\u0430\u043a",
        "\u0430", "\u0435\u0433\u043e", "\u043d\u043e", "\u043e\u043d\u0430",
    ],
}

# Aliase: "german" -> "deutsch" etc.
LANG_ALIASES: dict[str, str] = {
    "deutsch": "deutsch", "german": "deutsch", "de": "deutsch",
    "english": "english", "englisch": "english", "en": "english",
    "francais": "francais", "french": "francais", "franzoesisch": "francais", "fr": "francais",
    "espanol": "espanol", "spanish": "espanol", "spanisch": "espanol", "es": "espanol",
    "italiano": "italiano", "italian": "italiano", "italienisch": "italiano", "it": "italiano",
    "russisch": "russisch", "russian": "russisch", "ru": "russisch",
}


# Unicode-Wort-Regex: \p{L} matched alle Buchstaben inkl. Umlaute und Cyrillic.
# Python 3.7+ unterstuetzt dies mit dem `regex`-Modul, in stdlib via
# `re` mit `re.UNICODE` aber ohne \p{L}. Wir nutzen daher eine
# pragmatische Variante: alle Unicode-Buchstaben via `str.isalpha()`-Filter.
_LETTER_RE = re.compile(r"\w{2,30}", re.UNICODE)
_PHRASE_RE = re.compile(
    r"(\w+(?:[\s,.;:!?\-\u2013\u2014]+\w+){1,4})"
    r"(?:[\s,.;:!?\-\u2013\u2014]+\1){6,}",
    re.UNICODE,
)
_WORD_RE = re.compile(r"\w{3,}", re.UNICODE)
# Nicht-druckbare / Replacement-Char-Cluster (3+ in Folge)
_MOJIBAKE_RE = re.compile("[\uFFFD\u0000-\u0008\u000B-\u001F]{3,}")
# Satzendezeichen
_SENT_END_RE = re.compile(r"[.!?:;\u2013\u2014\n]+")


class DegenerationResult(TypedDict, total=False):
    ok: bool
    reason: str


def _normalize_lang(lang: str) -> Optional[str]:
    if not lang:
        return None
    return LANG_ALIASES.get(lang.strip().lower())


def _extract_words(text: str) -> list[str]:
    return [w.lower() for w in _WORD_RE.findall(text)]


def detect_degeneration(
    text: str,
    expected_language: Optional[str] = None,
) -> Union[DegenerationResult, dict]:
    """
    Prueft `text` auf Degeneration. Liefert entweder
    `{"ok": True}` oder `{"ok": False, "reason": "..."}`.
    """
    if not text or len(text.strip()) < 50:
        return {"ok": False, "reason": "Text ist leer oder zu kurz (< 50 Zeichen)."}

    # 1. Token-Loop (>= 10x dasselbe Wort)
    #    Da stdlib re kein \p{L} kennt, nehmen wir \w mit UNICODE.
    #    Wortgrenzen sind \b, aber \b in stdlib versteht kein Unicode;
    #    daher nutzen wir die explizite Form mit [^\w]-Lookarounds.
    loop = re.search(
        r"(\w{2,30})(?:[^\w]+\1){9,}",
        text,
        flags=re.UNICODE,
    )
    if loop:
        word = loop.group(1)
        return {
            "ok": False,
            "reason": (
                f"Wiederholungsschleife erkannt - das Wort \"{word}\" "
                f"wurde mindestens 10x hintereinander generiert. "
                f"Das Modell ist in einer Degeneration-Schleife gefangen."
            ),
        }

    # 2. Phrasen-Loop (>= 7x dieselbe 2-5-Wort-Gruppe)
    phrase = _PHRASE_RE.search(text)
    if phrase:
        return {
            "ok": False,
            "reason": (
                "Phrasen-Wiederholungsschleife erkannt - die gleiche "
                "Wortgruppe wurde mehr als 7x hintereinander generiert."
            ),
        }

    # 3. Single-Token-Spam (>= 25% des Texts)
    words = _extract_words(text)
    if len(words) > 100:
        counts: dict[str, int] = {}
        for w in words:
            counts[w] = counts.get(w, 0) + 1
        max_word = max(counts, key=counts.get)
        max_count = counts[max_word]
        ratio = max_count / len(words)
        if ratio > 0.25 and max_count > 30:
            return {
                "ok": False,
                "reason": (
                    f"UEbermaessige Wiederholung des Wortes \"{max_word}\" "
                    f"({max_count}x = {ratio*100:.0f}% aller Woerter). "
                    f"Modell-Output ist degeneriert."
                ),
            }

    # 4. Mojibake / nicht-druckbare Cluster
    garbage = _MOJIBAKE_RE.search(text)
    if garbage:
        return {
            "ok": False,
            "reason": (
                "Nicht-druckbare Zeichen (Muell-Bytes) im Text - "
                "Modell-Output ist beschaedigt."
            ),
        }

    # 5. Endlos-Satz (> 300 Woerter ohne Satzendezeichen)
    for segment in _SENT_END_RE.split(text):
        seg_words = [w for w in segment.split() if w]
        if len(seg_words) > 300:
            return {
                "ok": False,
                "reason": (
                    f"Endlos-Satz erkannt - {len(seg_words)} Woerter "
                    f"ohne Satzendzeichen. Das Modell ist in einen "
                    f"Word-Salad-Modus gefallen."
                ),
            }

    # 6. Sprach-Mismatch
    if expected_language and len(words) > 80:
        key = _normalize_lang(expected_language)
        if key and key in STOP_WORDS:
            expected_set = set(STOP_WORDS[key])
            english_set = set(STOP_WORDS["english"])
            expected_hits = sum(1 for w in words if w in expected_set)
            english_hits = sum(1 for w in words if w in english_set)
            # Drift ins Englische
            if key != "english" and english_hits > expected_hits * 3 and english_hits > 20:
                return {
                    "ok": False,
                    "reason": (
                        f"Sprach-Mismatch erkannt - erwartet wurde "
                        f"{expected_language}, aber der Output enthaelt "
                        f"ueberwiegend englische Funktionswoerter "
                        f"({english_hits}x vs. {expected_hits}x "
                        f"{expected_language}). Das Modell ist in eine "
                        f"andere Sprache gedriftet."
                    ),
                }
            # Generell zu wenige Treffer der Zielsprache
            if expected_hits / len(words) < 0.01 and len(words) > 200:
                return {
                    "ok": False,
                    "reason": (
                        f"Sprach-Mismatch erkannt - nur {expected_hits} "
                        f"{expected_language}-Funktionswoerter in "
                        f"{len(words)} Woertern Text. Der Output ist "
                        f"vermutlich in einer anderen Sprache."
                    ),
                }

    return {"ok": True}


# Mini-Self-Test
if __name__ == "__main__":
    # Normal
    r1 = detect_degeneration(
        "Der Vater spannte das Pferd an. Die Kinder rannten hinterher. "
        "Es war eisig kalt und der Schnee knirschte unter ihren Fuessen.",
        expected_language="deutsch",
    )
    print("Normal:", r1)

    # Loop
    r2 = detect_degeneration("hallo hallo hallo hallo hallo hallo hallo hallo hallo hallo hallo")
    print("Loop:", r2)

    # Drift
    r3 = detect_degeneration(
        ("The " * 200) + "father was cold.",
        expected_language="deutsch",
    )
    print("Drift:", r3)
