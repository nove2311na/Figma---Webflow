# Prompt: Extract Figma Context

This prompt is used to extract Figma tree nodes, variables, styles, and metadata into a stable node bundle.

## Instructions for Agent

1. **Do NOT generate HTML.** This phase is purely for data extraction.
2. **Do NOT choose final CSS classes.** Class resolution occurs in a downstream phase.
3. **Do NOT call Webflow MCP tools.** Webflow operations are forbidden during extraction.
4. **Output Location**: All outputs must go to `workspace/figma/` directory.

## Large Frame Policy

If the target frame is extremely large and contains complex sections:
1. Extract top-level metadata first to identify section boundaries.
2. Slice the frame by top-level sections.
3. Re-run node extraction context for each section.
4. Merge section bundles into a single cohesive `figma.node-bundle.json`.

## Expected Output Files

- `workspace/figma/figma.node-bundle.json`: Raw node JSON tree and styles.
- `workspace/figma/metadata.json`: Frame name, dimensions, file version hash, and timestamp.
- `workspace/figma/variable-defs.json`: Figma variable collection definitions.
- `workspace/figma/screenshot.png` (optional): Visual screenshot of the frame.
- `workspace/figma/extract-run.log`: Execution log of the extractor.
