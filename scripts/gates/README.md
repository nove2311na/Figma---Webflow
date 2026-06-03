# scripts/gates/

Validation gates for the HTML-first compiler pipeline.

## Runner

```cmd
# Run all HTML-first compiler gates:
python scripts\gates\run_quality_gate.py --profile html-first

# Run default/general validation:
python scripts\gates\run_quality_gate.py
```

## Pipeline Gates (per compiler stage)

| Script | Validates |
|---|---|
| `validate_css_contract.py` | Client-First Library Contract generated correctly |
| `validate_css_index.py` | CSS class/variable index files exist |
| `validate_figma_node_bundle.py` | Figma extraction output schema |
| `validate_figma_normalization.py` | Normalized tree — no blockers, success flag |
| `validate_design_system_sync.py` | Figma tokens match CSS contract variables |
| `validate_component_matching.py` | Component signature matching report |
| `validate_semantic_ir.py` | Semantic IR — confidence ≥ 0.60, missing classes = 0 |
| `validate_html_blueprint.py` | HTML blueprint — wrapper elements exist, no inline styles |
| `validate_asset_policy.py` | Asset manifest alt policy compliance |
| `validate_html_chunks.py` | Section chunks sliced correctly, manifest balanced |
| `validate_resolver_benchmark.py` | Benchmark: ≥95% tag accuracy, 0 invented classes, broken fixtures fail |
| `validate_native_build_plan.py` | Native build plan — safe branch, no destructive ops, contract classes only |

## System Gates (structural/quality)

| Script | Validates |
|---|---|
| `validate_agentic_structure.py` | All required specs, rules, schemas, folders exist |
| `validate_workspace_artifacts.py` | Workspace JSON files schema compliance |
| `validate_archive_cleanup.py` | Old scripts archived, no active stale references |
| `validate_project_library.py` | Per-project Client-First library completeness |
| `validate_client_first_library.py` | Global client-first-class-map.json |
| `validate_build_contract.py` | Build contract between blueprint and Webflow state |
| `validate_phase_state.py` | Phase state machine transitions |
| `validate_relative_paths.py` | No absolute paths in runtime files |
| `validate_agent_system_spec.py` | Agent system spec required sections |
| `validate_skills.py` | Agent skill files present and valid |
| `scan_secrets.py` | No hardcoded secrets or credentials |
