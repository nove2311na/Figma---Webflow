# Skills Architecture — Script Invocation Detail

**Date:** 2026-06-04
**Purpose:** Document for each of the 3 Claude Code skills exactly which scripts are called, when, and what each script does (including cascading calls).

---

## Skill 1: `design-system-sync`

**Trigger:** User asks to sync Figma Variables and Styles to a Webflow project using Finsweet 2.2.

**LLM does:** Reads inputs, picks CF classes, fills templates, makes MCP calls.

### Scripts called (in order)

#### Task 0: `extract_client_first_baseline.py`
- **Called by:** SKILL.md Task 0
- **When:** Step 1 of any sync run — must complete before Task 1
- **Purpose:** Parse Webflow-exported CSS → isolate Client-First classes/variables, reject native (`.w-*`, `.wf-*`, default tags)
- **Input:** Webflow CSS path
- **Output:**
  - `workspace/<workspace-name>/design-system/client-first-baseline-contract.json` — the contract
  - `workspace/<workspace-name>/design-system/validations/client-first-extraction-report.json` — report
- **Halts if:** No Client-First classes/variables found (exit 1, error `NO_CLIENT_FIRST_BASELINE_FOUND`)
- **Triggers:** Nothing (leaf script)

#### Task 2: `validate_figma_extraction.py`
- **Called by:** SKILL.md Task 2
- **When:** After LLM fills `figma-contract.json` (Task 1) from Figma MCP `get_variable_defs`
- **Imports:** `_shared/selector_guards.py` (denylist check)
- **Purpose:** Safety gate — verify Figma extraction maps to baseline; flag `.w-*` native references, placeholder values, missing attributes
- **Input:** workspace name + baseline contract + figma-webflow-mapping.md
- **Output:** `validation_report.json` + `validation_report.txt`
- **Halts if:** Validation fails — delete invalid files, halt, ask user to fix Figma
- **Triggers:** Nothing (leaf script)

#### Task 3: `map_variables.py`
- **Called by:** SKILL.md Task 3
- **When:** After Task 2 passes
- **Purpose:** Map Figma variables → Webflow (Finsweet) variables, validate against baseline
- **Input:** `figma-contract.json` + baseline + mapping.md
- **Output:**
  - `workspace/<workspace-name>/design-system/webflow-contract.json`
  - `workspace/<workspace-name>/design-system/validations/mapping-report.json`
- **Halts if:** Mapping to native `.w-*` classes or non-existent baseline selectors without `projectExtension: true`
- **Triggers:** Nothing (leaf script)

#### Task 4: Webflow MCP write (NOT a script)
- **Action:** LLM uses Webflow MCP `variable_tool` + `style_tool` to push to branch
- **Before:** LLM writes preview to `webflow-sync-preview.json` + appends to `write-audit-log.jsonl`, then **stops for user approval** (`approve`/`revise`/`cancel`)
- **Branch:** `ws/<workspace-name>/design-system-sync` (never production)

### Script chain summary

```
SKILL.md Task 0 → extract_client_first_baseline.py (leaf)
SKILL.md Task 2 → validate_figma_extraction.py → selector_guards.py (import)
SKILL.md Task 3 → map_variables.py (leaf)
SKILL.md Task 4 → Webflow MCP tools (LLM in-loop, approval-gated)
```

---

## Skill 2: `figma-to-html-architect`

**Trigger:** User asks to turn a Figma node into Webflow-ready HTML.

**LLM does:** Extracts via Figma MCP, picks tags, picks CF classes, applies semantic mapping.

### Scripts called (in order)

#### Task 1: Figma MCP `get_design_context` (NOT a script)
- **Action:** LLM calls Figma MCP with `nodeId`, `artifactType: "REUSABLE_COMPONENT"`, `clientLanguage: "html, css"`, `forceCode: true`
- **Critical:** Figma variables preserved as `var(...)` in inline style (don't resolve to absolute values)
- **Output:** `workspace/<workspace-name>/components/<node-id>/raw-figma.html`

#### Task 2: `validate_figma_html.py`
- **Called by:** SKILL.md Task 2
- **When:** After LLM writes `raw-figma.html`
- **Imports:** `_shared/selector_guards.py` (denylist check via same pattern as Task 2 in design-system-sync)
- **Reads:** `html-semantic-mapping.json` (from references/) to validate `data-name` conventions
- **Purpose:** Verify approved `data-name` attributes; flag names conflicting with native Webflow widgets (`w-nav`, `w-slider`, `w-tabs`)
- **Modes:** `strict` (production) / `warn` (dev default) / `ignore`
- **Input:** workspace + node-id + mode
- **Output:** `html_validation_report.json`
- **Halts if:** Severe naming issues / widget conflicts in `strict` mode — delete raw file, halt, ask user
- **Triggers:** Nothing (leaf script)

#### Task 3: `process_html.py`
- **Called by:** SKILL.md Task 3
- **When:** After Task 2 passes
- **Imports:** `_shared/selector_guards.py` (denylist)
- **Reads:** `client-first-baseline-contract.json` + `webflow-contract.json` (do not hardcode class matching)
- **Reads:** `html-semantic-mapping.json` for rule objects (not substring matching)
- **Purpose:** Map raw HTML → final Webflow HTML
  - Map `data-name` → semantic tags
  - Map inline styles → baseline + design system classes
  - Preserve class ordering, handle self-closing tags, accessibility checks
- **Output:** `workspace/<workspace-name>/components/<node-id>/final-webflow.html`
- **Halts before completion:** Write `architect-diff-preview.json` + append to `write-audit-log.jsonl`, then **stop for user approval** (`approve`/`revise`/`cancel`). The architect never writes to Webflow directly.

### Script chain summary

```
SKILL.md Task 1 → Figma MCP get_design_context (LLM)
SKILL.md Task 2 → validate_figma_html.py → selector_guards.py (import) + html-semantic-mapping.json
SKILL.md Task 3 → process_html.py → selector_guards.py (import) + baseline + webflow-contract
                    → diff preview + audit log → STOP for user approval
```

---

## Skill 3: `figma-to-webflow-orchestrator`

**Trigger:** User starts a full Figma → Webflow migration (`/project:figma-to-webflow-orchestrator <workspace-name> <node-id>`).

**LLM does:** Coordinates the 2 other skills in parallel; consolidates evidence.

### Scripts called (in order)

#### Phase 1: Sequential contract init

1. **Triggers Skill 1, Task 0** — `extract_client_first_baseline.py` (described in Skill 1 above)
2. **Triggers Skill 1, Task 1** — Figma MCP `get_variable_defs` (LLM)
3. **Run safety gate:**
   ```bash
   python .claude/skills/design-system-sync/scripts/validate_figma_extraction.py --workspace <workspace-name>
   ```
   - **Called by:** Orchestrator SKILL.md Phase 1 step 3
   - **If fail:** halt, ask user/designer to fix missing variables in Figma
4. **Run variable mapping:**
   ```bash
   python .claude/skills/design-system-sync/scripts/map_variables.py --workspace <workspace-name>
   ```
   - **Called by:** Orchestrator SKILL.md Phase 1 step 4
   - **Output:** `webflow-contract.json`

#### Phase 2: Parallel processing

**Branch A (Webflow sync):** Triggers Skill 1, Task 4 (LLM, approval-gated, branch-first Webflow MCP writes)

**Branch B (HTML architect):** Spawns subagent to run Skill 2 in parallel:
1. LLM: Figma MCP `get_design_context` → `raw-figma.html`
2. `validate_figma_html.py` (Skill 2, Task 2)
3. `process_html.py` (Skill 2, Task 3) → `final-webflow.html`
4. Subagent returns status report

#### Phase 3: Consolidation

- LLM verifies `final-webflow.html` integrity
- LLM prints summary: variables synced, classes created, HTML files processed
- LLM notifies user

### Script chain summary

```
Orchestrator Phase 1:
  Trigger Skill 1 Task 0 → extract_client_first_baseline.py
  Trigger Skill 1 Task 1 → Figma MCP get_variable_defs (LLM)
  Run safety gate       → validate_figma_extraction.py (re-called by orchestrator)
  Run variable mapping  → map_variables.py (re-called by orchestrator)

Orchestrator Phase 2 (parallel):
  Branch A: Skill 1 Task 4 (LLM, Webflow MCP, approval-gated)
  Branch B: Spawn subagent → Skill 2 Tasks 1-3
              → validate_figma_html.py → process_html.py

Orchestrator Phase 3: LLM consolidate + report
```

**Note:** The orchestrator's own `orchestrate.py` script exists at `.claude/skills/figma-to-webflow-orchestrator/scripts/orchestrate.py` but is **never invoked by any code path**. The orchestrator skill is LLM-driven via SKILL.md, not script-driven. Kept as future entrypoint if user wants script-driven orchestration.

---

## Cross-cutting shared scripts (not skill-specific)

These are NOT called by any SKILL.md. They are infrastructure invoked manually or by other scripts.

| Script | Called by | Use case |
|---|---|---|
| `_shared/scripts/index_css_library.py` | Manual CLI | One-time setup: parse `source-css/` → `knowledge-base/generated/` |
| `_shared/scripts/resolve_client_first.py` | Agent `client-first-architect` | Figma inline styles → CF classes (used when agent runs the architect skill manually, not via orchestrator) |
| `_shared/scripts/run_quality_gate.py` | Manual CLI | Full html-first quality gate |
| `_shared/scripts/validate_artifacts.py` | `validate_artifact_contracts.py` subprocess + CLAUDE.md rule | Q2 schema validation block/warn/log |
| `_shared/scripts/utils.py` | `resolve_client_first.py` import | `parse_color`, `slugify`, `to_rem`, `color_distance` |
| `_shared/scripts/css_indexer/*.py` | `index_css_library.py` import | CSS parsing |
| `_shared/selector_guards.py` | `process_html.py` + `validate_figma_extraction.py` imports | Native class denylist |

---

## Approval gates (cross-cutting)

Every skill that writes to Webflow follows this pattern:
1. Render preview
2. Write preview file + append to `write-audit-log.jsonl`
3. **STOP** for user `approve` / `revise` / `cancel`
4. On approve, write to branch (never production)
5. Append success entry to `write-audit-log.jsonl`

Gates enforced at:
- Skill 1, Task 4 (Webflow sync)
- Skill 2, Task 3 (HTML diff before apply)
- Orchestrator Phase 2, Branch A (cascading)
