# Automatisierte KDP-Kampagne für übersetzte Public-Domain-Klassiker

> Status: **Entwurf / Plan** — wird später schrittweise umgesetzt.
> Erstellt 2026-06-17. Begleitende Plandatei:
> `~/.claude/plans/wir-produizeren-hier-automatische-glistening-frost.md`.

## Context

Das Repo `peter-the-one` ist heute eine reine **Übersetzungs-Pipeline**: RTF-Quelle →
LLM-Übersetzung pro Szene/Kapitel → Assembly → DOCX/EPUB-Export (`tools/export_manuscript.py`).
Es gibt **keinerlei** Marketing-/Publishing-Automatik (kein KDP-, Amazon-Ads-, Social-,
E-Mail- oder Landingpage-Code; `.env.example` kennt nur OpenRouter). Buch 1
("Peter der Erste") ist fertig und soll auf Amazon KDP beworben werden; im Repo liegen drei
Buchpakete (Peter I, Anna Karenina, Pharao). Ziel: eine **wiederholbare, weitgehend
automatisierte Kampagne pro Buch**, die auf die bestehende Buchpaket-Architektur aufsetzt.

**Geschäftliche Eckdaten (vom Nutzer bestätigt):**
- Markt: **Amazon.de**, deutschsprachig (`language: de-DE`).
- Ad-Budget: **50 €-Test**, iterativ skalieren wenn Verkäufe kommen.
- Kanäle: **Amazon Ads, Instagram/TikTok, Blog/Landingpage**.
- Automatikgrad: **maximal auto-ausführen** (Social-Posting voll automatisch; Ads via API
  wo möglich; KDP-Listing/Upload bleibt technisch manuell — Amazon hat keine öffentliche
  Publishing-API).

## Ehrliche Rahmenbedingungen (wichtig vor Umsetzung)

1. **PD-Differenzierung (KDP-Pflicht):** Amazon verbietet undifferenzierte Public-Domain-Uploads.
   Eine eigene Übersetzung qualifiziert als "differenziert" — der Titel/Untertitel **muss**
   den Übersetzer ausweisen (z. B. „Peter der Erste – Neu übersetzt 2025"). Ist bereits in
   `export.yaml` als `translator` vorhanden; muss in der KDP-Listing-Logik erzwungen werden.
2. **Kein KDP-Publishing-API:** Buch-Upload + Listing-Eingabe bleiben manuell (Copy-Paste der
   generierten Assets). „Maximal auto" greift bei Social-Posting, Landingpage-Deploy und
   (mit API-Zugang) Amazon Ads.
3. **Reviews = Engpass:** Sponsored Products konvertieren ohne 3–5 ehrliche Rezensionen schlecht.
   Fake-Reviews sind ausgeschlossen (Policy). Empfehlung: kurze Soft-Launch-Phase + KDP-Select
   Gratis-Aktionstage, **bevor** nennenswertes Ad-Budget fließt.
4. **Amazon-Ads-API braucht Freigabe** (Amazon-Advertising-Konto + LWA-App + Profil-Zugang,
   Vorlaufzeit). Fallback bis dahin: System erzeugt **Bulk-Upload-CSV**, die im Ads-Konsole
   hochgeladen wird.

## Architektur (an Buchpaket-Konvention angelehnt)

Pro Buch eine neue Config + Outputs unter dem Paket, neue CLIs in `tools/` im Stil der
bestehenden (argparse, `--book`, Logging über `tools/lib/log_writer.py`, Buchdiscovery über
`tools/lib/book_project.py`, Copy-Generierung über `tools/lib/openrouter_client.py`).

```
books/<book-id>/
  marketing.yaml                 # NEU: Kampagnen-Config (Keywords-Seed, Kategorien,
                                 #      Ad-Budget, Kanäle, Zeitplan, Vergleichs-ASINs)
  marketing/
    listing/                     # KDP-Texte: description.md, keywords.txt, categories.md,
                                 #   aplus/*.md, title.txt  (Copy-Paste in KDP)
    social/                      # Zitatkacheln (.png), reels-script.md, captions.md
    landing/                     # generierte index.html (SEO + schema.org Book)
    ads/                         # sponsored_products_bulk.csv, ad-copy.md, bid-plan.md
    reports/                     # eingelesene Ads-Performance + Optimierungs-Log
```

### Neue Tools

- **`tools/build_listing.py`** — erzeugt KDP-Listing-Assets aus `book.yaml`/`export.yaml` +
  Volltext: Rufus/A10-optimierte Beschreibung (natürliche Sprache, Themen/Tropes/„emotional
  payoff" → Semantic Tokens), 7 Keywords je Format, 3 **enge** Subkategorien, A+-Content-Blöcke,
  Übersetzer-pflichtiger Titel. Wiederverwendet `openrouter_client.py` + vorhandene
  `description`/`summary`/`author_bio` aus `export.yaml`.
- **`tools/promo_assets.py`** — extrahiert zitierfähige Passagen aus dem assemblierten DE-Text
  (`exports/<style>/book/work/` bzw. `work/assembled/`), rendert Zitatkacheln mit **Pillow**
  (neue Dep), generiert Reels/TikTok-Skripte + Captions/Hashtags via OpenRouter.
- **`tools/build_landing.py`** — statische SEO-Landingpage pro Buch (Leseprobe = 1. Kapitel aus
  Export, Amazon-Kauf-Button, schema.org `Book`-Markup, OG-Tags). Deploy via GitHub Pages /
  Netlify / Cloudflare Pages (frei, scriptbar).
- **`tools/ads_plan.py`** — baut Amazon-Ads-Kampagnenplan: 1 Auto-Kampagne + 1 manuelle
  Keyword-Kampagne + 1 **ASIN-Targeting**-Kampagne gegen vergleichbare deutsche Klassiker-
  Ausgaben (dtv/Reclam/Insel/Anaconda). Niedrige Gebote (~0,15–0,30 €), Tagesbudget passend zu
  50 €-Test. Output = Bulk-CSV; optional Push via Amazon-Ads-API.
- **`tools/social_publish.py`** — voll automatisches Posting über **Make.com / n8n / Buffer/
  Metricool-Webhook** (übernimmt Plattform-Auth für IG/TikTok). Liest geplante Posts aus
  `marketing/social/`.
- **`tools/campaign.py`** — Orchestrator: führt die Pipeline pro Buch aus und enthält die
  **iterative Ads-Optimierung** (Report einlesen → Regeln: Keyword mit Ausgaben & 0 Sales
  pausieren; ACOS niedrig + Sales → Gebot/Budget hoch). Per Scheduler (cron) wiederholbar →
  deckt „iterativ skalieren wenn gekauft wird" ab.

### Dashboard
Neuer Tab **„Marketing/Kampagne"** in `tools/dashboard.py` (neben den 8 bestehenden Tabs):
Assets erzeugen/vorschauen, Kampagne starten, Ads-Performance + Optimierungs-Log anzeigen.

### Secrets (`.env.example` erweitern, Werte lokal)
`AMAZON_ADS_CLIENT_ID/SECRET/REFRESH_TOKEN/PROFILE_ID`, `MAKE_WEBHOOK_URL` (oder
`BUFFER_TOKEN`), `DEPLOY_TOKEN` (Pages/Netlify). Regel aus AGENTS.md beachten: **keine Secrets
ins Repo**.

## Umsetzungs-Phasen (iterativ, je Phase verifizierbar)

1. **Listing-Fundament** (`build_listing.py` + `marketing.yaml`-Schema)
   → verify: für Peter I werden `description.md`, `keywords.txt` (7), `categories.md` (3 enge),
   A+-Blöcke und übersetzter Titel erzeugt; manuell in KDP eingefügt.
2. **Asset-Fabrik** (`promo_assets.py`, `build_landing.py`)
   → verify: ≥10 Zitatkacheln + Reels-Skripte; Landingpage rendert mit Leseprobe & Kauf-Link.
3. **Distributions-Automatik** (`social_publish.py`, Landing-Deploy)
   → verify: Testpost erscheint automatisch auf IG/TikTok via Webhook; Landingpage live (HTTPS).
4. **Amazon Ads 50 €-Test** (`ads_plan.py`)
   → verify: Bulk-CSV importierbar (oder API-Push); 3 Kampagnen live, Tagesbudget ⇒ ~50 €
   über Testzeitraum; nach 14–30 Tagen erste Klick-/Sales-Daten.
5. **Iterative Optimierung** (`campaign.py` + Scheduler)
   → verify: Loop liest Report, pausiert Verlierer, skaliert Gewinner; Optimierungs-Log in
   `marketing/reports/`.

## Verifikation (End-to-End)
- `python tools/campaign.py --book peter-i-buch-01 --dry-run` zeigt geplante Assets/Kampagnen ohne externe Calls.
- Smoke-Test pro neuem CLI unter `tests/` (Stil der bestehenden Smoke-/Unit-Tests).
- Echter Mini-Lauf: Listing live + 1 Social-Testpost + Landing live + Ads-CSV importiert; nach
  Testzeitraum Performance-Report im Dashboard sichtbar.

## Hinweise / offene Punkte
- Reihenfolge der Wirkung für No-Platform-PD-Klassiker: **Listing/Cover/Preis → Ads (ASIN-Targeting
  auf Vergleichsausgaben) → Social/Landing (Top-of-Funnel + SEO)**. Reviews-Engpass zuerst über
  Soft-Launch/KDP-Select-Gratistage entschärfen.
- Amazon-Ads-API-Zugang früh beantragen (Vorlaufzeit); bis dahin CSV-Workflow.
- Hook an Buch-Erstellung: nach EPUB-Export `campaign.py --book <id>` auslösen → „alles läuft
  automatisch".

## Quellen (2026-Recherche)
- [Reedsy – Amazon Ads for Authors 2026](https://reedsy.com/blog/amazon-ads-for-authors/)
- [KDP Amazon Ad Campaign Guide 2026](https://kdpformatters.com/kdp-amazon-ad-campaign-guide/)
- [Reedsy – 96 Book Marketing Ideas 2026](https://reedsy.com/blog/book-marketing-ideas/)
- [Manuscript Report – KDP Categories 2026](https://manuscriptreport.com/blog/kdp-category-selection-guide)
- [River – KDP Keyword Research 2026](https://rivereditor.com/guides/amazon-kdp-keyword-research-2026)
- [ebookpbook – KDP Categories & Keywords 2026 (A10/Rufus)](https://www.ebookpbook.com/2026/06/01/kdp-categories-keywords-explained/)
