"""tools.lib — Python-Package für die peter-the-one-Pipeline.

Module:
- rtf_parser: liest RTF-Bücher, erkennt Heading-Paragraphen
- status_manager: verwaltet den JSON-Status pro Buch
- log_writer: schreibt pro-Kapitel-Logdateien

Hinweis: Die Top-Level-Skripte (`tools/extract_chapters.py`, `tools/status.py`)
legen `tools/` selbst auf sys.path und greifen dann via `from lib.<modul> ...`
zu. Die `__init__.py` hier macht `tools.lib` zusätzlich zu einem regulären
Python-Package, sodass auch andere Stellen mit absoluten Importen arbeiten
können.
"""
