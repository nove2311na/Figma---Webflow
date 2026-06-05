"""CLI for bootstrapping a Webflow site's workspace.

This is a thin wrapper around `site_registry.bootstrap_workspace`. It does
NOT call the Webflow MCP itself — the site dict must be supplied via
`--site-data` (JSON string) or `--site-data-file` (path to JSON file). The
LLM or orchestrator is responsible for fetching the site data via
`data_sites_tool.list_sites` / `get_site` first.

Usage:
    # One-shot from a single site-data JSON string
    python init_workspace.py --site-data '{"id":"...","shortName":"..."}'

    # Batch from a file containing an array of site objects
    python init_workspace.py --site-data-file ./sites.json

    # List already-registered sites
    python init_workspace.py --list
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator

SKILLS_DIR = Path(__file__).resolve().parent.parent.parent
if str(SKILLS_DIR) not in sys.path:
    sys.path.insert(0, str(SKILLS_DIR))
from _shared.scripts.repo_root import find_repo_root  # noqa: E402
from site_registry import (  # noqa: E402
    bootstrap_workspace,
    list_known_sites,
    SiteInfo,
)

SITE_DATA_SCHEMA = (
    Path(__file__).resolve().parent.parent
    / "schema"
    / "webflow-site-data.schema.json"
)


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Bootstrap a Webflow site workspace.")
    parser.add_argument(
        "--site-data",
        help='JSON string of one Webflow site object (must contain "id" + "shortName").',
    )
    parser.add_argument(
        "--site-data-file",
        help="Path to a JSON file with one site object, or a list of site objects.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List already-registered sites and exit.",
    )
    parser.add_argument(
        "--force-refresh",
        action="store_true",
        help="Re-create the workspace dir even if the site is already registered.",
    )
    return parser.parse_args()


def _load_json_schema(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _validate_site_payload(payload: Any) -> list[dict[str, str]]:
    schema = _load_json_schema(SITE_DATA_SCHEMA)
    validator = Draft202012Validator(schema)
    errors = sorted(validator.iter_errors(payload), key=lambda error: list(error.path))
    return [
        {
            "path": "$" if not error.path else "$." + ".".join(str(part) for part in error.path),
            "message": error.message,
        }
        for error in errors
    ]


def _load_sites(args: argparse.Namespace) -> list[dict]:
    sites: list[dict] = []
    if args.site_data:
        parsed = json.loads(args.site_data)
        errors = _validate_site_payload(parsed)
        if errors:
            raise ValueError(f"--site-data does not match {SITE_DATA_SCHEMA}: {errors}")
        sites.append(parsed if isinstance(parsed, dict) else parsed[0])
    if args.site_data_file:
        raw = json.loads(Path(args.site_data_file).read_text(encoding="utf-8"))
        errors = _validate_site_payload(raw)
        if errors:
            raise ValueError(f"--site-data-file does not match {SITE_DATA_SCHEMA}: {errors}")
        sites.extend(raw if isinstance(raw, list) else [raw])
    return sites


def main() -> int:
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    args = _parse_args()
    repo_root = find_repo_root()

    if args.list:
        known = list_known_sites(repo_root)
        sys.stdout.write(json.dumps([s.to_dict() for s in known], indent=2) + "\n")
        return 0

    try:
        sites = _load_sites(args)
    except (json.JSONDecodeError, ValueError) as exc:
        sys.stderr.write(f"Error: invalid Webflow site data input: {exc}\n")
        return 2
    if not sites:
        sys.stderr.write("Error: provide --site-data, --site-data-file, or --list\n")
        return 2

    results: list[SiteInfo] = []
    for site in sites:
        info = bootstrap_workspace(site, repo_root=repo_root, force_refresh=args.force_refresh)
        results.append(info)

    sys.stdout.write(json.dumps([r.to_dict() for r in results], indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
