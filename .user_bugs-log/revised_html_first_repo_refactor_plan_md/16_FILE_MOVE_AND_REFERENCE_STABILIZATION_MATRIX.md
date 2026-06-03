# 16 — File Move, Create, Update & Stabilization Matrix

## Move/archive

| Current path | New path | Stabilization |
|---|---|---|
| `agentic/memory/final-report-saas-futuristic-app.md` | `archive/runs/saas-futuristic-app/final-report.md` | Update refs to archive-only. |
| `scripts/phase2a_reconcile_library.py` | `archive/runs/saas-futuristic-app/scripts/phase2a_reconcile_library.py` | Replace command with CSS contract indexer. |
| `scripts/phase2b_synthesize_logs.py` | `archive/runs/saas-futuristic-app/scripts/phase2b_synthesize_logs.py` | Remove from active workflow. |
| `scripts/phase3_fix_library.py` | `archive/runs/saas-futuristic-app/scripts/phase3_fix_library.py` | Replace with missing mapping report workflow. |
| `scripts/phase3_fix_tokenmap.py` | `archive/runs/saas-futuristic-app/scripts/phase3_fix_tokenmap.py` | Replace with design sync gate. |
| `scripts/run_all_gates.py` | `archive/runs/saas-futuristic-app/scripts/run_all_gates.py` | Replace with `run_quality_gate.py --profile html-first`. |
| `knowledge-base/libraries/<old-site-id>/` | `archive/site-libraries/<old-site-id>/` | Remove active hardcoded site IDs. |
| `agentic/prompts/write-html-contract.md` | `archive/deprecated-workflows/write-html-contract.webflow-first.md` | Replace with split prompts. |

## Create specs

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

## Create rules

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

## Create schemas

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

## Create scripts/tools

```text
tools/css_indexer/parser.py
tools/css_indexer/classifier.py
tools/css_indexer/contract_builder.py
scripts/index_css_library.py
scripts/normalize_figma_nodes.py
scripts/match_components.py
scripts/render_html_from_blueprint.py
scripts/slice_html_into_chunks.py
scripts/compile_native_ops_from_html.py
```

## Update runtime docs

```text
README.md
CLAUDE.md
llm-instructions.md
agentic/README.md
agentic/orchestration/workflow-map.md
agentic/orchestration/sop.md
agentic/orchestration/retry-and-stop-conditions.md
agentic/policies/approval-gates.md
agentic/policies/mcp-risk-auth-map.md
agentic/specs/workspace-artifact-schemas.md
agentic/evals/rubric-default.md
agentic/evals/reflection-rubric.md
agentic/evals/standalone-architecture-baseline.md
pyproject.toml
```

## Keep mostly as-is

```text
scripts/archive_workspace.py
scripts/restore_workspace.py
scripts/gates/scan_secrets.py
scripts/gates/validate_relative_paths.py
tools/utils.py
knowledge-base/client-first-theory.md
knowledge-base/client-first-class-map.json
AGENTS.md
```

`knowledge-base/client-first-class-map.json` remains curated. Generated CSS contract wins.
