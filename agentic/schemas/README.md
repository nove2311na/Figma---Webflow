# agentic/schemas/

Schemas are grouped by pipeline stage. Each sub-folder contains JSON Schema definitions for the data structures used at that stage.

| Folder | Purpose |
|---|---|
| `_shared/` | Shared common schema components (meta, variable and style entries, reference envelopes) |
| `html/` | HTML pipeline outputs — alt policy |
| `semantic/` | Semantic IR trees (semantic-tree.schema.json) |
| `webflow/` | Webflow-side structures — native write audit log, mcp sync reports (indexed in [schema_index.json](webflow/schema_index.json)) |
| `library/` | CSS contract and project library schemas (indexed in [schema_index.json](library/schema_index.json)) |
| `workspace/` | Runtime workspace file schemas — meta, state, blueprint, page structure, qa report, subagent task, error log |
| `figma/` | (Planned) Figma extraction inputs — node bundles, normalized tree, mapping reports |
| `component/` | (Planned) Component registry and matching report schemas |

> [!NOTE]
> Design-system sync schema files (e.g. `figma-design-system-contract.schema.json` and `webflow-design-system-contract.schema.json`) are stored within the skill directory at `.claude/skills/design-system-sync/schema/`.

## Schema ↔ Pipeline Stage Mapping

```
Figma MCP extraction  →  (Planned) figma-node-bundle.schema.json
Figma normalization   →  (Planned) figma-normalized-tree.schema.json
Semantic resolution   →  semantic/semantic-tree.schema.json
HTML rendering        →  workspace/blueprint.schema.json
Asset policy          →  html/alt-policy.schema.json
Webflow native ops    →  (Planned) webflow-native-build-plan.schema.json
                         webflow/webflow-write-audit-log.schema.json
```
