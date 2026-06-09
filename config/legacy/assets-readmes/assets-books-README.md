# Buch-Assets

Dieser Ordner ist fuer buchbezogene Produktions-Assets gedacht.

Empfohlene Struktur fuer neue Buecher:

```text
assets/books/<book-id>/
  covers/
    cover.png
  notes/
```

Beispiel:

```text
assets/books/peter-i-buch-01/covers/cover.png
```

Globale Cover in `assets/covers/` bleiben weiterhin unterstuetzt. Fuer neue
Buecher ist die buchbezogene Struktur aber klarer, weil Cover, Notizen und
spaetere Zusatzmaterialien nicht durcheinander geraten.
