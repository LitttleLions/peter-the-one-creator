"""Asset-Bildoptimierung: PNG/JPEG resize und JPEG-Exportkopien ohne Master-Loeschen."""

from __future__ import annotations

import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from PIL import Image


IMAGE_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")
JPEG_EXTENSIONS = (".jpg", ".jpeg")
ALT_SUFFIX = "_alt"

DEFAULT_ILLUSTRATION_PROCESSING: dict[str, Any] = {
    "format": "JPEG",
    "jpeg_quality": 60,
    "max_width": 1024,
    "max_height": 1024,
}

DEFAULT_COVER_PROCESSING: dict[str, Any] = {
    "format": "JPEG",
    "jpeg_quality": 75,
    "max_width": 1600,
    "max_height": 2400,
}

# Hochwertige Nebenkopie der Quelle (kein Resize), bevor Export-JPG ueberschrieben wird.
ARCHIVE_JPEG_PROCESSING: dict[str, Any] = {
    "format": "JPEG",
    "jpeg_quality": 92,
    "max_width": None,
    "max_height": None,
}


@dataclass(frozen=True)
class AssetKind:
    name: str  # cover | chapter | scene
    source: Path
    jpeg_target: Path
    processing: dict[str, Any]


def is_alt_stem(stem: str) -> bool:
    return stem.endswith(ALT_SUFFIX)


def alt_jpeg_path(destination: Path) -> Path:
    return destination.with_name(f"{destination.stem}{ALT_SUFFIX}.jpg")


def resize_image(image: Image.Image, processing: dict[str, Any]) -> Image.Image:
    max_w = processing.get("max_width")
    max_h = processing.get("max_height")
    if not max_w and not max_h:
        return image
    orig_w, orig_h = image.size
    target_w = int(max_w) if max_w else orig_w
    target_h = int(max_h) if max_h else orig_h
    if orig_w <= target_w and orig_h <= target_h:
        return image
    image = image.copy()
    image.thumbnail((target_w, target_h), Image.Resampling.LANCZOS)
    return image


def _write_jpeg_bytes(image: Image.Image, destination: Path, quality: int) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    rgb = image.convert("RGB")
    rgb.save(destination, format="JPEG", quality=quality, optimize=True)


def save_as_jpeg(source: Path, destination: Path, processing: dict[str, Any]) -> dict[str, Any]:
    """Write JPEG to destination. Never deletes PNG or ``*_alt.jpg`` masters.

    If source and destination are the same JPEG path, writes via a temp file
    and replaces in place.
    """
    quality = int(processing.get("jpeg_quality", 60))
    bytes_source = source.stat().st_size
    with Image.open(source) as image:
        before = image.size
        image = resize_image(image, processing)
        after = image.size
        destination.parent.mkdir(parents=True, exist_ok=True)
        same_file = source.resolve() == destination.resolve()
        if same_file:
            fd, tmp_name = tempfile.mkstemp(
                suffix=".jpg",
                prefix=f".{destination.stem}.",
                dir=str(destination.parent),
            )
            os.close(fd)
            tmp_path = Path(tmp_name)
            try:
                _write_jpeg_bytes(image, tmp_path, quality)
                tmp_path.replace(destination)
            except Exception:
                if tmp_path.exists():
                    tmp_path.unlink()
                raise
        else:
            _write_jpeg_bytes(image, destination, quality)
    return {
        "source": str(source),
        "destination": str(destination),
        "quality": quality,
        "size_before": before,
        "size_after": after,
        "bytes_source": bytes_source,
        "bytes_dest": destination.stat().st_size,
    }


def preserve_existing_jpeg(
    source: Path,
    destination: Path,
    processing: dict[str, Any] | None = None,
) -> Path | None:
    """Keep a higher-quality ``stem_alt.jpg`` before overwriting the export JPG.

    - If ``*_alt.jpg`` already exists: leave it untouched.
    - Else if source is PNG: write a full-size high-quality JPEG archive from PNG.
    - Else if destination JPG still looks larger than the export target: copy it
      to ``*_alt.jpg`` (skip if it is already at/under the export size).
    """
    alt = alt_jpeg_path(destination)
    if alt.exists():
        return None
    if source.suffix.lower() == ".png" and source.is_file():
        save_as_jpeg(source, alt, ARCHIVE_JPEG_PROCESSING)
        return alt
    if destination.is_file() and destination.suffix.lower() in JPEG_EXTENSIONS:
        if processing and not _jpeg_exceeds_target(destination, processing):
            return None
        shutil.copy2(destination, alt)
        return alt
    return None


def _jpeg_exceeds_target(path: Path, processing: dict[str, Any]) -> bool:
    max_w = processing.get("max_width")
    max_h = processing.get("max_height")
    if not max_w and not max_h:
        return True
    with Image.open(path) as image:
        width, height = image.size
    if max_w and width > int(max_w):
        return True
    if max_h and height > int(max_h):
        return True
    return False


def load_illustration_processing(book: dict[str, Any]) -> dict[str, Any]:
    cfg = dict(DEFAULT_ILLUSTRATION_PROCESSING)
    hf = book.get("higgsfield") or {}
    if not isinstance(hf, dict):
        return cfg
    ip = hf.get("image_processing")
    if not isinstance(ip, dict):
        return cfg
    for key in ("format", "jpeg_quality", "max_width", "max_height"):
        if key in ip and not isinstance(ip[key], dict):
            cfg[key] = ip[key]
    return cfg


def load_cover_processing(book: dict[str, Any]) -> dict[str, Any]:
    cfg = dict(DEFAULT_COVER_PROCESSING)
    illustration = load_illustration_processing(book)
    hf = book.get("higgsfield") or {}
    if not isinstance(hf, dict):
        return cfg
    ip = hf.get("image_processing")
    if not isinstance(ip, dict):
        return cfg
    cover = ip.get("cover")
    if isinstance(cover, dict):
        for key in ("format", "jpeg_quality", "max_width", "max_height"):
            if key in cover and not isinstance(cover[key], dict):
                cfg[key] = cover[key]
        return cfg
    if "format" in illustration:
        cfg["format"] = illustration["format"]
    if "jpeg_quality" in illustration:
        cfg["jpeg_quality"] = illustration["jpeg_quality"]
    return cfg


def _prefer_source(directory: Path, stem: str) -> Path | None:
    """Prefer PNG master, else ``*_alt.jpg`` archive, else export JPEG."""
    if is_alt_stem(stem):
        return None
    png = directory / f"{stem}.png"
    if png.is_file():
        return png
    alt = directory / f"{stem}{ALT_SUFFIX}.jpg"
    if alt.is_file():
        return alt
    for ext in JPEG_EXTENSIONS:
        candidate = directory / f"{stem}{ext}"
        if candidate.is_file():
            return candidate
    return None


def _collect_stems(directory: Path, pattern: str) -> set[str]:
    stems: set[str] = set()
    if not directory.is_dir():
        return stems
    for path in directory.glob(pattern):
        if not path.is_file() or path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        if is_alt_stem(path.stem):
            continue
        stems.add(path.stem)
    return stems


def discover_export_assets(
    book_root: Path,
    *,
    include_cover: bool = True,
    include_chapter: bool = True,
    include_scene: bool = True,
    include_test: bool = False,
    illustration_processing: dict[str, Any] | None = None,
    cover_processing: dict[str, Any] | None = None,
) -> list[AssetKind]:
    """Find cover/chapter/scene assets that should have an optimized .jpg."""
    assets = book_root / "assets"
    if not assets.is_dir():
        return []
    ill = illustration_processing or DEFAULT_ILLUSTRATION_PROCESSING
    cov = cover_processing or DEFAULT_COVER_PROCESSING
    found: list[AssetKind] = []

    if include_cover:
        covers = assets / "covers"
        if covers.is_dir():
            stems: set[str] = set()
            for path in covers.iterdir():
                if not path.is_file() or path.suffix.lower() not in IMAGE_EXTENSIONS:
                    continue
                if is_alt_stem(path.stem):
                    continue
                stems.add(path.stem)
            for stem in sorted(stems):
                source = _prefer_source(covers, stem)
                if source is None:
                    continue
                found.append(AssetKind("cover", source, covers / f"{stem}.jpg", cov))

    if include_chapter:
        chapter_dir = assets / "chapter"
        for stem in sorted(_collect_stems(chapter_dir, "chapter-*")):
            source = _prefer_source(chapter_dir, stem)
            if source is None:
                continue
            found.append(
                AssetKind("chapter", source, chapter_dir / f"{stem}.jpg", ill)
            )
        if include_test:
            test_dir = chapter_dir / "test"
            if test_dir.is_dir():
                for path in sorted(test_dir.iterdir()):
                    if not path.is_file() or path.suffix.lower() not in IMAGE_EXTENSIONS:
                        continue
                    if is_alt_stem(path.stem):
                        continue
                    source = _prefer_source(test_dir, path.stem)
                    if source is None:
                        continue
                    found.append(
                        AssetKind(
                            "chapter",
                            source,
                            test_dir / f"{path.stem}.jpg",
                            ill,
                        )
                    )

    if include_scene:
        scene_root = assets / "scene"
        if scene_root.is_dir():
            for chapter_dir in sorted(p for p in scene_root.iterdir() if p.is_dir()):
                for stem in sorted(_collect_stems(chapter_dir, "scene-*")):
                    source = _prefer_source(chapter_dir, stem)
                    if source is None:
                        continue
                    found.append(
                        AssetKind(
                            "scene",
                            source,
                            chapter_dir / f"{stem}.jpg",
                            ill,
                        )
                    )

    return found


# Backwards-compatible alias used by older callers/tests.
def discover_png_assets(*args: Any, **kwargs: Any) -> list[AssetKind]:
    return discover_export_assets(*args, **kwargs)


def plan_conversions(
    assets: list[AssetKind],
    *,
    skip_existing: bool = False,
) -> tuple[list[AssetKind], list[AssetKind]]:
    """Split into work vs skipped.

    Default: rewrite every .jpg target (PNG / ``*_alt.jpg`` masters stay untouched).
    With skip_existing=True: only create missing .jpg sidecars.
    """
    todo: list[AssetKind] = []
    skipped: list[AssetKind] = []
    for item in assets:
        if skip_existing and item.jpeg_target.exists():
            skipped.append(item)
        else:
            todo.append(item)
    return todo, skipped
