#!/usr/bin/env python3
"""Thin orchestrator runner for the figma-to-webflow-orchestrator skill.

This script automates the deterministic steps of the Figma→Webflow migration
flow that can run without an LLM in the loop. Steps that require Figma MCP or
Webflow MCP (Task 1 and Task 4 of design-system-sync, plus the Figma HTML
extract of the architect skill) are intentionally left to the LLM — see the
parent SKILL.md for the in-loop protocol.

Sequence (matches SKILL.md Phase 1 → Phase 2 Branch B → Phase 3):

  Phase 1 (sequential):
    0. design-system-sync/scripts/validate_figma_extraction.py
       (Task 2 — runs against the Figma-produced figma-design-system.json)
    1. design-system-sync/scripts/map_variables.py
       (Task 3 — produces webflow-design-system.json)

  Phase 2 (parallel):
    Branch A: Webflow MCP sync (LLM in-loop, 🛑 APPROVAL GATE before any write)
    Branch B: this script runs
                figma-to-html-architect/scripts/validate_figma_html.py
              then
                figma-to-html-architect/scripts/process_html.py

  Phase 3 (join): LLM consolidates and prints the final evidence-backed report.

Usage:
    python .claude/skills/figma-to-webflow-orchestrator/scripts/orchestrate.py \
        --workspace <workspace-name> --node-id <node-id>

Exit codes:
    0 — every deterministic step passed
    non-zero — the first failing step's exit code (see status output)
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import subprocess
import sys
from pathlib import Path

SKILLS_DIR = Path(__file__).resolve().parent.parent.parent
if str(SKILLS_DIR) not in sys.path:
    sys.path.insert(0, str(SKILLS_DIR))
from _shared.scripts.repo_root import find_repo_root  # noqa: E402

REPO_ROOT = find_repo_root()
SYNC_DIR = SKILLS_DIR / "design-system-sync" / "scripts"
ARCH_DIR = SKILLS_DIR / "figma-to-html-architect" / "scripts"

PHASE_1_STEPS = [
    ("Task 2  validate_figma_extraction", SYNC_DIR / "validate_figma_extraction.py",
     ["--workspace", "{ws}"]),
    ("Task 3  map_variables", SYNC_DIR / "map_variables.py",
     ["--workspace", "{ws}"]),
]

PHASE_2_BRANCH_B_STEPS = [
    ("Task 2  validate_figma_html", ARCH_DIR / "validate_figma_html.py",
     ["--workspace", "{ws}", "--node-id", "{node}", "--mode", "warn"]),
    ("Task 3  process_html", ARCH_DIR / "process_html.py",
     ["--workspace", "{ws}", "--node-id", "{node}",
      "--webflow-design-system", str(REPO_ROOT / "workspace" / "{ws}" / "design-system" / "webflow-design-system.json")]),
]


def _run(label: str, script: Path, args: list[str], cwd: Path) -> dict:
    print(f"\n>>> {label}")
    print(f"    {script.name} {' '.join(args)}")
    result = subprocess.run(
        [sys.executable, str(script), *args],
        cwd=str(cwd),
        capture_output=True,
        text=True,
    )
    if result.stdout:
        print(result.stdout, end="" if result.stdout.endswith("\n") else "\n")
    if result.stderr:
        print(result.stderr, end="" if result.stderr.endswith("\n") else "\n", file=sys.stderr)
    return {
        "label": label,
        "script": script.name,
        "args": args,
        "returncode": result.returncode,
        "passed": result.returncode == 0,
    }


def run_phase_1(workspace: str, cwd: Path) -> list[dict]:
    results: list[dict] = []
    for label, script, args_template in PHASE_1_STEPS:
        args = [a.format(ws=workspace) for a in args_template]
        result = _run(label, script, args, cwd)
        results.append(result)
        if not result["passed"]:
            print(f"\nPhase 1 halted at {label} (exit {result['returncode']}). "
                  f"Fix the failure and re-run; later steps were not attempted.")
            return results
    return results


def run_phase_2_branch_b(workspace: str, node_id: str, cwd: Path) -> list[dict]:
    results: list[dict] = []
    for label, script, args_template in PHASE_2_BRANCH_B_STEPS:
        args = [a.format(ws=workspace, node=node_id) for a in args_template]
        result = _run(label, script, args, cwd)
        results.append(result)
        if not result["passed"]:
            print(f"\nBranch B halted at {label} (exit {result['returncode']}).")
            return results
    return results


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--workspace", required=True,
                        help="Workspace name (used as the discriminator under workspace/<workspace-name>/).")
    parser.add_argument("--node-id", required=True,
                        help="Figma node ID for the component to migrate.")
    parser.add_argument("--cwd", default=".",
                        help="Directory to run scripts from (default: current dir).")
    args = parser.parse_args()

    cwd = REPO_ROOT if args.cwd == "." else Path(args.cwd).resolve()

    for script in [s for _, s, _ in PHASE_1_STEPS + PHASE_2_BRANCH_B_STEPS]:
        if not script.exists():
            print(f"Error: required script not found: {script}", file=sys.stderr)
            return 2

    print(f"=== Phase 1: sequential contract init (workspace={args.workspace}) ===")
    p1 = run_phase_1(args.workspace, cwd)
    if any(not r["passed"] for r in p1):
        return 1

    print(f"\n=== Phase 2: parallel branches (workspace={args.workspace}, node={args.node_id}) ===")
    print("Branch A: Webflow MCP sync — handled by the LLM in-loop.")
    print("         See SKILL.md Phase 2 Branch A and the 🛑 APPROVAL GATE.")
    print("Branch B: this script (deterministic HTML pipeline).")

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
        future_b = pool.submit(run_phase_2_branch_b, args.workspace, args.node_id, cwd)
        # Branch A is LLM-driven; nothing to submit. Surface a placeholder so
        # the join is explicit.
        future_a = pool.submit(lambda: [{
            "label": "Branch A  webflow_sync (LLM in-loop)",
            "script": "<see SKILL.md>",
            "args": [],
            "returncode": 0,
            "passed": None,  # None = "left to LLM, not script-driven"
        }])
        p2a = future_a.result()
        p2b = future_b.result()

    print(f"\n=== Phase 3: join (LLM consolidates evidence) ===")
    summary = {
        "workspace": args.workspace,
        "node_id": args.node_id,
        "phase_1": p1,
        "phase_2_branch_a": p2a,
        "phase_2_branch_b": p2b,
    }
    print(json.dumps(summary, indent=2))

    all_deterministic_passed = all(r["passed"] for r in p1) and all(r["passed"] for r in p2b)
    return 0 if all_deterministic_passed else 1


if __name__ == "__main__":
    sys.exit(main())
