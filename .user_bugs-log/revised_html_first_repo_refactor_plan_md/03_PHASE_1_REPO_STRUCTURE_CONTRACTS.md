# 03 — Phase 1: Repo Structure & Contracts

> Audience: intern mới vào dự án, chưa biết repo, chưa biết Figma → HTML → Webflow pipeline.  
> Mode hiện tại: **strict mode** — missing token/class/style/component = dừng và báo lỗi.  
> Rule lõi: **Client-First CSS contract là ràng buộc bắt buộc**; final HTML chỉ được dùng class/var đã có trong contract hoặc Webflow native index/structural conventions.


## 1. Bối cảnh

Sau khi archive file cũ, repo cần structure mới cho compiler. Nếu không có specs/rules/schemas, agent sẽ lại phụ thuộc prompt tự do.

## 2. Create folders

```text
source-css/
knowledge-base/generated/
agentic/rules/
workspace/figma/
workspace/semantic/
workspace/html/chunks/
workspace/webflow-native/section-tasks/
workspace/webflow-native/section-results/
workspace/reports/
tests/fixtures/figma/
tests/fixtures/expected/
tests/fixtures/broken/
tests/goldens/
```

## 3. Create specs

```text
agentic/specs/html-first-pipeline.md
agentic/specs/client-first-library-contract.md
agentic/specs/figma-extraction-contract.md
agentic/specs/figma-design-system-contract.md
agentic/specs/figma-normalization-policy.md
agentic/specs/html-tag-resolution.md
agentic/specs/component-registry-contract.md
agentic/specs/component-signature-matching.md
agentic/specs/html-to-webflow-native-ops.md
agentic/specs/asset-and-image-policy.md
agentic/specs/tailwind-trace-to-client-first-evidence.md
agentic/specs/webflow-branch-strategy.md
```

Required content:
- `html-first-pipeline.md`: order and forbidden actions.
- `client-first-library-contract.md`: CSS contract wins over curated maps/examples.
- `figma-extraction-contract.md`: MCP output requirements.
- `figma-normalization-policy.md`: messy Figma recovery.
- `component-signature-matching.md`: exact/usable/candidate/no-match levels.
- `tailwind-trace-to-client-first-evidence.md`: Tailwind-like output is evidence only.
- `webflow-branch-strategy.md`: branch-first/audit/no publish.

## 4. Create rules

```text
agentic/rules/tag.rules.yaml
agentic/rules/class-selection.rules.yaml
agentic/rules/component-match.rules.yaml
agentic/rules/html-qa.rules.yaml
agentic/rules/figma-normalization.rules.yaml
agentic/rules/asset-alt.rules.yaml
agentic/rules/webflow-native-ops.rules.yaml
agentic/rules/concurrency-policy.yaml
agentic/rules/retry-policy.yaml
```

Minimum `class-selection.rules.yaml`:

```yaml
selection_policy:
  strict_mode: true
  missing_class_behavior: block
  allow_inline_style: false
  allow_hardcoded_hex: false
  allow_new_class_proposals: false
  final_class_source:
    - client-first-library-contract
    - webflow-native-class-index
    - structural-conventions

structural_convention_classes:
  - page-wrapper
  - main-wrapper
```

## 5. Create schemas

```text
agentic/schemas/client-first-library-contract.schema.json
agentic/schemas/figma-node-bundle.schema.json
agentic/schemas/figma-extract-run-log.schema.json
agentic/schemas/design-system-sync-report.schema.json
agentic/schemas/component-registry.schema.json
agentic/schemas/component-signature.schema.json
agentic/schemas/component-match-report.schema.json
agentic/schemas/component-sync-report.schema.json
agentic/schemas/figma-normalized-tree.schema.json
agentic/schemas/figma-normalization-report.schema.json
agentic/schemas/figma-semantic-tree.schema.json
agentic/schemas/missing-mapping-report.schema.json
agentic/schemas/html-blueprint.schema.json
agentic/schemas/html-validation-report.schema.json
agentic/schemas/asset-manifest.schema.json
agentic/schemas/alt-policy.schema.json
agentic/schemas/section-manifest.schema.json
agentic/schemas/webflow-native-build-plan.schema.json
agentic/schemas/webflow-section-task.schema.json
agentic/schemas/webflow-write-audit-log.schema.json
```

MVP schema can be skeleton but must be valid JSON.

## 6. Update workspace artifact spec

Update:

```text
agentic/specs/workspace-artifact-schemas.md
```

New workspace:

```text
workspace/
  figma/
  semantic/
  html/
  html/chunks/
  webflow-native/
  webflow-native/section-tasks/
  webflow-native/section-results/
  reports/
```

Legacy optional:
```text
workspace/rawdata/
workspace/contents/
workspace/blueprints/
```

## 7. Update dependencies

If `pyproject.toml` exists, add:

```toml
dependencies = [
  "tinycss2>=1.2.1",
  "pydantic>=2.0",
  "typer>=0.12",
  "beautifulsoup4>=4.12"
]
```

Optional later:
```toml
"selectolax>=0.3.21"
```

## 8. Gate

Update/create:

```text
scripts/gates/validate_agentic_structure.py
```

Checks:
```text
[ ] folders exist
[ ] specs exist
[ ] rules exist
[ ] schemas parse as JSON
[ ] workspace spec updated
[ ] pyproject dependencies documented
```

## 9. Done checklist

```text
[ ] New folders exist.
[ ] Specs created.
[ ] Rules created.
[ ] Schemas created.
[ ] Workspace spec updated.
[ ] Dependencies updated/documented.
[ ] validate_agentic_structure.py passes.
```
