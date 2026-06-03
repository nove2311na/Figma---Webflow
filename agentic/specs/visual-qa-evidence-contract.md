# Visual QA Evidence Contract

QA must compare the approved blueprint against actual Webflow state or a captured snapshot. Reports without evidence cannot produce `[APPROVED]`.

## Required Fields

| Field | Required | Meaning |
|---|---|---|
| `blueprint_path` | yes | Relative path to the approved blueprint. |
| `webflow_state_ref` | yes | Relative path or MCP observation summary for the inspected Webflow state. |
| `snapshot_refs` | no | Relative paths to screenshots or captured state files. |
| `checks` | yes | List of visual, hierarchy, class, unit, and component checks. |
| `mismatches` | yes | Empty only when approval is justified. |
| `verdict` | yes | `[APPROVED]` or `[FIX]`. |
| `fix_owner` | required for `[FIX]` | Agent responsible for the next fix loop. |

## Report Shape

```json
{
  "blueprint_path": "workspace/blueprints/home.json",
  "webflow_state_ref": "workspace/state.json",
  "snapshot_refs": ["workspace/snapshots/home-after-build.png"],
  "checks": [
    {"name": "Client-First hierarchy", "status": "pass", "evidence": "workspace/page_structure.json"},
    {"name": "REM units", "status": "pass", "evidence": "workspace/state.json"}
  ],
  "mismatches": [],
  "verdict": "[APPROVED]",
  "fix_owner": "",
  "recorded_by": "client-first-architect"
}
```

## Rejection Rule

Return `[FIX]` when any mismatch lacks an owner, required fix, or evidence reference. Return `[FIX]` when Webflow state cannot be inspected.

