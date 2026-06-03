#!/usr/bin/env python3
"""Validate the per-project Client-First library for a given Webflow site ID."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

# Allow importing from tools/ when run as CLI from repo root
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.library_resolver import (
    CHANGELOG_FILENAME,
    LIBRARIES_DIR,
    LIBRARY_FILENAME,
    TOKEN_MAP_FILENAME,
    _library_dir,
    load_registry,
)

REQUIRED_CF_CATEGORIES = {
    "text-color",
    "background-color",
    "border-color",
    "spacing",
    "font-size",
    "font-weight",
    "border-radius",
    "opacity",
}
REQUIRED_CLASS_FIELDS = {"figma_token", "cf_category", "webflow_property", "value"}
REQUIRED_TOKEN_MAP_ENTRY_FIELDS = {"figma_value"}


def validate_project_library(root: Path, site_id: str) -> list[str]:
    """Return list of failure strings; empty list means pass."""
    failures: list[str] = []
    lib_dir = _library_dir(root, site_id)

    # 1. Registry entry exists
    registry = load_registry(root)
    registered_ids = {p["webflow_site_id"] for p in registry.get("projects", [])}
    if site_id not in registered_ids:
        failures.append(f"site_id '{site_id}' not in registry.json")

    # 2. Library dir exists
    if not lib_dir.is_dir():
        failures.append(f"library dir missing: {LIBRARIES_DIR}/{site_id}/")
        return failures  # Cannot continue without dir

    # 3. client-first-library.json
    lib_path = lib_dir / LIBRARY_FILENAME
    if not lib_path.exists():
        failures.append(f"{LIBRARY_FILENAME} missing for {site_id}")
    else:
        try:
            library = json.loads(lib_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"{LIBRARY_FILENAME} invalid JSON: {exc}")
            library = {}

        for field in ("project_id", "webflow_site_id", "figma_file_id", "version", "classes"):
            if not library.get(field):
                failures.append(f"{LIBRARY_FILENAME} missing or empty field: {field}")

        classes = library.get("classes", {})
        if not isinstance(classes, dict):
            failures.append(f"{LIBRARY_FILENAME} 'classes' must be an object")
        else:
            for class_name, class_def in classes.items():
                for req in REQUIRED_CLASS_FIELDS:
                    if not class_def.get(req):
                        failures.append(
                            f"{LIBRARY_FILENAME} class '{class_name}' missing field: {req}"
                        )
                cf_cat = class_def.get("cf_category", "")
                if cf_cat and cf_cat not in REQUIRED_CF_CATEGORIES:
                    failures.append(
                        f"{LIBRARY_FILENAME} class '{class_name}' invalid cf_category: '{cf_cat}'"
                    )

    # 4. figma-token-map.json
    token_map_path = lib_dir / TOKEN_MAP_FILENAME
    if not token_map_path.exists():
        failures.append(f"{TOKEN_MAP_FILENAME} missing for {site_id}")
    else:
        try:
            token_map = json.loads(token_map_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"{TOKEN_MAP_FILENAME} invalid JSON: {exc}")
            token_map = {}

        for field in ("figma_file_id", "mappings", "naming_convention"):
            if field not in token_map:
                failures.append(f"{TOKEN_MAP_FILENAME} missing field: {field}")

        mappings = token_map.get("mappings", {})
        for token_path, entry in mappings.items():
            if not entry.get("figma_value"):
                failures.append(
                    f"{TOKEN_MAP_FILENAME} token '{token_path}' missing figma_value"
                )

        # 5. Cross-check: every class in library has a source token in token-map
        if "classes" in locals() and isinstance(classes, dict) and isinstance(mappings, dict):
            for class_name, class_def in classes.items():
                token = class_def.get("figma_token", "")
                if token and token not in mappings:
                    failures.append(
                        f"class '{class_name}' references figma_token '{token}' "
                        f"not found in {TOKEN_MAP_FILENAME}"
                    )

    # 6. changelog.json exists and non-empty if library has classes
    changelog_path = lib_dir / CHANGELOG_FILENAME
    if not changelog_path.exists():
        failures.append(f"{CHANGELOG_FILENAME} missing for {site_id}")
    else:
        try:
            changelog = json.loads(changelog_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"{CHANGELOG_FILENAME} invalid JSON: {exc}")
            changelog = []

        lib_classes = {}
        if lib_path.exists():
            try:
                lib_classes = json.loads(lib_path.read_text(encoding="utf-8")).get("classes", {})
            except json.JSONDecodeError:
                pass
        if lib_classes and not changelog:
            failures.append(
                f"{CHANGELOG_FILENAME} is empty but library has classes — "
                "every class must have at least one changelog entry"
            )

    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-id", required=True, help="Webflow site ID")
    parser.add_argument("--target", default=".", help="Repo root path")
    args = parser.parse_args(argv)

    root = Path(args.target).resolve()
    failures = validate_project_library(root, args.site_id)

    if failures:
        print(f"project library gate: fail ({args.site_id})")
        for failure in failures:
            print(f"  - {failure}")
        return 1

    print(f"project library gate: pass ({args.site_id})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
