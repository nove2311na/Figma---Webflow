#!/usr/bin/env python3
"""Validate the Claude Code-native MAS standalone scaffold structure."""
from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class Requirement:
    path: str
    kind: str = "file"
    profile: str = "standard"
    note: str = ""


PROFILE_ORDER = {"minimal": 0, "standard": 1, "full": 2}

REQUIREMENTS = [
    Requirement("CLAUDE.md", profile="minimal", note="Claude Code entrypoint"),
    Requirement("agentic/memory/team-memory.md", profile="minimal", note="team memory"),
    Requirement("agentic/policies/runtime-instructions.md", profile="minimal", note="system mandate"),
    Requirement("agentic/orchestration/sop.md", profile="minimal", note="workflow SOP"),
    Requirement("agentic/memory/session-handoff.md", profile="minimal", note="session handoff"),
    Requirement(".claude/agents", "dir", "minimal", "Claude agents"),
    Requirement(".claude/skills", "dir", "minimal", "Claude skills"),
    Requirement("agentic/README.md", profile="minimal", note="agentic index"),
    Requirement("agentic/knowledge", "dir", "minimal", "knowledge layer"),
    Requirement("agentic/memory", "dir", "minimal", "memory layer"),
    Requirement("agentic/policies", "dir", "minimal", "policy layer"),
    Requirement("agentic/orchestration", "dir", "minimal", "workflow contracts"),
    Requirement("scripts/gates", "dir", "minimal", "validation gates"),
    Requirement("scripts/init_workspace.py", profile="minimal", note="Python workspace init"),
    Requirement("scripts/archive_workspace.py", profile="minimal", note="Python workspace archive"),
    Requirement("scripts/restore_workspace.py", profile="minimal", note="Python workspace restore"),
    Requirement("scripts/gates/run_quality_gate.py", profile="minimal", note="quality gate"),
    Requirement("scripts/gates/scan_secrets.py", profile="minimal", note="secret scan"),
    Requirement("scripts/gates/validate_agent_system_spec.py", profile="standard", note="system spec gate"),
    Requirement("scripts/gates/validate_skills.py", profile="standard", note="skill anatomy gate"),
    Requirement("scripts/gates/validate_workspace_artifacts.py", profile="standard", note="workspace artifact gate"),
    Requirement("scripts/gates/validate_phase_state.py", profile="standard", note="phase state gate"),
    Requirement("scripts/gates/validate_relative_paths.py", profile="standard", note="relative path gate"),
    Requirement("scripts/gates/validate_client_first_library.py", profile="standard", note="Client-First library gate"),
    Requirement("agentic/specs/agent-system-spec.md", profile="standard", note="system spec"),
    Requirement("agentic/specs/scaffold-file-plan.md", profile="standard", note="scaffold plan"),
    Requirement("agentic/specs/workspace-artifact-schemas.md", profile="standard", note="artifact schemas contract"),
    Requirement("agentic/specs/visual-qa-evidence-contract.md", profile="standard", note="visual QA evidence contract"),
    Requirement("agentic/specs/figma-to-client-first-mapping.md", profile="standard", note="Figma to Client-First map"),
    Requirement("agentic/evals/standalone-architecture-baseline.md", profile="standard", note="standalone baseline"),
    Requirement("agentic/evals/reflection-rubric.md", profile="standard", note="reflection rubric"),
    Requirement("agentic/orchestration/reflection-loop.md", profile="standard", note="reflection loop"),
    Requirement("agentic/orchestration/phase-state-machine.md", profile="standard", note="phase state machine"),
    Requirement("agentic/schemas", "dir", "standard", "JSON schema contracts"),
    Requirement("knowledge-base/client-first-class-map.json", profile="standard", note="Client-First class map"),
    Requirement("agentic/policies/mcp-risk-auth-map.md", profile="standard", note="MCP risk map"),
    Requirement("pyproject.toml", profile="standard", note="Python project metadata"),
    Requirement(".user_versions/README.md", profile="standard", note="version log index"),
    Requirement(".user_versions/VERSION_HISTORY.md", profile="standard", note="version history"),
    Requirement(".claude/settings.json.example", profile="full", note="Claude settings example"),
    Requirement("agentic/policies/mcp-config.example.json", profile="full", note="MCP config example"),
]


def applies(requirement: Requirement, profile: str) -> bool:
    return PROFILE_ORDER[requirement.profile] <= PROFILE_ORDER[profile]


def path_exists(root: Path, requirement: Requirement) -> bool:
    path = root / requirement.path
    if requirement.kind == "dir":
        return path.is_dir()
    return path.is_file()


def validate(root: Path, profile: str) -> dict[str, Any]:
    applicable = [requirement for requirement in REQUIREMENTS if applies(requirement, profile)]
    missing = [requirement.path for requirement in applicable if not path_exists(root, requirement)]
    return {
        "target": str(root),
        "profile": profile,
        "status": "pass" if not missing else "fail",
        "summary": {
            "requirements": len(applicable),
            "passed": len(applicable) - len(missing),
            "missing": len(missing),
        },
        "missing": missing,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=".", help="Folder to validate")
    parser.add_argument("--profile", choices=sorted(PROFILE_ORDER), default="standard")
    parser.add_argument("--json", action="store_true", help="Emit JSON")
    args = parser.parse_args(argv)

    report = validate(Path(args.target).resolve(), args.profile)
    if args.json:
        print(json.dumps(report, indent=2, ensure_ascii=False))
    else:
        print("== MAS agentic structure validation ==")
        print(f"target: {report['target']}")
        print(f"profile: {report['profile']}")
        print(f"status: {report['status']}")
        print(f"passed: {report['summary']['passed']}/{report['summary']['requirements']}")
        if report["missing"]:
            print("\nMissing:")
            for item in report["missing"]:
                print(f"  - {item}")
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
