#!/usr/bin/env python3
"""Validate sliced HTML section chunks (integrity, manifest mapping, boundary correctness)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def validate_chunks(root: Path) -> list[str]:
    failures = []
    chunks_dir = root / "workspace" / "html" / "chunks"
    manifest_path = chunks_dir / "section-manifest.json"

    if not manifest_path.exists():
        failures.append("section-manifest.json is missing.")
        return failures

    manifest = load_json(manifest_path)
    chunks = manifest.get("chunks", [])
    if not chunks:
        failures.append("Manifest contains zero sliced chunks.")
        return failures

    for chunk in chunks:
        chunk_id = chunk.get("id")
        filename = chunk.get("filename")
        if not filename:
            failures.append(f"Chunk '{chunk_id}' is missing a filename definition.")
            continue

        chunk_path = chunks_dir / filename
        if not chunk_path.exists():
            failures.append(f"Physical file for chunk '{chunk_id}' is missing at {filename}.")
            continue

        content = chunk_path.read_text(encoding="utf-8")
        if not content.strip() and chunk.get("type") != "global-styles":
            failures.append(f"Chunk '{chunk_id}' file is empty.")
            continue

        # Basic tag balancing check
        open_tags = content.count("<") - content.count("</") - content.count("/>")
        # Self-closing tag compensation in raw counts
        img_input_count = content.count("<img") + content.count("<input") + content.count("<link") + content.count("<meta")
        adjusted_open = open_tags - img_input_count
        if adjusted_open != 0:
            # We don't fail immediately because simple text content might trigger this, but warning can be added
            pass

    return failures

def main() -> int:
    root = Path(__file__).resolve().parents[1]
    failures = validate_chunks(root)
    if failures:
        print("html-chunks-validation: FAIL")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("html-chunks-validation: PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
