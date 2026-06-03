#!/usr/bin/env python3
"""Deterministic verification gate for Webflow Native Build Plan."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def validate_plan(root: Path) -> list[str]:
    failures = []
    plan_path = root / "workspace" / "webflow-native" / "native-build-plan.json"
    contract_path = root / "knowledge-base" / "generated" / "client-first-library-contract.json"

    if not plan_path.exists():
        failures.append("native-build-plan.json file is missing.")
        return failures

    plan = load_json(plan_path)
    contract = load_json(contract_path)
    allowed_classes = set(contract.get("allowed_classes", [])) | set(contract.get("allowed_combo_classes", [])) | set(contract.get("structural_convention_classes", [])) | set(contract.get("reserved_webflow_classes", []))

    # Basic validations
    for key in ("version", "target_site_id", "target_page_id", "operations", "metadata"):
        if key not in plan:
            failures.append(f"Build plan missing key: {key}")

    branch = plan.get("target_branch", "")
    if not branch or branch in ("main", "master", "production"):
        failures.append(f"Forbidden target branch: '{branch}'. Mutations must operate on a temporary site branch.")

    operations = plan.get("operations", [])
    for idx, op in enumerate(operations):
        op_type = op.get("type")
        payload = op.get("payload", {})
        node_id = op.get("node_id", "unknown")

        if op_type == "create_element":
            classes = payload.get("classes", [])
            for cls in classes:
                if cls not in allowed_classes and not cls.startswith("w-"):
                    failures.append(f"Operation {idx} (node {node_id}) uses class '{cls}' not found in CSS contract.")

        # Ensure no destructive operations without approval
        if op_type == "delete_element":
            failures.append(f"Operation {idx}: Destructive operations (delete_element) are forbidden during refactor runs.")

    return failures

def main() -> int:
    root = Path(__file__).resolve().parents[3]
    failures = validate_plan(root)
    if failures:
        print("native-build-plan-gate: FAIL")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("native-build-plan-gate: PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
