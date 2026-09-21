# Review Kapitel 000

- Buch: Der Pharao (pharao)
- Stil: stil-02-poetisch
- RU-Szenen: 1
- DE-Szenen: 1
- Fehler: 3
- Warnungen: 0
- Hinweise: 0

## Befunde

### ERROR: length_ratio (000, Szene 01)

DE/PL-Wortverhaeltnis ist stark auffaellig (0.23).

> PL=1420, DE=322

Empfehlung: Auf Auslassung, Doppelung oder Ausschweifung pruefen.

### ERROR: paragraph_drop (000, Szene 01)

DE-Szene hat deutlich weniger Absaetze als die PL-Quelle (12 statt 24) und weniger Woerter (0.23 x).

> DE-Absaetze=12, Quell-Absaetze=24, DE/PL-Woerter=322/1420 (0.23)

Empfehlung: Auf Raffung/Auslassung pruefen; betroffene Szene mit Chunking neu uebersetzen (translate_chapter.py --chunk-char-limit 7000).

### ERROR: length_outlier (000, Szene 01)

DE/PL-Wortverhaeltnis 0.23 weicht stark vom Buch-Median 1.22 ab.

> PL=1420, DE=322, Buch-Median=1.22

Empfehlung: Auf Raffung pruefen; betroffene Szene mit Chunking neu uebersetzen (translate_chapter.py --chunk-char-limit 7000).
