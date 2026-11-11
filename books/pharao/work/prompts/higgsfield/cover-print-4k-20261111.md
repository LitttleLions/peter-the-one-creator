# Cover-Prompt Druckcover (4k, Text im Bild)

Buch: `pharao` (Der Pharao, Boleslaw Prus)
Ziel: `assets/covers/cover-print.jpg`, Panel des Wrap, 300 dpi
Modell: `gpt_image_2_5`, `aspect_ratio 2:3`, `resolution 4k`, `quality medium`
Motivvorgabe: vorhandenes Cover (`assets/covers/cover.jpg`, 1200x1800) -
Pharao im Profil nach rechts, Sonnenscheibe, Heer mit Streitwagen, Tempel und
Obelisk am Nil. Typografie IM Bild, wie beim Ebook-Cover.
Freigabe: Nutzer 2026-11-11 (4k-Render mit Text; ein Lauf)

## Abweichungen vom Sprache-des-Anderen-Prompt

- Statt `BAND 1`-Badge steht hier `MOTIVATIER CLASSICS` als Fusszeile (das
  Ebook-Cover hat kein Reihen-Badge; Der Pharao ist kein Band der Reihe
  "Zwischen Rhein und Maas").
- Das Ebook-Cover setzt den Titel in einer Gold-Serifenschrift mit sehr
  weitem Sperrsatz (`P H A R A O`). Diese Wirkung wird hier beschrieben.
- Kein Diakritikum im Autorennamen: `BOLESLAW PRUS`. Das Original schreibt
  `Boleslaw` (Wolne Lektury); das vorhandene Cover zeigt ein `BOLESŁAW` mit
  L-Strich, das ist ein Zusatz der Gestaltung. Wenn der Renderer das `L` mit
  Strich trotzdem setzt und sauber aussieht, ist das kein Fehler.

## Prompt

Vertical German historical novel cover, 2:3, full-bleed artwork, no border frame.

SCENE: Colossal stone head of an ancient Egyptian pharaoh in profile facing right, wearing the blue-and-gold striped nemes headcloth with a golden uraeus cobra on the brow, serene and severe, filling the upper half of the composition. Behind it a huge pale golden sun disc. Below and behind, receding to the right: a line of Egyptian soldiers with spears, shields and a war chariot, a columned temple with two massive pylons, a tall slender obelisk, date palms, and the Nile with small boats under a hazy golden sky. Left edge: an Egyptian wall with carved hieroglyphs and a striding god figure in sunk relief. Warm golden light, deep shadows, fine painterly detail, restrained palette of gold leaf, lapis blue, sandstone, linen white and deep brown. Cinematic literary historical illustration, grave and monumental mood, ancient Egypt of the New Kingdom.

TYPOGRAPHY, integrated into the artwork across the dark lower third, clean sharp serif capitals, every word spelled exactly:
- Centered above the title, in smaller capitals: DER
- Below, centered title in one very large line: PHARAO, in golden serif capitals with generous letter spacing, an oversized ornamental P and a long swash on the final O.
- Under the title a thin horizontal golden rule with a small ornament in the middle.
- Then, centered and widely letter-spaced, smaller pale capitals: BOLESLAW PRUS
- At the bottom, centered and widely letter-spaced, smallest capitals: MOTIVATIER CLASSICS
- Keep a clear word space between every word: DER, PHARAO, BOLESLAW PRUS and MOTIVATIER CLASSICS must each read as separate words with generous spacing, never merged into one long word.

Safe margins: no lettering and no ornamental line may come closer than 7 percent of the height to the top or bottom edge and 7 percent of the width to the left or right edge. The title block must end well above the lower margin, with clear empty artwork beneath it. No other text. No barcode, no price, no watermark, no text boxes, no drop shadows.
