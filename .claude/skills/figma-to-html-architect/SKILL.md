---
name: figma-to-html-architect
description: Use this skill when a Figma section/page node must be turned into Webflow-ready HTML — it extracts the raw HTML tree via Figma MCP, validates `data-name` conventions for semantic element resolution, maps inline styles to the workspace Webflow design system, and halts for user review before any Webflow write.
---

# Figma to HTML Architect Skill

## 🎯 Goal
Convert a raw Figma section/page node into a semantic Webflow-ready HTML file using native HTML elements and approved Client-First/Webflow classes from the workspace design system.

## 📋 Core Workflow

### Task 1: Extract Raw Section/Page HTML from Figma
- **Action**: Use the `call_mcp_tool` with `figma-dev-mode-mcp-server` -> `get_design_context`.
- **Input Schema**: `nodeId: "<target-node>"`, `artifactType: "SECTION_OR_PAGE_HTML"`, `taskType: "CREATE_ARTIFACT"`, `clientLanguage: "html, css"`, `forceCode: true`.
  - **CRITICAL**: You must instruct the MCP tool (if applicable) or enforce that the output preserves Figma variables as CSS variables (`var(...)`) in the inline `style`. Do NOT resolve variables to their absolute Hex/Pixel values if they are linked to a Figma variable.
- **Output**: Write the raw extracted HTML tree to `workspace/<workspace-name>/html-nodes/<node-id>/raw-figma.html`.
- **Raw HTML Contract**: The raw tree may represent a full section or page. Every meaningful node should preserve:
  - `style`: inline CSS from Figma, used later for class/token matching.
  - `data-node-id`: original Figma node id for traceability.
  - `data-name`: original Figma layer name, used later for semantic tag resolution.

### Task 2: Validate Figma Naming Convention
- **Action**: Run the semantic naming gate to ensure `data-name` values provide enough intent to choose correct HTML tags, for example `button` -> `<button>`, `form_input` -> `<input>`, `heading_h1` -> `<h1>`. Also reject names that conflict with native Webflow widgets (e.g. `w-nav`, `w-slider`, `w-tabs`).
- **Command**: `python .claude/skills/figma-to-html-architect/scripts/validate_figma_html.py --workspace <workspace-name> --node-id <node-id> --mode warn`
- **Output**: Saves `html_validation_report.json` and logs warnings/errors. If validation fails in `strict` mode (or if severe naming issues/widget conflicts occur), delete `raw-figma.html`, halt, present the validation report, and require explicit user `approve`/`revise`/`cancel` before any downstream Webflow apply (the orchestrator's Branch A is responsible for that apply step — the architect never writes to Webflow directly).

### Task 3: Replace Inline CSS with Design-System Classes
- **Action**: Read the inline CSS from `raw-figma.html` and match it against `workspace/<workspace-name>/design-system/webflow-design-system.json`.
- **Command**: `python .claude/skills/figma-to-html-architect/scripts/process_html.py --workspace <workspace-name> --node-id <node-id>`
- **Output**: The processor removes inline styles when an approved design-system class/style is matched, preserves unmatched inline styles for review, and records the mapping decisions in `html_processing_report.json`.

### Task 4: Produce Webflow-Ready HTML
- **Action**: Use `html-semantic-mapping.json` rule objects and the validated `data-name` values to rewrite generic Figma `<div>` output into semantic/native elements available in Webflow, such as `<section>`, `<nav>`, `<button>`, `<input>`, `<form>`, `<img>`, and heading tags.
- **Output**: Write the final result to `workspace/<workspace-name>/html-nodes/<node-id>/final-webflow.html`.
- **Important**: Do not inject Webflow native behavior classes like `.w-nav`, `.w-slider`, or `.w-tabs`. If a Webflow native widget is needed, halt and ask for an explicit implementation decision.

### 🛑 APPROVAL GATE (Task 4, mandatory)
Before declaring Task 4 complete, the architect MUST:
1. Render a diff of `raw-figma.html` vs `final-webflow.html` (semantic tag changes, classes added, inline styles removed/preserved) from the processing report.
2. Write the diff to `workspace/<workspace-name>/html-nodes/<node-id>/validations/architect-diff-preview.json`.
3. Append `{ "phase": "figma-to-html-architect", "task": 4, "action": "approval-requested", "preview": "<path>" }` to `workspace/<workspace-name>/write-audit-log.jsonl`.
4. STOP and present the diff to the user. Do not return control to the orchestrator's Branch A until the user replies with `approve` / `revise` / `cancel`. The architect itself never writes to Webflow; the gate exists so the human reviews the HTML diff before any Webflow apply.

---

## 📚 Knowledge Lookup

Before processing HTML, pull only the conceptual rules this skill actually needs. Relevant topic tags:

- `naming`, `utility`, `combo`, `custom` (concepts/01-class-system)
- `spacing`, `rem`, `layout` (concepts/02-spacing, 08-layout-system)
- `typography`, `headings`, `body-text` (concepts/03-typography)
- `color`, `theme`, `alias-chains` (concepts/04-colors)
- `sizing`, `container`, `max-width` (concepts/05-sizing)
- `responsive`, `breakpoint`, `hide-on-breakpoint` (usability/01)
- `a11y`, `aria`, `focus`, `semantic-html` (usability/02)
- `rtl`, `ltr`, `direction` (usability/03)
- `dark-mode`, `theme`, `mode-switching`, `alias` (usability/04)
- `grid`, `columns`, `rows`, `gap` (usability/05)
- `forms`, `input`, `label`, `validation` (usability/06)
- `w-prefix`, `wf-prefix`, `webflow-native`, `denylist` (gotchas/04)
- `rem`, `px`, `unit-conversion` (gotchas/07)
- `w-nav`, `w-slider`, `w-tabs`, `layer-name-conflict` (gotchas/08)

**How to use**: read `agentic/knowledge/client-first/INDEX.yaml`, filter by `applicable_skill: figma-to-html-architect`, pull 1-3 files. Never full-dump.

```bash
python -c "
import yaml
d = yaml.safe_load(open('agentic/knowledge/client-first/INDEX.yaml'))
mine = [e for e in d['entries'] if 'figma-to-html-architect' in e.get('applicable_skill',[])]
for e in mine[:6]: print(f\"  - {e['file_path']}  [tags: {e['topic_tags']}]\")
"
```

---

## 🛡️ Policies & Constraints

### HTML Processing Rule
- `process_html.py` must not hardcode CSS class matching rules.
- It must read class/style definitions from `workspace/<workspace-name>/design-system/webflow-design-system.json`.
- The matching logic must strictly restrict matching to approved Client-First classes (never match native element selectors like `h1` or auto-inject `.w-*` native classes unless explicitly specified in semantic rules).
- It must preserve class ordering, handle self-closing/void tags correctly, and perform accessibility checks.

### Semantic Mapping Rule
- Semantic HTML mapping must use `html-semantic-mapping.json` rule objects, not simple substring matching.
- The processor must distinguish between semantic elements, layout wrappers, interactive elements, form elements, typography elements, media elements, and decorative elements.

### Validation Mode
- `validate_figma_html.py` must support:
  - `strict`: Fails the build if any generic layer is in a semantic-critical zone, if generic names like `Frame` are found, or if any layer name implies native Webflow widget behaviors.
  - `warn`: Logs warnings for generic wrappers and native widget names, but passes the build. (Recommended default for active development).
  - `ignore`: Silently passes generic/wrapper layers, checking only critical interactive elements.
- The agent should use `strict` only when generating production-ready final markup.

### Rules & Policy Files
- Spacing, naming, and HTML validation rules are specified in:
  - [class-selection.rules.yaml](file:///g:/My%20Drive/10_Learning/_Research/auto-research/.docs/source/MAS-Figma-Webflow-khang/agentic/rules/class-selection.rules.yaml) (Class matching & selection policy)
  - [html-qa.rules.yaml](file:///g:/My%20Drive/10_Learning/_Research/auto-research/.docs/source/MAS-Figma-Webflow-khang/agentic/rules/html-qa.rules.yaml) (HTML quality checklist & rule definitions)
  - [asset-alt.rules.yaml](file:///g:/My%20Drive/10_Learning/_Research/auto-research/.docs/source/MAS-Figma-Webflow-khang/agentic/rules/asset-alt.rules.yaml) (Alt tag assignment rules)
