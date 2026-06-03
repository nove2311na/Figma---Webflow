#!/usr/bin/env python3
"""Helper: print LLM instructions to update the per-project CF library from Figma variables.

This script does not call Figma MCP directly -- it prints a structured instruction
block for the LLM agent to follow. The LLM then calls Figma MCP get_variable_defs,
applies the naming rules from the prompt template, and writes the updated JSON files.

After the LLM writes the files, run:
  python scripts/gates/validate_project_library.py --site-id <id>
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.library_resolver import (
    CHANGELOG_FILENAME,
    LIBRARIES_DIR,
    LIBRARY_FILENAME,
    TOKEN_MAP_FILENAME,
    _library_dir,
    load_registry,
    scaffold_library_dir,
    register_project,
)


def print_update_instructions(root: Path, site_id: str, figma_file_id: str) -> None:
    """Print structured LLM instructions for Figma -> library update."""
    lib_dir = _library_dir(root, site_id)
    library_path = lib_dir / LIBRARY_FILENAME
    token_map_path = lib_dir / TOKEN_MAP_FILENAME
    changelog_path = lib_dir / CHANGELOG_FILENAME
    prompt_path = root / "agentic" / "prompts" / "generate-cf-library.md"

    current_classes: dict = {}
    if library_path.exists():
        try:
            current_classes = json.loads(library_path.read_text(encoding="utf-8")).get("classes", {})
        except json.JSONDecodeError:
            pass

    print("=" * 60)
    print("FIGMA -> CLIENT-FIRST LIBRARY UPDATE INSTRUCTIONS")
    print("=" * 60)
    print(f"\nProject:       {site_id}")
    print(f"Figma file:    {figma_file_id}")
    print(f"Library path:  {LIBRARIES_DIR}/{site_id}/{LIBRARY_FILENAME}")
    print(f"Token map:     {LIBRARIES_DIR}/{site_id}/{TOKEN_MAP_FILENAME}")
    print(f"Changelog:     {LIBRARIES_DIR}/{site_id}/{CHANGELOG_FILENAME}")
    print(f"Existing classes: {len(current_classes)} defined")
    print()
    print("STEP 1 -- Read the prompt template:")
    print(f"  {prompt_path.relative_to(root)}")
    print()
    print("STEP 2 -- Call Figma MCP:")
    print(f"  get_variable_defs(figma_file_id='{figma_file_id}')")
    print()
    print("STEP 3 -- Apply naming rules from prompt template.")
    print("  For each Figma variable:")
    print("    - Derive cf_category from variable type and path")
    print("    - Derive semantic_name from last path segment (slugified)")
    print("    - Build class name: {cf_category}-{semantic_name}")
    print("    - Convert px -> rem (divide by 16) for spacing/typography")
    print("    - Color variables generate text-color-*, background-color-*, border-color-* classes")
    print()
    print("STEP 4 -- Write updated files:")
    print(f"  {LIBRARIES_DIR}/{site_id}/{TOKEN_MAP_FILENAME}")
    print(f"  {LIBRARIES_DIR}/{site_id}/{LIBRARY_FILENAME}")
    print()
    print("STEP 5 -- Append changelog entries:")
    print(f"  {LIBRARIES_DIR}/{site_id}/{CHANGELOG_FILENAME}")
    print("  Format: {timestamp, class, old_value, new_value, source, reason}")
    print()
    print("STEP 6 -- Validate:")
    print(f"  python scripts/gates/validate_project_library.py --site-id {site_id}")
    print("=" * 60)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-id", required=True, help="Webflow site ID")
    parser.add_argument("--figma-file-id", default="", help="Figma file ID (not full URL)")
    parser.add_argument("--project-name", default="", help="Human-readable project name")
    parser.add_argument("--target", default=".", help="Repo root path")
    args = parser.parse_args(argv)

    root = Path(args.target).resolve()

    # Scaffold if library dir does not exist yet
    lib_dir = _library_dir(root, args.site_id)
    if not lib_dir.exists():
        for action in scaffold_library_dir(root, args.site_id, args.figma_file_id):
            print(action)
        register_project(root, {
            "webflow_site_id": args.site_id,
            "figma_file_id": args.figma_file_id,
            "name": args.project_name or args.site_id,
        })

    print_update_instructions(root, args.site_id, args.figma_file_id)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
