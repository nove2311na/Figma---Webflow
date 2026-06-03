#!/usr/bin/env python3
"""Validate Webflow build contracts in blueprints before a parallel-section build.

Checks that every section carries an HTML contract + class list, that every referenced
class either already exists in the per-project library or is declared in the page-level
new_classes list, and that no two sections declare the same class name with conflicting
definitions (the parallel-build naming-race guard).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.library_resolver import load_library

REQUIRED_SECTION_FIELDS = ("section_id", "html_contract", "cf_classes")
REQUIRED_NEW_CLASS_FIELDS = ("name", "cf_category", "webflow_property", "value")


def _iter_blueprints(root: Path, blueprint: str | None) -> list[Path]:
    if blueprint:
        return [Path(blueprint)]
    bp_dir = root / "workspace" / "blueprints"
    if not bp_dir.is_dir():
        return []
    return sorted(bp_dir.glob("*.json"))


def validate_build_contract(root: Path, site_id: str, blueprint: str | None = None) -> list[str]:
    """Return list of failure strings; empty list means pass."""
    failures: list[str] = []

    # Existing classes from the per-project library
    existing_classes: set[str] = set()
    try:
        library = load_library(root, site_id)
        existing_classes = set(library.get("classes", {}).keys())
    except FileNotFoundError:
        failures.append(f"site_id '{site_id}' not in registry; cannot resolve library")

    blueprints = _iter_blueprints(root, blueprint)
    if not blueprints:
        failures.append("no blueprints found to validate")
        return failures

    for bp_path in blueprints:
        if not bp_path.exists():
            failures.append(f"blueprint not found: {bp_path}")
            continue
        try:
            data = json.loads(bp_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"{bp_path.name}: invalid JSON: {exc}")
            continue

        name = bp_path.name

        # Page-level new_classes: detect duplicate names with conflicting definitions (naming-race guard)
        new_classes: dict[str, str] = {}
        for entry in data.get("new_classes", []):
            for field in REQUIRED_NEW_CLASS_FIELDS:
                if not entry.get(field):
                    failures.append(f"{name}: new_class missing field '{field}': {entry.get('name', '?')}")
            cls_name = entry.get("name", "")
            if not cls_name:
                continue
            definition = json.dumps(
                {k: entry.get(k) for k in REQUIRED_NEW_CLASS_FIELDS},
                sort_keys=True,
            )
            if cls_name in new_classes and new_classes[cls_name] != definition:
                failures.append(
                    f"{name}: class '{cls_name}' declared with conflicting definitions "
                    "in new_classes (naming-race risk)"
                )
            new_classes[cls_name] = definition

        declarable = existing_classes | set(new_classes.keys())

        sections = data.get("sections", [])
        for i, section in enumerate(sections):
            sec_id = section.get("section_id", f"index_{i}")
            for field in REQUIRED_SECTION_FIELDS:
                if not section.get(field):
                    failures.append(f"{name}: section '{sec_id}' missing field '{field}'")

            for cls in section.get("cf_classes", []):
                if cls not in declarable:
                    failures.append(
                        f"{name}: section '{sec_id}' references class '{cls}' "
                        "not in library and not declared in new_classes"
                    )

    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-id", required=True, help="Webflow site ID")
    parser.add_argument("--target", default=".", help="Repo root path")
    parser.add_argument("--blueprint", default=None, help="Single blueprint path (default: all workspace/blueprints/*.json)")
    args = parser.parse_args(argv)

    root = Path(args.target).resolve()
    failures = validate_build_contract(root, args.site_id, args.blueprint)

    if failures:
        print(f"build contract gate: fail ({args.site_id})")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print(f"build contract gate: pass ({args.site_id})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
