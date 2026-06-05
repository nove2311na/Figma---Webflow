"""Helpers for locating the repository root from nested skill scripts."""
from __future__ import annotations

from pathlib import Path


def find_repo_root(start: Path | None = None) -> Path:
    """Return the repo root by walking up from the given path."""
    current = (start or Path(__file__)).resolve()
    for candidate in [current, *current.parents]:
        if (candidate / ".claude").exists() and (candidate / "agentic").exists():
            return candidate
    raise RuntimeError("Could not locate repo root")


def resolve_repo_path(root: Path, value: str | Path | None) -> Path | None:
    """Resolve a path against the repo root unless it is already absolute."""
    if value is None:
        return None
    path = Path(value)
    return path if path.is_absolute() else root / path
