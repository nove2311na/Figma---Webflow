---
name: Figma to HTML Architect
description: Extract raw HTML from Figma, validate naming conventions, and automatically resolve Semantic Tags and Client-First CSS classes.
---

# Figma to HTML Architect Skill

## 🎯 Goal
Convert a raw Figma node into a perfectly formatted, semantic Webflow-ready HTML file (using Client-First CSS classes).

## 📋 Core Workflow

### Task 1: Extract Raw HTML from Figma
- **Action**: Use the `call_mcp_tool` with `figma-dev-mode-mcp-server` -> `get_design_context`.
- **Input Schema**: `nodeId: "<target-node>"`, `artifactType: "REUSABLE_COMPONENT"`, `taskType: "CREATE_ARTIFACT"`, `clientLanguage: "html, css"`, `forceCode: true`. 
  - **CRITICAL**: You must instruct the MCP tool (if applicable) or enforce that the output preserves Figma variables as CSS variables (`var(...)`) in the inline `style`. Do NOT resolve variables to their absolute Hex/Pixel values if they are linked to a Figma variable.
- **Output**: Write the raw extracted HTML (must include `style`, `data-node-id`, `data-name` attributes) to `workspace/<workspace-name>/components/<node-id>/raw-figma.html`.

### Task 2: Validate Figma Naming Convention
- **Action**: Run the safety gate to ensure the designer used approved `data-name` attributes and that no layer names conflict with native Webflow widgets (e.g. `w-nav`, `w-slider`, `w-tabs`).
- **Command**: `python .claude/skills/[new]-figma-to-html-architect/scripts/validate_figma_html.py --workspace <workspace-name> --node-id <node-id> --mode warn`
- **Output**: Saves `html_validation_report.json` and logs warnings/errors. If validation fails in `strict` mode (or if severe naming issues/widget conflicts occur), delete `raw-figma.html`, halt, and report errors to the user.

### Task 3: Process HTML (Semantic Tags & Client-First CSS)
- **Action**: Map the raw HTML to final Webflow HTML, matching styles against the baseline and mapped contracts.
- **Command**: `python .claude/skills/[new]-figma-to-html-architect/scripts/process_html.py --workspace <workspace-name> --node-id <node-id> --baseline workspace/<workspace-name>/design-system/client-first-baseline-contract.json`
- **Output**: The script reads the raw HTML, maps data-names to semantic tags, maps inline styles to matching baseline and design system classes, and writes the output to `workspace/<workspace-name>/components/<node-id>/final-webflow.html`.

---

## 🛡️ Policies & Constraints

### HTML Processing Rule
- `process_html.py` must not hardcode CSS class matching rules.
- It must read class/style definitions from `workspace/<workspace-name>/design-system/webflow-contract.json` and `workspace/<workspace-name>/design-system/client-first-baseline-contract.json`.
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
