#!/usr/bin/env python3
"""Scan committed files for common secret patterns."""
from __future__ import annotations

import argparse
import re
from pathlib import Path


SKIP_DIRS = {".git", ".venv", "venv", "__pycache__", "node_modules", "workspace", "archives"}
SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token|password)\s*[:=]\s*['\"]?[A-Za-z0-9_\-]{16,}"),
    re.compile(r"sk-[A-Za-z0-9]{20,}"),
    re.compile(r"xox[baprs]-[A-Za-z0-9\-]{20,}"),
]


def should_skip(path: Path) -> bool:
    return any(part in SKIP_DIRS for part in path.parts)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def scan(root: Path) -> list[str]:
    findings: list[str] = []
    for path in root.rglob("*"):
        if should_skip(path) or not path.is_file():
            continue
        text = read_text(path)
        if any(pattern.search(text) for pattern in SECRET_PATTERNS):
            findings.append(str(path.relative_to(root)))
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=".", help="Folder to scan")
    args = parser.parse_args(argv)

    findings = scan(Path(args.target).resolve())
    if findings:
        print("secret scan: fail")
        for finding in findings:
            print(f"  - {finding}")
        return 1
    print("secret scan: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

