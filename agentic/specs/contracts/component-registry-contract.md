# Component Registry Contract

## Purpose
This contract dictates how the system identifies high-level components from Figma and maps them to Webflow Symbols. Unlike legacy pipelines that attempted to guess complex micro-components, the modern pipeline relies strictly on Finsweet Client-First for structure and only uses this registry for macro-level Symbols.

## Allowed Symbols
Only sections that are typically reused across an entire Webflow site should be registered here.
- `Navbar`
- `Footer`

## Workflow Integration
1. During the execution of `resolve_client_first.py`, the script checks the top-level sections against `agentic/knowledge/component-signatures.json`.
2. If a match is found (e.g., node name is "Navigation"), the semantic tree node will be tagged with `"symbol": "Navbar"`.
3. The Webflow Sync Agent reads this tag and consults `agentic/knowledge/component-registry.json` to invoke the Webflow Symbol ID instead of building the section from scratch.

## Maintenance
To add a new Webflow Symbol, developers must:
1. Add the Symbol definition to `component-registry.json`.
2. Add the Regex signature patterns to `component-signatures.json`.
