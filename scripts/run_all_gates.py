#!/usr/bin/env python3
"""B.4: Run all 11 Python gates, print summary table, return non-zero on any failure.

Sequential execution. Each gate is run as a subprocess; we capture exit code + tail
of stdout/stderr. No interactive prompts.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
GATES_DIR = REPO / "scripts" / "gates"
EVIDENCE = REPO / "workspace" / "sections" / "gate-results.json"

# (gate_script, extra_args). --target is appended.
GATES = [
    ("validate_agentic_structure.py", []),
    ("scan_secrets.py", []),
    ("validate_skills.py", []),
    ("validate_agent_system_spec.py", []),
    ("validate_workspace_artifacts.py", []),
    ("validate_phase_state.py", []),
    ("validate_relative_paths.py", []),
    ("validate_client_first_library.py", []),
    ("validate_build_contract.py", ["--site-id", "6920a7d45c61690dd10ac690"]),
    ("validate_project_library.py", ["--site-id", "6920a7d45c61690dd10ac690"]),
    ("run_quality_gate.py", []),
]


def main() -> int:
    results = []
    print(f"{'gate':<40} {'exit':<6} {'status':<8} duration_ms")
    print("-" * 80)
    for script, extra in GATES:
        path = GATES_DIR / script
        if not path.exists():
            results.append({"script": script, "exit": 127, "status": "MISSING", "stdout": "", "stderr": "script not found"})
            print(f"{script:<40} {'n/a':<6} {'MISSING':<8}")
            continue
        cmd = [sys.executable, str(path), "--target", str(REPO), *extra]
        t0 = datetime.now(timezone.utc)
        try:
            r = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
            dt = (datetime.now(timezone.utc) - t0).total_seconds() * 1000
            status = "PASS" if r.returncode == 0 else "FAIL"
            results.append({
                "script": script,
                "exit": r.returncode,
                "status": status,
                "stdout_tail": r.stdout[-400:] if r.stdout else "",
                "stderr_tail": r.stderr[-400:] if r.stderr else "",
                "duration_ms": int(dt),
            })
            print(f"{script:<40} {r.returncode:<6} {status:<8} {int(dt)}")
            if r.returncode != 0 and r.stderr:
                print(f"  stderr: {r.stderr.strip()[-200:]}")
        except subprocess.TimeoutExpired:
            results.append({"script": script, "exit": -1, "status": "TIMEOUT"})
            print(f"{script:<40} TIMEOUT")
    print("-" * 80)
    passed = sum(1 for r in results if r["status"] == "PASS")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    print(f"SUMMARY: {passed} pass, {failed} fail of {len(GATES)}")
    EVIDENCE.parent.mkdir(parents=True, exist_ok=True)
    EVIDENCE.write_text(json.dumps({"ran_at": datetime.now(timezone.utc).isoformat(), "results": results}, indent=2), encoding="utf-8")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
