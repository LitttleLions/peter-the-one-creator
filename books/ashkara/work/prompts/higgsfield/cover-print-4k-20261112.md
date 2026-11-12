# Cover-Prompt Druckcover (4k, Text im Bild)

Buch: `ashkara` (Ashkar, Das Glasmeer)
Ziel: `assets/covers/cover-print.jpg`, 6 x 9 in + Beschnitt, 300 dpi
Modell: `gpt_image_2_5`, `aspect_ratio 2:3`, `resolution 4k`, `quality medium`
Stand: 2026-11-12. Motiv wie `cover-branded.png` (Glasmeer, Turm links, Blitz rechts,
einzelne Figur); Typografie-Block aus `python tools/cover_text.py --book ashkara`,
Titel ohne Bandzahl wie im bisherigen Cover, Randregel fuer den Druck.

## Prompt

Vertical premium German science fiction novel cover, 2:3, full-bleed artwork, no border frame.

SCENE: A vast Glass Sea of black and amber glass over ancient mineral plains, cracks glowing gold, light refracting through fractures and edges; beneath the dark glass surface faint hidden underground human settlements glow amber. On the left horizon a tall dark needle-like tower city with a long reflection; on the right a distant peak under blue electric lightning. Sky with electric storms, drifting charged dust and faint auroras in amber and cold blue. In the foreground on a dark rocky ledge a single small human figure in a long coat seen from behind, looking out over the glass expanse to give a sense of scale. Monumental, intelligent, alien, grave and dignified mood. Refined painterly realism, cinematic light, deep atmospheric depth. Palette: black glass, amber and gold, muted blue, bronze and milky white.

TYPOGRAPHY, integrated into the artwork, refined tall serif lettering in aged ivory and antique gold, every word spelled exactly:
- At the very top, centered, small widely letterspaced golden capitals: MOTIVATIER CLASSICS, with a thin gold rule and a tiny diamond ornament beneath it.
- Large main title across the upper third in tall refined gold serif capitals: ASHKAR
- Below it, in smaller elegant serif letters: Das Glasmeer, with a thin gold rule and a tiny diamond ornament beneath.
- Near the bottom, centered, widely letterspaced capitals: TIMO VERITA
- Very small and discreet at the very bottom, letterspaced capitals: MOTIVATIER STIFTUNG
- Keep a clear word space between every word.

Safe margins: no lettering and no ornamental line may come closer than 7 percent of the height to the top or bottom edge and 7 percent of the width to the left or right edge. The figure and the tower must not overlap any lettering. No other text. No barcode, no price, no watermark, no text boxes.
