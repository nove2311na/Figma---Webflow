#!/usr/bin/env python3
"""Deterministic quality gate for Figma Normalization."""
from __future__ import annotations

import json
import sys
from pathlib import Path

def validate_normalization(root: Path) -> list[str]:
    failures = []
    report_path = root / "workspace" / "reports" / "figma-normalization-report.json"
    tree_path = root / "workspace" / "figma" / "figma.normalized-tree.json"

    if not report_path.exists():
        failures.append("Normalization report is missing.")
        return failures
    if not tree_path.exists():
        failures.append("Normalized Figma tree file is missing.")
        return failures

    try:
        report = json.loads(report_path.read_text(encoding="utf-8"))
    except Exception as e:
        failures.append(f"Failed to parse normalization report JSON: {e}")
        return failures

    try:
        tree = json.loads(tree_path.read_text(encoding="utf-8"))
    except Exception as e:
        failures.append(f"Failed to parse normalized tree JSON: {e}")
        return failures

    if not report.get("success", False):
        failures.append("Figma normalization report indicates FAILURE.")
    
    blockers = report.get("blockers", [])
    if blockers:
        for b in blockers:
            failures.append(f"Blocker at node '{b.get('node_id')}': {b.get('reason')}")

    # Schema integrity check
    for key in ("node_id", "name", "normalized_tree", "metadata"):
        if key not in tree:
            failures.append(f"Normalized tree missing key: {key}")

    return failures

def main() -> int:
    root = Path(__file__).resolve().parents[2]
    failures = validate_normalization(root)
    if failures:
        print("figma-normalization-gate: FAIL")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("figma-normalization-gate: PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
