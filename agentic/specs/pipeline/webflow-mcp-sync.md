# Webflow MCP Sync Pipeline

## Overview
This document specifies the behavior of the Agent responsible for pushing the generated `figma.semantic-tree.json` to Webflow using the Webflow MCP Server.

## Data Source
The Agent MUST only use `workspace/semantic/figma.semantic-tree.json` as its ground truth. Raw Figma data or intermediate blueprints are strictly off-limits during this phase.

## Operations
The Webflow Sync Agent performs three distinct synchronization tasks:

### 1. Variables Sync
- **Action**: Extract all required CSS variables (colors, sizing, typography) from the semantic tree metadata.
- **MCP Call**: Invoke the appropriate Webflow MCP tool to create or update these variables in the target Webflow project.
- **Rule**: Do not delete existing variables unless explicitly instructed by the user.

### 2. Styles (Classes) Sync
- **Action**: For all Finsweet Client-First classes present in the semantic tree, update their values on Webflow if the design dictates an override.
- **MCP Call**: Invoke the Webflow MCP tool for patching style properties.

### 3. Structure (HTML) Publish
- **Action**: Map the semantic tree nodes into Webflow DOM elements.
- **Component Linking**: If a node matches an entry in `agentic/knowledge/component-registry.json` (e.g., Navbar), the Agent MUST link the existing Webflow Symbol rather than creating raw HTML elements for that section.
- **MCP Call**: Inject the structure into the Webflow page.

## Audit & Verification
- Output a `mcp-sync-report.json` in `workspace/reports/` upon completion.
- Require user approval before triggering the actual Webflow site "Publish" event.
