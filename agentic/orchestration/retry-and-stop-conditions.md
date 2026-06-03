# Retry and Stop Conditions

This spec governs stop criteria and retry limits across all compiler phases.

| Compiler Phase | Retry Limit | Stop Conditions |
|---|---:|---|
| CSS Contract Extraction | 1 | Output index JSONs successfully parsed, or CSS hashes missing. |
| Figma Extraction | 2 | Extraction bundle successfully written, or Figma token auth failed. |
| Design-System Sync | 2 | Sync report success with zero blockers, or missing design token blocks. |
| Component Matching | 1 | Signature report matches all primitives, or confidence < 0.60. |
| Figma Normalization | 1 | Normalized tree written, or raw untokenized color value exists. |
| Semantic IR Resolution | 1 | Tag/Class resolved tree generated, or confidence score < 0.60, or unknown class used in strict mode. |
| HTML Rendering & QA | 1 | HTML blueprint written, or structural errors (missing wrappers) found. |
| Asset manifest | 1 | manifest file generated, or alt policy gate fails (missing alt). |
| Chunk Slicing | 1 | manifests cataloged, or component root breached. |
| Webflow Native Plan | 1 | plan compiled, or destructive deletion ops found. |
| Webflow Deploys (Phase 11) | 3 | branch mutations serialized, or tool failure, or audit log mismatch. |

If any strict gate blocker is triggered, the compiler stops and reports the failure. No downstream operations may execute.
