#!/usr/bin/env python3
"""Fail when source files contain local absolute filesystem paths."""
from __future__ import annotations

import argparse
import re
from pathlib import Path


SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", "workspace", "archives"}
SKIP_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".zip", ".pyc"}
WINDOWS_PATH_PATTERN = re.compile(r"\b[A-Za-z]:[\\/][^\s\"'<>)]*")
UNC_PATH_PATTERN = re.compile(r"\\\\[A-Za-z0-9_.-]+\\[^\s\"'<>)]*")
LOCAL_UNIX_PATH_PATTERN = re.compile(r"(?<![\w:])/(?:Users|home|mnt|Volumes|tmp|var)/[^\s\"'<>)]*")
BAD_PATH_TOKENS = ("Mye" + "Drive", "Mys" + "Drive", "Leart" + "ing")


def should_skip(path: Path, root: Path) -> bool:
    relative = path.relative_to(root)
    if any(part in SKIP_DIRS for part in relative.parts):
        return True
    return path.suffix.lower() in SKIP_EXTENSIONS


def scan_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="ignore")
    failures: list[str] = []
    for pattern in (WINDOWS_PATH_PATTERN, UNC_PATH_PATTERN, LOCAL_UNIX_PATH_PATTERN):
        for match in pattern.findall(text):
            failures.append(f"{path.as_posix()} contains absolute path {match}")
    for token in BAD_PATH_TOKENS:
        if token in text:
            failures.append(f"{path.as_posix()} contains typo path token {token}")
    return failures


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file() or should_skip(path, root):
            continue
        failures.extend(scan_file(path))
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=".", help="Folder to validate")
    args = parser.parse_args(argv)

    failures = validate(Path(args.target).resolve())
    if failures:
        print("relative path gate: fail")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("relative path gate: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
