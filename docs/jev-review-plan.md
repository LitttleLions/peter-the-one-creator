# Jev Fast Review Layer — Umsetzungsplan

Status: **geplant, nicht implementiert** (2026-09-21 abends).
Naechster Start: **Phase 0 (Alignment), dann Phase 0.5 (Kill-Test)**.
Offener Posten: [offene-punkte.md](./offene-punkte.md) Punkt 13.
Kein Code, kein Export-Gate, kein OpenRouter in diesem Plan-Stand.

TypeSafe-Docs (nicht raten):
[Introduction](https://docs.typesafe.ai/introduction.md),
[API](https://docs.typesafe.ai/api.md),
[Python SDK](https://docs.typesafe.ai/sdk/python.md),
[State](https://docs.typesafe.ai/concepts/state.md),
[Models](https://docs.typesafe.ai/models.md),
[Jev 1.13 jaggedness](https://docs.typesafe.ai/model-jaggedness/jev-1.13.md).

---

## Erfolgskriterium

Nicht: „Funktioniert Jev?“

Sondern: Erkennt Jev **reale** semantische Fehler in den Motivatier-Sprachpaaren (zuerst RU→DE) zuverlässig genug, dass ein großer Teil der unauffälligen Übersetzung ohne starken LLM-Review passieren kann?

Entscheidende Größen:

- `RECALL_REAL_ERROR` (primär)
- Critical Error Recall
- Escalation Rate
- False Positive Rate auf `REAL_CLEAN`
- Cost per Book / Runtime per Book (erst Shadow-Buchlauf)

Idealfall: sehr hoher Recall echter Fehler + niedrige bis moderate Escalation + sehr geringe Jev-Kosten. Konkrete Schwellen erst nach dem ersten echten Benchmark.

Wirtschaftliches Ziel: erstmals ~100 % der Segmente semantisch vorprüfen und nur Auffällige an den bestehenden (optionalen) Deep-Check geben. Nicht „bestehende Deep-Reviews verbilligen“ — der Deep-Check läuft heute nicht über jedes Segment und nicht im Export-Gate.

```text
DETERMINISTIC QA
       ↓
JEV ON ~100 % OF SEGMENTS
       ↓
      ROUTING
     /       \
 PASS       SUSPICIOUS
               ↓
          STRONG LLM REVIEW
```

---

## Ist-Architektur (unverändert)

```text
translate_chapter.py
  degeneration + 1 Retry
        │
        ▼
review_manuscript.py
  1. review_chapter_deterministic   ← Gate-Input
  2. apply_length_outliers          ← Gate-Input, buchweit
  3. add_llm_findings               ← optional, nie im Export-Gate
  4. write_reports
        │
        ▼
export_manuscript.py::preflight_review_gate
  nur (1)+(2), ERROR>0 → Exit 2
```

Bestehende Schichten:

- **Deterministisch (Gate):** `missing_de_scene`, `cyrillic_in_translation`, `encoding_garbage`, `mojibake`, `accented_transliteration`, `length_ratio`, `paragraph_drop`, `length_outlier`, `degeneration`, `empty_or_short`, `long_sentence`, `duplicate_heading`. Code: [`tools/lib/review_checks.py`](../tools/lib/review_checks.py).
- **Stil, nie ERROR:** `repetition_style` in [`tools/lib/repetition.py`](../tools/lib/repetition.py).
- **LLM Deep-Check (nicht Gate):** ganze Szene, JSON, `meaning|omission|addition|names|register|grammar|formatting`.
- **Translation-Chunks** in [`tools/lib/translation_chunks.py`](../tools/lib/translation_chunks.py) sind nur fürs Übersetzen; nach dem Stitch bleibt `scene-XX.md`. Chunk-`part-YY` ist **keine** Absatzzuordnung.

Jev hängt **nicht** in `review_chapter_deterministic` und **nicht** ins Export-Gate.

---

## Phase 0 — Alignment Inspection

### Was die Pipeline heute wirklich koppelt

Stabile ID gibt es nur auf **Szene**:

- Source: `books/<id>/work/scenes/<source_lang>/<NNN>/scene-XX.md`
- Target: `books/<id>/work/scenes/de/<style>/<NNN>/scene-XX.md`
- Matching: `parse_scene_number` / `find_scene_translations` in [`tools/lib/output_paths.py`](../tools/lib/output_paths.py)

Es gibt **keine** gespeicherten Absatz-IDs, Satz-IDs oder Source-Target-Spans. Review (`paragraph_drop`) zählt Absätze nur szenenweit und erwartet bewusst, dass DE Absätze zusammenzieht.

Beleg für Fehlzuordnung: Peter `001/scene-01` — DE beginnt mit erfundenem Auftakt-Blockquote, RU nicht. Index 0 vs. Index 0 vergleicht Lede mit Handlung. Jev würde `possible_addition` / niedrige Fidelity melden, obwohl das ein bekanntes Editionsmerkmal ist (offene-punkte Klasse 3).

`work/chunks/` mappt nur Übersetzungs-Teile einer **überlangen Szene**, nicht Absatz zu Absatz, und ist nach dem Stitch optional/ephemer.

### Strategie (billig, kein Align-LLM)

```text
SOURCE + TARGET (gleiche scene-id)
      │
      ▼
CHEAP ALIGNMENT CHECK  (Code, $0)
      │
      ├── aligned     → Jev auf Review-Unit
      └── uncertain   → kein Normal-Call
                       größerer Kontext (Szene/Fenster)
                       Risk darf nicht als Übersetzungsfehler zählen
```

Signale, in dieser Reihenfolge, ohne neue KI-Schicht:

1. **Scene membership** (hart, vorhanden)
2. **Paragraph-count ratio** der Szene (schon in `paragraph_drop`; starke Abweichung → unsicher für Index-Paare)
3. **Leading extras** (DE-Blockquote/Lede ohne RU-Pendant → überspringen oder als non-source markieren)
4. **Anchor overlap** im Kandidatenpaar: Glossarnamen, Zahlen (Extraktion in Code)
5. **Paar-length-ratio** vs. Szenen-Median: lokal extrem, Szene normal → eher Misalignment als Raffung
6. Chunk-Metadaten nur als Fallback, nie als Absatz-Truth

Review-Unit bleibt voraussichtlich **Absatz**, aber nur wenn `alignment.status = aligned`. Sonst Fenster oder ganze Szene, gelabelt `uncertain`.

```yaml
alignment:
  status: aligned | uncertain | skipped
  confidence: 0.0-1.0
  method: scene_id | para_index+anchors | scene_window
```

Regel für Auswertung: unsicheres Alignment + hoher Jev-Risk = **kein REAL_ERROR**, höchstens `AMBIGUOUS` / Alignment-Artefakt.

Deliverable Phase 0: kurzer Abschnitt in `docs/jev-review.md` (Alignment-Strategie). Noch kein Framework.

---

## Phase 0.5 — Multilingual Kill Test (vor Infrastruktur)

Klein, live, ohne CLI/Cache/Dashboard. Ein Script, z. B. `tools/jev_kill_test.py`, plus festes JSONL.

Zielgröße ~60–100 Fälle, **nur aligned** (sonst testen wir Alignment, nicht Jev):

- ~20 `REAL_CLEAN` — aktuell gute Peter-Absätze/Kurzfenster mit passender Absatzzahl und Anchors
- ~20 `REAL_ERROR` — historische Fehler: vor allem Raffungs-Backups `*.bak-20260917-*` (z. B. `011/scene-03.md.bak-20260917-103650`) gegen RU; wo nötig kurze Fenster aus der gerafften vs. korrigierten Fassung. Encoding-`.bak-20260916-*` **nicht** als semantischer Goldfehler (das ist Deterministik)
- ~20 kontrollierte Mutationen auf aligned clean Paaren: Negation, Temporal, Name, Halbsatz-Omission, Addition — getrennt als `SYNTHETIC_EASY`

Fragen im Kill-Test (ein Request, atomar):

- `possible_omission` (Noul)
- `possible_addition` (Noul)
- `semantic_contradiction` (Noul)
- `fidelity` (Score 0–4)
- optional `possible_name_problem` nur bei `relevant_names`

API: `jev-1.13.0`, `TYPESAFE_API_KEY`, `--live`, kein OpenRouter. Ohne Key: Script bricht mit klarer Meldung ab (Kill-Test braucht Live).

Report `benchmarks/jev/kill-test-ru-de.md`:

```text
JEV MULTILINGUAL VIABILITY TEST
Language pair: RU → DE
REAL_CLEAN false-positive rate
REAL_ERROR recall          ← führend
SYNTHETIC_EASY recall      ← nur Sanity
Conclusion: GO / QUESTIONABLE / STOP
```

Richtwerte (keine Produktionsgrenzen):

- `RECALL_REAL_ERROR` < ~80 % → **STOP**
- 80–90 % → **QUESTIONABLE** (nachlesen, nicht Framework aufblasen)
- 90–95 % → interessant
- ≥ 95 % → **GO** für Phase 1

### Stop-Regel

Negatives Ergebnis ist valide. Kein Retten durch Prompt-Türme, Wrapper und Heuristiken. Dann:

```text
Jev ist für diesen Motivatier-Classics-Anwendungsfall derzeit nicht geeignet.
```

Bestehende Pipeline bleibt unverändert. Phase 1–5 entfallen.

---

## Jev-API (für Kill-Test und später)

- `POST https://api.typesafe.ai/v1/systemone`
- Auth `TYPESAFE_API_KEY`
- Modell **`jev-1.13.0` pinnen** (nicht `jev-latest`)
- SDK `typesafe-sdk`; Retries eingebaut
- State JSON-Objekt; Fragen parallel
- $0.042 / MTok Input, Output frei; 70–500 ms
- Noul: Float 0–1, keine Confidence
- Score: `score` + `probabilities` + `confidence`
- Docs: Englisch primär — genau deshalb Kill-Test zuerst
- Jev 1.13: nicht zählen/rechnen, State klein halten, atomare Fragen, Komposition im Code

---

## Question Set v1 (`fidelity-v1.yaml`) — nach GO

- `possible_omission` (Noul, immer): relevante Source-Information fehlt im Target
- `possible_addition` (Noul, immer): Target enthält relevante Information, die im Source nicht steht (Editions-Lede separat, nicht als Fehler-Gold)
- `semantic_contradiction` (Noul, immer): Target widerspricht der Source-Bedeutung (Negation, Temporal, Richtung, Geschlecht)
- `entity_reference_problem` (Noul, immer): Person, Sprecher, Pronomen, Ort falsch zugeordnet
- `possible_name_problem` (Noul, nur bei `relevant_names`): Glossarform aus `names.yaml` inkonsistent/falsch
- `possible_context_problem` (Noul, nur mit prev/next): nur aus Nachbarschaft
- `fidelity` (Score 0–4, immer): 0 materially incorrect … 4 faithful

Nicht in v1: `possible_mistranslation`, `possible_meaning_shift`, Encoding, Zahlen, Style (`repetition.py`).

---

## State v1 (nach GO)

- `book.id`, `book.title`, `language.source/target`
- `segment.id` z. B. `peter-i-buch-01/011/03/p012`
- `alignment.status|confidence|method`
- `source.previous|current|next`, `target.previous|current|next` nur bei aligned Absatz-Unit
- `statistics` in Code: Wörter, `length_ratio`
- `relevant_names` gefiltert
- `features.numeric_mismatch` (Code, nicht Jev-Frage)

Context-Flags: `minimal` / `local` (Default) / `enriched`. Local nur nach Alignment.

---

## Routing (nach GO)

v1: `risk = max(error nouls)` plus niedriger Fidelity-Score; unsichere Score-`confidence` → mindestens LIGHT. Global: &lt;0.30 PASS, 0.30–0.60 LIGHT, 0.60–0.85 DEEP, &gt;0.85 MANDATORY.

Config-Form so anlegen, dass später per Kategorie eigene Thresholds möglich sind. Werte entstehen aus der Escalation-Kurve. Keine komplexe Engine vor dem Benchmark.

Fallback Timeout/429/529: Jev skip, Pipeline unverändert. Uncertain alignment: nie automatisch MANDATORY als Übersetzungsfehler.

---

## Phasenfolge (verbindlich)

### Phase 0 — Alignment

Dokumentieren, billigen Check spezifizieren. Kein Jev-Framework.

### Phase 0.5 — Kill Test

~60–100 aligned RU→DE. `RECALL_REAL_ERROR`. GO / QUESTIONABLE / STOP.

### Phase 1 — Infrastruktur (nur GO)

`docs/jev-review.md`, `config/jev_review.yaml`, Question Set, `tools/lib/jev/`, `tools/review_jev.py`, Mock+SDK, Cache, Report, `tests/test_jev_review.py`. `.env.example` `TYPESAFE_API_KEY=`. `typesafe-sdk` in requirements. **Kein** Eingriff in Gate/Dashboard/`review_checks` Severity.

```text
py -3 tools/review_jev.py --book peter-i-buch-01 --style stil-02-poetisch --chapter 011 --mode shadow
py -3 tools/review_jev.py --book peter-i-buch-01 --style stil-02-poetisch --all --live
py -3 tools/benchmark_jev.py --set peter-i-v1
```

Artefakte: `books/<id>/work/reviews/<style>/jev/`. Optionaler Hook in `review_manuscript.py` erst ab Phase 3, nur schreiben, Counts unberührt. Modi `disabled|shadow|advisory|gate`, Default shadow, gate tot bis Phase 5.

### Phase 2 — Benchmark (500–1000)

Klassen: `REAL_ERROR`, `REAL_CLEAN`, `SYNTHETIC_EASY`, `SYNTHETIC_HARD`, `AMBIGUOUS`.

Primär: `RECALL_REAL_ERROR`. Synthetik = Regression/Frageentwicklung.

Produktauswertung: Threshold-/Escalation-Kurve (Recall echter Fehler vs. Escalation Rate vs. FPR). 98 % Recall bei ~22 % Escalation = interessant; 98 % bei 81 % Escalation = Jev bringt wenig.

### Phase 3 — Full Book Shadow

Mindestens ein Werk, kein Gate. Laufzeit, Kosten, Kapitel-Heatmap, Escalation, Cluster.

### Phase 4 — Selective Deep Review Experiment

`Jev → verdächtige Segmente → bestehender LLM-Reviewer`. OpenRouter nur mit Freigabe.

### Phase 5 — Gate Decision

Erst jetzt `shadow` / `advisory` / `gate`. Default bleibt shadow, bis die Kurve überzeugt.

---

## Was bewusst unverändert bleibt

- Shadow Default; kein Export-Gate; bestehende Reviewer bleiben
- Zahlen und Encoding nicht durch Jev
- Kein Dashboard in v1; kein Vercel-Provider nötig
- Direct TypeSafe + Mock; Modellversion pinnen
- Absatz als intendierte Review-Unit **nach Alignment**
- Local Context als Ausgangspunkt
- Fallback auf bestehende Pipeline; Caching; Question-Set-Versionierung
- Kein Zwei-Pass-Jev vor erstem Benchmark
- Kein produktiver Gate-Betrieb ohne Benchmark
- Recommendation in Code, State klein, nicht zählen lassen

---

## Akzeptanz je Phase

**Phase 0:** Alignment-Doku nennt Szene-ID als einzige harte Kopplung und die Lede-Falle.

**Phase 0.5:** Report mit `RECALL_REAL_ERROR` und GO/STOP; ohne Framework.

**Phase 1 (nur GO):** Unittests ohne Key grün; Gate-Regression; Shadow ändert keine Szenen; Key nie geloggt.

**Phase 2:** Kurve + `RECALL_REAL_ERROR` liegen als reproduzierbares JSON/MD unter `benchmarks/jev/`.
