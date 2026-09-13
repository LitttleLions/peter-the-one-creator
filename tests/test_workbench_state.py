from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

from lib.book_project import find_book, write_yaml  # noqa: E402
from lib.workbench_state import chapter_ids  # noqa: E402


class ChapterIdsTests(unittest.TestCase):
    def _book_root(self, root: Path, *, source_lang: str, target_lang: str) -> Path:
        book_root = root / "books" / "sample-de"
        write_yaml(
            book_root / "book.yaml",
            {
                "id": "sample-de",
                "title": "Sample DE",
                "author": "Autor",
                "source_path": "source/sample.txt",
                "source_lang": source_lang,
                "target_lang": target_lang,
                "style_mode": "stil-01-original",
            },
        )
        (book_root / "styles").mkdir(parents=True)
        (book_root / "styles" / "stil-01-original.md").write_text("Profil", encoding="utf-8")
        return book_root

    def test_style_dir_is_not_a_chapter_id_when_source_lang_equals_target_lang(self) -> None:
        # Regression (Die dritte Chronik): work/scenes/de enthaelt neben den
        # Kapitelordnern auch den Style-Ordner mit den Zielszenen. Der wurde
        # vorher als Kapitel-ID "stil-01-original" gezaehlt.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book_root = self._book_root(root, source_lang="de", target_lang="de")
            (book_root / "work" / "chapters").mkdir(parents=True)
            (book_root / "work" / "chapters" / "001-source.md").write_text("Kapitel 1", encoding="utf-8")
            source_scene = book_root / "work" / "scenes" / "de" / "001"
            source_scene.mkdir(parents=True)
            (source_scene / "scene-01.md").write_text("Szene 1", encoding="utf-8")
            target_scene = book_root / "work" / "scenes" / "de" / "stil-01-original" / "001"
            target_scene.mkdir(parents=True)
            (target_scene / "scene-01.md").write_text("Szene 1 DE", encoding="utf-8")

            book = find_book(root, "sample-de")
            ids = chapter_ids(book, root)

        self.assertEqual(ids, ["001"])

    def test_style_like_dir_without_scenes_is_not_a_chapter_id(self) -> None:
        # Zweites Signal fuer source_lang == target_lang: Ordner ohne direkte
        # Szenen sind Style-/Vergleichsordner, keine Kapitel.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book_root = self._book_root(root, source_lang="de", target_lang="de")
            chapter_dir = book_root / "work" / "scenes" / "de" / "007"
            chapter_dir.mkdir(parents=True)
            (chapter_dir / "scene-01.md").write_text("Szene 1", encoding="utf-8")
            legacy_style = book_root / "work" / "scenes" / "de" / "stylized" / "007"
            legacy_style.mkdir(parents=True)
            (legacy_style / "scene-01.md").write_text("Szene 1 alt", encoding="utf-8")

            book = find_book(root, "sample-de")
            ids = chapter_ids(book, root)

        self.assertEqual(ids, ["007"])

    def test_source_scene_chapters_still_counted_for_other_source_lang(self) -> None:
        # Kein Nebeneffekt: fremdsprachige Quellen zaehlen weiterhin normal.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book_root = self._book_root(root, source_lang="ru", target_lang="de")
            source_scene = book_root / "work" / "scenes" / "ru" / "004"
            source_scene.mkdir(parents=True)
            (source_scene / "scene-01.md").write_text("Сцена", encoding="utf-8")
            target_scene = book_root / "work" / "scenes" / "de" / "stil-01-original" / "004"
            target_scene.mkdir(parents=True)
            (target_scene / "scene-01.md").write_text("Szene", encoding="utf-8")

            book = find_book(root, "sample-de")
            ids = chapter_ids(book, root)

        self.assertEqual(ids, ["004"])


if __name__ == "__main__":
    unittest.main()
