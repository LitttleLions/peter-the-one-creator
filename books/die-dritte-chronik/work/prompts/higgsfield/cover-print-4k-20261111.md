# Cover-Prompt Druckcover (4k, Text im Bild)

Buch: `die-dritte-chronik` (Die dritte Chronik, Timo Verita)
Ziel: `assets/covers/cover-print.jpg`, Panel des Wrap (6x9 + Beschnitt), 300 dpi
Modell: `gpt_image_2_5`, `aspect_ratio 2:3`, `resolution 4k`, `quality medium`
Motivvorgabe: vorhandenes Ebook-Cover (`assets/covers/cover.jpg`, 1086x1448) -
drei Chronisten an einem Tisch vor der Zeltstadt von Karakorum, Blick durch
einen mit Troddeln behaengten Rahmen auf Berge und ein grosses Zelt.
Typografie IM Bild, wie beim Ebook-Cover.
Freigabe: Nutzer 2026-11-11 (4k-Render mit Text; ein Lauf)

## Abweichungen vom Ebook-Cover

- Der Rahmen mit Troddeln bleibt, aber **schmaler** als im Ebook-Cover: das
  Druckpanel ist 0,662 breit (6,125 x 9,25 in), das Ebook-Cover 0,75. Ein zu
  breiter Rahmen wuerde beim Beschnitt angeschnitten.
- Untertitel, "Ein historischer Roman" und das Jubilaeums-Badge entfallen im
  Druck (Platz); Titel, Reihenzeile und Autorname bleiben.
- Keine Umlaute im Rendertext: `DIE DRITTE CHRONIK` und `TIMO VERITA` sind
  ohnehin ohne. Der Untertitel wird englisch beschrieben, aber nicht gesetzt.

## Prompt

Vertical German historical novel cover, 2:3, full-bleed artwork, slim ornamental border only.

SCENE: Three chroniclers seated at a low table inside a richly decorated tent, seen from the front. Left: a woman in a deep red and gold embroidered robe with a jewelled headdress, writing on parchment with a reed pen. Centre: a young man in a blue and gold patterned coat, writing in an open book, a rolled scroll and an inkwell with brass fittings on the table before him. Right: an older man with long grey hair and a dark embroidered robe, resting his hands on a closed book. On the table lie open folios, rolled scrolls and a small brass lamp. Behind them the tent opens onto a vast encampment: hundreds of round white yurts with blue and gold banners, horsemen in the middle distance, a great golden-topped pavilion, snow-capped mountains under a bright sky with scattered clouds, and a tall standard with a blue banner and a sun emblem on the right. Warm daylight, gold, deep red, lapis blue and cream palette, fine painterly detail, cinematic historical illustration, grave and dignified mood, Mongol empire of the thirteenth century.

TYPOGRAPHY, integrated into the artwork, clean sharp serif capitals, every word spelled exactly:
- At the very top, centered, small letterspaced gold capitals: MOTIVATIER CLASSICS
- Below it a thin gold rule with a small ornament in the middle.
- Below that, centered title in two very large lines in golden serif capitals with generous letterspacing: DIE DRITTE, then CHRONIK, with an ornamental flourish under the final word.
- Across the bottom, centered and widely letterspaced in gold capitals on the dark table edge: TIMO VERITA
- Keep a clear word space between every word: MOTIVATIER CLASSICS, DIE DRITTE CHRONIK and TIMO VERITA must each read as separate words with generous spacing, never merged into one long word.

Safe margins: no lettering and no ornamental line may come closer than 7 percent of the height to the top or bottom edge and 7 percent of the width to the left or right edge. Any decorative border must stay well inside those margins. No other text. No barcode, no price, no watermark, no text boxes, no drop shadows.
