#!/usr/bin/env python3
"""Validate the structured Client-First class library."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


REQUIRED_GROUPS = ("structure", "typography", "spacing", "color", "layout", "state")
REQUIRED_TOP_LEVEL = ("version", "principles", "class_groups", "figma_property_map")
REQUIRED_ITEM_KEYS = ("applies_to", "figma_signals", "webflow_properties", "class_strategy")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def validate(root: Path) -> list[str]:
    path = root / "knowledge-base" / "client-first-class-map.json"
    if not path.is_file():
        return ["knowledge-base/client-first-class-map.json is missing"]

    failures: list[str] = []
    try:
        payload = load_json(path)
    except (OSError, json.JSONDecodeError) as error:
        return [f"knowledge-base/client-first-class-map.json invalid JSON: {error}"]

    if not isinstance(payload, dict):
        return ["knowledge-base/client-first-class-map.json must be an object"]

    for key in REQUIRED_TOP_LEVEL:
        if key not in payload:
            failures.append(f"class map missing {key}")

    class_groups = payload.get("class_groups", {})
    if not isinstance(class_groups, dict):
        failures.append("class_groups must be an object")
        class_groups = {}

    for group in REQUIRED_GROUPS:
        items = class_groups.get(group)
        if not isinstance(items, list) or not items:
            failures.append(f"class_groups.{group} must be a non-empty list")
            continue
        for index, item in enumerate(items):
            if not isinstance(item, dict):
                failures.append(f"class_groups.{group}[{index}] must be an object")
                continue
            if "class" not in item and "class_pattern" not in item:
                failures.append(f"class_groups.{group}[{index}] needs class or class_pattern")
            for key in REQUIRED_ITEM_KEYS:
                if key not in item or item[key] in ("", [], {}):
                    failures.append(f"class_groups.{group}[{index}] missing {key}")

    mappings = payload.get("figma_property_map", [])
    if not isinstance(mappings, list) or len(mappings) < 8:
        failures.append("figma_property_map must contain at least 8 mapping rules")
    else:
        for index, item in enumerate(mappings):
            if not isinstance(item, dict):
                failures.append(f"figma_property_map[{index}] must be an object")
                continue
            for key in ("figma_property", "signals", "client_first_decision"):
                if key not in item or item[key] in ("", [], {}):
                    failures.append(f"figma_property_map[{index}] missing {key}")

    theory_path = root / "knowledge-base" / "client-first-theory.md"
    if not theory_path.is_file():
        failures.append("knowledge-base/client-first-theory.md is missing")
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=".", help="Folder to validate")
    args = parser.parse_args(argv)

    failures = validate(Path(args.target).resolve())
    if failures:
        print("client-first library gate: fail")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("client-first library gate: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

