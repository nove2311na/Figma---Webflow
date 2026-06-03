# MCP Risk and Authorization Map

This policy maps risk categories for external MCP servers (Figma, Webflow, Notion) and enforces authorization constraints.

## Risk Categories

- **R0 (No Risk)**: Reading local files, syntax compilation.
- **R1 (Low Risk)**: Reading remote Figma variables/nodes (readonly).
- **R2 (Medium Risk)**: Writing local blueprints, normalized trees, or build plans.
- **R3 (High Risk)**: Writing elements/styles to temporary Webflow site branches.
- **R4 (Critical Risk)**: Writing elements/styles to production Webflow pages, publishing sites, deleting elements.

## Authorization & Guardrails

1. **Production Writes**: Direct mutations to production pages or master branches are forbidden.
2. **Branching Enforcement**: All mutations must target temporary site branches.
3. **Rollback Requirement**: High-risk modifications must compile a rollback plan showing parent IDs and original elements before starting mutations.
4. **Approval Step**: Any write mutation (Risk R3/R4) requires explicit user approval of the compiled `native-build-plan.json` first.
