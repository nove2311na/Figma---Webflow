#!/usr/bin/env python3
"""Run a lightweight quality gate for the MAS Claude Code workspace."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.gates.validate_project_library import validate_project_library
from scripts.gates.validate_build_contract import validate_build_contract


REQUIRED_TEXT = {
    "CLAUDE.md": ["Claude Code", "Python", "MCP-352", "Webflow", "client-first-class-map.json"],
    "agentic/memory/team-memory.md": ["Hard Invariants", "Agent Team", "standalone baseline"],
    "agentic/policies/runtime-instructions.md": ["Claude Code", "Python", "Webflow", "approval"],
    "agentic/orchestration/sop.md": ["Phase 0", "Phase 1", "Phase 2", "Phase 3", "Approved"],
    "agentic/orchestration/reflection-loop.md": ["reflection_review", "revise", "Stop Conditions"],
    "agentic/specs/agent-system-spec.md": ["Seed Input", "Agents", "MCP Servers", "Standalone Architecture Baseline"],
    "agentic/specs/figma-to-client-first-mapping.md": ["figma_property", "client_first_class", "class_strategy"],
    "agentic/specs/visual-qa-evidence-contract.md": ["[APPROVED]", "[FIX]", "webflow_state_ref"],
    "agentic/knowledge/client-first-library.md": ["client-first-class-map.json", "figma_property", "webflow_property"],
    "agentic/policies/tool-risk-levels.md": ["R0", "R4", "risk_class"],
    "agentic/policies/approval-gates.md": ["Webflow external write", "Blueprint completion"],
    ".user_versions/VERSION_HISTORY.md": ["v0.1.0", "v0.2.0", "v0.3.0"],
}

FORBIDDEN_TEXT = {
    "CLAUDE.md": ["n" + "pm run"],
    "README.md": ["n" + "pm ci", "Gemi" + "ni-native"],
    "agentic/policies/runtime-instructions.md": ["." + "gemini/agents", "." + "gemini/skills"],
    "agentic/orchestration/sop.md": ["Node" + ".js"],
}


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def _load_workspace_site_id(root: Path) -> str:
    """Return webflowSiteId from workspace/meta.json if present; empty string otherwise."""
    meta_path = root / "workspace" / "meta.json"
    if not meta_path.exists():
        return ""
    try:
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        return meta.get("webflowSiteId", "")
    except (json.JSONDecodeError, OSError):
        return ""


def validate(root: Path) -> list[str]:
    failures: list[str] = []
    for relative_path, phrases in REQUIRED_TEXT.items():
        text = read_text(root / relative_path)
        if not text.strip():
            failures.append(f"{relative_path} is missing or empty")
            continue
        for phrase in phrases:
            if phrase not in text:
                failures.append(f"{relative_path} missing phrase {phrase}")

    for relative_path, phrases in FORBIDDEN_TEXT.items():
        text = read_text(root / relative_path)
        for phrase in phrases:
            if phrase in text:
                failures.append(f"{relative_path} contains deprecated phrase {phrase}")

    # Auto-run project library gate when workspace has a webflowSiteId
    site_id = _load_workspace_site_id(root)
    if site_id:
        lib_failures = validate_project_library(root, site_id)
        for failure in lib_failures:
            failures.append(f"[project-library:{site_id}] {failure}")

        # Build-contract gate only when blueprints exist (a build is in progress)
        if (root / "workspace" / "blueprints").is_dir() and any(
            (root / "workspace" / "blueprints").glob("*.json")
        ):
            contract_failures = validate_build_contract(root, site_id)
            for failure in contract_failures:
                failures.append(f"[build-contract:{site_id}] {failure}")

    return failures


def run_sub_gate(gate_script: str) -> list[str]:
    import subprocess
    res = subprocess.run(
        [sys.executable, f"scripts/gates/{gate_script}" if "/" not in gate_script else gate_script],
        capture_output=True,
        text=True,
        encoding="utf-8"
    )
    if res.returncode != 0:
        return [f"Gate {gate_script} failed: {res.stderr.strip() or res.stdout.strip()}"]
    return []

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=".", help="Folder to validate")
    parser.add_argument("--profile", default=None, help="Validation profile (e.g. html-first)")
    args = parser.parse_args(argv)

    root = Path(args.target).resolve()
    
    if args.profile == "html-first":
        print("Running HTML-first compiler validation profile...")
        failures = []
        
        # List of gates to execute sequentially
        gates = [
            "validate_agentic_structure.py",
            "validate_workspace_artifacts.py",
            "validate_css_contract.py",
            "validate_css_index.py",
            "validate_figma_normalization.py",
            "validate_semantic_ir.py",
            "validate_html_blueprint.py",
            "validate_asset_policy.py",
            "scripts/validate_html_chunks.py",
            "validate_resolver_benchmark.py",
            "validate_native_build_plan.py"
        ]
        
        for gate in gates:
            print(f"Executing gate: {gate}...")
            failures.extend(run_sub_gate(gate))
            
        if failures:
            print("\nquality gate [html-first]: FAIL")
            for failure in failures:
                print(f"  - {failure}")
            return 1
        print("\nquality gate [html-first]: PASS")
        return 0

    failures = validate(root)
    if failures:
        print("quality gate: fail")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("quality gate: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
