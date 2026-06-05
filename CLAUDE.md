# CLAUDE.md

Claude Code-native agentic workspace for the MAS V3 Figma→HTML→Webflow pipeline.

The pipeline is backed by two infrastructure layers:
- **Knowledge layer (Q1)**: `agentic/knowledge/client-first/` — distilled Finsweet Client-First docs (concepts, usability, gotchas) indexed at `INDEX.yaml`. Skills pull 1–3 files at runtime; never dump the whole folder.
- **Schema layer (Q2)**: `agentic/schemas/` + `.claude/skills/design-system-sync/schema/` — canonical JSON Schema 2020-12 for every pipeline artifact. Stable `figmaId` on every variable entry. Validated by `.claude/skills/_shared/scripts/validate_artifacts.py`. Refer to [Library Schema Index](agentic/schemas/library/schema_index.json) and [Webflow Schema Index](agentic/schemas/webflow/schema_index.json).

## Read First

1. Read `agentic/knowledge/token-sync-architecture.md` for the Figma→Repo→Webflow token flow model.
2. Read `agentic/specs/system/agent-system-spec.md` for the standalone agent-system contract.
3. Read `agentic/policies/approval-gates.md` before using Webflow, Figma, file writes, archiving and restoring, or any external connector.
4. Read `agentic/knowledge/client-first/INDEX.yaml` before selecting or validating Client-First classes — filter by `applicable_skill` to pull only relevant files.
5. Read `agentic/schemas/_shared/variable-entry.schema.json` before writing or transforming any design token — `figmaId` (format `VariableID:<id>:<index>`) is required on every entry.
6. Read `agentic/specs/README.md` for specifications reading order and pipeline stage guides.
7. Read `agentic/schemas/README.md` for JSON Schema file organizations and stage mappings.

## Common Commands

```bash
# 1. Parse CSS library and generate contracts/indexes
python .claude/skills/_shared/.claude/skills/_shared/scripts/index_css_library.py \
  --normalize agentic/knowledge/source-css/normalize.css \
  --webflow agentic/knowledge/source-css/webflow.css \
  --client-first agentic/knowledge/source-css/client-first-v2-2.webflow.css \
  --out agentic/knowledge/generated

# 2. Resolve Client-First classes (called by figma-to-html-architect skill)
python .claude/skills/_shared/scripts/resolve_client_first.py \
  --input workspace/semantic/tagged-blueprint.json

# 3. Validate workspace artifacts (block tier — must pass before any Webflow write)
python .claude/skills/_shared/scripts/validate_artifacts.py --workspace <name> --tier block

# 4. Unified quality gate (runs structure, contracts, variables, and index validations)
python .claude/skills/_shared/scripts/run_quality_gate.py --profile html-first

# Or run individual sub-gates for diagnostic purposes:
python .claude/skills/_shared/scripts/validate_agentic_structure.py
python .claude/skills/_shared/scripts/validate_workspace_artifacts.py
python .claude/skills/_shared/scripts/validate_css_contract.py
python .claude/skills/_shared/scripts/validate_css_index.py
python .claude/skills/_shared/scripts/validate_artifact_contracts.py

# 5. Deterministic orchestrator execution (Phase 1, Phase 2 Branch B)
python .claude/skills/figma-to-webflow-orchestrator/scripts/orchestrate.py \
  --workspace <name> --node-id <id>
```
## Local Setup

This repository must not track local configuration files such as `.claude/settings.local.json`.

To configure your local environment:
1. Copy `.claude/settings.example.json` to `.claude/settings.local.json`.
2. Configure local-only values (e.g., specific permissions) in `.claude/settings.local.json`.
3. Never commit `.claude/settings.local.json` to Git.

## Operating Rules

- **CSS Contract is Binding**: Allowed CSS variables/classes defined by `agentic/knowledge/generated/client-first-library-contract.json` are the binding source of truth. Cross-reference with `agentic/knowledge/client-first/INDEX.yaml` for semantic context.
- **Strict Class Selection**: Final HTML cannot use a class unless it exists in the contract, Webflow native classes, or approved structural conventions. Proposing or inventing new classes in strict mode blocks compilation. Governed by [class-selection.rules.yaml](agentic/rules/class-selection.rules.yaml).
- **Knowledge Lookup Before Class Selection**: Before selecting or validating Client-First classes, load `agentic/knowledge/client-first/INDEX.yaml` and pull only the 1–3 files matching the task's `applicable_skill` tag. Do not load all files.
- **figmaId is Mandatory**: Every design token/variable entry must carry a stable `figmaId` in `VariableID:<id>:<index>` format. Never use display names alone as cross-machine references — they drift on rename. Schema: `agentic/schemas/_shared/variable-entry.schema.json`.
- **Schema Validation Before Webflow Write**: Run `python .claude/skills/_shared/scripts/validate_artifacts.py --workspace <name> --tier block` before any Webflow mutation. A non-zero exit on the block tier is a hard stop.
- **Branch-First Deployments**: All mutations to Webflow must operate on a temporary site branch, never directly on main/master setups.
- **Single-Threaded Writes**: Webflow writes must be serialized to avoid database lockups. Concurrency policy ([concurrency-policy.yaml](agentic/rules/concurrency-policy.yaml)) enforces serial writes.
- **Retry Policy**: Webflow MCP API requests are governed by retry rules defined in [retry-policy.yaml](agentic/rules/retry-policy.yaml).
- **Webflow MCP Policy**: Operations must adhere to the tool limitations in [webflow-mcp.rules.yaml](agentic/rules/webflow-mcp.rules.yaml).
- **HTML QA and Alt Text Policies**: Output HTML is validated against the policies in [html-qa.rules.yaml](agentic/rules/html-qa.rules.yaml) and [asset-alt.rules.yaml](agentic/rules/asset-alt.rules.yaml).
- **Audit Trails**: Every Webflow mutation must write to `write-audit-log.jsonl` containing payloads and response codes.
- **Auto-Publish Forbidden**: Auto-publish is strictly forbidden from the build pipeline. Publishing is manually triggered or gated separately.
- Never silently overwrite existing files.
- Never use `whtml_builder`; build with Webflow native element operations.
- Always use REM units for spacing, sizes, and typography.
- **Never use absolute paths in the repository**: All references, documentation, scripts, and configurations must use relative paths (never absolute paths containing local directory prefixes like `Users/...`) unless absolutely required.
- **Mandatory Response Narration**: At the end of every response to the user, you MUST append a detailed narration explaining exactly what you did during the turn. List each step, the tool used, the specific action or command executed, and the output/result achieved in an `### Execution Log` markdown list.
- **User personal folders are off-limits**: Never suggest deleting, moving, or modifying `.user_bugs-log/`, `.user_guides/`, or `.user_versions/`. These are user-owned notes and version history, not pipeline artifacts. Skip them during any cleanup, audit, or file filtering pass.
- **Reference Integrity on Delete/Move**: Whenever you delete a file or modify a file path, you must check for any files referencing the old path. If the file path is modified, update the reference path in all occurrences. If the file is deleted, inspect and rewrite the referencing sections in those files, as deleting the file may impact their operation.

## Workflow Summary

1. User request enters via Claude Code chat. The orchestrator skill (`figma-to-webflow-orchestrator`) coordinates Branch A (design-system-sync) and Branch B (figma-to-html-architect).
2. Branch A extracts Figma raw data into `workspace/figma/` and `workspace/reports/`. Each variable entry must include `figmaId`.
3. Branch B normalizes nodes, resolves semantic roles/tags/classes using `agentic/knowledge/client-first/INDEX.yaml`, renders logical HTML blueprints, and slices chunks.
4. Orchestrator presents the logical build plan and stops for user approval.
5. Branch A compiles native operations. Runs `validate_artifacts.py --tier block` before any Webflow write.
6. Branch A builds in Webflow using serialization and branching rules.
7. Branch B runs `run_quality_gate.py --profile html-first` (includes artifact contract validation) and checks audit logs.
8. Orchestrator reports evidence-backed completion.
## Code Intelligence & Context (GitNexus & Repomix)

This repository is equipped with two tools to help you understand the codebase quickly:

1. **Repomix (Codebase Packager)**:
   - **What it is**: A tool that bundles all text files in the repository into a single structured file.
   - **Output file**: [repomix-output.xml](repomix-output.xml) (contains the full codebase content in XML format). Read this file if you need a complete picture of the code or want to search across all files quickly.
   - **Config file**: [repomix.config.json](repomix.config.json).

2. **GitNexus (Code Graph Indexer)**:
   - **What it is**: A code intelligence tool that builds a local knowledge graph of all symbols, relationships, and execution flows.
   - **Local Database**: Stored in `.gitnexus/` (gitignored).
   - **AI-Agent Guides**: See the GitNexus section below for rules, resources, and specific instruction manuals located in [.claude/skills/gitnexus/](.claude/skills/gitnexus/).

**Automatic Updates (Git Pre-Commit Hook)**:
A Git `pre-commit` hook is active in [.git/hooks/pre-commit](.git/hooks/pre-commit). Every time a commit is made, it automatically runs `repomix` and `gitnexus analyze` to update the XML context file and index database, then stages the changes automatically.

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
