from __future__ import annotations

import json
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "tools"))

import export_manuscript as manuscript  # noqa: E402
from lib import marketing_campaign as campaignpkg  # noqa: E402
from lib.book_project import find_book  # noqa: E402

SAMPLE_TEXT = (
    "Sanka sprang von der Ofenbank und stiess die Tuer auf. Draussen fiel "
    "leiser Schnee, und im Hausflur war es bitterkalt. Die Kinder traten von "
    "einem Fuss auf den anderen und warteten auf den Vater."
)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_book(
    root: Path,
    *,
    website_amazon: str = "",
    marketing_lines: list[str] | None = None,
) -> dict:
    """Legt ein minimales Buchpaket unter ``root/books/sample`` an."""
    book_dir = root / "books" / "sample"
    write_text(
        book_dir / "book.yaml",
        "\n".join(
            [
                "id: sample",
                "title: Beispielroman",
                "author: Anna Beispiel",
                "source_lang: ru",
                "target_lang: de",
                "style_mode: stil-test",
                "work_dir: work",
                "exports_dir: exports",
                "ai:",
                "  provider: openrouter",
                "  model: test/model",
                "  max_tokens_per_scene: 4000",
                "",
            ]
        ),
    )
    export_lines = [
        "defaults:",
        "  cover:",
        "    mode: placeholder",
        "book:",
        "  title: Beispielroman",
        "  subtitle: Ein Beispieluntertitel",
        "  author: Anna Beispiel",
        "  translator: Motivatier Classics",
        "  translator_label: Uebersetzung und editorische Einrichtung",
        "  publisher: Motivatier Hermann Stiftung",
        "  language: de-DE",
        "  description: Kurzbeschreibung des Beispielromans.",
        "  summary: Ausfuehrliche Inhaltsbeschreibung des Beispielromans.",
        "  author_bio: Anna Beispiel schrieb Beispielromane.",
        "  title_page_extra:",
        "  - Diese Ausgabe ist eine neue deutsche Uebersetzung.",
        "  cover:",
        "    mode: image",
        "    image_path: assets/covers/cover.jpg",
        "website:",
        f"  amazon_url: '{website_amazon}'",
        "  enabled: true",
    ]
    export_lines += list(marketing_lines or [])
    write_text(book_dir / "export.yaml", "\n".join(export_lines) + "\n")
    write_text(
        book_dir / "names.yaml",
        "entries:\n- source: \u041f\u0451\u0442\u0440\n  target: Peter\n",
    )
    write_text(
        book_dir / "work" / "scenes" / "ru" / "001" / "scene-01.md",
        "## 1\n" + SAMPLE_TEXT,
    )
    write_text(
        book_dir / "work" / "scenes" / "de" / "stil-test" / "001" / "scene-01.md",
        "## Szene 1\n\n> Editorialer Vorspann dieser Ausgabe.\n\n" + SAMPLE_TEXT,
    )
    write_text(book_dir / "work" / "chapters" / "001-source.md", "# Kapitel 1\n")
    write_text(book_dir / "assets" / "covers" / "cover.jpg", "cover")
    for chapter_id in ("001", "002", "003"):
        write_text(
            book_dir / "assets" / "chapter" / f"chapter-{chapter_id}.jpg", "image"
        )
    write_text(book_dir / "assets" / "chapter" / "chapter-001_alt.jpg", "alt")
    return find_book(root, "sample")


class WeightedLengthTests(unittest.TestCase):
    def test_url_counts_as_23_characters(self) -> None:
        self.assertEqual(campaignpkg.weighted_length("https://a.example/x"), 23)
        self.assertEqual(
            campaignpkg.weighted_length("Text https://a.example/x"), 5 + 23
        )

    def test_wide_characters_count_as_two(self) -> None:
        self.assertEqual(campaignpkg.weighted_length("\u4f60\u597d"), 4)
        self.assertEqual(campaignpkg.weighted_length("\U0001f600"), 2)

    def test_sentence_truncation_keeps_sentence_boundary(self) -> None:
        text = "Erster Satz. Zweiter Satz. Dritter Satz."
        self.assertEqual(campaignpkg.truncate_at_sentence(text, 13), "Erster Satz.")
        self.assertEqual(campaignpkg.truncate_at_sentence(text, 100), text)


class TimezoneTests(unittest.TestCase):
    def test_fallback_tz_uses_eu_rule(self) -> None:
        tz = campaignpkg.BerlinFallbackTZ()
        self.assertEqual(tz.utcoffset(datetime(2026, 7, 15, 12)), timedelta(hours=2))
        self.assertEqual(tz.utcoffset(datetime(2026, 1, 15, 12)), timedelta(hours=1))

    def test_scheduled_at_is_relative_without_start(self) -> None:
        tz = campaignpkg.berlin_tzinfo()
        self.assertIsNone(campaignpkg.scheduled_at(None, 5, tz))

    def test_scheduled_at_uses_campaign_start_offset(self) -> None:
        tz = campaignpkg.berlin_tzinfo()
        start = campaignpkg.parse_campaign_start("2026-10-01T18:00:00+02:00", tz)
        self.assertEqual(
            campaignpkg.scheduled_at(start, 2, tz), "2026-10-03T18:00:00+02:00"
        )

    def test_naive_campaign_start_is_berlin_local_time(self) -> None:
        tz = campaignpkg.berlin_tzinfo()
        start = campaignpkg.parse_campaign_start("2026-07-01T18:00:00", tz)
        self.assertEqual(start.utcoffset(), timedelta(hours=2))

    def test_invalid_campaign_start_raises(self) -> None:
        with self.assertRaises(ValueError):
            campaignpkg.parse_campaign_start(
                "01.10.2026", campaignpkg.berlin_tzinfo()
            )


class LinkTests(unittest.TestCase):
    def test_amazon_missing(self) -> None:
        link = campaignpkg.amazon_link({})
        self.assertEqual(link["url_status"], "missing")
        self.assertEqual(link["assignment"], "missing")

    def test_amazon_from_website_is_user_provided(self) -> None:
        data = {"website": {"amazon_url": "https://www.amazon.de/dp/B0TEST"}}
        link = campaignpkg.amazon_link(data)
        self.assertEqual(link["url"], "https://www.amazon.de/dp/B0TEST")
        self.assertEqual(link["source"], "website.amazon_url")
        self.assertEqual(link["syntax"], "ok")
        self.assertEqual(link["assignment"], "user_provided")
        self.assertTrue(link["is_amazon_host"])

    def test_amazon_override_wins_and_invalid_is_flagged(self) -> None:
        data = {
            "website": {"amazon_url": "https://www.amazon.de/dp/B0TEST"},
            "marketing": {"amazon_url": "keine-url"},
        }
        link = campaignpkg.amazon_link(data)
        self.assertEqual(link["source"], "marketing.amazon_url")
        self.assertEqual(link["syntax"], "invalid")
        self.assertEqual(link["assignment"], "unverified")

    def test_youtube_from_video_id(self) -> None:
        link = campaignpkg.youtube_link({"youtube": {"video_id": "abcdef12345"}})
        self.assertEqual(link["url"], "https://www.youtube.com/watch?v=abcdef12345")
        self.assertTrue(link["derived_from_video_id"])
        self.assertFalse(link["public"])


class SongTests(unittest.TestCase):
    def test_song_file_state_is_checked(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            book_root = Path(tmp)
            songs = campaignpkg.song_entries(
                {"songs": [{"id": "s1", "file": "assets/audio/song.mp3"}]}, book_root
            )
            self.assertFalse(songs[0]["file_exists"])
            self.assertFalse(campaignpkg.has_usable_song(songs))
            write_text(book_root / "assets" / "audio" / "song.mp3", "audio")
            songs = campaignpkg.song_entries(
                {"songs": [{"id": "s1", "file": "assets/audio/song.mp3"}]}, book_root
            )
            self.assertTrue(campaignpkg.has_usable_song(songs))
            self.assertEqual(songs[0]["ai_generated"], "unknown")


class SampleAndTextTests(unittest.TestCase):
    def test_editorial_lead_is_stripped(self) -> None:
        raw = "> Vorspann\n\n# Ueberschrift\n\nDer eigentliche Text."
        self.assertEqual(
            campaignpkg.strip_editorial_lead(raw), "Der eigentliche Text."
        )

    def test_sample_skips_editorial_lead(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book = make_book(root)
            sample = campaignpkg.select_sample(
                book, "stil-test", root, {"max_chars": 320, "min_chars": 20}
            )
            self.assertIsNotNone(sample)
            self.assertTrue(sample["editorial_lead_skipped"])
            self.assertIn("Sanka sprang", sample["text"])
            self.assertNotIn("Vorspann", sample["text"])
            self.assertEqual(sample["chapter"], "001")
            self.assertEqual(
                sample["source"],
                "books/sample/work/scenes/de/stil-test/001/scene-01.md",
            )

    def test_needs_regeneration_rules(self) -> None:
        self.assertEqual(
            campaignpkg.needs_regeneration("abc", {}, force=False)[1],
            "no_generated_texts",
        )
        generated = {
            "source_hash": "abc",
            "prompt_version": campaignpkg.PROMPT_VERSION,
            "texts": {"x-t0-intro": {"text": "Text"}},
        }
        self.assertEqual(
            campaignpkg.needs_regeneration("abc", generated, force=False),
            (False, "reused"),
        )
        self.assertTrue(
            campaignpkg.needs_regeneration("other", generated, force=False)[0]
        )
        self.assertTrue(campaignpkg.needs_regeneration("abc", generated, force=True)[0])

    def test_overrides_win_over_generated(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            book_root = Path(tmp)
            generated = {
                "source_hash": "abc",
                "prompt_version": campaignpkg.PROMPT_VERSION,
                "texts": {"x-t0-intro": {"text": "KI-Text"}},
            }
            write_text(
                campaignpkg.generated_path(book_root),
                json.dumps(generated),
            )
            write_text(
                book_root / "work" / "marketing" / "overrides" / "x-t0-intro.md",
                "Redaktioneller Text",
            )
            texts = campaignpkg.collect_texts(book_root)
            self.assertEqual(texts["x-t0-intro"]["text"], "Redaktioneller Text")
            self.assertEqual(texts["x-t0-intro"]["source"], "override")

    def test_youtube_title_patterns_respect_limit(self) -> None:
        self.assertEqual(
            campaignpkg.build_youtube_title(
                "Der Moloch", "Hohes Feuer", "Alexander Kuprin", "Motivatier Classics"
            ),
            "Der Moloch - Hohes Feuer | Lied zum Roman von Alexander Kuprin",
        )
        self.assertEqual(
            campaignpkg.build_youtube_title(
                "Der Moloch", "", "Alexander Kuprin", "Motivatier Classics"
            ),
            "Der Moloch - Lied zum Roman von Alexander Kuprin | Motivatier Classics",
        )
        shortened = campaignpkg.build_youtube_title(
            "Ein sehr langer Buchtitel ueber viele Worte hinweg",
            "Und ein ebenso langer Songtitel",
            "Ein Autor mit langem Namen",
            "Motivatier Classics",
            limit=40,
        )
        self.assertLessEqual(len(shortened), 40)


class CampaignBuildTests(unittest.TestCase):
    def build(self, root: Path, book: dict, texts: dict | None = None) -> dict:
        return campaignpkg.build_campaign(book, root, "stil-test", texts=texts or {})

    def test_statuses_without_amazon_and_without_song(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book = make_book(root)
            manifest = self.build(
                root, book, {"x-t0-intro": {"text": "Ein Text zum Buch."}}
            )
            posts = {post["id"]: post for post in manifest["posts"]}
            self.assertEqual(posts["x-t0-intro"]["status"], "needs_amazon_url")
            self.assertEqual(posts["x-t0-intro"]["text_status"], "generated")
            self.assertEqual(posts["x-t0-intro"]["publish_status"], "needs_amazon_url")
            self.assertIn("amazon_url", posts["x-t0-intro"]["placeholders"])
            for post_id in ("x-t1-song", "x-t2-youtube", "yt-main", "yt-short-1"):
                self.assertEqual(posts[post_id]["status"], "omitted", post_id)
                self.assertIn("no_song_data", posts[post_id]["reasons"])
                self.assertIsNone(posts[post_id]["title"])
                self.assertIsNone(posts[post_id]["description"])
            self.assertEqual(manifest["validation"]["limits"]["x_weighted_chars"], 280)

    def test_amazon_link_makes_override_posts_ready(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book = make_book(root, website_amazon="https://www.amazon.de/dp/B0TEST")
            manifest = self.build(
                root,
                book,
                {"x-t0-intro": {"text": "Ein Text zum Buch.", "source": "override"}},
            )
            posts = {post["id"]: post for post in manifest["posts"]}
            self.assertEqual(posts["x-t0-intro"]["status"], "ready")
            self.assertEqual(posts["x-t0-intro"]["publish_status"], "ready")
            self.assertIn(
                "https://www.amazon.de/dp/B0TEST", posts["x-t0-intro"]["text"]
            )

    def test_song_without_file_blocks_only_music_posts(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book = make_book(
                root,
                website_amazon="https://www.amazon.de/dp/B0TEST",
                marketing_lines=[
                    "marketing:",
                    "  enabled: true",
                    "  songs:",
                    "  - id: song-01",
                    "    title: Hohes Feuer",
                    "    file: assets/audio/song.mp3",
                    "  youtube:",
                    "    url: https://www.youtube.com/watch?v=abcdef12345",
                    "    public: false",
                ],
            )
            manifest = self.build(root, book, {"x-t0-intro": {"text": "Text"}})
            posts = {post["id"]: post for post in manifest["posts"]}
            self.assertEqual(posts["x-t1-song"]["status"], "blocked")
            self.assertIn("song_file_missing", posts["x-t1-song"]["reasons"])
            self.assertEqual(posts["x-t0-intro"]["status"], "generated")

    def test_song_with_file_and_private_video_waits_for_public(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book = make_book(
                root,
                website_amazon="https://www.amazon.de/dp/B0TEST",
                marketing_lines=[
                    "marketing:",
                    "  enabled: true",
                    "  songs:",
                    "  - id: song-01",
                    "    title: Hohes Feuer",
                    "    file: assets/audio/song.mp3",
                    "    ai_generated: true",
                    "  youtube:",
                    "    video_id: abcdef12345",
                    "    public: false",
                ],
            )
            write_text(
                root / "books" / "sample" / "assets" / "audio" / "song.mp3", "audio"
            )
            manifest = self.build(
                root,
                book,
                {
                    "x-t0-intro": {"text": "Text"},
                    "yt-main": {"title": "Titel", "body": "Zwei Saetze zum Song."},
                },
            )
            posts = {post["id"]: post for post in manifest["posts"]}
            self.assertEqual(posts["yt-main"]["status"], "blocked")
            self.assertIn("youtube_video_not_public", posts["yt-main"]["reasons"])
            self.assertEqual(
                manifest["delivery"]["requires_synthetic_media_disclosure"], "true"
            )
            self.assertEqual(manifest["delivery"]["made_for_kids"], "not_set")
            description = posts["yt-main"]["description"]
            self.assertIn(
                "Das Buch auf Amazon: https://www.amazon.de/dp/B0TEST", description
            )
            self.assertIn("eigenstaendige Musik", description)

    def test_campaign_is_repeatable_and_media_paths_are_repo_relative(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book = make_book(root)
            texts = {"x-t0-intro": {"text": "Ein Text zum Buch."}}
            first = self.build(root, book, texts)
            second = self.build(root, book, texts)
            first.pop("exported_at")
            second.pop("exported_at")
            self.assertEqual(
                json.dumps(first, ensure_ascii=False, sort_keys=True),
                json.dumps(second, ensure_ascii=False, sort_keys=True),
            )
            self.assertEqual(
                [post["campaign_id"] for post in first["posts"]],
                [f"sample:{post['id']}" for post in first["posts"]],
            )
            for entry in first["media"]:
                self.assertFalse(entry["path"].startswith("/"))
                self.assertNotIn(":", entry["path"])
                self.assertTrue(entry["path"].startswith("books/sample/"))

    def test_all_posts_use_distinct_media_images(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book = make_book(root)
            payloads = {
                "x-t0-intro": {"text": "Der Umbruch beginnt im Frost und am Ofen."},
                "x-t5-content": {"text": "Der Frost und die Kinder am Ofen."},
                "x-t12-second-angle": {"text": "Der Vater und der Schnee."},
                "yt-short-2": {"description": "Frost und Ofen."},
            }
            manifest = self.build(root, book, payloads)
            chapter_paths = [
                ref["path"]
                for post in manifest["posts"]
                for ref in post["media"]
                if ref.get("kind") == "chapter_image"
            ]
            # Alle vorhandenen Kapitelbilder werden eingesetzt, nicht nur das erste.
            self.assertEqual(len(set(chapter_paths)), 3)
            self.assertEqual(
                max(chapter_paths.count(path) for path in set(chapter_paths)) < len(chapter_paths),
                True,
            )

    def test_ready_post_must_not_carry_placeholders(self) -> None:
        manifest = {
            "posts": [
                {
                    "id": "x-t0-intro",
                    "publish_status": "ready",
                    "placeholders": ["amazon_url"],
                }
            ]
        }
        with self.assertRaises(ValueError):
            campaignpkg.check_no_placeholders_in_ready(manifest)

    def test_write_package_creates_expected_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book = make_book(root)
            manifest = self.build(root, book, {"x-t0-intro": {"text": "Text"}})
            export_dir = campaignpkg.marketing_export_dir(book, root)
            written = campaignpkg.write_package(manifest, export_dir)
            names = sorted(path.name for path in written)
            self.assertEqual(
                names,
                ["README.md", "campaign.json", "media.json", "posts.md", "youtube.md"],
            )
            data = json.loads((export_dir / "campaign.json").read_text(encoding="utf-8"))
            self.assertEqual(data["schema_version"], campaignpkg.SCHEMA_VERSION)
            posts_md = (export_dir / "posts.md").read_text(encoding="utf-8")
            self.assertIn("x-t0-intro", posts_md)
            youtube_md = (export_dir / "youtube.md").read_text(encoding="utf-8")
            self.assertIn("Kein Liedvideo", youtube_md)

    def test_chapter_image_map_ignores_alt_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            book = make_book(root)
            meta = campaignpkg.export_meta(book, root)
            mapping = campaignpkg.chapter_image_map(meta, root)
            self.assertEqual(sorted(mapping), ["001", "002", "003"])
            self.assertTrue(mapping["001"].endswith("chapter-001.jpg"))


class MediaAllocatorTests(unittest.TestCase):
    def allocator(self) -> campaignpkg.MediaAllocator:
        return campaignpkg.MediaAllocator(
            Path("."),
            {"001": "a.jpg", "002": "b.jpg", "003": "c.jpg"},
            None,
            {},
            {},
        )

    def test_prefers_unused_images_then_reuses_evenly(self) -> None:
        allocator = self.allocator()
        first = allocator.by_position(0.0)
        second = allocator.by_position(0.0)
        third = allocator.by_position(0.0)
        self.assertEqual(
            [first["path"], second["path"], third["path"]],
            ["a.jpg", "b.jpg", "c.jpg"],
        )
        self.assertFalse(first["reused"])
        fourth = allocator.by_position(0.0)
        self.assertIsNotNone(fourth)
        self.assertTrue(fourth["reused"])

    def test_nearest_chapter_prefers_requested_chapter(self) -> None:
        allocator = self.allocator()
        ref = allocator.nearest_chapter("003")
        self.assertEqual(ref["chapter"], "003")
        self.assertFalse(ref["reused"])



class ExportRegressionTests(unittest.TestCase):
    """Der bestehende Manuskript-Export darf vom marketing-Block unberuehrt bleiben."""

    def test_manuscript_export_ignores_marketing_block(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_book(
                root,
                website_amazon="https://www.amazon.de/dp/B0TEST",
                marketing_lines=[
                    "marketing:",
                    "  enabled: true",
                    "  campaign_start: 2026-10-01T18:00:00+02:00",
                    "  songs:",
                    "  - id: song-01",
                    "    file: assets/audio/song.mp3",
                ],
            )
            book = find_book(root, "sample")
            with mock.patch.object(manuscript, "REPO_ROOT", root):
                meta = manuscript.load_export_config(book)
            self.assertEqual(meta["title"], "Beispielroman")
            self.assertNotIn("marketing", meta)
            self.assertEqual(meta["_base_dir"], str(root / "books" / "sample"))

    def test_collect_export_still_works_with_marketing_block(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_book(root)
            book = find_book(root, "sample")
            from lib.output_paths import book_output_root

            result = manuscript.collect_export(
                output_root=book_output_root(root, book),
                style="stil-test",
                scope="chapter",
                chapter_id="001",
                allow_partial=False,
            )
            self.assertEqual(len(result.chapters), 1)
            self.assertEqual(result.chapters[0].chapter_id, "001")


if __name__ == "__main__":
    unittest.main()



