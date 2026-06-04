# CLAUDE.md

Claude Code-native agentic workspace for the MAS V3 Figma→HTML→Webflow pipeline.

The pipeline is backed by two infrastructure layers:
- **Knowledge layer (Q1)**: `knowledge-base/client-first/` — distilled Finsweet Client-First docs (concepts, usability, gotchas) indexed at `INDEX.yaml`. Skills pull 1–3 files at runtime; never dump the whole folder.
- **Schema layer (Q2)**: `agentic/schemas/` + `.claude/skills/design-system-sync/schema/` — canonical JSON Schema 2020-12 for every pipeline artifact. Stable `figmaId` on every variable entry. Validated by `scripts/validation/validate_artifacts.py`.

## Read First

1. Read `agentic/memory/team-memory.md` for the current agent team, invariants, and operating boundaries.
2. Read `agentic/policies/runtime-instructions.md` for the MAS V3 mandates adapted to Claude Code.
3. Read `agentic/orchestration/sop.md` before starting any Figma-to-Webflow run.
4. Read `agentic/specs/agent-system-spec.md` for the standalone agent-system contract.
5. Read `agentic/orchestration/reflection-loop.md` and `agentic/orchestration/phase-state-machine.md` before closing or changing phases.
6. Read `agentic/policies/approval-gates.md` before using Webflow, Figma, file writes, archiving and restoring, or any external connector.
7. Read `knowledge-base/client-first/INDEX.yaml` before selecting or validating Client-First classes — filter by `applicable_skill` to pull only relevant files.
8. Read `agentic/schemas/_shared/variable-entry.schema.json` before writing or transforming any design token — `figmaId` (format `VariableID:<id>:<index>`) is required on every entry.

## Common Commands

```cmd
# 1. Parse CSS library to build contract
python scripts/pipeline/index_css_library.py --normalize source-css/normalize.css --webflow source-css/webflow.css --client-first source-css/client-first-v2-2.webflow.css --out knowledge-base/generated

# 2. Extract raw styling and layout blueprint from Figma
python scripts/pipeline/extract_raw_styling.py --input workspace/figma/figma.raw-context.json

# 3. Resolve Client-First classes and snap variables
python scripts/pipeline/resolve_client_first.py --input workspace/figma/raw-layout-blueprint.json

# 4. Render HTML from blueprint
python scripts/pipeline/render_html_from_blueprint.py

# 5. Slice page HTML into section chunks
python scripts/pipeline/slice_html_into_chunks.py

# 6. Compile native ops plan
python scripts/pipeline/compile_native_ops_from_html.py

# 7. Validate workspace artifacts (block tier must pass before Webflow write)
python scripts/validation/validate_artifacts.py --workspace <workspace-name> --tier block

# 8. Unified quality gate
python scripts/gates/run_quality_gate.py --profile html-first
```

## Operating Rules

- **CSS Contract is Binding**: Allowed CSS variables/classes defined by `knowledge-base/generated/client-first-library-contract.json` are the binding source of truth. Cross-reference with `knowledge-base/client-first/INDEX.yaml` for semantic context.
- **Strict Class Selection**: Final HTML cannot use a class unless it exists in the contract, Webflow native classes, or approved structural conventions. Proposing or inventing new classes in strict mode blocks compilation.
- **Knowledge Lookup Before Class Selection**: Before selecting or validating Client-First classes, load `knowledge-base/client-first/INDEX.yaml` and pull only the 1–3 files matching the task's `applicable_skill` tag. Do not load all files.
- **figmaId is Mandatory**: Every design token/variable entry must carry a stable `figmaId` in `VariableID:<id>:<index>` format. Never use display names alone as cross-machine references — they drift on rename. Schema: `agentic/schemas/_shared/variable-entry.schema.json`.
- **Schema Validation Before Webflow Write**: Run `python scripts/validation/validate_artifacts.py --workspace <name> --tier block` before any Webflow mutation. A non-zero exit on the block tier is a hard stop.
- **Branch-First Deployments**: All mutations to Webflow must operate on a temporary site branch, never directly on main/master setups.
- **Single-Threaded Writes**: Webflow writes must be serialized to avoid database lockups. Concurrency policy enforces serial writes.
- **Audit Trails**: Every Webflow mutation must write to `write-audit-log.jsonl` containing payloads and response codes.
- **Auto-Publish Forbidden**: Auto-publish is strictly forbidden from the build pipeline. Publishing is manually triggered or gated separately.
- Never silently overwrite existing files.
- Never use `whtml_builder`; build with Webflow native element operations.
- Always use REM units for spacing, sizes, and typography.
- **Never use absolute paths in the repository**: All references, documentation, scripts, and configurations must use relative paths (never absolute paths containing local directory prefixes like `Users/...`) unless absolutely required.
- **Mandatory Response Narration**: At the end of every response to the user, you MUST append a detailed narration explaining exactly what you did during the turn. List each step, the tool used, the specific action or command executed, and the output/result achieved in an `### Execution Log` markdown list.
- **User personal folders are off-limits**: Never suggest deleting, moving, or modifying `.user_bugs-log/`, `.user_guides/`, or `.user_versions/`. These are user-owned notes and version history, not pipeline artifacts. Skip them during any cleanup, audit, or file filtering pass.

## Workflow Summary

1. `@pm` receives the user request and checks `agentic/memory/session-handoff.md`, `agentic/orchestration/sop.md`, and workspace state.
2. `@operator` extracts Figma/raw data into `workspace/figma/` and `workspace/reports/`. Each variable entry must include `figmaId`.
3. `@architect` normalizes nodes, resolves semantic roles/tags/classes using `knowledge-base/client-first/INDEX.yaml`, renders logical HTML blueprints, and slices chunks.
4. `@pm` presents the logical build plan and stops for approval.
5. `@operator` compiles native operations. Runs `validate_artifacts.py --tier block` before any Webflow write.
6. `@operator` builds in Webflow using serialization and branching rules.
7. `@gatekeeper` runs `run_quality_gate.py --profile html-first` (includes artifact contract validation) and checks audit logs.
8. `@pm` updates `agentic/memory/session-handoff.md` and reports evidence-backed completion.
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

This project is indexed by GitNexus as **Figma---Webflow** (1145 symbols, 1323 relationships, 16 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

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

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
