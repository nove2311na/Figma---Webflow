---
name: design-system-sync
description: Use this skill when the user asks to sync Figma Variables and Styles to a Webflow project using Finsweet 2.2 conventions — it extracts the Client-First baseline, validates the Figma extraction, maps variables, and writes to Webflow only after explicit user approval of the planned `variable_tool`/`style_tool` calls.
---

# Design System Sync Skill

## 🎯 Goal
Synchronize the base design system (Colors, Typography, Spacing variables) from the Figma file directly into the Webflow project, ensuring only the Finsweet Client-First CSS layer is used as the baseline.

## 📋 Core Workflow

### Task 0: Extract Client-First Baseline
- **Action**: Parse the Webflow exported CSS to isolate Client-First classes and variables, rejecting Webflow native/core CSS (`.w-*`, `.wf-*`, default tag styles).
- **Command**: `python .claude/skills/design-system-sync/scripts/extract_client_first_baseline.py --input-css <css-path> --output-contract workspace/<workspace-name>/design-system/client-first-baseline-contract.json --report workspace/<workspace-name>/design-system/validations/client-first-extraction-report.json --strict`
- **Output**: Generates the baseline contract `client-first-baseline-contract.json` and a report.
- **Halt Condition**: If no Client-First variables/classes are parsed, exit with code 1 and error `NO_CLIENT_FIRST_BASELINE_FOUND`.

### Task 1: Extract from Figma
- **Action**: Use the `call_mcp_tool` with `figma-dev-mode-mcp-server` -> `get_variable_defs`.
- **Input Schema**: `type: "var,style"`, `filterTypes: "all"`, `scope: "file"`.
- **Output**: Write the extracted data in **JSON Format** to `workspace/<workspace-name>/design-system/figma-contract.json`. 
- **Format**: Must strictly follow the template located at `.claude/skills/design-system-sync/template/figma-design-system-contract.json`.

### Task 2: Validate Data
- **Action**: Run the safety gate to ensure variables and styles map correctly to the extracted Client-First baseline contract and that no Webflow native elements or HTML tags are referenced.
- **Command**: `python .claude/skills/design-system-sync/scripts/validate_figma_extraction.py --workspace <workspace-name>`
- **Output**: Saves `validation_report.json` and `validation_report.txt`.
- **Halt Condition**: If validation fails (e.g., placeholder values exist, mapping references `.w-*` native classes or native HTML tag selectors, etc.), delete the invalid files, halt, and ask the user to fix the Figma designs.

### Task 3: Translate to Webflow Conventions
- **Action**: Map Figma variables to Webflow (Finsweet) variables, validating targets against the baseline contract.
- **Command**: `python .claude/skills/design-system-sync/scripts/map_variables.py --workspace <workspace-name> --strict`
- **Output**: Outputs `webflow-contract.json` and `mapping-report.json`.
- **Halt Condition**: If mapping fails (e.g. mapping to native `.w-*` classes or non-existent baseline selectors without `projectExtension: true`), halt and report errors.

### Task 4: Sync to Webflow
- **🛑 APPROVAL GATE (mandatory)**: Before any `variable_tool` or `style_tool` call, the agent MUST:
  1. Render a preview block of the planned `variable_tool` and `style_tool` calls (diffs vs. current Webflow state).
  2. Write the preview to `workspace/<workspace-name>/design-system/validations/webflow-sync-preview.json`.
  3. Append an entry to `workspace/<workspace-name>/write-audit-log.jsonl` with `{ "phase": "design-system-sync", "task": 4, "action": "approval-requested", "preview": "<path>" }`.
  4. STOP and present the preview to the user. Do not proceed until the user replies with one of: `approve` / `revise` / `cancel`.
- **Branch-first Deployments**: On `approve`, branch the Webflow project to `ws/<workspace-name>/design-system-sync` before writing. Do not write to the production branch.
- **Action**: Use the Webflow MCP Server tools to push updates from the JSON file on the branch.
- **Variables**: Use `variable_tool` to create or update Webflow variables.
- **Classes/Styles**: Use `style_tool` to update CSS properties for classes based on the contract.
- **Audit**: Append `{ "phase": "design-system-sync", "task": 4, "action": "webflow-write", "calls": <count>, "branch": "<branch-name>" }` to `write-audit-log.jsonl` after each batch.

---

## 📚 Knowledge Lookup

Before extracting/mapping variables, consult the Finsweet Client-First knowledge index for context on naming, alias chains, multi-mode, and cross-machine stability. This skill's relevant topic tags:

- `figma`, `webflow` (supporting-content: figma-integration, webflow-integration)
- `variables`, `color`, `theme`, `alias-chains` (concepts: colors, figma-integration)
- `modes`, `multi-mode`, `adaptation` (gotchas: variable-modes-figma-webflow)
- `stable-id`, `figmaId`, `cross-machine`, `cross-person` (gotchas: display-name-vs-stable-id)
- `multi-machine`, `sync`, `drift` (gotchas: multi-machine-sync-drift)

**How to use**: read `agentic/knowledge/client-first/INDEX.yaml`, filter by `applicable_skill: design-system-sync`, pull 1-3 relevant files. Never full-dump.

```bash
python -c "
import yaml
d = yaml.safe_load(open('agentic/knowledge/client-first/INDEX.yaml'))
mine = [e for e in d['entries'] if 'design-system-sync' in e.get('applicable_skill',[])]
for e in mine[:5]: print(f\"  - {e['file_path']}  [tags: {e['topic_tags']}]\")
"
```

---

## 🛡️ Policies & Constraints

### Source of Truth Policy
- **Finsweet Client-First CSS layer** on Webflow is the baseline and core architectural standard. Webflow native/core CSS (`.w-*`, `.wf-*`, default HTML element selectors) must *never* bleed into the Figma-side design system.
- **Figma library** is the project/runtime source of truth for values and visual decisions once synchronized.
- The **mapping contract** is the source of truth for translating Figma names to Webflow names.
- Mapped variables/classes outside the baseline scope require `projectExtension: true` in the Figma metadata.

### Contract Rule
- Do not use shallow style contracts.
- Every style/class contract must define typed CSS properties, allowed breakpoints, match policy, and update policy.

### Mapping Rule
- `map_variables.py` must produce a real `webflow-contract.json` and `mapping-report.json`.
- If the script outputs mock status or baseline mapping violations (e.g., mapping to native `.w-*` classes or native HTML tags), the agent must halt and report the issue.

### Schemas & Contracts
- The schemas for design system contracts map to `agentic/schemas/library/schema_index.json`.
- All design system data artifacts are verified against the JSON schemas indexed in [schema_index.json](agentic/schemas/library/schema_index.json).
