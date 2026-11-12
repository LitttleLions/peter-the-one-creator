# Cover-Prompt Druckcover (4k, Text im Bild)

Buch: `der-lotse-von-ruegen` (Der Lotse von Rügen)
Ziel: `assets/covers/cover-print.jpg`, 6 x 9 in + Beschnitt, 300 dpi
Modell: `gpt_image_2_5`, `aspect_ratio 2:3`, `resolution 4k`, `quality medium`
Stand: 2026-11-12. Motiv wie `cover.jpg` (Lotse mit Bleilot und Tau, junge Frau mit
Brief am Boot, Sperre aus versenkten Schiffen, Kirche); Typografie-Block aus
`python tools/cover_text.py --book der-lotse-von-ruegen` (Untertitel aus den
Buchdaten, Verlag klein unten), Randregel fuer den Druck.

## Prompt

Vertical German historical novel cover, 2:3, full-bleed artwork, no border frame.

SCENE: On a muddy shore of the Baltic lagoon of the Greifswalder Bodden at low evening sun, a weathered bearded man of about fifty in a dark tarred wool coat and heavy boots, a coiled rope and a lead sounding weight in his hands, looks out over the water. Beside him, standing in an old wooden fishing boat with a rope-wrapped mooring post, a young woman with braided brown hair in a green-brown dress and a dark blue shawl, holding a folded letter against her chest, gazing the same way. Behind them a shallow bay with the broken ribs and masts of sunken hulls forming a barrier, small sailing ships on the horizon, a small red-brick church with a short tower on a wooded rise on the right. Dramatic dark blue storm clouds above, low golden sun breaking through over the water. Painterly cinematic realism, fine detail, September 1715, grave and tense mood. Palette: deep slate blue, gold, weathered brown, muted green.

TYPOGRAPHY, integrated into the artwork, clean sharp serif lettering in cream-gold, every word spelled exactly:
- At the very top, centered, small letterspaced capitals: MOTIVATIER CLASSICS, with a thin gold rule beneath.
- Centered title in two very large lines of cream-gold serif capitals: DER LOTSE, then VON RÜGEN
- Below the title, smaller letterspaced capitals: EIN RÜGEN-ROMAN AUS DEM SEPTEMBER 1715
- Near the bottom, centered, letterspaced capitals: TIMO VERITA
- Very small and discreet at the very bottom, letterspaced capitals: MOTIVATIER STIFTUNG
- Keep a clear word space between every word; keep the umlaut Ü in RÜGEN.

Safe margins: no lettering and no ornamental line may come closer than 7 percent of the height to the top or bottom edge and 7 percent of the width to the left or right edge. The two figures must not overlap any lettering. No other text. No barcode, no price, no watermark, no text boxes.
