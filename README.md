# peter-the-one

Regelbasierte kapitelweise Übersetzung literarischer Werke.

Aktuelles Buch: **„Peter der Erste"** (Пётр Первый) von Alexei Tolstoi
aus dem Russischen ins Deutsche.

## Was das Projekt ist und wozu

Eine Python-CLI-Pipeline, die

- Bücher in beliebiger Ausgangssprache kapitelweise einliest
- pro Kapitel den Status trackt (pending → in_progress → done / needs_review)
- pro Kapitel eine Übersetzung erzeugt, optional unter Anwendung eines
  Regelkatalogs (siehe `logic/`)
- Logfiles pro Kapitel schreibt
- über `config/books.yaml` mehrere Bücher parallel verwalten kann

## Aktueller Stand (Juni 2026)

**Peter I – Buch 01**

- 18 Kapitel erkannt (Книга 1: 7, Книга 2: 5, Книга 3: 6)
- 228.951 Wörter Original (russisch)
- Status: 1/18 (5.6 %) – Kapitel 1 in `needs_review`

**Was existiert bereits:**

- `config/books.yaml`, `pipeline.yaml`, `rules-overrides.yaml`
- `config/naming_proposal_peter_i.md` (Stil A bestätigt)
- `tools/extract_chapters.py`, `status.py` + `tools/lib/` (3 Module)
- `output/Peter I/chapters/001-source.md` … `018-source.md`
- `output/Peter I/chapters/001-translation.md` (Pilot)
- `status/Peter I.status.json` (18 Einträge)
- `status/logs/Peter I/001.log.md`

**Was offen ist:**

- Kapitel 1 noch nicht vollständig (Szenen 4–19 stehen aus)
- Kapitel 2–18 noch nicht übersetzt
- Regeln ggf. nach erstem Review anpassen

## Verzeichnisstruktur

```
.
├── AGENTS.md                    # zentrale KI-Kontextdatei
├── CLAUDE.md                    # Verweis auf AGENTS.md
├── .gitignore                   # Müll, Secrets, Python-Build
├── .gitattributes               # LF-Zeilenenden, Binärflags
├── README.md                    # dieses Dokument
├── requirements.txt             # Python-Abhängigkeiten
│
├── books/                       # Original-Bücher (nicht verändern!)
│   ├── Peter I - Buch 01 - royallib.ru.doc
│   └── Peter I - Buch 01 - royallib.ru.rtf   # Duplikat, prüfen
├── logic/                       # Original-Regelkataloge
│   └── peter the one - Regeln 001.txt
│
├── config/                      # Konfiguration
│   ├── books.yaml               # Bücher-Registry
│   ├── pipeline.yaml            # Pipeline-Einstellungen
│   ├── rules-overrides.yaml     # Pro-Buch-Overrides
│   └── naming_proposal_peter_i.md
│
├── tools/                       # Python-CLI
│   ├── extract_chapters.py      # Buch einlesen, Kapitel extrahieren
│   ├── status.py                # Status-Übersicht / -Manipulation
│   └── lib/
│       ├── rtf_parser.py        # striprtf-basiert
│       ├── status_manager.py    # JSON-Status
│       └── log_writer.py        # Logfiles
│
├── output/                      # Übersetzungen
│   └── Peter I/
│       └── chapters/
│           ├── 001-source.md
│           ├── 001-translation.md
│           └── ...
│
└── status/                      # Status & Logs
    ├── Peter I.status.json
    └── logs/
        └── Peter I/
            └── 001.log.md
```

## Einrichtung

```bash
# Abhängigkeiten
pip install -r requirements.txt
```

## Benutzung

```bash
# Buch einlesen, Kapitel extrahieren, Status initialisieren
python tools/extract_chapters.py

# Status anzeigen
python tools/status.py summary
python tools/status.py list
python tools/status.py next

# Kapitel zur Bearbeitung markieren
python tools/status.py mark 001 in_progress

# Nach dem Übersetzen:
python tools/status.py mark 001 done --words 2300 --title-de "Erstes Kapitel"
# oder:
python tools/status.py mark 001 needs_review
```

## Workflow (pro Kapitel)

1. `mark 001 in_progress` – Kapitel reservieren
2. Im Chat: russisches Kapitel anfordern, ich übersetze gemäß Regelwerk
3. Logfile in `status/logs/Peter I/001.log.md` wird mitgeschrieben
4. `mark 001 done --words <Wortzahl> --title-de "..."` oder
   `mark 001 needs_review`
5. Nach jeweils 3–5 Kapiteln: Konsistenz-Check (Namen, Ton, Regelanwendung)

## Wichtige Hinweise für neue Mitwirkende

- `AGENTS.md` lesen – dort sind die Konventionen und Pfade dokumentiert.
- `logic/`-Dateien sind **heilig** – nie ohne Rückfrage ändern.
- `books/`-Dateien sind **heilig** – nie ohne Rückfrage ändern.
- Status & Logfiles immer über die CLI ändern, nie direkt in JSON-Dateien.
- Im Zweifel nachfragen, nicht still annehmen.
