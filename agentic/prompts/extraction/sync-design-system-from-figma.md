# Prompt: Sync Design System from Figma

This prompt describes how to validate and synchronize the Figma variable collections and styles against the Client-First CSS contract.

## Context

This phase runs after the Figma extraction node bundle is saved. You must read from the extraction files directly (`workspace/figma/figma.node-bundle.json` and `workspace/figma/variable-defs.json`). Do NOT make live Figma MCP requests.

## Strict Sync Rules

1. **Strict Token Matching**: Every design system token (colors, spacing, font weight) used in the design frame must match a corresponding allowed variable in the Client-First Library Contract.
2. **Missing Token = Blocker**: If a Figma variable or theme alias cannot be resolved to an allowed CSS variable, flag it as a `blocker` and stop the pipeline.
3. **No Automatic Class Proposals**: If a styling value is missing or untokenized, the sync tool must NOT propose new classes or variables.
4. **No Hardcoded Hex/Rem Values**: All properties must resolve to variable-backed Client-First classes. Hardcoded spacing or color values on elements are blockers.

## Sync Report Output

Write the sync report to `workspace/reports/design-system-sync-report.json` with the following structure:
- `timestamp`: Sync runtime.
- `matched_tokens`: Mapped variable names and target CSS variables.
- `missing_tokens`: List of Figma variables that are missing in the CSS contract (leads to failure).
- `unmapped_styles`: List of style guides or styles not mapped.
- `hardcoded_values`: List of layers containing raw color/spacing overrides.
- `blockers`: List of blocker errors.
- `status`: `"pass"` | `"failed"` (fails if any blockers or missing tokens exist).
