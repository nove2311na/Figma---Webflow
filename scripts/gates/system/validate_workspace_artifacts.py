#!/usr/bin/env python3
"""Validate generated workspace artifacts when a workspace exists."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_REACT_FIELDS = ("reason", "action", "observation", "next_decision")
CORE_FILES = ("meta.json", "page_structure.json", "state.json", "error-logs.json")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def require_keys(payload: dict[str, Any], keys: tuple[str, ...], path: Path, failures: list[str]) -> None:
    for key in keys:
        if key not in payload or payload[key] in ("", None):
            failures.append(f"{path.as_posix()} missing {key}")


def validate_state_entries(entries: Any, path: Path) -> list[str]:
    failures: list[str] = []
    if not isinstance(entries, list):
        return [f"{path.as_posix()} must be a list"]

    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            failures.append(f"{path.as_posix()} entry {index} must be an object")
            continue
        require_keys(entry, ("agent", "phase", "type", "message"), path, failures)
        entry_type = str(entry.get("type", "")).lower()
        phase = str(entry.get("phase", "")).lower()
        if "webflow" in entry_type or phase == "phase_2_webflow_build":
            missing = [field for field in REQUIRED_REACT_FIELDS if not str(entry.get(field, "")).strip()]
            if missing:
                failures.append(f"{path.as_posix()} entry {index} missing ReAct fields: {', '.join(missing)}")
    return failures


def validate_workspace(root: Path) -> list[str]:
    workspace = root / "workspace"
    if not workspace.exists():
        return []

    failures: list[str] = []
    for filename in CORE_FILES:
        path = workspace / filename
        if not path.is_file():
            failures.append(f"workspace/{filename} is missing")

    for path in workspace.rglob("*.json"):
        try:
            payload = load_json(path)
        except (OSError, json.JSONDecodeError) as error:
            failures.append(f"{path.as_posix()} invalid JSON: {error}")
            continue

        if path.name == "meta.json" and isinstance(payload, dict):
            require_keys(payload, ("projectName", "figmaUrl", "initializedAt", "runtime"), path, failures)
        if path.name == "state.json":
            failures.extend(validate_state_entries(payload, path))
        if path.name == "error-logs.json" and not isinstance(payload, list):
            failures.append(f"{path.as_posix()} must be a list")
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=".", help="Folder to validate")
    args = parser.parse_args(argv)

    failures = validate_workspace(Path(args.target).resolve())
    if failures:
        print("workspace artifact gate: fail")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("workspace artifact gate: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

