# Workflow Map (Modern Figma-to-Webflow)

This outlines the streamlined, 3-phase pipeline for converting Figma designs into Webflow structures.

## Phase 1: Design Extraction
- **Trigger**: New compile run requested.
- **Actor**: Figma Extraction Agent / Script (`extract_raw_styling.py`).
- **Steps**:
  1. Authenticate with Figma via Figma MCP Server.
  2. Parse the target node structure and extract exact CSS values (spacing, typography, colors).
  3. Output a raw HTML blueprint with inline CSS styles (`workspace/figma/raw-layout-blueprint.json` and `workspace/html/raw-inline.html`).

## Phase 2: Client-First Translation
- **Trigger**: Raw layout blueprint generated.
- **Actor**: Translation Script (`resolve_client_first.py`).
- **Steps**:
  1. Map extracted inline spacings and typography to Finsweet Client-First utility classes.
  2. Snap raw colors and font sizes to the pre-defined Webflow project CSS variables.
  3. Reconstruct the layout using semantic tags (`<section>`, `<nav>`, `<footer>`) and structure classes (`page-wrapper`, `main-wrapper`).
  4. Generate the definitive Semantic Tree (`workspace/semantic/figma.semantic-tree.json`).

## Phase 3: Webflow Synchronization
- **Trigger**: Semantic Tree validated.
- **Actor**: Webflow Sync Agent using Webflow MCP Server.
- **Steps**:
  1. Parse the Semantic Tree for required Variables and Styles.
  2. Call Webflow MCP to sync/create missing Variables.
  3. Call Webflow MCP to update Style definitions.
  4. Identify Webflow Symbols (using `agentic/knowledge/component-registry.json`).
  5. Push the standard HTML structure to Webflow.
  6. Trigger the site build/publish routine and generate the `mcp-sync-report.json`.

## Stop Conditions
The workflow halts and requests PM approval if:
- Extracted nodes do not match any known structure patterns.
- Client-First translation generates unresolved classes.
- Webflow MCP encounters a mutation conflict or rate limit.
