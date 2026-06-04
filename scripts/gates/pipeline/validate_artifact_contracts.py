#!/usr/bin/env python3
"""Wire validate_artifacts.py into the html-first quality gate.

For each workspace under <target>/workspace/*, run
scripts/validation/validate_artifacts.py --workspace <name> and aggregate
results. Block-tier violations in any workspace fail this gate.

Exit codes:
    0 — all workspaces pass
    1 — block-tier violation in one or more workspaces
    2 — internal error
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
VALIDATE_SCRIPT = REPO_ROOT / "scripts/validation/validate_artifacts.py"


def discover_workspaces(target: Path) -> list[str]:
    workspaces_dir = target / "workspace"
    if not workspaces_dir.exists():
        return []
    return sorted(p.name for p in workspaces_dir.iterdir() if p.is_dir())


def validate_workspace(name: str) -> tuple[int, str]:
    res = subprocess.run(
        [sys.executable, str(VALIDATE_SCRIPT), "--workspace", name],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    output = (res.stdout or "") + (res.stderr or "")
    return res.returncode, output


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--target", default=".", help="Repo root (where workspace/ lives)")
    args = parser.parse_args(argv)

    target = Path(args.target).resolve()
    if not VALIDATE_SCRIPT.exists():
        print(f"ERROR: missing {VALIDATE_SCRIPT}", file=sys.stderr)
        return 2

    workspaces = discover_workspaces(target)
    if not workspaces:
        print("artifact-contracts gate: no workspaces found, skipping")
        return 0

    failures = 0
    for name in workspaces:
        rc, output = validate_workspace(name)
        print(f"--- workspace: {name} (rc={rc}) ---")
        print(output.rstrip() or "(no output)")
        if rc == 2:
            failures += 1
        elif rc not in (0, 1, 3):
            print(f"ERROR: unexpected exit code {rc} for {name}", file=sys.stderr)
            failures += 1

    if failures:
        print(f"\nartifact-contracts gate: FAIL ({failures} workspace(s) with block-tier violations)")
        return 1
    print(f"\nartifact-contracts gate: PASS ({len(workspaces)} workspace(s))")
    return 0


if __name__ == "__main__":
    sys.exit(main())
