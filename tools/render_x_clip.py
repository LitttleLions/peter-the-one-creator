#!/usr/bin/env python
"""
render_x_clip.py
================

Rendert einen quadratischen X-Clip (MP4) aus Coverbild + Song-Ausschnitt.

X kann keine reinen Audiodateien abspielen; der Clip ist ein statisches
Covervideo (1080x1080, H.264 + AAC, faststart) als Anhang fuer X-Posts.

Der Befehl veraendert keine Quellen (Cover, Audio) und veroeffentlicht
nichts. Benötigt System-ffmpeg/ffprobe im PATH.
"""

from __future__ import annotations

import argparse
import io
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))

from lib import x_clip as xclip  # noqa: E402
from lib.book_project import find_book  # noqa: E402
from lib import marketing_campaign as campaign  # noqa: E402


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="X-Clip (Covervideo aus Cover + Song) rendern."
    )
    parser.add_argument("--book", default=None, help="Buch-ID")
    parser.add_argument("--song", default="song-01", help="Song-ID aus export.yaml")
    parser.add_argument("--cover", default=None, help="Coverpfad (repo-relativ)")
    parser.add_argument("--start", type=float, default=0.0, help="Startsekunde")
    parser.add_argument("--duration", type=float, default=45.0, help="Clipdauer")
    parser.add_argument("--size", type=int, default=1080, help="Quadratkante")
    parser.add_argument("--crf", type=int, default=21, help="x264-Qualitaet")
    parser.add_argument("--preset", default="medium", help="x264-Preset")
    parser.add_argument("--fps", type=int, default=30, help="Bildrate")
    parser.add_argument("--out", default=None, help="Zieldatei (repo-relativ)")
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args(argv)


def _repo_rel(repo_root: Path, path: Path) -> str:
    try:
        return path.resolve().relative_to(repo_root.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def resolve_inputs(book: dict, repo_root: Path, args: argparse.Namespace):
    book_root = campaign.book_root(book, repo_root)
    export_data = campaign.load_export_data(book, repo_root)
    marketing = campaign.marketing_block(export_data)
    songs = campaign.song_entries(marketing, book_root)
    song = next((s for s in songs if s["id"] == args.song), None)
    if song is None:
        ids = ", ".join(s["id"] for s in songs) or "keine Songs in export.yaml"
        raise ValueError(f"Song '{args.song}' nicht gefunden ({ids})")
    if not song["file_exists"]:
        raise ValueError(f"Songdatei fehlt: {song['file']}")
    audio = book_root / song["file"]
    if args.cover:
        cover = (repo_root / args.cover) if not Path(args.cover).is_absolute() else Path(args.cover)
    else:
        meta = campaign.export_meta(book, repo_root)
        cover_rel = str((meta.get("cover") or {}).get("image_path") or "")
        if not cover_rel:
            raise ValueError("Kein Cover in export.yaml (cover.image_path leer)")
        cover = (repo_root / meta["_base_dir"]) / cover_rel
    if not cover.is_file():
        raise ValueError(f"Cover nicht gefunden: {cover}")
    if args.out:
        out = (repo_root / args.out) if not Path(args.out).is_absolute() else Path(args.out)
    else:
        out = (
            campaign.marketing_export_dir(book, repo_root)
            / xclip.CLIPS_SUBDIR
            / xclip.default_clip_name(song["id"], args.duration)
        )
    title = f"{book.get('title')} - {song['title'] or song['id']} | X-Preview"
    return audio, cover, out, title, song


def main(argv: list[str] | None = None) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        if hasattr(sys.stdout, "buffer"):
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    args = parse_args(argv)
    try:
        book = find_book(REPO_ROOT, args.book)
        audio, cover, out, title, song = resolve_inputs(book, REPO_ROOT, args)
        request = xclip.XClipRequest(
            cover=cover, audio=audio, output=out,
            start=args.start, duration=args.duration, size=args.size,
            crf=args.crf, preset=args.preset, fps=args.fps,
            title=title, overwrite=args.overwrite,
        )
    except (ValueError, FileNotFoundError) as exc:
        print(f"FEHLER: {exc}")
        return 1
    print(f"=== X-Clip: {book.get('title')} ({book.get('id')}) ===")
    print(f"Song: {song['id']} ({song['title'] or 'ohne Titel'}) "
          f"[ai_generated={song['ai_generated']}]")
    print(f"Cover: {_repo_rel(REPO_ROOT, cover)}")
    print(f"Audio: {_repo_rel(REPO_ROOT, audio)}")
    print(f"Ziel: {_repo_rel(REPO_ROOT, out)} "
          f"(Start {args.start:g}s, Dauer {args.duration:g}s)")
    try:
        found = xclip.check_ffmpeg()
    except Exception:
        found = {}
    if not found.get("ffmpeg") or not found.get("ffprobe"):
        print("FEHLER: ffmpeg/ffprobe nicht im PATH. "
              "Installation z. B.: winget install --id Gyan.FFmpeg")
        return 1
    if args.dry_run:
        print("[dry-run] ffmpeg-Befehl:")
        print("  " + " ".join(xclip.build_command(request)))
        print("[dry-run] keine Datei geschrieben")
        return 0
    try:
        result = xclip.render(request)
    except xclip.XClipError as exc:
        print(f"FEHLER: {exc}")
        return 1
    print(f"Songlaenge: {result.song_duration:.1f}s")
    for warning in result.warnings:
        print(f"Hinweis: {warning}")
    print(f"Geschrieben: {_repo_rel(REPO_ROOT, result.output)} "
          f"({result.output.stat().st_size} Bytes, {result.duration:.1f}s)")
    print(f"Kontrollbild: {_repo_rel(REPO_ROOT, result.check_image)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
