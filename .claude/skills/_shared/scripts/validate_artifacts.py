#!/usr/bin/env python3
"""Validate JSON artifacts against the V3 schema catalog.

Reads `agentic/policies/validation-gates.md` for the block/warn/log tier map
(via the embedded tier map below), and runs `jsonschema` validation per tier.

Usage:
    python .claude/skills/_shared/scripts/validate_artifacts.py --workspace <name>
    python .claude/skills/_shared/scripts/validate_artifacts.py --workspace <name> --tier block
    python .claude/skills/_shared/scripts/validate_artifacts.py --list-tiers
    python .claude/skills/_shared/scripts/validate_artifacts.py --path <file>

Exit codes:
    0 — all artifacts at the requested tier(s) pass
    1 — usage error
    2 — block-tier violation
    3 — internal error
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from jsonschema import Draft202012Validator
from referencing import Registry, Resource
from referencing.jsonschema import DRAFT202012

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

# ---------------------------------------------------------------------------
# Schema registry: $id → file path
# ---------------------------------------------------------------------------
SCHEMA_PATHS: dict[str, Path] = {
    "https://figwebflow.local/schemas/_shared/meta.schema.json":
        REPO_ROOT / "agentic/schemas/_shared/meta.schema.json",
    "https://figwebflow.local/schemas/_shared/variable-entry.schema.json":
        REPO_ROOT / "agentic/schemas/_shared/variable-entry.schema.json",
    "https://figwebflow.local/schemas/_shared/style-entry.schema.json":
        REPO_ROOT / "agentic/schemas/_shared/style-entry.schema.json",
    "https://figwebflow.local/schemas/figma-design-system-contract.schema.json":
        REPO_ROOT / ".claude/skills/design-system-sync/schema/figma-design-system-contract.schema.json",
    "https://figwebflow.local/schemas/webflow-design-system-contract.schema.json":
        REPO_ROOT / ".claude/skills/design-system-sync/schema/webflow-design-system-contract.schema.json",
    "https://figwebflow.local/schemas/agentic/schemas/webflow/webflow-write-audit-log.schema.json":
        REPO_ROOT / "agentic/schemas/webflow/webflow-write-audit-log.schema.json",
    "https://figwebflow.local/schemas/agentic/schemas/webflow/mcp-sync-report.schema.json":
        REPO_ROOT / "agentic/schemas/webflow/mcp-sync-report.schema.json",
    "https://figwebflow.local/schemas/agentic/schemas/semantic/semantic-tree.schema.json":
        REPO_ROOT / "agentic/schemas/semantic/semantic-tree.schema.json",
    "https://figwebflow.local/schemas/agentic/schemas/html/alt-policy.schema.json":
        REPO_ROOT / "agentic/schemas/html/alt-policy.schema.json",
    "https://figwebflow.local/schemas/agentic/schemas/library/client-first-library.schema.json":
        REPO_ROOT / "agentic/schemas/library/client-first-library.schema.json",
    "https://figwebflow.local/schemas/agentic/schemas/workspace/page-structure.schema.json":
        REPO_ROOT / "agentic/schemas/workspace/page-structure.schema.json",
    "https://figwebflow.local/schemas/.claude/skills/design-system-sync/schema/client-first-baseline-contract.schema.json":
        REPO_ROOT / ".claude/skills/design-system-sync/schema/client-first-baseline-contract.schema.json",
}

# ---------------------------------------------------------------------------
# Tier map: artifact filename (relative to workspace/) → (schema $id, tier)
# ---------------------------------------------------------------------------
TIER_MAP: dict[str, tuple[str, str]] = {
    "design-system/webflow-contract.json": (
        "https://figwebflow.local/schemas/webflow-design-system-contract.schema.json",
        "block",
    ),
    "design-system/figma-contract.json": (
        "https://figwebflow.local/schemas/figma-design-system-contract.schema.json",
        "block",
    ),
    "design-system/client-first-baseline-contract.json": (
        "https://figwebflow.local/schemas/.claude/skills/design-system-sync/schema/client-first-baseline-contract.schema.json",
        "block",
    ),
    "design-system/validations/webflow-sync-preview.json": (
        "https://figwebflow.local/schemas/agentic/schemas/webflow/mcp-sync-report.schema.json",
        "block",
    ),
    "components/{node_id}/validations/architect-diff-preview.json": (
        "https://figwebflow.local/schemas/agentic/schemas/webflow/mcp-sync-report.schema.json",
        "warn",
    ),
    "write-audit-log.jsonl": (
        "https://figwebflow.local/schemas/agentic/schemas/webflow/webflow-write-audit-log.schema.json",
        "block",
    ),
    "qa-report.json": (
        "https://figwebflow.local/schemas/agentic/schemas/webflow/mcp-sync-report.schema.json",
        "warn",
    ),
    "phase-state.json": (
        "https://figwebflow.local/schemas/agentic/schemas/workspace/page-structure.schema.json",
        "log",
    ),
}


def load_registry() -> Registry:
    store = {}
    for sid, path in SCHEMA_PATHS.items():
        if not path.exists():
            continue
        try:
            s = json.loads(path.read_text(encoding="utf-8"))
            store[sid] = s
        except Exception as e:
            print(f"WARN: failed to load schema {path}: {e}", file=sys.stderr)
    return Registry().with_resources(
        [(sid, Resource(contents=s, specification=DRAFT202012)) for sid, s in store.items()]
    )


def validate_file(path: Path, schema_id: str, registry: Registry) -> list[str]:
    schema = registry.contents(Resource(contents={}, specification=DRAFT202012)) if False else None
    for sid, res in registry._resources.items():
        if sid == schema_id:
            schema = res.contents
            break
    if schema is None:
        return [f"schema not loaded: {schema_id}"]
    if not path.exists():
        return [f"file not found: {path}"]
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"invalid JSON: {e}"]
    if path.suffix == ".jsonl":
        data = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    validator = Draft202012Validator(schema, registry=registry)
    errors = []
    items = data if isinstance(data, list) else [data]
    for idx, item in enumerate(items):
        for err in validator.iter_errors(item):
            p = ".".join(str(x) for x in err.absolute_path) or "(root)"
            errors.append(f"[{idx}] {p}: {err.message[:200]}")
    return errors


def run_validation(workspace: str, tier: Optional[str], registry: Registry) -> tuple[int, int, int]:
    ws_path = REPO_ROOT / "workspace" / workspace
    if not ws_path.exists():
        print(f"ERROR: workspace not found: {ws_path}", file=sys.stderr)
        return 0, 0, 1
    block_fail = warn_fail = log_fail = 0
    block_pass = warn_pass = log_pass = 0
    for rel_path, (schema_id, art_tier) in TIER_MAP.items():
        if tier and art_tier != tier:
            continue
        actual = rel_path
        for node_id_token in ("{node_id}",):
            actual = actual.replace(node_id_token, "*")
        candidates = list(ws_path.glob(actual)) if "*" in actual else [ws_path / actual]
        if not candidates:
            continue
        for path in candidates:
            errors = validate_file(path, schema_id, registry)
            if errors:
                msg = f"[{art_tier.upper()}] FAIL {path.relative_to(REPO_ROOT)}: {len(errors)} errors"
                print(msg)
                for e in errors[:3]:
                    print(f"    {e}")
                if art_tier == "block":
                    block_fail += 1
                elif art_tier == "warn":
                    warn_fail += 1
                else:
                    log_fail += 1
            else:
                print(f"[{art_tier.upper()}] OK   {path.relative_to(REPO_ROOT)}")
                if art_tier == "block":
                    block_pass += 1
                elif art_tier == "warn":
                    warn_pass += 1
                else:
                    log_pass += 1
    print(f"\nSummary: block={block_pass}P/{block_fail}F  warn={warn_pass}P/{warn_fail}F  log={log_pass}P/{log_fail}F")
    if block_fail:
        return 0, 0, 2
    return block_pass + warn_pass + log_pass, 0, 0


def list_tiers() -> int:
    print("Validation tier map (from agentic/policies/validation-gates.md):\n")
    print(f"  {'ARTIFACT':<70} {'TIER':<8}")
    print(f"  {'-'*70} {'-'*8}")
    for rel_path, (_, tier) in TIER_MAP.items():
        print(f"  {rel_path:<70} {tier:<8}")
    print("\nTiers:")
    print("  block — must pass. Build halts on failure. Exit code 2.")
    print("  warn  — should pass. Build continues. Logged to qa-report.")
    print("  log   — tracked, not gated. Stats only.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--workspace", help="Workspace name (workspace/<name>/)")
    parser.add_argument("--tier", choices=["block", "warn", "log"], help="Restrict to one tier")
    parser.add_argument("--path", help="Validate a single file (overrides --workspace/--tier)")
    parser.add_argument("--list-tiers", action="store_true", help="Print the tier map and exit")
    args = parser.parse_args()

    if args.list_tiers:
        return list_tiers()
    if args.path:
        path = Path(args.path)
        if not path.is_absolute():
            path = REPO_ROOT / path
        registry = load_registry()
        schema_id = TIER_MAP.get(path.relative_to(REPO_ROOT).as_posix(), (None, None))[0] if path.relative_to(REPO_ROOT).as_posix() in TIER_MAP else None
        if schema_id is None:
            for rel, (sid, _) in TIER_MAP.items():
                if path.match(f"**/{rel.split('/')[-1]}"):
                    schema_id = sid
                    break
        if schema_id is None:
            print(f"ERROR: no schema mapped for {path}. Add to TIER_MAP.", file=sys.stderr)
            return 1
        errors = validate_file(path, schema_id, registry)
        if errors:
            for e in errors:
                print(f"  {e}")
            return 2
        print(f"OK: {path}")
        return 0
    if not args.workspace:
        parser.error("--workspace is required (or use --list-tiers / --path)")
    registry = load_registry()
    _, _, rc = run_validation(args.workspace, args.tier, registry)
    return rc


if __name__ == "__main__":
    sys.exit(main())
