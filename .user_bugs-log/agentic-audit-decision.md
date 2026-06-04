# Agentic Folder Audit — Decision Record

**Date:** 2026-06-04
**Trigger:** Q1 (knowledge layer) + Q2 (schema layer) complete. Repo now has 3 Claude Code skills (`design-system-sync`, `figma-to-html-architect`, `figma-to-webflow-orchestrator`) that handle the Figma → HTML → Webflow flow natively. The legacy `agentic/orchestration/`, `agentic/prompts/`, partial `agentic/memory/` multi-agent docs reference scripts/paths that no longer exist.

**Outcome:** Keep legacy multi-agent docs (no execution of mass-deletion). Record decision so future work can re-activate selectively when needed.

---

## 1. State Trước (what exists)

### 1.1 `agentic/orchestration/` (282 lines total)

| File | Lines | Loaded by code? | Gate-pinned? | Historical role |
|---|---|---|---|---|
| `sop.md` | 45 | No (refs `extract_raw_styling.py` which doesn't exist) | Yes (keywords `Phase 0` `Phase 1` `Phase 2` `Phase 3` `approval`) | 4-phase multi-agent SOP (extract → translate → audit → sync) |
| `workflow-map.md` | 37 | No | No | Visual flow diagram, refs deleted `component-registry.json` paths |
| `phase-state-machine.md` | 55 | No | No | State machine for 4 phases (0/1/2/3 + reflection) |
| `reflection-loop.md` | 42 | No | Yes (keywords `reflection_review` `revise` `Stop Conditions`) | Per-phase reflection protocol |
| `handoff-contracts.md` | 84 | No | No | JSON contract for agent-to-agent handoffs |
| `retry-and-stop-conditions.md` | 19 | No | No | Multi-agent retry policy |

**Historical role:** This folder documents the MAS V3 multi-agent system (PM + Architect + Operator + Gatekeeper). The 4 agents communicate via workspace JSON artifacts, not direct calls. With Q1/Q2 done, Claude Code's 3 skills replace this — they coordinate via user's chat, not via workspace handoffs.

### 1.2 `agentic/prompts/` (450 lines total)

| File | Lines | Loaded by code? | Historical role |
|---|---|---|---|
| `extraction/extract-figma-context.md` | 26 | No | Prompt template for Figma extraction |
| `extraction/read-figma-data.md` | 229 | No | Long prompt for raw Figma data reading |
| `extraction/sync-design-system-from-figma.md` | 25 | No | Prompt template for design system sync |
| `resolution/generate-cf-library.md` | 170 | No | Prompt for generating Client-First library |

**Historical role:** Hand-crafted prompt templates for each MAS V3 agent task. The skills in `.claude/skills/*/SKILL.md` now embed workflow directly — no need for separate prompt files.

### 1.3 `agentic/memory/` (131 lines total)

| File | Lines | Loaded by code? | Gate-pinned? | Historical role |
|---|---|---|---|---|
| `README.md` | 14 | No | No | Explains memory folder purpose |
| `team-memory.md` | 45 | No | No | Hard Invariants + Agent Team table. Refs deleted `agentic/evals/standalone-architecture-baseline.md` |
| `session-handoff.md` | 45 | No | No | Per-session state handoff between PM and agents |
| `memory-candidates.md` | 5 | No | No | Scratchpad for promoting long-term memory |

**Historical role:** Persistent state between agent sessions. The session-handoff + memory-candidates pattern supports the @pm role which is not used in current Claude Code skill flow.

### 1.4 `agentic/knowledge/` (305 lines, partial stale)

| File | Lines | Stale ref to | Role |
|---|---|---|---|
| `token-sync-architecture.md` | 142 | None — current | **KEEP** — describes Figma → Repo → Webflow 3-way ledger |
| `project-overview.md` | 21 | `client-first-theory.md` (deleted), `MCP-352` | Stale |
| `system-map.md` | 28 | `archives/` (deleted) | Stale |
| `source-index.md` | 24 | `agentic/evals/` (deleted) | Stale |
| `webflow-mcp-capabilities.md` | 90 | Likely | Capability list, age unknown |
| ~~`client-first-library.md`~~ | ~~65~~ | n/a | **DELETED** in 2026-06-04 cleanup |

### 1.5 `agentic/specs/` (584 lines, mixed)

**Keep:**
- `system/agent-system-spec.md` (179) — describes the 3 skills + agent matrix (still accurate)
- `system/workspace-artifact-schemas.md` (25) — workspace folder contract
- `contracts/figma-to-client-first-mapping.md` (219) — Sections A–G real decision algorithm

**Stale/light:**
- `pipeline/figma-extraction-contract.md` (12) — minimal
- `pipeline/html-tag-resolution.md` (12) — refs `[new]-semantic-html-resolver` (doesn't exist)
- `pipeline/asset-and-image-policy.md` (10) — minimal
- `pipeline/webflow-branch-strategy.md` (11) — minimal
- `pipeline/webflow-mcp-sync.md` (28) — minimal
- `pipeline/html-first-pipeline.md` (23) — minimal
- `contracts/client-first-library-contract.md` (8) — minimal
- `contracts/component-registry-contract.md` (19) — refs deleted `tools/library_resolver.py`
- `contracts/visual-qa-evidence-contract.md` (38) — old `[APPROVED]` format, doesn't match current

### 1.6 `agentic/policies/` (372 lines, mixed)

**Keep:**
- `approval-gates.md` (16) — list of approval gates
- `validation-gates.md` (73) — block/warn/log tier policy (Q2)

**Likely stale:**
- `build-discipline.md` (136) — 8 patterns D-1..D-8 for multi-agent, doesn't apply to Claude Code
- `mcp-risk-auth-map.md` (18) — MCP risk levels, may be stale
- `no-overwrite-policy.md` (20) — overlap with CLAUDE.md
- `runtime-instructions.md` (97) — MAS V3 mandates, may be stale
- `tool-risk-levels.md` (12) — R0–R4 risk class

### 1.7 `agentic/rules/` (6 YAML files, ~285 lines total)

| File | Lines | Loaded by code? |
|---|---|---|
| `class-selection.rules.yaml` | 348 bytes | Yes (loaded by `resolve_client_first.py` via `--class-rules`) |
| `webflow-mcp.rules.yaml` | 271 bytes | No (was for old operator agent) |
| `html-qa.rules.yaml` | 316 bytes | No |
| `asset-alt.rules.yaml` | 285 bytes | No |
| `concurrency-policy.yaml` | 203 bytes | No |
| `retry-policy.yaml` | 195 bytes | No |

**Status:** Only `class-selection.rules.yaml` is actively loaded. Others are policy declarations without runtime consumers — kept for documentation.

### 1.8 `agentic/schemas/` (Q2 layer, all actively used)

- `_shared/{meta,ref-envelope,variable-entry}.schema.json` — building blocks
- `library/{client-first-library,library-registry,project-library}.schema.json` + `schema_index.json`
- `webflow/{mcp-sync-report,webflow-write-audit-log}.schema.json` + `schema_index.json`
- `semantic/semantic-tree.schema.json`
- `html/alt-policy.schema.json`
- `workspace/{blueprint,error-log,meta,page-structure}.schema.json`

All loaded by `scripts/validation/validate_artifacts.py` with tier-based policy (block/warn/log).

---

## 2. State Sau (proposed — NOT YET EXECUTED)

### 2.1 KEEP AS-IS (used by current pipeline)

- `agentic/schemas/` — Q2 layer, all wired into validate_artifacts.py + gates
- `agentic/schemas/_shared/` — variable-entry, ref-envelope, meta
- `agentic/specs/contracts/figma-to-client-first-mapping.md` — Sections A–G decision algorithm
- `agentic/specs/system/agent-system-spec.md` — describes the 3 skills
- `agentic/specs/system/workspace-artifact-schemas.md` — workspace layout
- `agentic/knowledge/token-sync-architecture.md` — Figma → Repo → Webflow token flow
- `agentic/policies/approval-gates.md` — approval gate list
- `agentic/policies/validation-gates.md` — block/warn/log tier
- `agentic/rules/` — 6 YAML rule files (1 actively loaded, 5 documented)
- `agentic/memory/README.md` — explains memory structure
- `tools/`, `source-css/`, `knowledge-base/`, `.claude/skills/`, `scripts/`

### 2.2 REWRITE (content stale, intent still valid)

- `README.md` — full rewrite for Q1/Q2 architecture (currently describes old pipeline)
- `CLAUDE.md` Read First item 4 — fix path `agentic/specs/agent-system-spec.md` → `agentic/specs/system/agent-system-spec.md`
- `AGENTS.md` — currently only contains GitNexus block; can be deleted or rewritten

### 2.3 LEGACY (no current use, kept for future re-activation)

- `agentic/orchestration/` (6 files, 282 lines) — multi-agent SOP, 4-phase state machine, handoff contracts
- `agentic/prompts/` (4 files, 450 lines) — extract-figma-context, read-figma-data, sync-design-system-from-figma, generate-cf-library
- `agentic/memory/team-memory.md`, `session-handoff.md`, `memory-candidates.md` (3 files, 95 lines)

These reference scripts and concepts that no longer exist (e.g. `extract_raw_styling.py`, `mcp-352`, `[new]-semantic-html-resolver`). Kept for now — not actively misleading because no agent reaches them in current flow.

---

## 3. Re-activation Triggers (when to bring back legacy)

| Future need | Re-activate from section 2.3 |
|---|---|
| Need PM-led orchestration with user-facing chat | `agentic/memory/team-memory.md` + `agentic/orchestration/sop.md` |
| Need 4-phase state machine | `agentic/orchestration/phase-state-machine.md` |
| Need ReAct trace format for debugging | `agentic/orchestration/handoff-contracts.md` |
| Need per-phase reflection protocol | `agentic/orchestration/reflection-loop.md` |
| Need prompt template for Figma extraction (when re-introducing Figma MCP call patterns) | `agentic/prompts/extraction/extract-figma-context.md` |
| Need prompt template for raw Figma data reading | `agentic/prompts/extraction/read-figma-data.md` |
| Need prompt template for design system sync | `agentic/prompts/extraction/sync-design-system-from-figma.md` |
| Need prompt template for Client-First library generation | `agentic/prompts/resolution/generate-cf-library.md` |
| Need session-to-session state handoff | `agentic/memory/session-handoff.md` |
| Need memory promotion protocol | `agentic/memory/memory-candidates.md` |

---

## 4. Risks if not cleaned up later

- Agent could read `agentic/orchestration/sop.md` and try to call `extract_raw_styling.py` (doesn't exist) → hallucinate or fail
- Agent could read `agentic/knowledge/project-overview.md` and see refs to `client-first-theory.md` (deleted) → confused
- Future contributor sees large `agentic/` folder with stale content → assumes multi-agent system is active → adds new code targeting deleted paths
- Quality gates continue to check `Phase 0` `Phase 1` keywords in `sop.md` (working as designed — gate passes since file exists with those strings) but the actual content is documentation-only

## 5. Risks if cleaned up now

- If user later wants to revive multi-agent system, no reference docs to copy from
- Loss of historical context for why certain decisions were made in MAS V3

**Net assessment:** Risk of confusion > risk of losing future reference, **but** documentation cost is low (just leave files + this decision record), so keep-with-record is the safer call right now.
