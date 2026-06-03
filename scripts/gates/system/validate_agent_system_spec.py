#!/usr/bin/env python3
"""Validate required sections in agentic/specs/agent-system-spec.md."""
from __future__ import annotations

import argparse
from pathlib import Path


REQUIRED_SECTIONS = [
    "## Summary",
    "## Seed Input",
    "## Agents",
    "## Skills",
    "## Tools",
    "## MCP Servers",
    "## Workflows",
    "## Memory",
    "## Gates",
    "## Scaffold Files",
    "## Validation Report",
]

REQUIRED_PHRASES = [
    "risk_class",
    "approval_policy",
    "auth_requirements",
    "allowed_agents",
    "standalone_architecture_baseline",
    "MCP-352",
    "Client-First",
    "Python",
    "client_first_library",
    "reflection_react_contract",
]


def validate(root: Path) -> list[str]:
    path = root / "agentic" / "specs" / "agent-system-spec.md"
    failures: list[str] = []
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ["agentic/specs/agent-system-spec.md is missing"]

    for section in REQUIRED_SECTIONS:
        if section not in text:
            failures.append(f"missing section {section}")
    for phrase in REQUIRED_PHRASES:
        if phrase not in text:
            failures.append(f"missing phrase {phrase}")
    return failures


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", default=".", help="Folder to validate")
    args = parser.parse_args(argv)

    failures = validate(Path(args.target).resolve())
    if failures:
        print("agent system spec gate: fail")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    print("agent system spec gate: pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
