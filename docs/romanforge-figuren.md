# RomanForge-Figuren in peter (Spiegel und Abgleich)

Stand: 2026-11-09 (Aussehen folgt RomanForge, Tabelle `--aussehen`). Gilt nur fuer Buecher, die in RomanForge als eigenes Original entstehen. Uebersetzungen fremder Vorlagen haben keine RomanForge-Figuren und bleiben unberuehrt.

## Idee

RomanForge fuehrt die Figuren-Stammdaten der Quellsprache (Name, Rolle, Aussehen). Jede Figur hat dort eine stabile `uid`, die auch beim Neu-Import oder Neu-Extrahieren erhalten bleibt. peter liest die Figuren aus der Uebergabe, legt sie als Spiegel im Buchpaket ab und gleicht sie mit `names.yaml` ab. Es gibt keine zweite Pflege derselben Daten.

## Dateien

| Datei | Zweck | Bearbeiten |
|---|---|---|
| `books/<id>/romanforge/characters.json` | Spiegel des letzten Abrufs (Format `romanforge-characters/1`) | nie von Hand, wird erzeugt |
| `books/<id>/names.yaml` | Namen, Zielformen, Aliase, Bild-Prompt | Peter-Felder von Hand, RomanForge-Felder nur ueber das Werkzeug |

## Wem welches Feld gehoert

| Feld in `names.yaml` | Eigentuemer | Verhalten beim Abgleich |
|---|---|---|
| `source`, `rf_uid`, `rf_appearance_sha` | RomanForge | wird gesetzt bzw. nachgezogen |
| `target`, `aliases`, `type`, `note`, `status` | peter | wird nie ueberschrieben |
| `visual` (Bild-Prompt) | peter, mit Ausnahme | wird nie ueberschrieben, **ausser** es ist leer oder noch unberuehrt (Hash von `visual` == `rf_appearance_sha`): dann folgt es dem geaenderten Aussehen aus RomanForge. Von Hand angepasstes `visual` bleibt |
| `rf_visual_check: true` | Werkzeug | Hinweis, dass das Aussehen in RomanForge geaendert wurde, `visual` aber von Hand angepasst ist; nach Pruefung von Hand entfernen (verschwindet, wenn `visual` wieder folgt) |

Eintraege ohne `rf_uid` (Orte, Begriffe, peter-eigene) bleiben unberuehrt.

## Ablauf

Immer zuerst der Trockenlauf (zeigt nur eine Tabelle):

```text
.\.venv\Scripts\python.exe tools/sync_romanforge_characters.py --book <id> --handoff <uebergabe-id>
```

Danach mit `--apply` uebernehmen. Der Trockenlauf gehoert nach jeder Uebernahme aus RomanForge zum Ablauf (auch bei unveraenderten Figuren); `--apply` ist die einzige Freigabe, die dann noch fehlt.

Gegenueberstellung fuer die Bilderzeugung (schreibt nichts):

```text
.\.venv\Scripts\python.exe tools/sync_romanforge_characters.py --book <id> --aussehen
```

Sie zeigt je Figur die Zeichenzahl des Aussehens in RomanForge und von `visual` sowie den Stand (`gleich`, `folgt RomanForge`, `weicht ab (von Hand)`, `visual leer`, `nur in peter`, `fehlt in beiden`, `nicht verknuepft`). Die Bildgenerierung nutzt `visual` fuer bis zu drei Figuren, die im Szenentext vorkommen; eine Figur ohne `visual` erscheint ohne Beschreibung. Ohne `--handoff` nutzt das Werkzeug den vorhandenen Spiegel, mit `--snapshot datei.json` eine lokale Handoff-Datei (offline).

Neues Buch: `import_markdown_original.py --new --handoff <id>` legt Spiegel und `names.yaml` (Eintraege mit `status: draft`) gleich mit an.

Aktionen der Tabelle:

| Aktion | Bedeutung |
|---|---|
| `neu` | Figur ist neu in RomanForge: neuer Eintrag `draft`, `visual` aus dem Aussehen vorbefuellt, `target` = `source` nur wenn Quell- und Zielsprache gleich sind |
| `verknuepfen` | einmaliger Abgleich eines Eintrags ohne `rf_uid` ueber Name oder Alias (nur bei genau einem Treffer) |
| `umbenannt` | gleiche `uid`, neuer Name: nur `source` wird nachgezogen, `target` und `aliases` pruefen |
| `aussehen-nachgezogen` | Aussehen in RomanForge geaendert oder erstmals vorhanden und `visual` war leer oder unberuehrt: `visual` uebernimmt das neue Aussehen |
| `aussehen-geaendert` | Aussehen in RomanForge geaendert, `visual` aber von Hand angepasst: `visual` bleibt, Hinweis `rf_visual_check` |
| `in-romanforge-geloescht` | Figur fehlt in RomanForge: Eintrag bleibt (Bilder haengen daran), `status: removed_in_rf` |
| `konflikt` | zwei Figuren gleichen Namens oder mehrdeutiger Treffer: wird nicht automatisch zugeordnet, Exit-Code 1 |

## Grenzen

- Nur Figuren der Quellsprache; keine Glossar-Begriffe, keine Zielsprachen-Namen aus RomanForge.
- Rueckschreiben von Bild-/Zielfeldern nach RomanForge gibt es bewusst noch nicht.
- Die Uebergabe muss aus einer RomanForge-Version stammen, die Figuren mitliefert (Feld `characters`).
- `names.yaml` wird beim Schreiben vollstaendig neu serialisiert (wie bei der Workbench); Inhalt bleibt gleich, Zeilenumbrueche und Anfuehrungszeichen koennen sich im Diff aendern.
