# Perfect Sight Without Glasses

## Buchpaket

Dieses Paket enthält die englische Quelle, die deutsche Übersetzung und die
Exportmetadaten für William Horatio Bates’ *Perfect Sight Without Glasses*.
Die produktive Pipeline bleibt unverändert:

```text
Quelle → Kapitel/Szenen → Übersetzung oder Prompt-Datei → Assembly → Export
```

Kapitelbilder werden erst beim Export aus `assets/chapter/` gelesen. Sie sind
kein Bestandteil der Übersetzung, der Szenen-Dateien oder der Assembly.

## Bildkonfiguration

In [`export.yaml`](export.yaml) ist für dieses Buch festgelegt:

```yaml
illustrations:
  enabled: true
  chapter_images: true
  scene_images: false
  inline_figures:
    enabled: false
```

Das bedeutet:

- Kapitelbilder werden eingebunden, wenn ein passendes
  `assets/chapter/chapter-NNN.*` vorhanden ist.
- Szenenbilder bleiben ausgeschaltet.
- Die 64 Quellabbildungen unter `assets/figures/` werden nicht automatisch als
  Inline-Figuren in den Text eingesetzt.
- Fehlende Kapitelbilder sind unproblematisch; der Export überspringt sie.
- Pro Kapitel wird genau das Asset verwendet, das dem Dateinamen
  `chapter-NNN` entspricht. Bei mehreren Dateien desselben Kapitels sollte nur
  eine aktive Datei verbleiben.

## Aktive Kapitelbild-Zuordnungen

Die redaktionellen Zuordnungen stehen in:

[`assets/figures/placements.yaml`](assets/figures/placements.yaml)

Aktuell sind sieben historische Dokumentar-/Porträt-/Untersuchungsmotive für
die Kapitel 002, 003, 004, 007, 028, 031 und 032 aktiviert. Die Dateien unter
`assets/chapter/` sind Kopien der jeweiligen Originalscans aus
`assets/figures/`; die Originale werden nicht verändert.

Die Datei bleibt zunächst im Status `draft` und dient zugleich als nachvoll-
ziehbares Redaktionsprotokoll: Kapitel-ID, Quellabbildung, Scan-Seite,
Exportpfad und Begründung sind dort festgehalten. Die Scan-Seite ist nur
Kontext und darf nicht als Kapitelnummer interpretiert werden.

## Neue Kapitelbilder hinzufügen

1. Kapitelüberschrift in `work/chapters/NNN-source.md` prüfen.
2. Motiv im Bildinventar `assets/figures/analysis-report.md` und im
   `assets/figures/manifest.yaml` prüfen.
3. Nur ein geeignetes dokumentarisches Motiv auswählen; Diagramme,
   schematische Tafeln und reine Messgrafiken bleiben aus der Kapitelbild-
   Auswahl ausgeschlossen.
4. Original nach `assets/chapter/chapter-NNN.<ext>` kopieren. Unterstützte
   Formate sind `.jpg`, `.jpeg`, `.png` und `.webp`.
5. Die Zuordnung in `assets/figures/placements.yaml` ergänzen.
6. Export zunächst als EPUB-Dry-run oder Prüfexport ausführen:

```powershell
python tools/export_manuscript.py --book perfect.sight `
  --scope book --style stil-05-sachbuch --format epub --allow-partial
```

Die Ausgabe muss das Kapitelbild als `chapter-illustration` enthalten. Die
Bilddatei kann im EPUB unter einem vom Exporter vergebenen Namen liegen.

## Kandidaten-Generierung

Für optionale Higgsfield-Kandidaten gibt es das buchlokale Hilfswerkzeug:

```powershell
python tools/generate_perfect_sight_figure_candidate.py `
  --figure figure-013 --profile historical-illustration --dry-run
```

Der Dry-run schreibt nur eine Prompt-Datei nach
`work/prompts/figures/`. Er ersetzt niemals ein Original automatisch. Eine
echte Generierung benötigt die konfigurierte Higgsfield-Authentifizierung und
ist bewusst von der Exportfreigabe getrennt.

## Rückwärtskompatibilität und Sicherheitsregeln

- `translate_chapter.py`, `translate_batch.py`, alle Provider
  (`openrouter`, `ollama`, `prompt_file`, `workspace_ai`) und
  `assemble_chapter.py` lesen die Kapitelbilder nicht.
- DOCX, EPUB und PDF verwenden dieselbe optionale Kapitelbild-Erkennung; bei
  deaktivierten Illustrationen oder fehlenden Assets bleibt der bisherige
  Text-/Cover-Export erhalten.
- `scene_images: false` verhindert zusätzliche Szenenbilder.
- `inline_figures.enabled: false` verhindert, dass die 64 importierten
  Abbildungen in Übersetzungs- oder Exporttext eingefügt werden.
- Diese `placements.yaml` darf nicht allein durch Setzen von
  `inline_figures.enabled: true` aktiviert werden. Inline-Figuren verwenden
  ein anderes, bestätigungsbasiertes Schema (`figure_id`, `scene_number`,
  `after_paragraph`, `confirmed`). Eine spätere Inline-Freigabe braucht daher
  eine eigene Schema-Prüfung und einen separaten Testexport.
- Keine Dateien unter `source/` und keine Originaldateien unter
  `assets/figures/` löschen, umbenennen oder überschreiben.

## Prüfkommandos

YAML und aktive Assets prüfen:

```powershell
@'
from pathlib import Path
import yaml

root = Path('books/perfect.sight')
export = yaml.safe_load((root / 'export.yaml').read_text(encoding='utf-8'))
placements = yaml.safe_load(
    (root / 'assets/figures/placements.yaml').read_text(encoding='utf-8')
)
illustrations = export['defaults']['illustrations']
assert illustrations['enabled'] is True
assert illustrations['chapter_images'] is True
assert illustrations['inline_figures']['enabled'] is False
items = placements['placements']
assert len({str(item['chapter_id']) for item in items}) == len(items)
assert all((root / item['export_path']).is_file() for item in items)
print(f'{len(items)} eindeutige Kapitelbilder validiert')
'@ | python -
```

Ein fehlendes `pytest` verhindert keinen Export; für die allgemeine Test-Suite
muss `pytest` gemäß `requirements.txt` in der virtuellen Umgebung installiert
sein.