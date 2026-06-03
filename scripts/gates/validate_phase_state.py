#!/usr/bin/env python3
"""Validate MAS phase transitions when runtime state exists."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load_state(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("workspace/state.json must be a list")
    return [entry for entry in payload if isinstance(entry, dict)]


def has_blueprint_approval(entries: list[dict[str, Any]]) -> bool:
    for entry in entries:
        text = " ".join(str(entry.get(key, "")) for key in ("type", "phase", "message", "approver"))
        if "approval" in text.lower() and "phase_1_blueprint" in text and "Approved" in text and "user" in text:
            return True
    return False


def phase_2_started(entries: list[dict[str, Any]]) -> bool:
    for entry in entries:
        phase = str(entry.get("phase", ""))
        entry_type = str(entry.get("type", "")).lower()
        if phase == "phase_2_webflow_build" or "webflow" in entry_type:
            return True
    return False


def validate(root: Path) -> list[str]:
    state_path = root / "workspace" / "state.json"
    if not state_path.exists():
        return []
    try:
        entries = load_state(state_path)
    except (OSError, json.JSONDecodeError, ValueError) as error:
        return [f"workspace/state.json invalid: {error}"]

    if phase_2_started(entries) and not has_blueprint_approval(entries):
        return ["phase_2_webflow_build started without user approval for phase_1_blueprint"]
    return []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=".", help="Folder to validate")
    args = parser.parse_args(argv)

    failures = validate(Path(args.target).resolve())
    if failures:
        print("phase state gate: fail")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("phase state gate: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

