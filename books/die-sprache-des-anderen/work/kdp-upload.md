# KDP-Upload: Die Sprache des Anderen

Stand 2026-11-10. Erzeugt aus `export.yaml` über `tools/lib/kdp_mapping.py`
(`map_kdp_soll`) – bei Änderungen am Buch den Soll neu bauen, nicht diese Datei
von Hand nachziehen (außer den KDP-Feldern, die nicht im Mapping stehen).

Soll-Ist-Abgleich nach dem Login:
`tools/kdp_sync.py login` → `pull` → `diff`. Der Publish-Wizard des
eingebundenen Skills ist laut README noch in Entwicklung; Inhalt und Cover
lädst du im Browser, diese Datei liefert die Werte.

## Dateien

| Zweck | Datei | Maße / Größe |
|---|---|---|
| eBook | `exports/stil-01-original/book/epub/book-die-sprache-des-anderen-stil-01-original-20261110-155537.epub` | 8,0 MB, 34 Kapitelbilder |
| eBook-Cover | `assets/covers/cover.jpg` | 1725 × 2625 px, 300 dpi |
| Taschenbuch Innenleben | `exports/stil-01-original/book/print/book-die-sprache-des-anderen-stil-01-original-55x85-classic-head-20261110-155553-paperback-interior.pdf` | 330 Seiten, 139,7 × 215,9 mm |
| Taschenbuch Umschlag (Wrap) | `exports/stil-01-original/book/print/book-die-sprache-des-anderen-stil-01-original-55x85-classic-head-20261110-155553-paperback-wrap.pdf` | 306,6 × 222,2 mm, Rücken 20,96 mm |

Wichtig: Für das Taschenbuch lädt KDP den **Wrap** hoch, nicht
`cover-print.jpg`. Das Vorderbild taugt nur für Vorschauen. Für das eBook ist
`cover.jpg` das Cover.

## Metadaten (beide Formate)

| Feld | Wert |
|---|---|
| Titel | Die Sprache des Anderen |
| Untertitel | Ein Straßburger Roman aus dem 9. Jahrhundert |
| Autor | Timo Verita (Vorname *Timo*, Nachname *Verita*) |
| Verlag | Motivatier Stiftung |
| Sprache | Deutsch |
| Reihe | Zwischen Rhein und Maas |
| Band | 2 |
| Erscheinungsdatum | 2026 |
| Rechte | © 2026 Motivatier Stiftung für diesen Text, editorische Einrichtung, Zusatztexte, Satz und Covergestaltung. |
| Öffentliche Domain | nein |
| Inhalte für Erwachsene | nein |

Hinweis zur Bandnummer: Die Metadaten sagen **Band 2**, das Covermotiv trägt
noch „Romanreihe Band 1". Das ist bewusst so (Cover wird beim nächsten
Coverlauf gestellt); im KDP-Formular die Reihennummer 2 eintragen.

## Kategorien (KDP-Dropdown, Klartext)

1. Belletristik > Historische Romane
2. Belletristik > Historischer Roman > Mittelalter
3. Belletristik > Familienleben

## Keywords (7 Felder)

1. Historischer Roman 9. Jahrhundert
2. Karolinger und Frankenreich
3. Straßburg im Mittelalter
4. historischer Roman starke Frauen
5. Recht und Schrift im Mittelalter
6. Familienroman Mittelalter
7. deutsche Geschichte 842

## Beschreibung (HTML, für das KDP-Feld)

```html
<p>Zwei Könige stehen vor Straßburg, und dazwischen liegt eine Frau mit fünf Kähnen. Alda führt den Fuhrbetrieb ihres verstorbenen Mannes weiter – und schuldet dem Grundherrn Raginbert dreißig Pfund Silber, fällig am Martinstag. Bis dahin will er Schiff und Vieh, bis dahin will er ihr Haus.</p>
<p>Doch Raginbert ist nur die Hand, die das Unrecht vollzieht. Die eigentliche Macht liegt beim Wort: in der lateinischen Urkunde, die Alda nicht lesen kann, im Bannrecht des Heerbanns, in Listen, die über ihr Leben verfügen. Um zu überleben, braucht sie genau das, was ihr fehlt – einen Schreiber, einen Weg über die Zaberner Steige, ein Bündnis der Fuhrleute und einen Handel, der größer ist als die Schulden.</p>
<p>Ein historischer Roman über Arbeit und Schulden im 9. Jahrhundert, über die Sprache der Herrschenden und die stille Sprache derer, die sie nicht beherrschen – und über einen Jungen, der lesen lernt, weil seine Mutter den Preis dafür bezahlt hat.</p>
```

964 Zeichen von 4000. Absätze kommen aus `book.description` (literaler
YAML-Block mit Leerzeilen) – nicht auf `>-` umstellen, sonst wird daraus ein
einziger Absatz.

## eBook-Einstellungen

- Preise (Entwurf, `amazon.kindle.price_eur` / `price_usd`): 4,99 € / 5,99 $
- Tantiemen: 70 % nur im Korridor 2,99–9,99 €; 4,99 € liegt darin
- DRM: nach deiner Entscheidung; KDP setzt es standardmäßig an, lässt sich abschalten
- Länderrechte: weltweit
- KDP Select: nach deiner Entscheidung (Exklusivität 90 Tage; schließt andere
  Shops aus)

## Taschenbuch-Einstellungen

- Trim: 5,5 × 8,5 in (13,97 × 21,59 cm), Classic-Satz, Kapitelbilder als Kopfvignette
- Papier: **Cream** (330 Seiten, Limit 776)
- Beschnitt: ja, mit Beschnittzugabe im Wrap
- Umschlag: matt
- Rücken: 20,96 mm (330 Seiten × 0,0635 mm) – im Wrap bereits gesetzt
- Preis: im Wizard festlegen; KDP zeigt den Mindestpreis aus den Druckkosten.
  Vorschlag 14,99 €, aber erst nach Anzeige der Mindestkosten bestätigen.
- ISBN: KDP-ISBN (kostenlos) verwenden, solange keine eigene beantragt ist.
  Bei eigener ISBN die Verlagsangabe „Motivatier Stiftung" eintragen.

## Nach dem Upload

1. Kindle Previewer: eBook lokal prüfen (Titelei, Kapitelbilder, Cover,
   Kolophon/Impressum, Reihenkatalog).
2. KDP-Printvorschau: Druckfahne durchblättern, vor allem die Kopfvignetten
   und die letzte Seite.
3. Käufer-Ansicht prüfen: Reihenangabe (Band 2), Kategorien, Keywords,
   Beschreibung mit drei Absätzen.
4. Erst danach „Veröffentlichen".

## Offen vor dem Klick

- Covermotiv sagt „Band 1" (bewusst; Fix beim nächsten Coverlauf).
- Tippfehler in der RomanForge-Quelle: „ann, 25 Jahre" bei Gerwin (nicht in
  dieser Ausgabe, nur im Quelldatensatz).
