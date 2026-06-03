# Approval Gates

This policy defines target gates and check parameters for operations inside the compiler workflow.

| Action | Gate | Verification Criteria |
|---|---|---|
| Create/Scaffold File | Paths must be relative and write mode is create-only. | Folder limits respected. |
| CSS Contract Generation | Contract built from source stylesheets. | Hash computed and index files written. |
| Figma Extraction | Node bundle written under `workspace/figma/`. | Node bundle schema validation passes. |
| Figma Normalization | Normalized tree and report written. | Success is true and blockers count is 0. |
| Semantic Resolution | Resolved tags/classes verified against contract. | Confidence >= 0.60, missing classes = 0. |
| HTML Rendering |logical blueprint rendered to physical HTML. | Wrapper elements (`page-wrapper`, `main-wrapper`) exist. |
| Alt Policy Manifest | Asset manifest Alt rules validated. | Informative assets have alts, decorative use empty alts. |
| Slicing chunks | Section chunks sliced correctly. | Manifest tags matched and tags balanced. |
| Native build plan | serialized plan written. | No destructive element deletions. Target branch isn't main. |
| Webflow writes | Target branch set. Preflight check run. | Serialized writes. logs saved. User approved plan. |
