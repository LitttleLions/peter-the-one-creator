# Cover-Prompt Druckcover (4k, Text im Bild) - v3 mit Marke

Buch: `die-sprache-des-anderen`
Reihe: Zwischen Rhein und Maas, **Band 2**
Ziel: `assets/covers/cover-print.jpg`, 6 x 9 in + 3,175 mm Beschnitt, 300 dpi
Modell: `gpt_image_2_5`, `aspect_ratio 2:3`, `resolution 4k`
Stand: 2026-11-12, noch nicht generiert.

Aenderung gegenueber v2: oben steht die Marke `MOTIVATIER CLASSICS`
(Herausgeber), unten nur klein der Verlag `MOTIVATIER STIFTUNG`; Bandnummer 2
statt 1. Der Typografie-Block folgt `python tools/cover_text.py --book
die-sprache-des-anderen`; Layout-Angaben (Titel in drei Zeilen, Abzeichen,
Randregel) stammen aus v2.

## Prompt

Vertical German historical novel cover, 2:3, full-bleed artwork, no border frame.

SCENE: A young woman seen from behind at a stone parapet, long braided light-brown hair, deep oxblood-red wool cloak over a grey linen dress, looking out over a wide river valley at golden sunset. A long medieval stone bridge with arches crosses the river; beyond it a dense medieval town with a tall Romanesque church spire and red-tiled roofs, a small boat on the water. Distant blue-violet hills, warm haze, low sun near the horizon on the right, golden light reflecting on the water. Painterly cinematic realism, fine detail, restrained palette of gold, slate blue, oxblood red and warm grey. Ninth-century Carolingian Frankish setting, grave and quiet mood.

TYPOGRAPHY, integrated into the artwork, clean sharp serif lettering, every word spelled exactly:
- At the very top, centered, small letterspaced gold capitals (publisher brand): MOTIVATIER CLASSICS
- Below it, centered, letter-spaced small capitals: TIMO VERITA
- Below, centered title in three lines: DIE (small), then SPRACHE in very large capitals with an oversized ornamental capital A and a long swash on the S, then DES ANDEREN in capitals. Title color deep oxblood red, slightly darker outline for legibility.
- Under the title a thin horizontal rule with a small round interlaced ornament in the middle.
- Then, centered, letter-spaced small capitals in oxblood: EIN STRASSBURGER ROMAN AUS DEM 9. JAHRHUNDERT
- On the left below the subtitle, four short lines of ivory serif capitals: Hoffnung. / Macht. / Drei Reiche. / Ein Schicksal.
- Bottom left, small white letter-spaced capitals: HISTORISCHER ROMAN
- Bottom right, very small white letter-spaced capitals (legal publisher): MOTIVATIER STIFTUNG
- Bottom center, a thin white rectangular frame with two lines inside: ROMANREIHE / BAND 2, white letter-spaced small capitals.
- Keep a clear word space between every word.

Safe margins: no lettering and no frame line may come closer than 7 percent of the height to the top or bottom edge and 7 percent of the width to the left or right edge. The rectangular badge must end well above the lower margin, with clear empty artwork beneath it. No other text. No barcode, no price, no watermark, no text boxes, no drop shadows.
