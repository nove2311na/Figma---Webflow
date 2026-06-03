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
# 1. Parse CSS library to build contract
python scripts\index_css_library.py --normalize source-css\normalize.css --webflow source-css\webflow.css --client-first source-css\client-first-v2-2.webflow.css --out knowledge-base\generated

# 2. Normalize Figma nodes
python scripts\normalize_figma_nodes.py --input workspace\figma\figma.node-bundle.json

# 3. Resolve semantic roles and classes
python scripts\resolve_semantic_ir.py

# 4. Render HTML from blueprint
python scripts\render_html_from_blueprint.py

# 5. Slice page HTML into section chunks
python scripts\slice_html_into_chunks.py

# 6. Compile native ops plan
python scripts\compile_native_ops_from_html.py

# 7. Unified quality gate validation
python scripts\gates\run_quality_gate.py --profile html-first
```

Workspace lifecycle:

```cmd
python scripts\archive_workspace.py
python scripts\restore_workspace.py
python scripts\restore_workspace.py 0
```

## Operating Rules

- **CSS Contract is Binding**: Allowed CSS variables/classes defined by the generated CSS library contract (`client-first-library-contract.json`) are the binding source of truth.
- **Strict Class Selection**: Final HTML cannot use a class unless it exists in the contract, Webflow native classes, or approved structural conventions. Proposing or inventing new classes in strict mode blocks compilation.
- **Branch-First Deployments**: All mutations to Webflow must operate on a temporary site branch, never directly on main/master setups.
- **Single-Threaded Writes**: Webflow writes must be serialized to avoid database lockups. Concurrency policy enforces serial writes.
- **Audit Trails**: Every Webflow mutation must write to `write-audit-log.jsonl` containing payloads and response codes.
- **Auto-Publish Forbidden**: Auto-publish is strictly forbidden from the build pipeline. Publishing is manually triggered or gated separately.
- Never silently overwrite existing files.
- Never use `whtml_builder`; build with Webflow native element operations.
- Always use REM units for spacing, sizes, and typography.
- Keep local filesystem references relative inside this folder.

## Workflow Summary

1. `@pm` receives the user request and checks `agentic/memory/session-handoff.md`, `agentic/orchestration/sop.md`, and workspace state.
2. `@operator` extracts Figma/raw data into `workspace/figma/` and `workspace/reports/`.
3. `@architect` normalizes nodes, resolves semantic roles/tags/classes, renders logical HTML blueprints, and slices chunks.
4. `@pm` presents the logical build plan and stops for approval.
5. `@operator` compiles native operations and builds in Webflow using serialization and branching rules.
6. `@gatekeeper` runs quality gates and checks audit logs.
7. `@pm` updates `agentic/memory/session-handoff.md` and reports evidence-backed completion.

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
