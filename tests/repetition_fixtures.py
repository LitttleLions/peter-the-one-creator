"""Fixtures: echte Problemstellen aus der Dritten Chronik, Kap. 008."""
from pathlib import Path

EXAMPLE_ANAPHORA = """Güyük las jede Seite zweimal

Er las von den Ärzten ihren Berichten ihren vorsichtigen Formulierungen ihrem Schweigen zwischen den Zeilen

Er las vom Gelage an jenem Abend von den Gästen von den Speisen vom Wein

Er las vom plötzlichen Zusammenbruch von der Eile von der Stille danach

Er las nichts über einen verschwundenen Diener

Er las nichts über einen goldenen Becher mit ungewöhnlichem Inhalt

Er las nichts was er nicht schon wusste oder was er nicht schon vermutet hätte"""

EXAMPLE_CHINQAI = """Das Schweigen fiel wieder ein schwerer Vorhang zwischen ihnen beiden schwerer Stoff schweres Schweigen schweres Wissen das beide teilten ohne es auszusprechen:

Chinqai wusste etwas Chinqai könnte eines Tages sprechen Chinqai könnte eines Tages sterben bevor er spricht – je nachdem wer wen fand wen schützte wen tötete bevor es zu spät wäre für alles außer Schweigen außer Vergessen außer dem Tod der alles beendet aber nichts löst nichts erklärt nichts heilt sondern nur zudeckt nur vergräbt nur wegsperrt in einer Truhe deren Schlüssel verloren ist im Sand der Zeit im Wind des Vergessens im endlosen Kreislauf von Macht und Blut und Stille immer wieder Stille immer wieder Schweigen immer wieder Tod:

Der Tod des Khans Der Tod seines Vaters Der Tod eines Mannes dessen Name fällt oder fällt gelassen wird je nachdem wer spricht wer schweigt wer stirbt bevor beide möglich sind bevor beides geschieht bevor nichts mehr"""

LITANY_OK = """Der Frühling kam nach Karakorum. Fatima stand am Fenster der Kanzlei.

Sie dachte an die Briefe. Sie dachte an den Hof. Sie dachte an die Regentin.

Drei Sätze genügen. Danach endet die Anapher bewusst."""


def scene_path_008() -> Path:
    """Echte Datei des Problemfalls (Kap. 008, Der Heimkehrer)."""
    return (
        Path(__file__).resolve().parents[1]
        / "books" / "die-dritte-chronik" / "work" / "scenes" / "de"
        / "stil-01-original" / "008" / "scene-01.md"
    )
