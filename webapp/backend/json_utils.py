"""JSON helpers for API responses built from local workbench objects."""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any


def jsonable(value: Any, repo_root: Path | None = None) -> Any:
    """Convert local service objects into plain JSON-compatible structures."""
    if is_dataclass(value):
        return jsonable(asdict(value), repo_root)
    if isinstance(value, Path):
        if repo_root is not None:
            try:
                return value.resolve().relative_to(repo_root.resolve()).as_posix()
            except ValueError:
                pass
        return value.as_posix()
    if isinstance(value, dict):
        return {str(key): jsonable(item, repo_root) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [jsonable(item, repo_root) for item in value]
    return value
