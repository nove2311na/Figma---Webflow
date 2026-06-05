---
name: design-system-sync
description: Use this skill when the user asks to sync a prepared Figma design-system file into Webflow. It creates figma-design-system.json from the Figma MCP payload and the Figma contract template, maps it to webflow-design-system.json using the mapping guide and Webflow contract template, validates both artifacts, and only writes to Webflow after explicit user approval.
---

# Design System Sync Skill

## Goal

Synchronize a prepared Figma design-system file into the Webflow project through two canonical runtime artifacts:

- `workspace/<workspace-name>/design-system/figma-design-system.json`
- `workspace/<workspace-name>/design-system/webflow-design-system.json`

This pipeline does not require a CSS source file. The active Webflow library contract is:

- `.claude/skills/design-system-sync/template/webflow-design-system-contract.json`

## Required Inputs

### Prepared Figma File

The Figma file must be prepared to match the structure of:

- `.claude/skills/design-system-sync/template/figma-design-system-contract.json`

The Figma file may change values, modes, aliases, resolved values, style values, and Figma ids. It must not change the key structure expected by the template.

Hard stop if the Figma file is not prepared:

- Required variables or styles are missing.
- Variable/style names cannot be matched to the template.
- The MCP payload cannot be overlaid onto the template without inventing keys.
- Placeholder template values would remain in the output.

Do not fabricate missing Figma variables, styles, ids, aliases, or modes. Report the missing keys and ask the user to fix the Figma file.

### Mapping Guide

Use this file as the only mapping source between Figma and Webflow names:

- `.claude/skills/design-system-sync/references/figma-webflow-mapping.md`

### Webflow Contract Template

Use this file as the allowed Webflow variable/style/class contract:

- `.claude/skills/design-system-sync/template/webflow-design-system-contract.json`

## Core Workflow

### Task 1: Extract Figma Design System

Use the Figma MCP server to fetch variables and styles from the prepared Figma file.

Expected MCP intent:

- Tool: `figma-dev-mode-mcp-server`
- Operation: `get_variable_defs`
- Scope: file-level variables and styles
- Data kinds: variables and styles

When calling the MCP tool, request output that can be normalized to this input schema:

- `.claude/skills/design-system-sync/schema/figma-mcp-variable-defs.schema.json`

Desired JSON shape:

```json
{
  "meta": {
    "source": "figma-mcp",
    "operation": "get_variable_defs",
    "fileKey": "<figma-file-key>",
    "nodeId": "<optional-node-id-or-file-scope>",
    "normalizedAt": "<iso-8601>"
  },
  "variables": {
    "Layout / Gaps / Large": {
      "name": "Layout / Gaps / Large",
      "figmaId": "VariableID:<real-id>:<index>",
      "type": "size",
      "value": 16,
      "resolvedValue": 16,
      "unit": "px",
      "mode": "default",
      "modes": { "default": 16 },
      "collection": "Layout"
    }
  },
  "styles": {
    "Heading Style / H1": {
      "name": "Heading Style / H1",
      "figmaStyleName": "Heading Style / H1",
      "figmaId": "StyleID:<real-id>",
      "type": "text-style",
      "properties": {
        "font-size": { "value": 64, "unit": "px" }
      },
      "mode": "default",
      "category": "heading"
    }
  }
}
```

If the MCP response does not already match this shape, normalize it before saving the build input. Allowed normalization:

- Rename MCP fields to canonical fields, for example `id` or `variableId` -> `figmaId`.
- Move nested variable/style records into top-level `variables` and `styles` objects keyed by normalized Figma names.
- Preserve MCP-provided values, modes, aliases, ids, and style properties.

Forbidden normalization:

- Invent missing variables, styles, ids, modes, aliases, or values.
- Rename Figma design-system keys to make mapping pass.
- Fill missing required data from templates.

Save the raw MCP response to:

- `workspace/<workspace-name>/design-system/raw/figma-mcp-variable-defs.original.json` when the server returns a non-canonical shape.

Save the normalized, schema-valid build input to:

- `workspace/<workspace-name>/design-system/raw/figma-mcp-variable-defs.json`

Then create `workspace/<workspace-name>/design-system/figma-design-system.json` by running:

```bash
python .claude/skills/design-system-sync/scripts/build_figma_design_system.py \
  --workspace <workspace-name> \
  --input workspace/<workspace-name>/design-system/raw/figma-mcp-variable-defs.json
```

The script overlays the MCP payload onto `.claude/skills/design-system-sync/template/figma-design-system-contract.json`.

Rules:

- Validate the build input against `.claude/skills/design-system-sync/schema/figma-mcp-variable-defs.schema.json` before overlay.
- Preserve the template key structure.
- Replace template values with Figma values.
- Replace template ids with real stable Figma ids.
- Preserve aliases and modes from Figma when present.
- Keep every variable/style traceable to a stable Figma id.
- Halt if any required key cannot be matched.
- Halt if the normalized MCP input is schema-invalid.
- Review `workspace/<workspace-name>/design-system/validations/build-figma-design-system-report.json` if the build fails.

### Task 2: Validate Figma Extraction

Run:

```bash
python .claude/skills/design-system-sync/scripts/validate_figma_extraction.py --workspace <workspace-name>
```

Expected input:

- `workspace/<workspace-name>/design-system/figma-design-system.json`

Validation checks:

- JSON schema compliance.
- Required variables/styles exist.
- No unresolved template placeholders remain.
- Figma keys can map through `.claude/skills/design-system-sync/references/figma-webflow-mapping.md`.
- Mapping targets exist in `.claude/skills/design-system-sync/template/webflow-design-system-contract.json` unless explicitly marked as a project extension.
- Webflow native selectors such as `.w-*`, `.wf-*`, and native HTML tag selectors are not used as design-system targets.

Halt on validation failure. Do not continue to Webflow mapping until the Figma artifact is valid.

### Task 3: Map to Webflow Design System

Run:

```bash
python .claude/skills/design-system-sync/scripts/map_variables.py --workspace <workspace-name> --strict
```

Expected input:

- `workspace/<workspace-name>/design-system/figma-design-system.json`
- `.claude/skills/design-system-sync/references/figma-webflow-mapping.md`
- `.claude/skills/design-system-sync/template/webflow-design-system-contract.json`

Expected output:

- `workspace/<workspace-name>/design-system/webflow-design-system.json`
- `workspace/<workspace-name>/design-system/validations/mapping-report.json`

Rules:

- Map only through the mapping guide.
- Use the Webflow contract template as the allowed output shape.
- Preserve typed CSS properties, breakpoints, match policy, and update policy from the Webflow template.
- Transfer values from the validated Figma artifact.
- Halt if a Figma key maps to no Webflow target.
- Halt if a Webflow target is not present in the Webflow template and is not explicitly allowed as a project extension.

### Task 4: Validate Runtime Artifacts

Run:

```bash
python .claude/skills/_shared/scripts/validate_artifacts.py --workspace <workspace-name> --tier block
```

Required block-tier artifacts:

- `workspace/<workspace-name>/design-system/figma-design-system.json`
- `workspace/<workspace-name>/design-system/webflow-design-system.json`

Halt on any block-tier validation failure.

### Task 5: Prepare Webflow Sync Preview

Before any Webflow write, create a preview of planned Webflow MCP operations.

Preview output:

- `workspace/<workspace-name>/design-system/validations/webflow-sync-preview.json`

Audit output:

- Append to `workspace/<workspace-name>/write-audit-log.jsonl`

Audit entry shape:

```json
{ "phase": "design-system-sync", "task": 5, "action": "approval-requested", "preview": "workspace/<workspace-name>/design-system/validations/webflow-sync-preview.json" }
```

Stop after rendering the preview. Present the planned variable/style changes to the user and wait for one of:

- `approve`
- `revise`
- `cancel`

### Task 6: Sync to Webflow

Only run after explicit user approval.

Rules:

- Create or use a branch named `ws/<workspace-name>/design-system-sync`.
- Do not write directly to the production branch.
- Use Webflow MCP variable tools for variables.
- Use Webflow MCP style tools for classes/styles.
- Source all write data from `workspace/<workspace-name>/design-system/webflow-design-system.json`.
- Append a write audit entry after each batch.

Audit entry shape:

```json
{ "phase": "design-system-sync", "task": 6, "action": "webflow-write", "calls": 0, "branch": "ws/<workspace-name>/design-system-sync" }
```

## Knowledge Lookup

Before validating or mapping variables, consult the Client-First knowledge index for naming, alias chains, modes, stable ids, and drift risks.

Read:

- `agentic/knowledge/client-first/INDEX.yaml`

Filter by:

- `applicable_skill: design-system-sync`

Pull only the 1-3 files relevant to the current issue. Do not load the entire knowledge folder.

Useful topic tags:

- `figma`
- `webflow`
- `variables`
- `color`
- `theme`
- `alias-chains`
- `modes`
- `multi-mode`
- `stable-id`
- `figmaId`
- `multi-machine`
- `sync`
- `drift`

## Policies

### Source of Truth

- The prepared Figma file is the source of truth for design values.
- `.claude/skills/design-system-sync/schema/figma-mcp-variable-defs.schema.json` is the source of truth for the normalized Figma MCP input passed into Task 1.
- `.claude/skills/design-system-sync/template/figma-design-system-contract.json` is the source of truth for the expected Figma artifact structure.
- `.claude/skills/design-system-sync/references/figma-webflow-mapping.md` is the source of truth for Figma-to-Webflow naming.
- `.claude/skills/design-system-sync/template/webflow-design-system-contract.json` is the source of truth for allowed Webflow output structure.
- `workspace/<workspace-name>/design-system/webflow-design-system.json` is the runtime source of truth for Webflow updates.

### Template-Only Webflow Library Contract

Do not require an exported stylesheet or a generated CSS library contract for this skill. The only allowed Webflow library contract for this skill is `.claude/skills/design-system-sync/template/webflow-design-system-contract.json`.

### Stable Keys

The Figma-side keys must remain stable and template-compatible. The designer may change values, not the contract shape.

If a rename is intentional, update all of these together:

- Figma file variable/style name.
- `figma-design-system-contract.json` template key.
- `figma-webflow-mapping.md`.
- Validation fixtures/tests if present.

### No Fabrication

Never create missing variables/styles/classes just to make validation pass. Missing data is a Figma preparation issue or a mapping/template issue.

### Webflow Safety

Never write to Webflow without preview and explicit approval.

Never map design-system output to:

- Webflow native selectors: `.w-*`
- Webflow internal selectors: `.wf-*`
- Native HTML element selectors such as `body`, `a`, `h1`, `section`

Use explicit class/style targets from the Webflow design-system contract.

## Success Criteria

The skill is complete when:

- `figma-design-system.json` exists and validates.
- `webflow-design-system.json` exists and validates.
- The mapping report has no strict errors.
- The user has approved the preview before Webflow writes.
- Webflow write actions, if performed, are recorded in `write-audit-log.jsonl`.
