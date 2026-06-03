# Standard Operating Procedure - HTML-First Figma-to-Webflow Compiler

This SOP governs the Claude Code-native, Python-first MAS HTML-first compiler workflow.

## Phase 0: Setup and Audit
- Steward validates/initializes workspace paths.
- Ensure old files are archived.
- Runs `python scripts/gates/validate_archive_cleanup.py`.

## Phase 1: CSS Contract Extraction
- Compile `client-first-library-contract.json` from source stylesheets.
- Run `python scripts/gates/validate_css_contract.py` and `validate_css_index.py`.

## Phase 2: Figma Extraction
- Fetch Figma nodes and output `figma.node-bundle.json`.
- Run `python scripts/gates/validate_figma_node_bundle.py`.

## Phase 3: Design-System Sync
- Sync Figma variable tokens with CSS Contract allowed variables.
- Run `python scripts/gates/validate_design_system_sync.py`.

## Phase 4: Component Signature Sync
- Match node layouts with known components in component registry.
- Run `python scripts/gates/validate_component_matching.py`.

## Phase 5: Figma Tree Normalization
- Recover generic names and auto-layouts; snap raw colors.
- Run `python scripts/gates/validate_figma_normalization.py`.

## Phase 6: Semantic IR Resolution
- Resolve tag intents and Client-First class choices strictly.
- Run `python scripts/gates/validate_semantic_ir.py`.

## Phase 7: HTML Blueprint Rendering & QA
- Render logical blueprint and compile physical HTML.
- Run `python scripts/gates/validate_html_blueprint.py`.

## Phase 8: Asset Alt Policy Manifest
- Generate `asset-manifest.json` and validate compliance.
- Run `python scripts/gates/validate_asset_policy.py`.

## Phase 9: Section Chunk Slicing & Benchmarks
- Slice page HTML into section chunks.
- Run `python scripts/validate_html_chunks.py` and benchmark accuracy using `validate_resolver_benchmark.py`.

## Phase 10: Webflow Native Build Plan
- Compile section chunks into serialized native operations plan.
- Run `python scripts/gates/validate_native_build_plan.py`.

## Phase 11: Deployment & Audit
- Operator requests user approval of build plan.
- Operator executes native mutations sequentially on target site branch.
- Logs every write transaction to `write-audit-log.jsonl`.
- Validates deployed DOM structures.
- Unified quality checks: `python scripts/gates/run_quality_gate.py --profile html-first`.
