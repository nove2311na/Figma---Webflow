#!/usr/bin/env python3
"""Initialize the MAS workspace without overwriting existing state."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from tools.library_resolver import register_project, scaffold_library_dir


WORKSPACE_DIR = Path(__file__).resolve().parents[1] / "workspace"


def _extract_figma_file_id(figma_url: str) -> str:
    """Extract file ID from a Figma URL, e.g. .../design/ABC123/... → 'ABC123'."""
    match = re.search(r"/(?:design|file)/([^/?#]+)", figma_url)
    return match.group(1) if match else ""


def write_json_if_missing(path: Path, payload: Any) -> bool:
    """Write JSON only when the file does not already exist."""
    if path.exists():
        return False
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return True


def initialize_workspace(
    project: str,
    figma: str,
    webflow_site_id: str = "",
    figma_file_id: str = "",
) -> list[str]:
    """Create workspace directories and seed files."""
    actions: list[str] = []
    WORKSPACE_DIR.mkdir(parents=True, exist_ok=True)
    actions.append("workspace root ready")

    for directory in ("blueprints", "contents", "rawdata"):
        path = WORKSPACE_DIR / directory
        if path.exists():
            actions.append(f"kept workspace/{directory}/")
        else:
            path.mkdir(parents=True)
            actions.append(f"created workspace/{directory}/")

    # Auto-extract figma file ID from URL when not provided explicitly
    resolved_figma_file_id = figma_file_id or _extract_figma_file_id(figma)

    # Resolve per-project library path for design-system.json
    library_path = (
        f"knowledge-base/libraries/{webflow_site_id}/client-first-library.json"
        if webflow_site_id
        else "knowledge-base/client-first-class-map.json"
    )

    initial_files: dict[str, Any] = {
        "meta.json": {
            "projectName": project,
            "figmaUrl": figma,
            "figmaFileId": resolved_figma_file_id,
            "webflowSiteId": webflow_site_id,
            "initializedAt": datetime.now(timezone.utc).isoformat(),
            "runtime": "claude_code_python",
        },
        "page_structure.json": [],
        "state.json": [],
        "error-logs.json": [],
        "design-system.json": {
            "variables": [],
            "global_classes": [],
            "client_first_library": library_path,
            "figma_mapping_contract": "agentic/specs/figma-to-client-first-mapping.md",
        },
    }

    for filename, payload in initial_files.items():
        created = write_json_if_missing(WORKSPACE_DIR / filename, payload)
        actions.append(f"{'created' if created else 'kept'} workspace/{filename}")

    # Scaffold per-project library if site ID provided
    if webflow_site_id:
        repo_root = Path(__file__).resolve().parents[1]
        for action in scaffold_library_dir(repo_root, webflow_site_id, resolved_figma_file_id):
            actions.append(action)
        register_project(repo_root, {
            "webflow_site_id": webflow_site_id,
            "figma_file_id": resolved_figma_file_id,
            "name": project,
        })
        actions.append(f"registered {webflow_site_id} in library registry")

    return actions


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project", default="New Project", help="Project name")
    parser.add_argument("--figma", default="", help="Figma design URL")
    parser.add_argument("--webflow-site-id", default="", help="Webflow site ID (keys per-project library)")
    parser.add_argument("--figma-file-id", default="", help="Figma file ID (auto-extracted from --figma URL if omitted)")
    args = parser.parse_args(argv)

    for action in initialize_workspace(
        args.project,
        args.figma,
        webflow_site_id=args.webflow_site_id,
        figma_file_id=args.figma_file_id,
    ):
        print(action)
    print("workspace ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
