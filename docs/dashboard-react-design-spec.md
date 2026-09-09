# React-Dashboard: Operative Design-Spezifikation

Basis ist `docs/dashboard-design-system.md`. Diese Datei konkretisiert die
Regeln fuer die Arbeitsoberflaeche.

## Layout

- Desktop: feste linke Navigation mit 280 px Breite, rechts ein Contentbereich
  mit maximal 1400 px.
- Mobile: Navigation als ausklappbarer Drawer; Content bleibt einspaltig.
- Arbeitsseiten bestehen aus Header, Kontextleiste und Inhaltsbereich.
- Karten werden nur fuer wiederholte Items, Jobdetails oder klar gerahmte
  Werkzeuge verwendet. Keine Karten-in-Karten-Strukturen.
- Statusdaten werden bevorzugt als dichte Tabellen, Listen oder Metrikleisten
  dargestellt.

## Look

- Schrift: Plus Jakarta Sans mit System-Fallback.
- Farben, Schatten und Radius folgen der bestehenden HSL-Token-Spezifikation.
- Flaechen bleiben ruhig und hell; Orange ist Akzent, nicht Hintergrundthema.
- Keine Hero-Flaechen in Arbeitsansichten.
- Keine dekorativen Orbs, Bokeh-Flächen oder Marketing-Illustrationen.

## Komponenten

- Navigation: Lucide-Icons, aktive Route mit dezentem Primary-Hintergrund.
- Buttons: Text plus Lucide-Icon bei Aktionen, Icon-only nur fuer klare
  Standardaktionen.
- Job-Panel: kompakte Liste links/oben im Inhalt, Detail rechts oder darunter.
- Tabellen: stabile Spalten, kleine Labels, kein Layout-Sprung bei Statuswechsel.
- Kontextleiste: kleine, scanbare Chips fuer Buch, Stil, Kapitel/Umfang und Job.

## Responsive Verhalten

- Ab 900 px: zweispaltige Uebersicht mit Status links und Jobdetail rechts.
- Unter 900 px: Inhalt einspaltig, Navigation als Drawer, Jobdetail unter der
  Jobliste.
- Texte duerfen nicht in Buttons oder Tabellen ueberlaufen; lange IDs werden
  gekuerzt und im Title-Attribut voll angezeigt.
