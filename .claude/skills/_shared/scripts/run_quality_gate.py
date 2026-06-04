#!/usr/bin/env python3
"""Run a lightweight quality gate for the MAS Claude Code workspace."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))


REQUIRED_TEXT = {
    "CLAUDE.md": ["Claude Code", "python", "Webflow", "client-first-library-contract.json"],
    "agentic/specs/system/agent-system-spec.md": ["Seed Input", "Agents", "MCP Servers", "Standalone Architecture Baseline"],
    "agentic/specs/contracts/figma-to-client-first-mapping.md": ["figma_property", "client_first_class", "class_strategy"],
    "agentic/specs/pipeline/html-first-pipeline.md": ["HTML-first Pipeline Specification"],
    "agentic/knowledge/token-sync-architecture.md": ["Figma", "Repo", "Webflow"],
    "agentic/knowledge/client-first/INDEX.yaml": ["applicable_skill", "file_path", "topic_tags"],
    "agentic/knowledge/client-first-class-map.json": ["class_groups", "version"],
    "agentic/policies/approval-gates.md": ["Webflow writes", "logical blueprint rendered to physical HTML"],
    "agentic/policies/validation-gates.md": ["block", "warn", "log"],
    ".user_versions/VERSION_HISTORY.md": ["v0.1.0", "v0.2.0", "v0.3.0"],
}

FORBIDDEN_TEXT = {
    "CLAUDE.md": ["n" + "pm run"],
    "README.md": ["n" + "pm ci", "Gemi" + "ni-native"],
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

    return failures


def run_sub_gate(gate_script: str) -> list[str]:
    import subprocess
    # All sub-gates now live flat in .claude/skills/_shared/scripts/
    here = Path(__file__).resolve().parent
    resolved = here / gate_script
    res = subprocess.run(
        [sys.executable, str(resolved)],
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
        
        # List of gates to execute sequentially (all live flat in _shared/scripts/)
        gates = [
            "validate_agentic_structure.py",
            "validate_workspace_artifacts.py",
            "validate_css_contract.py",
            "validate_css_index.py",
            "validate_artifact_contracts.py",
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
