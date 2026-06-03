#!/usr/bin/env python3
"""Check Webflow action entries for required ReAct fields."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_REACT_FIELDS = ("reason", "action", "observation", "next_decision")


def load_entries(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        raise ValueError("state file must contain a list")
    return [entry for entry in payload if isinstance(entry, dict)]


def find_failures(entries: list[dict[str, Any]]) -> list[str]:
    failures: list[str] = []
    for index, entry in enumerate(entries):
        entry_type = str(entry.get("type", "")).lower()
        phase = str(entry.get("phase", "")).lower()
        if "webflow" not in entry_type and "phase_2_webflow_build" != phase:
            continue
        missing = [field for field in REQUIRED_REACT_FIELDS if not str(entry.get(field, "")).strip()]
        if missing:
            failures.append(f"entry {index} missing {', '.join(missing)}")
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("state_path", help="Path to workspace/state.json")
    args = parser.parse_args(argv)

    failures = find_failures(load_entries(Path(args.state_path)))
    if failures:
        print("react entry check: fail")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("react entry check: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

