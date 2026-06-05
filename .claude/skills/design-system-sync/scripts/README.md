# Design System Sync Scripts

These scripts support the `design-system-sync` skill from saved Figma MCP data to workspace artifacts.

The canonical outputs are:

- `workspace/<workspace-name>/design-system/figma-design-system.json`
- `workspace/<workspace-name>/design-system/webflow-design-system.json`

## 1. `build_figma_design_system.py`

Builds `figma-design-system.json` from a normalized Figma MCP payload and the Figma template.

The agent should save the untouched Figma MCP response to `raw/figma-mcp-variable-defs.original.json` if the server returns a non-canonical shape, then normalize it into:

- `workspace/<workspace-name>/design-system/raw/figma-mcp-variable-defs.json`

The normalized input must validate against:

- `.claude/skills/design-system-sync/schema/figma-mcp-variable-defs.schema.json`

Then run:

```bash
python .claude/skills/design-system-sync/scripts/build_figma_design_system.py \
  --workspace <workspace-name> \
  --input workspace/<workspace-name>/design-system/raw/figma-mcp-variable-defs.json
```

Output:

- `workspace/<workspace-name>/design-system/figma-design-system.json`
- `workspace/<workspace-name>/design-system/validations/build-figma-design-system-report.json`

This script fails if the normalized MCP payload is schema-invalid or does not cover every variable/style key required by `.claude/skills/design-system-sync/template/figma-design-system-contract.json`.

## 2. `validate_figma_extraction.py`

Validates `figma-design-system.json` before mapping.

```bash
python .claude/skills/design-system-sync/scripts/validate_figma_extraction.py --workspace <workspace-name>
```

Output:

- `workspace/<workspace-name>/design-system/validations/validation_report.json`
- `workspace/<workspace-name>/design-system/validations/validation_report.txt`

## 3. `map_variables.py`

Maps the validated Figma artifact into Webflow's design-system contract.

```bash
python .claude/skills/design-system-sync/scripts/map_variables.py --workspace <workspace-name> --strict
```

Input:

- `workspace/<workspace-name>/design-system/figma-design-system.json`
- `.claude/skills/design-system-sync/references/figma-webflow-mapping.md`
- `.claude/skills/design-system-sync/template/webflow-design-system-contract.json`

Output:

- `workspace/<workspace-name>/design-system/webflow-design-system.json`
- `workspace/<workspace-name>/design-system/validations/mapping-report.json`

## Shared Path Helper

`contract_paths.py` centralizes canonical artifact and template paths. Use it when adding new design-system sync scripts.
