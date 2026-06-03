# CLAUDE.md

This folder is a Claude Code-native agentic workspace for the MAS V3 Figma-to-Webflow workflow.

## Read First

1. Read `agentic/memory/team-memory.md` for the current agent team, invariants, and operating boundaries.
2. Read `agentic/policies/runtime-instructions.md` for the MAS V3 mandates adapted to Claude Code.
3. Read `agentic/orchestration/sop.md` before starting any Figma-to-Webflow run.
4. Read `agentic/specs/agent-system-spec.md` for the standalone agent-system contract.
5. Read `agentic/orchestration/reflection-loop.md` and `agentic/orchestration/phase-state-machine.md` before closing or changing phases.
6. Read `agentic/policies/approval-gates.md` before using Webflow, Figma, file writes, archive/restore, or any external connector.

## Common Commands

```cmd
python scripts\init_workspace.py --project "Project Name" --figma "https://www.figma.com/design/file"
python scripts\gates\validate_agentic_structure.py --target .
python scripts\gates\run_quality_gate.py --target .
python scripts\gates\scan_secrets.py --target .
python scripts\gates\validate_agent_system_spec.py --target .
python scripts\gates\validate_skills.py --target .
python scripts\gates\validate_workspace_artifacts.py --target .
python scripts\gates\validate_phase_state.py --target .
python scripts\gates\validate_relative_paths.py --target .
```

Workspace lifecycle:

```cmd
python scripts\archive_workspace.py
python scripts\restore_workspace.py
python scripts\restore_workspace.py 0
```

## Operating Rules

- Never silently overwrite existing files.
- Never delete or restore `workspace/` unless the archive/restore safety gates pass.
- Never proceed from Blueprint to Webflow build until the user approves.
- Never use `whtml_builder`; build with Webflow native element operations and MCP-352.
- Always use REM units for spacing, sizes, and typography.
- Always record evidence in workspace JSON files before reporting progress.
- Always record Webflow actions with reason, action, observation, and next decision.
- Always run QA from real Webflow state or snapshots; do not guess visual parity.
- Treat `agentic/evals/standalone-architecture-baseline.md` as the local architecture baseline.
- Use `knowledge-base/client-first-class-map.json` before mapping Figma properties to Webflow classes.
- Use Python as the project automation language.
- Keep local filesystem references relative inside this folder.

## Workflow Summary

1. `@pm` receives the user request and checks `agentic/memory/session-handoff.md`, `agentic/orchestration/sop.md`, and workspace state.
2. `@operator` extracts Figma/raw data into `workspace/rawdata/` and `workspace/contents/`.
3. `@architect` produces Client-First blueprints in `workspace/blueprints/`.
4. `@pm` presents the blueprint and stops for approval.
5. `@operator` builds in Webflow using MCP-352.
6. `@gatekeeper` or `@architect` runs reflection review on risky artifacts.
7. `@architect` runs QA against actual Webflow state and records fixes.
8. `@pm` updates `agentic/memory/session-handoff.md` and reports evidence-backed completion.

<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **Figma---Webflow**. Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> Index stale? Run `node .gitnexus/run.cjs analyze` from the project root — it auto-selects an available runner. No `.gitnexus/run.cjs` yet? `npx gitnexus analyze` (npm 11 crash → `npm i -g gitnexus`; #1939).

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/Figma---Webflow/context` | Codebase overview, check index freshness |
| `gitnexus://repo/Figma---Webflow/clusters` | All functional areas |
| `gitnexus://repo/Figma---Webflow/processes` | All execution flows |
| `gitnexus://repo/Figma---Webflow/process/{name}` | Step-by-step execution trace |

<!-- gitnexus:end -->
