"""
Auto-Pilot: Uebersetzt Kapitel 2-18 nacheinander und baut Sammeldateien.

Das Skript ist bewusst klein gehalten: Es ueberspringt vorhandene
DE-Szenen, arbeitet relativ zum Repo-Root und nutzt denselben Python-
Interpreter, mit dem es gestartet wurde.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

from lib.output_paths import de_scene_path, list_ru_scene_paths, parse_scene_number


REPO_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_ROOT = REPO_ROOT / "output" / "Peter I"
MODEL = "deepseek/deepseek-v3.2"
STYLE = "stil-03-branderson"


def count_de_scenes(chapter: str) -> int:
    scene_dir = OUTPUT_ROOT / "scenes" / "de" / STYLE / chapter
    return len(list(scene_dir.glob("scene-*.md")))


def get_ru_scenes(chapter: str) -> list[Path]:
    return list_ru_scene_paths(OUTPUT_ROOT, chapter)


def run_tool(args: list[str], timeout: int) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, *args],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=timeout,
    )


failed = False
skipped = False

for chapter_num in range(2, 19):
    chapter = f"{chapter_num:03d}"
    ru_scenes = get_ru_scenes(chapter)
    target = len(ru_scenes)
    if target == 0:
        print(f"Kapitel {chapter}: Keine Szenen gefunden, ueberspringe.")
        skipped = True
        continue

    existing = count_de_scenes(chapter)
    if existing >= target:
        print(
            f"Kapitel {chapter}: Bereits vollstaendig "
            f"({existing}/{target}), ueberspringe."
        )
        continue

    print(f"\n=== Kapitel {chapter}: {target} Szenen, {existing} vorhanden ===")

    for scene_file in ru_scenes:
        scene_number = parse_scene_number(scene_file, chapter)
        if scene_number is None:
            print(f"  Szene nicht erkannt: {scene_file}, ueberspringe.")
            skipped = True
            continue
        scene_num = f"{scene_number:02d}"
        de_file = de_scene_path(OUTPUT_ROOT, chapter, scene_number, STYLE)
        if de_file.exists():
            print(f"  Szene {scene_num} bereits vorhanden, ueberspringe.")
            continue

        print(f"  Uebersetze Szene {scene_num}...")
        result = run_tool(
            [
                "tools/translate_chapter.py",
                "--chapter", chapter,
                "--scene", scene_num,
                "--style", STYLE,
                "--model", MODEL,
                "--overwrite",
            ],
            timeout=300,
        )
        if result.returncode != 0:
            failed = True
            detail = (result.stderr or result.stdout or "").strip()
            print(f"  FEHLER bei Szene {scene_num}: {detail[:500]}")
            time.sleep(5)
            continue

        print(f"  OK Szene {scene_num} fertig")
        time.sleep(2)

    if count_de_scenes(chapter) >= len(ru_scenes):
        print(f"  -> Baue Sammeldatei fuer Kapitel {chapter}...")
        result = run_tool(
            [
                "tools/assemble_chapter.py",
                "--chapter", chapter,
                "--style", STYLE,
            ],
            timeout=30,
        )
        if result.returncode != 0:
            failed = True
            detail = (result.stderr or result.stdout or "").strip()
            print(f"  FEHLER beim Zusammenbau: {detail[:500]}")
            continue
        print(f"  OK Sammeldatei Kapitel {chapter} erstellt")
        status_result = run_tool(
            ["tools/status.py", "mark", chapter, "needs_review"],
            timeout=30,
        )
        if status_result.returncode != 0:
            failed = True
            detail = (status_result.stderr or status_result.stdout or "").strip()
            print(f"  FEHLER beim Status-Update: {detail[:500]}")
            continue
        print(f"  OK Status Kapitel {chapter} = needs_review")

    print(f"  Fertig mit Kapitel {chapter}.")

if failed:
    print("\nFertig mit Fehlern. Bitte Log-Ausgaben oben pruefen.")
elif skipped:
    print("\nFertig, aber mindestens ein Kapitel/eine Szene wurde uebersprungen.")
else:
    print("\nAlle Kapitel fertig!")
