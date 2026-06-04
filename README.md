# Figma → HTML → Webflow Pipeline

Claude Code-native workspace for compiling Figma designs into Webflow pages with strict Finsweet Client-First V2 conformance.

## Goal

```
Figma file  →  valid HTML (Client-First)  →  Webflow site
```

Two compilation steps:
1. **Figma → HTML** — extract design, resolve inline styles into Finsweet Client-First classes, validate locally.
2. **HTML → Webflow** — push validated HTML to a Webflow site branch using Webflow MCP.

## Backing Infrastructure Layers

| Layer | Path | Purpose |
|---|---|---|
| **Knowledge (Q1)** | `agentic/knowledge/client-first/` | Distilled Finsweet Client-First docs (concepts, usability, gotchas) indexed at `INDEX.yaml`. Skills pull 1–3 files at runtime. |
| **Schema (Q2)** | `agentic/schemas/` | JSON Schema 2020-12 validations. Organised index at [schemas/README.md](file:///g:/My%20Drive/10_Learning/_Research/auto-research/.docs/source/MAS-Figma-Webflow-khang/agentic/schemas/README.md). Sub-indices: [Library Schemas](file:///g:/My%20Drive/10_Learning/_Research/auto-research/.docs/source/MAS-Figma-Webflow-khang/agentic/schemas/library/schema_index.json) & [Webflow Schemas](file:///g:/My%20Drive/10_Learning/_Research/auto-research/.docs/source/MAS-Figma-Webflow-khang/agentic/schemas/webflow/schema_index.json). |
| **Specs & reading** | `agentic/specs/` | Pipeline specifications index: [specs/README.md](file:///g:/My%20Drive/10_Learning/_Research/auto-research/.docs/source/MAS-Figma-Webflow-khang/agentic/specs/README.md). |
| **Token flow** | `agentic/knowledge/token-sync-architecture.md` | 3-way ledger model: Figma = design SoT, Repo = git-versioned ledger, Webflow = build target. |

## Pipeline

```
Figma MCP
  → index_css_library.py (parse agentic/knowledge/source-css/ → agentic/knowledge/generated/)
  → design-system-sync skill (extract + validate + map variables to Webflow)
  → .claude/skills/_shared/scripts/validate_artifacts.py --tier block  (block-tier gate)
  → figma-to-html-architect skill (Figma node → semantic HTML with CF classes)
  → User approval
  → figma-to-webflow-orchestrator skill (push HTML to Webflow branch)
  → .claude/skills/_shared/scripts/run_quality_gate.py --profile html-first  (full quality gate)
```

## Skills

The pipeline is driven by 3 Claude Code skills under `.claude/skills/`:

- **`design-system-sync`** — Sync Figma variables + styles to Webflow. Extract Client-First baseline, validate Figma extraction, map variables, write to Webflow (approval-gated). Reference schema definitions via [Library Schemas](file:///g:/My%20Drive/10_Learning/_Research/auto-research/.docs/source/MAS-Figma-Webflow-khang/agentic/schemas/library/schema_index.json).
- **`figma-to-html-architect`** — Turn a Figma node into Webflow-ready HTML with Client-First classes. Validates `data-name` conventions, resolves semantic tags, halts for review on failures. Reference policy rules: [class-selection](file:///g:/My%20Drive/10_Learning/_Research/auto-research/.docs/source/MAS-Figma-Webflow-khang/agentic/rules/class-selection.rules.yaml), [html-qa](file:///g:/My%20Drive/10_Learning/_Research/auto-research/.docs/source/MAS-Figma-Webflow-khang/agentic/rules/html-qa.rules.yaml), [asset-alt](file:///g:/My%20Drive/10_Learning/_Research/auto-research/.docs/source/MAS-Figma-Webflow-khang/agentic/rules/asset-alt.rules.yaml).
- **`figma-to-webflow-orchestrator`** — Coordinate the two above in parallel. Branch A pushes variables; Branch B renders HTML. Consolidates evidence at end. Runs deterministic steps via `orchestrate.py`. Governed by [concurrency-policy.yaml](file:///g:/My%20Drive/10_Learning/_Research/auto-research/.docs/source/MAS-Figma-Webflow-khang/agentic/rules/concurrency-policy.yaml) and [retry-policy.yaml](file:///g:/My%20Drive/10_Learning/_Research/auto-research/.docs/source/MAS-Figma-Webflow-khang/agentic/rules/retry-policy.yaml).

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

## Operating Rules

- **CSS Contract is Binding** — `agentic/knowledge/generated/client-first-library-contract.json` is the source of truth. Cross-reference `agentic/knowledge/client-first/INDEX.yaml` for semantic context.
- **Knowledge Lookup Before Class Selection** — Load `INDEX.yaml`, filter by `applicable_skill`, pull 1–3 files. Never full-dump.
- **figmaId is Mandatory** — Every variable entry must carry `figmaId` in `VariableID:<id>:<index>` format. Display names drift; figmaIds don't.
- **Schema Validation Before Webflow Write** — `validate_artifacts.py --tier block` exit 0 is required before any Webflow mutation. Refer to [Webflow Schemas](file:///g:/My%20Drive/10_Learning/_Research/auto-research/.docs/source/MAS-Figma-Webflow-khang/agentic/schemas/webflow/schema_index.json). Check against [concurrency-policy.yaml](file:///g:/My%20Drive/10_Learning/_Research/auto-research/.docs/source/MAS-Figma-Webflow-khang/agentic/rules/concurrency-policy.yaml), [retry-policy.yaml](file:///g:/My%20Drive/10_Learning/_Research/auto-research/.docs/source/MAS-Figma-Webflow-khang/agentic/rules/retry-policy.yaml), and [webflow-mcp.rules.yaml](file:///g:/My%20Drive/10_Learning/_Research/auto-research/.docs/source/MAS-Figma-Webflow-khang/agentic/rules/webflow-mcp.rules.yaml).
- **Branch-First Deployments** — All Webflow writes target temporary branches.
- **Single-Threaded Writes** — Webflow writes serialized to avoid lockups.
- **Audit Trails** — Every Webflow mutation logs to `write-audit-log.jsonl`.
- **Auto-Publish Forbidden** — Publishing is manual.
- **No `whtml_builder`** — Use Webflow native element operations.
- **REM Units** — Spacing, sizing, typography in REM.
- **Relative Paths Only** — No `Users/...` absolute paths in committed files.
- **User Personal Folders Off-Limits** — `.user_bugs-log/`, `.user_guides/`, `.user_versions/` are user-owned; never modify during cleanup.

## Repository Layout

```
FigWebflow/
├── CLAUDE.md                          # Operational rules + Read First
├── README.md                          # This file
├── agentic/
│   ├── knowledge/
│   │   ├── client-first/              # Q1: distilled Client-First docs + INDEX.yaml
│   │   ├── client-first-class-map.json # Structured CF class library
│   │   ├── generated/                 # Output of index_css_library.py
│   │   ├── source-css/                # Input: Finsweet + Webflow + normalize CSS
│   │   └── token-sync-architecture.md # Figma→Repo→Webflow ledger model
│   ├── schemas/                       # Q2: canonical JSON Schema 2020-12
│   ├── specs/                         # Pipeline + system specs
│   ├── policies/                      # approval-gates + validation-gates
│   ├── rules/                         # YAML rule files (1 actively loaded)
│   └── memory/                        # Memory folder README
├── .claude/skills/_shared/scripts/   # Cross-skill: CSS parser, resolver, gates, utils
├── .claude/
│   ├── skills/                        # 3 skills: design-system-sync, figma-to-html-architect, figma-to-webflow-orchestrator
│   └── agents/                        # Agent persona definitions
├── workspace/                         # Generated artifacts (per-run state)
└── .user_bugs-log/                    # User notes (off-limits)
```

## Verification

```bash
# All gates pass
python .claude/skills/_shared/scripts/run_quality_gate.py --profile html-first
# → quality gate [html-first]: PASS
```
