# agentic/schemas/

Schemas are grouped by pipeline stage. Each sub-folder contains JSON Schema definitions for the data structures used at that stage.

| Folder | Purpose |
|---|---|
| `figma/` | Figma extraction inputs — node bundles, normalized tree, semantic tree, normalization/mapping reports |
| `html/` | HTML pipeline outputs — blueprint, validation report, asset manifest, alt policy, section manifest |
| `webflow/` | Webflow-side structures — native build plan, section tasks, write audit log |
| `library/` | CSS contract and project library schemas |
| `component/` | Component registry, signature, and matching report schemas |
| `design-system/` | Design-system sync report schema |
| `workspace/` | Runtime workspace file schemas — meta, state, page structure, error log, etc. |

## Schema ↔ Pipeline Stage Mapping

```
Figma MCP extraction  →  figma/figma-node-bundle.schema.json
Figma normalization   →  figma/figma-normalized-tree.schema.json
                         figma/figma-normalization-report.schema.json
Semantic resolution   →  figma/figma-semantic-tree.schema.json
                         figma/missing-mapping-report.schema.json
HTML rendering        →  html/html-blueprint.schema.json
                         html/html-validation-report.schema.json
Asset policy          →  html/asset-manifest.schema.json
                         html/alt-policy.schema.json
Chunk slicing         →  html/section-manifest.schema.json
Webflow native ops    →  webflow/webflow-native-build-plan.schema.json
                         webflow/webflow-section-task.schema.json
                         webflow/webflow-write-audit-log.schema.json
```
