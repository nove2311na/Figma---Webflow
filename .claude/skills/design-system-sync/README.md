# `design-system-sync` Skill — Operating Manual

Caveman mode: full. No filler.

Sync a **prepared** Figma design-system file into a Webflow site through two canonical runtime artifacts. Branch A of the MAS V3 Figma→HTML→Webflow pipeline.

---

## 0. One-line mental model

```
Figma MCP payload  →  figma-design-system.json  →  webflow-design-system.json  →  Webflow MCP writes
       (extract)          (validate)                    (map)                          (sync)
```

6 Tasks. Each Task = one script + one or two artifact files. Never skip Tasks. Never reorder.

---

## 1. Folder map (what each file does, when it shows up)

### `.claude/skills/design-system-sync/`

| File | Role | Appears when |
|------|------|--------------|
| `SKILL.md` | Skill entry point. Declares name + description in YAML frontmatter (Claude auto-loads). Body = 6 Tasks, policies, success criteria. | LLM loads skill metadata at session start. Body read on demand. |
| `README.md` | This file. Human-facing operating manual. | Read first by humans and reviewers. |

### `template/` (authoritative shape, **never edit at runtime**)

| File | Role | Appears when |
|------|------|--------------|
| `template/figma-mcp-variable-defs.input-template.json` | Example normalized input shape for Figma MCP `get_variable_defs`. Used by agents as the requested/normalized payload format before Task 1 build. | LLM reads before calling or normalizing Figma MCP output. |
| `template/figma-design-system-contract.json` | Required Figma artifact shape. Figma file **must** expose these variable/style keys. Used by `build_figma_design_system.py` as overlay skeleton. | LLM reads first when user says "sync Figma to Webflow". Designer reads to prepare Figma file. |
| `template/webflow-design-system-contract.json` | Allowed Webflow output shape. Defines permitted variables/classes/styles. Source of truth for `webflow-design-system.json` produced by `map_variables.py`. | Read by `map_variables.py` (input) and `validate_figma_extraction.py` (allowlist check). |

### `references/` (load on demand, ordered)

| File | Role | Appears when |
|------|------|--------------|
| `references/README.md` | Tells LLMs to load `figma-webflow-mapping.md` after the Figma template. | LLM reads at Task 1 start. |
| `references/figma-webflow-mapping.md` | Translation contract: Figma display name → Webflow variable name. Consumed by `map_variables.py` and `validate_figma_extraction.py`. **Authoritative for naming.** | Task 2 (validate) + Task 3 (map). |

### `schema/` (JSON Schema 2020-12 contracts)

| File | Role | Appears when |
|------|------|--------------|
| `schema/schema_index.json` | Index of all schemas in this skill. Lists shared schemas (`agentic/schemas/_shared/...`) and contract schemas. | LLM reads at Task 1+ to pick the right `$ref`. |
| `schema/figma-mcp-variable-defs.schema.json` | Validates the normalized Figma MCP input saved to `raw/figma-mcp-variable-defs.json`. **BLOCK tier inside Task 1** — must pass before overlaying the template. | Used by `build_figma_design_system.py`. |
| `schema/figma-design-system-contract.schema.json` | Validates `figma-design-system.json`. Composes `ref-envelope` + `VariableEntry` + `StyleEntry`. **BLOCK tier** — must validate before Task 3. | Used by `validate_figma_extraction.py`. |
| `schema/webflow-design-system-contract.schema.json` | Validates `webflow-design-system.json`. Same composition + requires `figmaName` / `webflowName` / `updatePolicy` / `figmaStyleName` / `webflowClassName` per entry. **BLOCK tier** — must validate before Task 6. | Used by shared validator (`.claude/skills/_shared/scripts/validate_artifacts.py --tier block`). |

### `scripts/` (executable stages)

| File | Role | Appears when |
|------|------|--------------|
| `scripts/README.md` | Quick command reference. Points back to `SKILL.md` for policy. | LLM reads at Task 1+. |
| `scripts/contract_paths.py` | Centralizes canonical artifact + template paths. Re-exported across all 3 scripts. Use when adding new scripts. | Imported by `build_figma_design_system.py`, `validate_figma_extraction.py`, `map_variables.py`. |
| `scripts/build_figma_design_system.py` | **Task 1.** Validates normalized Figma MCP input, then overlays it onto Figma template. Produces `figma-design-system.json` + `build-figma-design-system-report.json`. Fails if input shape is invalid or any required key is missing. | Run after normalized MCP payload is saved to `workspace/<ws>/design-system/raw/figma-mcp-variable-defs.json`. |
| `scripts/validate_figma_extraction.py` | **Task 2.** Validates `figma-design-system.json` against schema, required-keys list, no placeholders, no native selector targets. Uses `jsonschema` + `selector_guards` from `_shared`. | Run after Task 1 succeeds, before Task 3. |
| `scripts/map_variables.py` | **Task 3.** Translates Figma names → Webflow names via `figma-webflow-mapping.md`, then overlays Webflow template. Produces `webflow-design-system.json` + `mapping-report.json`. | Run after Task 2 passes. |

### `tests/` (smoke + integration)

| File | Role | Appears when |
|------|------|--------------|
| `tests/test_sync.py` | Integration test. Bootstraps `workspace/test-sync-workspace/`, writes complete MCP payload, runs full pipeline (build → validate → map), asserts outputs. | Run on demand: `python -m unittest .claude/skills/design-system-sync/tests/test_sync.py`. CI hook optional. |

---

## 2. End-to-end workflow (the 6 Tasks)

### Task 1 — Extract Figma Design System

**Trigger:** user says "sync Figma to Webflow" / "sync design tokens" / similar.

**Steps:**
1. Call Figma MCP `get_variable_defs` and request output compatible with `.claude/skills/design-system-sync/schema/figma-mcp-variable-defs.schema.json`.
2. If MCP returns a non-canonical shape, save it to `workspace/<ws>/design-system/raw/figma-mcp-variable-defs.original.json`.
3. Normalize the MCP response into `workspace/<ws>/design-system/raw/figma-mcp-variable-defs.json` using the schema and `template/figma-mcp-variable-defs.input-template.json`.
4. Run `python .claude/skills/design-system-sync/scripts/build_figma_design_system.py --workspace <ws> --input workspace/<ws>/design-system/raw/figma-mcp-variable-defs.json`.

**Output:**
- `workspace/<ws>/design-system/figma-design-system.json`
- `workspace/<ws>/design-system/validations/build-figma-design-system-report.json`

**Files involved:** `SKILL.md` (Task 1), `scripts/build_figma_design_system.py`, `scripts/contract_paths.py`, `template/figma-mcp-variable-defs.input-template.json`, `template/figma-design-system-contract.json`, `schema/figma-mcp-variable-defs.schema.json`, `schema/figma-design-system-contract.schema.json`, `schema/schema_index.json`, `references/README.md`, `references/figma-webflow-mapping.md`.

**Hard stop if:** normalized MCP input is schema-invalid or any required Figma key is missing. Do not fabricate.

### Task 2 — Validate Figma Extraction

**Trigger:** Task 1 produced `figma-design-system.json`.

**Run:** `python .claude/skills/design-system-sync/scripts/validate_figma_extraction.py --workspace <ws>`

**Output:**
- `workspace/<ws>/design-system/validations/validation_report.json`
- `workspace/<ws>/design-system/validations/validation_report.txt`

**Files involved:** `scripts/validate_figma_extraction.py`, `scripts/contract_paths.py`, `template/webflow-design-system-contract.json` (allowlist), `references/figma-webflow-mapping.md` (resolvability), `schema/figma-design-system-contract.schema.json`, shared `selector_guards` + `repo_root` from `.claude/skills/_shared/scripts/`.

**Hard stop if:** any validation failure. Do not continue.

### Task 3 — Map to Webflow Design System

**Trigger:** Task 2 passed.

**Run:** `python .claude/skills/design-system-sync/scripts/map_variables.py --workspace <ws> --strict`

**Output:**
- `workspace/<ws>/design-system/webflow-design-system.json`
- `workspace/<ws>/design-system/validations/mapping-report.json`

**Files involved:** `scripts/map_variables.py`, `scripts/contract_paths.py`, `template/webflow-design-system-contract.json`, `references/figma-webflow-mapping.md`, `schema/webflow-design-system-contract.schema.json` (via Task 4).

**Hard stop if:** any Figma key maps to no Webflow target. Do not invent Webflow names.

### Task 4 — Validate Runtime Artifacts (BLOCK tier)

**Trigger:** Task 3 produced both contract files.

**Run:** `python .claude/skills/_shared/scripts/validate_artifacts.py --workspace <ws> --tier block`

**Files involved:** shared validator. Consumes both `figma-design-system.json` + `webflow-design-system.json` and their `.meta.json` siblings (per `agentic/schemas/_shared/meta.schema.json`).

**Hard stop if:** any BLOCK-tier failure.

### Task 5 — Prepare Webflow Sync Preview

**Trigger:** Task 4 passed.

**Action:** LLM renders planned Webflow MCP operations into `workspace/<ws>/design-system/validations/webflow-sync-preview.json`. Appends audit entry to `write-audit-log.jsonl`.

**Audit entry:**
```json
{ "phase": "design-system-sync", "task": 5, "action": "approval-requested", "preview": "workspace/<ws>/design-system/validations/webflow-sync-preview.json" }
```

**Stop.** Wait for user `approve` / `revise` / `cancel`.

### Task 6 — Sync to Webflow

**Trigger:** explicit `approve` from user.

**Action:** Use Webflow MCP `variable_tool` + `style_tool` to push `webflow-design-system.json` into site. Branch named `ws/<ws>/design-system-sync`. Append audit entry per batch.

**Files involved:** `workspace/<ws>/webflow-site-info.json` (site registry from `figma-to-webflow-orchestrator/scripts/site_registry.py`), `write-audit-log.jsonl`, `webflow-design-system.json` (read-only source).

**Audit entry shape:**
```json
{ "phase": "design-system-sync", "task": 6, "action": "webflow-write", "calls": 0, "branch": "ws/<ws>/design-system-sync" }
```

---

## 3. External files this skill touches or depends on

### Inside repo (sibling skills / shared infra)

| Path | Role |
|------|------|
| `workspace/<ws>/` | Per-site runtime root. Bootstrap by `figma-to-webflow-orchestrator/scripts/site_registry.py` (Phase 0 in orchestrator). |
| `workspace/<ws>/webflow-site-info.json` | Site registry entry. Created by `site_registry.bootstrap_workspace()`. Read by Task 6 to know which site to write. |
| `workspace/<ws>/design-system/` | This skill's working dir. |
| `workspace/<ws>/design-system/raw/figma-mcp-variable-defs.json` | Normalized Figma MCP input. Validated against `schema/figma-mcp-variable-defs.schema.json`; consumed by Task 1. |
| `workspace/<ws>/design-system/raw/figma-mcp-variable-defs.original.json` | Optional untouched MCP response when the server returns a non-canonical shape. Kept for audit/debug. |
| `workspace/<ws>/design-system/figma-design-system.json` | Output Task 1 / Input Task 2+3. |
| `workspace/<ws>/design-system/webflow-design-system.json` | Output Task 3 / Input Task 6. |
| `workspace/<ws>/design-system/validations/*.json` | All validation reports + sync preview. |
| `workspace/<ws>/write-audit-log.jsonl` | Append-only audit trail. Task 5 + Task 6 write here. |
| `agentic/schemas/_shared/variable-entry.schema.json` | Per-token schema. `figmaId` (format `VariableID:<id>:<index>`) required. |
| `agentic/schemas/_shared/style-entry.schema.json` | Per-style schema. |
| `agentic/schemas/_shared/meta.schema.json` | Provenance block. |
| `agentic/schemas/_shared/ref-envelope.schema.json` | Envelope composing meta + variables + styles. |
| `agentic/knowledge/client-first/INDEX.yaml` | Client-First knowledge index. Filter by `applicable_skill: design-system-sync`. Pull 1–3 files by topic tag. |
| `.claude/skills/_shared/scripts/repo_root.py` | `find_repo_root()`, `resolve_repo_path()`. Imported by all 3 scripts. |
| `.claude/skills/_shared/scripts/validate_artifacts.py` | BLOCK-tier validator. Task 4. |
| `.claude/skills/_shared/scripts/selector_guards.py` | `is_native_selector()`, `is_html_tag_selector()`. Task 2 rejects `.w-*`, `.wf-*`, native HTML tag selectors. |
| `.claude/skills/_shared/scripts/run_quality_gate.py` | Profile `html-first` runs structure + contracts + variables + index validators. Optional wrapper. |
| `.claude/skills/figma-to-webflow-orchestrator/scripts/site_registry.py` | Idempotent workspace bootstrap. Phase 0 prerequisite. |
| `.claude/skills/figma-to-webflow-orchestrator/scripts/init_workspace.py` | CLI wrapper for site registry. |
| `.claude/skills/figma-to-html-architect/scripts/resolve_figma_name.py` | Sibling Branch B. Independent of this skill but consumes `webflow-design-system.json` indirectly via shared workspace. |
| `.claude/rules/python.md` | Style rules for `.py` + `.sh` in this skill. |
| `.claude/rules/concurrency-policy.yaml` | Webflow writes must be serialized. |
| `.claude/rules/retry-policy.yaml` | Webflow MCP retry rules. |
| `.claude/rules/webflow-mcp.rules.yaml` | MCP tool limitations. |

### Outside repo (external systems)

| System | How the skill touches it |
|--------|--------------------------|
| Figma MCP server (`figma-dev-mode-mcp-server`) | Task 1: `get_variable_defs` over file-level variables + styles. Response is normalized into `design-system/raw/figma-mcp-variable-defs.json`; original non-canonical responses may be saved as `.original.json`. |
| Webflow MCP server | Task 6: `variable_tool` (variables) + `style_tool` (classes/styles). Writes against branch `ws/<ws>/design-system-sync`. |

---

## 4. Hard policies (read these or break the build)

1. **Figma file must be prepared.** Variables/styles use the exact `Layout / Gaps / Large` style path from `template/figma-design-system-contract.json`. If file unprepared → hard stop. No fabrication.
2. **figmaId is mandatory.** Format `VariableID:<id>:<index>`. Without it, round-trip traceability dies. Schema: `agentic/schemas/_shared/variable-entry.schema.json`.
3. **No native selectors as design-system targets.** `.w-*`, `.wf-*`, native HTML tag selectors (`body`, `a`, `h1`, `section`) banned. Enforced by `selector_guards`.
4. **No auto-publish.** Build pipeline never publishes. Task 6 writes to a Webflow branch; human publishes.
5. **Branch-first Webflow writes.** All Webflow writes go to `ws/<ws>/design-system-sync`. Never to main/master.
6. **Single-threaded writes.** Serialized per `concurrency-policy.yaml`.
7. **Audit everything.** Task 5 + Task 6 append to `write-audit-log.jsonl`.
8. **No silent overwrites.** Validation report per step; failures halt the run.
9. **Stable key shape.** Designer changes values, not contract keys. Renames must update Figma file + template + mapping guide + tests in lockstep.
10. **Input schema before artifact templates.** `schema/figma-mcp-variable-defs.schema.json` defines the normalized MCP input. `template/figma-design-system-contract.json` and `template/webflow-design-system-contract.json` define allowed runtime artifact structure. Runtime artifacts overlay on templates, never invent new top-level keys.

---

## 5. Quick command reference

```bash
# Phase 0 — bootstrap workspace (once per site, idempotent)
python .claude/skills/figma-to-webflow-orchestrator/scripts/init_workspace.py \
  --site-data-file ./site.json

# Task 1 — build Figma artifact (after MCP payload saved)
python .claude/skills/design-system-sync/scripts/build_figma_design_system.py \
  --workspace <ws> \
  --input workspace/<ws>/design-system/raw/figma-mcp-variable-defs.json

# Task 2 — validate Figma artifact
python .claude/skills/design-system-sync/scripts/validate_figma_extraction.py \
  --workspace <ws>

# Task 3 — map to Webflow contract
python .claude/skills/design-system-sync/scripts/map_variables.py \
  --workspace <ws> --strict

# Task 4 — block-tier validation (both contracts)
python .claude/skills/_shared/scripts/validate_artifacts.py \
  --workspace <ws> --tier block

# Tests — integration smoke
python -m unittest .claude/skills/design-system-sync/tests/test_sync.py
```

---

## 6. Success criteria

- `figma-design-system.json` exists, validates against its schema, has `figmaId` on every variable.
- `webflow-design-system.json` exists, validates against its schema, every entry carries `figmaName` + `figmaId` + `updatePolicy`.
- Mapping report has zero strict errors.
- User approved the Webflow sync preview before any write.
- Every Webflow write recorded in `write-audit-log.jsonl`.
- No native selectors leaked into Webflow output.

---

## 7. Failure modes & what to do

| Symptom | Likely cause | Action |
|---------|--------------|--------|
| `build_figma_design_system.py` exits 1 with `inputSchemaErrors` | MCP output was not normalized to the input schema | Save original MCP response separately, normalize into `raw/figma-mcp-variable-defs.json`, then re-run. |
| `build_figma_design_system.py` exits 1 with missing keys | Figma payload missing required key | Fix Figma file per `template/figma-design-system-contract.json`. Re-extract. |
| `validate_figma_extraction.py` reports placeholder | MCP dump incomplete | Re-run MCP `get_variable_defs` with full scope. |
| `map_variables.py` strict error | Figma name has no Webflow target | Add to `references/figma-webflow-mapping.md` + `template/webflow-design-system-contract.json` in same commit. |
| `validate_artifacts.py --tier block` fails | Schema violation | Re-run Task 1-3 in order; check `.meta.json` siblings exist. |
| `selector_guards` flags `.w-*` class | Bad template | Remove native selector from template; re-run Task 3. |
| Webflow MCP rejects write | Branch missing or wrong name | Confirm branch `ws/<ws>/design-system-sync` exists via `data_pages_tool.list_branches` or site dashboard. |
