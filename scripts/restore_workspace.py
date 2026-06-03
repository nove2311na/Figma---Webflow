#!/usr/bin/env python3
"""Restore a workspace archive into an empty workspace."""
from __future__ import annotations

import argparse
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKSPACE_DIR = ROOT / "workspace"
ARCHIVES_DIR = ROOT / "archives"


def list_archives() -> list[Path]:
    """Return workspace archives sorted by name."""
    if not ARCHIVES_DIR.exists():
        return []
    return sorted(path for path in ARCHIVES_DIR.iterdir() if path.suffix.lower() == ".zip")


def resolve_archive(selector: str) -> Path:
    """Resolve an archive by numeric index or filename."""
    archives = list_archives()
    if selector.isdigit():
        index = int(selector)
        if 0 <= index < len(archives):
            return archives[index]
    archive_path = ARCHIVES_DIR / selector
    if archive_path.exists() and archive_path.suffix.lower() == ".zip":
        return archive_path
    raise FileNotFoundError(f"archive not found: {selector}")


def ensure_safe_member(destination: Path, member_name: str) -> Path:
    """Prevent zip path traversal."""
    target = (destination / member_name).resolve()
    if destination.resolve() not in target.parents and target != destination.resolve():
        raise RuntimeError(f"unsafe archive member: {member_name}")
    return target


def restore(selector: str) -> Path:
    """Restore selected archive into an empty workspace."""
    archive_path = resolve_archive(selector)
    WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
    if any(WORKSPACE_DIR.iterdir()):
        raise RuntimeError("workspace is not empty; archive current workspace before restore")

    with zipfile.ZipFile(archive_path) as archive:
        for member in archive.infolist():
            target = ensure_safe_member(WORKSPACE_DIR, member.filename)
            if member.is_dir():
                target.mkdir(parents=True, exist_ok=True)
            else:
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(archive.read(member))
    return archive_path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", nargs="?", help="Archive filename or numeric index")
    args = parser.parse_args(argv)

    if not args.archive:
        archives = list_archives()
        if not archives:
            print("no archives found")
            return 0
        print("available archives:")
        for index, path in enumerate(archives):
            print(f"[{index}] {path.name}")
        return 0

    archive_path = restore(args.archive)
    print(f"workspace restored from: {archive_path.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

