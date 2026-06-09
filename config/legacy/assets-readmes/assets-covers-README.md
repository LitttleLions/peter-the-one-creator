# Coverbilder

Hier liegen optionale Coverbilder fuer DOCX-/EPUB-Exporte.

Empfohlen:

- `assets/covers/peter-i-buch-01.png`
- Seitenverhaeltnis ca. 2:3
- PNG oder JPG
- mindestens 1600 x 2400 px fuer saubere Reader-Darstellung

Aktivierung in `config/export.yaml`:

```yaml
books:
  peter-i-buch-01:
    cover:
      mode: image
      image_path: assets/covers/peter-i-buch-01.png
```

Wenn `mode: placeholder` gesetzt ist oder `image_path` leer bleibt, erzeugt
`tools/export_manuscript.py` automatisch ein einfaches Platzhalter-Cover.
