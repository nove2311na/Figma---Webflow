#!/usr/bin/env python3
"""Deterministic quality gate for Asset Alt policy conformance."""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

def load_json(path: Path) -> Any:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))

def validate_assets(root: Path) -> list[str]:
    failures = []
    manifest_path = root / "workspace" / "html" / "asset-manifest.json"
    rules_path = root / "agentic" / "rules" / "asset-alt.rules.yaml"

    if not manifest_path.exists():
        failures.append("Asset manifest file is missing.")
        return failures

    manifest = load_json(manifest_path)
    
    # Load rules
    import yaml
    rules = {}
    if rules_path.exists():
        try:
            rules = yaml.safe_load(rules_path.read_text(encoding="utf-8"))
        except Exception:
            rules = {}
    
    policy = rules.get("asset_alt_policy", {})
    forbidden_generics = set(policy.get("forbidden_generic_alts", ["image", "logo", "photo", "placeholder"]))

    assets = manifest.get("assets", [])
    for asset in assets:
        node_id = asset.get("figma_node_id", "unknown")
        role = asset.get("role", "informative")
        alt = asset.get("alt_text", "")
        aria_hidden = asset.get("aria_hidden", False)

        if role == "informative":
            if not alt.strip():
                failures.append(f"Node {node_id}: Informative image is missing alt text.")
            elif alt.strip().lower() in forbidden_generics:
                failures.append(f"Node {node_id}: Informative image uses forbidden generic alt text '{alt}'.")
        elif role == "decorative":
            if alt.strip() != "":
                failures.append(f"Node {node_id}: Decorative image must have empty alt text.")
            if not aria_hidden:
                failures.append(f"Node {node_id}: Decorative image must have aria_hidden set to true.")
        elif role == "functional":
            if not alt.strip():
                failures.append(f"Node {node_id}: Functional asset (icon/button) must have an accessible label.")
            elif alt.strip().lower() in forbidden_generics:
                failures.append(f"Node {node_id}: Functional asset uses forbidden generic alt text '{alt}'.")
        elif role == "complex":
            if not alt.strip():
                failures.append(f"Node {node_id}: Complex asset must have long description or alt text.")

    success = len(failures) == 0

    report_payload = {
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "total_assets_checked": len(assets),
        "failures_count": len(failures),
        "failures": failures,
        "success": success
    }

    report_path = root / "workspace" / "reports" / "asset-policy-report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report_payload, indent=2, ensure_ascii=False), encoding="utf-8")

    return failures

def main() -> int:
    root = Path(__file__).resolve().parents[2]
    failures = validate_assets(root)
    if failures:
        print("asset-policy-gate: FAIL")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("asset-policy-gate: PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
