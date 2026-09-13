"""x_clip.py
===========

Rendert einen quadratischen X-Clip (MP4) aus Coverbild + Song-Ausschnitt.

X kann keine reinen Audiodateien abspielen. Deshalb wird fuer Musikpositionen
ein statisches Covervideo erzeugt: unscharfer Vollformat-Hintergrund aus dem
Cover, scharfes Cover in der Mitte, darunter der Song-Ausschnitt als AAC-Ton.

Die Funktion ist bewusst deterministisch: kein Refrain-Auto, kein Ken-Burns.
Start und Dauer kommen aus Parametern und werden im Ergebnis dokumentiert.

Benötigt ein System-``ffmpeg``/``ffprobe`` im PATH (kein Python-Paket).
"""

from __future__ import annotations

import json
import shutil
import subprocess
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


DEFAULT_SIZE = 1080
DEFAULT_DURATION = 45.0
DEFAULT_START = 0.0
DEFAULT_CRF = 21
DEFAULT_PRESET = "medium"
DEFAULT_FPS = 30
CLIPS_SUBDIR = "clips"


class XClipError(RuntimeError):
    """Fehler beim Rendern des X-Clips (ffmpeg fehlt, Datei fehlt, ...)."""


@dataclass
class XClipRequest:
    """Parameter eines X-Clip-Renders."""

    cover: Path
    audio: Path
    output: Path
    start: float = DEFAULT_START
    duration: float = DEFAULT_DURATION
    size: int = DEFAULT_SIZE
    crf: int = DEFAULT_CRF
    preset: str = DEFAULT_PRESET
    fps: int = DEFAULT_FPS
    title: str = ""
    overwrite: bool = False


@dataclass
class XClipResult:
    """Ergebnis eines X-Clip-Renders."""

    output: Path
    check_image: Path
    command: list[str]
    duration: float
    song_duration: float
    start: float
    warnings: list[str] = field(default_factory=list)


def check_ffmpeg() -> dict[str, str | None]:
    """Prueft, ob ffmpeg/ffprobe im PATH verfuegbar sind."""
    return {
        "ffmpeg": shutil.which("ffmpeg"),
        "ffprobe": shutil.which("ffprobe"),
    }


def require_ffmpeg() -> None:
    """Wirft XClipError, wenn ffmpeg/ffprobe fehlen."""
    found = check_ffmpeg()
    missing = sorted(name for name, path in found.items() if not path)
    if missing:
        raise XClipError(
            "ffmpeg/ffprobe nicht gefunden "
            f"({', '.join(missing)} fehlt im PATH). "
            "Installation z. B. per winget: "
            "winget install --id Gyan.FFmpeg"
        )


def default_clip_name(song_id: str, duration: float) -> str:
    """Leitet den Clip-Dateinamen aus Song-ID und Dauer ab."""
    seconds = int(duration) if float(duration).is_integer() else duration
    return f"{song_id}-x-{seconds}s.mp4"


def build_filter(size: int) -> str:
    """Baut die Quadrat-Filterkette (Blur-BG, Cover, Shadow)."""
    inner = int(size * 880 / 1080)
    shadow = int(size * 900 / 1080)
    return (
        "[0:v]split=2[bg0][fg0];"
        f"[bg0]scale={size}:{size}:force_original_aspect_ratio=increase,"
        f"crop={size}:{size},gblur=sigma=24,"
        "eq=brightness=-0.22:saturation=0.82[bg];"
        f"[fg0]scale={inner}:{inner}:force_original_aspect_ratio=decrease[fg];"
        f"color=c=black@0.34:s={shadow}x{shadow},format=rgba[shadow];"
        "[bg][shadow]overlay=(W-w)/2:(H-h)/2[base];"
        "[base][fg]overlay=(W-w)/2:(H-h)/2:format=auto,format=yuv420p[v]"
    )


def build_command(request: XClipRequest) -> list[str]:
    """Baut den ffmpeg-Befehl fuer einen X-Clip."""
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "warning",
        "-loop", "1", "-framerate", str(request.fps),
        "-i", str(request.cover),
        "-ss", f"{request.start:g}", "-i", str(request.audio),
        "-t", f"{request.duration:g}",
        "-filter_complex", build_filter(request.size),
        "-map", "[v]", "-map", "1:a:0",
        "-c:v", "libx264", "-preset", request.preset,
        "-crf", str(request.crf), "-pix_fmt", "yuv420p",
        "-r", str(request.fps),
        "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2",
        "-movflags", "+faststart",
    ]
    if request.title:
        cmd += ["-metadata", f"title={request.title}"]
    cmd += [
        "-metadata", "comment=fixed square preview (static cover)",
        str(request.output),
    ]
    return cmd

def probe_duration(path: Path) -> float:
    """Liest die Mediendauer per ffprobe aus."""
    raw = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
        capture_output=True, text=True, check=False,
    )
    if raw.returncode != 0:
        raise XClipError(f"ffprobe scheiterte fuer {path}: {raw.stderr.strip()}")
    try:
        return float(raw.stdout.strip())
    except ValueError as exc:
        raise XClipError(f"ffprobe lieferte keine Dauer fuer {path}") from exc


def detect_leading_silence(audio: Path, window: float = 60.0) -> float:
    """Sucht fuehrende Stille (unter -45 dB, mind. 0,4 s), meldet deren Ende."""
    raw = subprocess.run(
        ["ffmpeg", "-hide_banner", "-nostats", "-i", str(audio),
         "-t", f"{window:g}",
         "-af", "silencedetect=noise=-45dB:d=0.4", "-f", "null", "-"],
        capture_output=True, text=True, check=False,
    )
    end = 0.0
    for line in (raw.stderr or "").splitlines():
        if "silence_end" in line and "silence_duration" in line:
            try:
                token = [t for t in line.split() if t.startswith("silence_end:")][0]
                end = float(token.split(":", 1)[1])
            except (IndexError, ValueError):
                continue
            break
    return end


def verify_clip(path: Path, expected_duration: float) -> dict[str, Any]:
    """Verifiziert Dauer und Laedbarkeit des gerenderten Clips."""
    raw = subprocess.run(
        ["ffprobe", "-v", "error",
         "-show_entries",
         "format=duration,size:stream=index,codec_name,codec_type,"
         "width,height,pix_fmt,avg_frame_rate,sample_rate,channels",
         "-of", "json", str(path)],
        capture_output=True, text=True, check=False,
    )
    if raw.returncode != 0:
        raise XClipError(f"Verifikation scheiterte fuer {path}: {raw.stderr.strip()}")
    try:
        info = json.loads(raw.stdout or "{}")
    except json.JSONDecodeError as exc:
        raise XClipError(f"ffprobe-JSON ungueltig fuer {path}") from exc
    duration = float(info.get("format", {}).get("duration") or 0.0)
    if abs(duration - expected_duration) > 0.6:
        raise XClipError(
            f"Clip-Dauer {duration:.1f}s weicht von {expected_duration:g}s ab"
        )
    size = int(info.get("format", {}).get("size") or path.stat().st_size)
    return {"duration": duration, "size": size, "info": info}


def extract_check_image(clip: Path, target: Path) -> Path:
    """Extrahiert ein Kontrollbild aus der Clip-Mitte."""
    duration = probe_duration(clip)
    middle = max(duration / 2.0, 0.5)
    raw = subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error",
         "-ss", f"{middle:.1f}", "-i", str(clip),
         "-frames:v", "1", "-q:v", "2", str(target)],
        capture_output=True, text=True, check=False,
    )
    if raw.returncode != 0:
        raise XClipError(f"Kontrollbild scheiterte: {raw.stderr.strip()}")
    return target


def render(request: XClipRequest) -> XClipResult:
    """Rendert den X-Clip (ffmpeg) und verifiziert das Ergebnis."""
    require_ffmpeg()
    if not request.cover.is_file():
        raise XClipError(f"Cover nicht gefunden: {request.cover}")
    if not request.audio.is_file():
        raise XClipError(f"Audio nicht gefunden: {request.audio}")
    if request.output.exists() and not request.overwrite:
        raise XClipError(
            f"Zieldatei existiert bereits: {request.output} (--overwrite)"
        )
    if request.start < 0:
        raise XClipError("Start darf nicht negativ sein")
    if request.duration <= 0:
        raise XClipError("Dauer muss groesser als 0 sein")

    song_duration = probe_duration(request.audio)
    warnings: list[str] = []
    if request.start >= song_duration:
        raise XClipError(
            f"Start {request.start:g}s liegt hinter dem Songende ({song_duration:.1f}s)"
        )
    if request.start + request.duration > song_duration + 0.25:
        warnings.append(
            f"Song ist nur {song_duration:.1f}s lang; "
            f"Clip endet bei {request.start + request.duration:g}s."
        )
    silence_end = detect_leading_silence(request.audio)
    if silence_end > 0.5 and request.start < silence_end:
        warnings.append(
            f"Fuehrende Stille bis ca. {silence_end:.1f}s erkannt; "
            f"Start {request.start:g}s verwendet (kein Auto-Versatz)."
        )

    command = build_command(request)
    request.output.parent.mkdir(parents=True, exist_ok=True)
    raw = subprocess.run(command, capture_output=True, text=True, check=False)
    if raw.returncode != 0:
        raise XClipError(f"ffmpeg scheiterte: {(raw.stderr or '').strip()[-2000:]}")

    verified = verify_clip(request.output, request.duration)
    check_image = request.output.with_name(request.output.stem + "-check.jpg")
    extract_check_image(request.output, check_image)
    return XClipResult(
        output=request.output,
        check_image=check_image,
        command=command,
        duration=float(verified["duration"]),
        song_duration=song_duration,
        start=request.start,
        warnings=warnings,
    )

