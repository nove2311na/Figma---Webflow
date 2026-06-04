# Validation Gates Policy

This policy defines which artifacts are schema-validated, at what severity, and by which gate. Mirrors `mcp-risk-auth-map.md` for MCP operations.

**Audience**: every skill that produces or consumes a JSON contract (`design-system-sync`, `figma-to-html-architect`, `figma-to-webflow-orchestrator`).

**How to apply**: `scripts/validation/validate_artifacts.py --workspace <name> --tier <block|warn|log>` runs the gates. Wire into `scripts/gates/run_quality_gate.py --profile html-first` for the standard pipeline run.

## Tiers

| Tier | Meaning | On failure |
|---|---|---|
| **block** | Artifact must be valid. Build halts. Operator must fix the producer. | Exit code 2, halt. |
| **warn** | Artifact should be valid. Build continues. Warning logged. | Exit code 0, log to `qa-report.json`. |
| **log** | Artifact tracked but not gated. Build continues. Stats emitted. | Exit code 0, log to `state.log`. |

## Artifact → tier map

### Block tier (must validate)

| Artifact | Schema | Producer | Validator |
|---|---|---|---|
| `write-audit-log.jsonl` | `agentic/schemas/webflow/webflow-write-audit-log.schema.json` | `figma-to-webflow-orchestrator` (Branch A) | `scripts/validation/validate_artifacts.py` |
| `figma-contract.json` | `.claude/skills/design-system-sync/schema/figma-design-system-contract.schema.json` | LLM via figma-dev-mode-mcp (Task 1) | `design-system-sync/scripts/validate_figma_extraction.py` |
| `webflow-contract.json` | `.claude/skills/design-system-sync/schema/webflow-design-system-contract.schema.json` | `map_variables.py` (Task 3) | `design-system-sync/scripts/validate_figma_extraction.py` |
| `blueprint.json` | `agentic/schemas/workspace/blueprint.schema.json` | `figma-to-html-architect` (Task 3) | `scripts/validation/validate_artifacts.py` |
| `subagent-task.json` | `agentic/schemas/workspace/subagent-task.schema.json` | `figma-to-webflow-orchestrator` (Phase 2 fork) | `scripts/validation/validate_artifacts.py` |
| `mcp-sync-report.json` | `agentic/schemas/webflow/mcp-sync-report.schema.json` | Branch A (Webflow MCP) | `scripts/validation/validate_artifacts.py` |
| `client-first-baseline-contract.json` | `.claude/skills/design-system-sync/schema/client-first-baseline-contract.schema.json` | `extract_client_first_baseline.py` (Task 0) | `scripts/validation/validate_artifacts.py` |

### Warn tier (should validate, build continues)

| Artifact | Schema | Producer | Validator |
|---|---|---|---|
| `qa-report.json` | `agentic/schemas/workspace/qa-report.schema.json` | `qa-gatekeeper` | `scripts/validation/validate_artifacts.py` |
| `page-structure.json` | `agentic/schemas/workspace/page-structure.schema.json` | `figma-to-html-architect` (Phase 2) | `scripts/validation/validate_artifacts.py` |

### Log tier (tracked, not gated)

| Artifact | Schema | Producer |
|---|---|---|
| `state.log` | (freeform) | orchestrator |
| `error.log` | `agentic/schemas/workspace/error-log.schema.json` | any |

## Cross-cutting rules

- **No silent overwrite** (CLAUDE.md): validation never mutates the artifact. If invalid, halt or warn — never patch.
- **Stable IDs are required** for `figma-contract.json` and `webflow-contract.json`. Templates use `VariableID:tpl-*`; production must replace with real ids.
- **REM units only** (CLAUDE.md): variable values with `unit: "em" | "vh" | "vw" | "pt"` are flagged warn.
- **Native class denylist**: any class matching `webflow-native-class-index.json` in the HTML output is block (per the `figma-to-html-architect` policy).

## Command surface

```bash
# Default: run all tiers
python scripts/validation/validate_artifacts.py --workspace <name>

# Single tier
python scripts/validation/validate_artifacts.py --workspace <name> --tier block

# List tiers + artifact map
python scripts/validation/validate_artifacts.py --list-tiers

# Validate a single artifact by path
python scripts/validation/validate_artifacts.py --path workspace/<name>/design-system/webflow-contract.json
```

## Exit codes

- `0` — all artifacts at the requested tier(s) pass.
- `1` — usage error (bad args, missing workspace).
- `2` — block-tier violation. Build halts.
- `3` — internal error (schema load failure, IO error). Investigate.
