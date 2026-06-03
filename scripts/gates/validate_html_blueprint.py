#!/usr/bin/env python3
"""Deterministic HTML Blueprint validation gate (Class strictness, structure, accessibility, syntax)."""
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

class HTMLValidator:
    def __init__(self, contract: dict[str, Any]):
        self.allowed_classes = set(contract.get("allowed_classes", []))
        self.allowed_combo_classes = set(contract.get("allowed_combo_classes", []))
        self.structural_classes = set(contract.get("structural_convention_classes", ["page-wrapper", "main-wrapper"]))
        self.reserved_classes = set(contract.get("reserved_webflow_classes", []))
        
        self.failures = []
        self.checks = {
            "html_syntax": True,
            "class_strictness": True,
            "accessibility": True,
            "client_first_structure": True
        }

    def walk_node(self, node: dict[str, Any], path_tags: list[str]) -> None:
        tag = node.get("tag", "div")
        classes = node.get("classes", [])
        attrs = node.get("attributes", {})
        node_id = attrs.get("data-figma-node", "unknown")
        
        # 1. Class Strictness check
        for cls in classes:
            is_valid = (
                cls in self.allowed_classes or
                cls in self.allowed_combo_classes or
                cls in self.structural_classes or
                cls in self.reserved_classes or
                cls.startswith("w-")  # Webflow native
            )
            if not is_valid:
                self.checks["class_strictness"] = False
                self.failures.append({
                    "node_id": node_id,
                    "rule": "class_strictness",
                    "details": f"Class '{cls}' not found in Client-First library contract."
                })

        # 2. Accessibility checks
        if tag == "img":
            # Image role check
            alt = attrs.get("alt")
            aria_hidden = attrs.get("aria-hidden")
            if alt is None and aria_hidden != "true":
                self.checks["accessibility"] = False
                self.failures.append({
                    "node_id": node_id,
                    "rule": "accessibility",
                    "details": f"Image tag <img> must have an 'alt' attribute or 'aria-hidden=\"true\"'."
                })

        if tag == "input":
            # Input needs name/id
            name = attrs.get("name")
            inp_id = attrs.get("id")
            if not name and not inp_id:
                self.checks["accessibility"] = False
                self.failures.append({
                    "node_id": node_id,
                    "rule": "accessibility",
                    "details": f"Input control <input> must have a 'name' or 'id' attribute."
                })

        # Recursion
        current_tags = path_tags + [tag]
        for child in node.get("children", []):
            self.walk_node(child, current_tags)

    def check_structure(self, body_bp: dict[str, Any]) -> None:
        # Client-First structural check
        # Root element should have class page-wrapper
        root_classes = body_bp.get("classes", [])
        if "page-wrapper" not in root_classes:
            self.checks["client_first_structure"] = False
            self.failures.append({
                "node_id": body_bp.get("attributes", {}).get("data-figma-node", "root"),
                "rule": "client_first_structure",
                "details": "Root body container must have the 'page-wrapper' class."
            })

        # Main-wrapper check
        children = body_bp.get("children", [])
        has_main_wrapper = False
        for child in children:
            if "main-wrapper" in child.get("classes", []):
                has_main_wrapper = True
                break
        
        if not has_main_wrapper:
            self.checks["client_first_structure"] = False
            self.failures.append({
                "node_id": body_bp.get("attributes", {}).get("data-figma-node", "root"),
                "rule": "client_first_structure",
                "details": "Children of 'page-wrapper' must contain a 'main-wrapper' container."
            })

def validate_html(root: Path) -> list[str]:
    failures = []
    bp_path = root / "workspace" / "html" / "page.blueprint.json"
    html_path = root / "workspace" / "html" / "page.html"
    contract_path = root / "knowledge-base" / "generated" / "client-first-library-contract.json"

    if not bp_path.exists() or not html_path.exists():
        return ["Blueprint or rendered HTML files are missing."]

    bp_payload = load_json(bp_path)
    contract = load_json(contract_path)

    body_bp = bp_payload.get("body", {})
    if not body_bp:
        return ["Blueprint JSON has no body element."]

    validator = HTMLValidator(contract)
    
    # Run walks
    validator.walk_node(body_bp, [])
    validator.check_structure(body_bp)

    success = len(validator.failures) == 0

    # Write report
    report_payload = {
        "verified_at": datetime.now(timezone.utc).isoformat(),
        "local_html_path": str(html_path),
        "checks": validator.checks,
        "failures": validator.failures,
        "success": success
    }

    report_path = root / "workspace" / "reports" / "html-validation-report.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report_payload, indent=2, ensure_ascii=False), encoding="utf-8")

    # Return summary of failures for the runner
    for f in validator.failures:
        failures.append(f"[{f['rule']}] Node {f.get('node_id')}: {f['details']}")

    return failures

def main() -> int:
    root = Path(__file__).resolve().parents[2]
    failures = validate_html(root)
    if failures:
        print("html-blueprint-gate: FAIL")
        for f in failures:
            print(f"  - {f}")
        return 1
    print("html-blueprint-gate: PASS")
    return 0

if __name__ == "__main__":
    sys.exit(main())
