#!/usr/bin/env python3
"""Deterministic quality gate for Semantic IR and Class Selection."""
from __future__ import annotations

import json
import sys
from pathlib import Path

def validate_semantic_ir(root: Path) -> list[str]:
    failures = []
    semantic_tree_path = root / "workspace" / "semantic" / "figma.semantic-tree.json"
    missing_report_path = root / "workspace" / "reports" / "missing-mapping-report.json"

    if not semantic_tree_path.exists():
        failures.append("Semantic IR tree file is missing.")
        return failures
    if not missing_report_path.exists():
        failures.append("Missing mapping report is missing.")
        return failures

    try:
        tree = json.loads(semantic_tree_path.read_text(encoding="utf-8"))
    except Exception as e:
        failures.append(f"Failed to parse semantic tree JSON: {e}")
        return failures

    try:
        report = json.loads(missing_report_path.read_text(encoding="utf-8"))
    except Exception as e:
        failures.append(f"Failed to parse missing mapping report JSON: {e}")
        return failures

    if not report.get("success", False):
        failures.append("Missing mapping report indicates FAILURE.")

    confidence = report.get("confidence_score", 0.0)
    if confidence < 0.60:
        failures.append(f"Semantic resolver confidence score {confidence} is below strict threshold 0.60")

    missing_classes = report.get("missing_classes", [])
    if missing_classes:
        for mc in missing_classes:
            failures.append(f"Missing class mapping on node '{mc.get('node_id')}': {mc.get('class_name')} - {mc.get('reason')}")

    # Schema check
    for key in ("node_id", "name", "semantic_tree", "metadata"):
        if key not in tree:
            failures.append(f"Semantic tree missing key: {key}")

    return failures

def main() -> int:
    root = Path(__file__).resolve().parents[3]
    failures = validate_semantic_ir(root)
    if failures:
        print("semantic-ir-gate: FAIL")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("semantic-ir-gate: PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
