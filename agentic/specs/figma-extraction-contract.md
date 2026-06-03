# Figma Extraction Contract Specification

## Figma MCP Extraction Requirements

- The Figma extraction must occur exactly once at the beginning of the pipeline.
- The results must be persisted to a stable `figma.node-bundle.json` in `workspace/figma/`.
- No subsequent pipeline phase is allowed to call Figma MCP tools directly to obtain raw tree nodes. They must read from the node bundle.
- The node bundle must include:
  - Node metadata
  - Figma styles (colors, typography, spacing)
  - Raw JSON tree representing the target frame and its descendants
  - Run metadata (timestamp, figma file version hash, extractor user)
