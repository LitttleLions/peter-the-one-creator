# Cover-Prompt Druckcover (4k, Text im Bild) - Versuch 2

Buch: `die-dritte-chronik` (Die dritte Chronik, Timo Verita)
Ziel: `assets/covers/cover-print.jpg`, Panel des Wrap (6x9 + Beschnitt), 300 dpi
Modell: `gpt_image_2_5`, `aspect_ratio 2:3`, `resolution 4k`, `quality medium`
Freigabe: Nutzer 2026-11-11 (zweiter Lauf: Sitzordnung + Geist)

## Was gegenueber Versuch 1 anders ist

1. **Fatima sitzt in der MITTE**, nicht links. Links der alte Mongole
   (Shigi Qutuqu, Oberrichter), rechts der persische Schreiber (Ata-Malik
   Juvaini). In allen bisherigen Entwuerfen (Ebook-Cover, cover2, cover-neu)
   sass die Frau links - das war falsch.
2. **Dschingis Khan als Geist**: harte Silhouette eines Reiters vor der
   Sonnenscheibe, mit dem Heer darunter. Vorbild ist der aeltere Entwurf
   `assets/covers/cover-neu.png`. Der Roman heisst "Im Schatten Dschingis
   Khans"; er ist die treibende Abwesenheit des Buches.

## Platzregel fuer den Geist

Der Reiter sitzt im **Mittelgrund zwischen Titel und Tisch** - auf Hoehe der
Zeltstadt und der Berge, **nicht am Himmel**. Sonst kollidiert er mit
`MOTIVATIER CLASSICS` und `DIE DRITTE CHRONIK` und der Renderer schreibt
Text ueber die Silhouette.

## Prompt

Vertical German historical novel cover, 2:3, full-bleed artwork, slim ornamental border only.

SCENE: Three chroniclers seated behind a low table inside a richly decorated tent, seen from the front, all three facing the viewer's table. In the CENTRE sits a woman in a deep red and gold embroidered robe with a jewelled headdress and long dark hair, writing on parchment with a reed pen. To her LEFT an older Mongol man with a long grey beard and a dark embroidered robe, resting his hands on a closed book. To her RIGHT a younger Persian scribe with a short beard, a patterned blue and gold coat and a cloth wrapped around his head, writing in an open book with a reed pen. On the table lie open folios, rolled scrolls, a sealed letter, an inkwell and a small brass lamp.

Beyond the tent opening: the vast encampment of Karakorum with hundreds of round white yurts, blue and gold banners, riders in the middle distance, and a great golden-topped pavilion. Behind the camp rise snow-capped mountains under a bright sky with scattered clouds. Low over the horizon hangs a huge pale golden sun disc, and ACROSS that disc, in the middle distance at the height of the camp and the mountains, rides the hard black silhouette of a lone horseman with a banner, a ghostly warlord who is no longer present, his horse in full stride, with the ghostly silhouettes of a small army behind him. The silhouette stays below the sky and never touches the top third of the image.

Warm daylight, gold, deep red, lapis blue and cream palette, fine painterly detail, cinematic historical illustration, grave and dignified mood, Mongol empire of the thirteenth century.

TYPOGRAPHY, integrated into the artwork, clean sharp serif capitals, every word spelled exactly:
- At the very top, centered, small letterspaced gold capitals: MOTIVATIER CLASSICS
- Below it a thin gold rule with a small ornament in the middle.
- Below that, centered title in two very large lines in golden serif capitals with generous letterspacing: DIE DRITTE, then CHRONIK, with an ornamental flourish under the final word.
- Across the bottom, centered and widely letterspaced in gold capitals on the dark table edge: TIMO VERITA
- Keep a clear word space between every word: MOTIVATIER CLASSICS, DIE DRITTE CHRONIK and TIMO VERITA must each read as separate words with generous spacing, never merged into one long word.

Safe margins: no lettering and no ornamental line may come closer than 7 percent of the height to the top or bottom edge and 7 percent of the width to the left or right edge. Any decorative border must stay well inside those margins. The ghost rider and his army must not overlap any lettering. No other text. No barcode, no price, no watermark, no text boxes, no drop shadows.
