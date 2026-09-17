# Aelita: Bildwiederherstellung

Nur verified/ und verified-manifest.json fuer die Zuordnung verwenden.
originals/ und jpg/ enthalten auch verworfene Mehrfachzuordnungen des ersten Prompt-Abgleichs; keine produktive Auswahl.
Keine neuen Bilder generiert. Keine wiedergefundenen Bilder in assets uebernommen.
Vorheriger Asset-Bestand vollstaendig unter before/ gesichert; Hashes geprueft.

## Eindeutig zugeordnete Ergebnisse

- 005 scene: downloaded (42e014dd-45d9-459e-aa51-09c0dc72a654)
- 011 chapter: failed (61108679-9c9f-48b1-87c9-835f16399540); HTTP Error 403: Forbidden
- 012 chapter: failed (9be55003-442f-4e58-8425-f63a07244776); HTTP Error 403: Forbidden
- 020 chapter: downloaded (45892f3e-6901-4be9-b162-9cf071d18980)
- 021 chapter: downloaded (bfcdca79-b9a8-4b87-84f2-9dae124c3c55)
- 021 scene: downloaded (ee25d222-2fa6-468f-a266-9dbacf06bb37)
- 022 chapter: downloaded (78fbfd66-1f85-405b-a5cf-fa17e4e45e09)
- 023 chapter: downloaded (81361b41-ecea-4817-a027-f68cc0998b93)
- 024 chapter: downloaded (50e78631-2dc2-4502-b97f-fb433ef39237)
- 025 chapter: downloaded (2f0b2ae9-4c0d-4551-a56e-2632938845c0)
- 026 chapter: downloaded (f4cc6097-1ccd-463e-a83e-34f02183ec02)
- 027 chapter: downloaded (da141a97-e572-48aa-95cb-cab701839797)
- 028 chapter: downloaded (f97d09c8-fe14-4c74-80d7-9d121b812678)
- 029 chapter: downloaded (7059ef8c-b32b-44f2-8237-07f596bda217)
- 030 chapter: downloaded (0f144e9b-d0d8-4966-a9f2-7fbf3d68d837)

Kapitel 011/012: gespeicherte URLs nicht abrufbar; CLI meldet fuer beide Job-IDs 'Job nicht gefunden'.
Nur die letzten 100 Live-Jobs und lokale History-Archive durchsucht; keine vollstaendige historische Abdeckung garantiert.

## Validierung
{
  "verified_downloads": 13,
  "failed": [
    "011",
    "012"
  ],
  "production_images": 10,
  "export_bytes_before": 14837385,
  "export_bytes_after": 2447759,
  "covers_and_png_unchanged": true,
  "backups_verified": true
}