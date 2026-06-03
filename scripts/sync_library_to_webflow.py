#!/usr/bin/env python3
"""Print ordered Webflow MCP style_tool calls to sync a project library.

This script does not call Webflow MCP directly. It loads the per-project
client-first-library.json and prints structured payloads for each class,
which the LLM agent then executes via Webflow MCP style_tool.

After the LLM executes all calls, the script stamps last_synced in registry.json.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.library_resolver import load_library, load_registry, update_last_synced


def build_style_payloads(library: dict) -> list[dict]:
    """Convert library classes to Webflow style_tool payload list."""
    payloads = []
    for class_name, class_def in library.get("classes", {}).items():
        payloads.append({
            "class_name": class_name,
            "webflow_property": class_def["webflow_property"],
            "value": class_def["value"],
            "figma_token": class_def.get("figma_token", ""),
            "cf_category": class_def.get("cf_category", ""),
        })
    return payloads


def print_sync_instructions(root: Path, site_id: str) -> int:
    """Load library and print MCP call sequence for LLM to execute."""
    try:
        library = load_library(root, site_id)
    except FileNotFoundError as exc:
        print(f"sync failed: {exc}")
        return 1

    payloads = build_style_payloads(library)
    if not payloads:
        print(f"sync skipped: no classes defined in library for {site_id}")
        return 0

    print("=" * 60)
    print("WEBFLOW STYLE SYNC INSTRUCTIONS")
    print("=" * 60)
    print(f"\nProject (Webflow site ID): {site_id}")
    print(f"Library version: {library.get('version', 'unknown')}")
    print(f"Classes to sync: {len(payloads)}")
    print()
    print("For each payload below, call Webflow MCP style_tool:")
    print("  style_tool(site_id=<site_id>, class_name=..., styles={property: value})")
    print()
    print("PAYLOADS (ordered by cf_category):")
    sorted_payloads = sorted(payloads, key=lambda p: (p["cf_category"], p["class_name"]))
    for i, payload in enumerate(sorted_payloads, 1):
        print(f"\n[{i}/{len(sorted_payloads)}]")
        print(f"  class_name:        {payload['class_name']}")
        print(f"  webflow_property:  {payload['webflow_property']}")
        print(f"  value:             {payload['value']}")
        print(f"  figma_token:       {payload['figma_token']}")

    print()
    print("After all calls succeed, run:")
    print(f"  python scripts/sync_library_to_webflow.py --site-id {site_id} --mark-synced")
    print("=" * 60)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--site-id", required=True, help="Webflow site ID")
    parser.add_argument("--target", default=".", help="Repo root path")
    parser.add_argument(
        "--mark-synced",
        action="store_true",
        help="Stamp last_synced in registry.json (call after LLM finishes MCP calls)",
    )
    args = parser.parse_args(argv)

    root = Path(args.target).resolve()

    if args.mark_synced:
        update_last_synced(root, args.site_id)
        print(f"last_synced stamped for {args.site_id}")
        return 0

    return print_sync_instructions(root, args.site_id)


if __name__ == "__main__":
    raise SystemExit(main())
