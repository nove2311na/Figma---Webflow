# `.claude/skills/_shared/`

Shared Python toolkit consumed by every skill in this workspace
(`design-system-sync`, `figma-to-html-architect`, `figma-to-webflow-orchestrator`).

Two layers:

| Layer | Role |
|-------|------|
| **Root files** | Reusable helpers importable from any skill script. No skill-specific logic. |
| **`scripts/`** | CLI entry points. Each script is runnable standalone and is also called by the `html-first` quality gate. |
| **`scripts/css_indexer/`** | Internal library used only by `scripts/index_css_library.py`. Not a CLI. |

---

## Root files

### `selector_guards.py`

Two predicate functions used to reject forbidden selectors in Client-First V2.2 builds.

- `is_native_selector(sel, webflow_native=())` — returns `True` for Webflow native classes (`w-*`, `wf-*`) and any selector listed in the baseline contract's `excluded.webflowNativeSelectors`. Strips leading `.` before comparing so callers may pass `.foo` or `foo`.
- `is_html_tag_selector(sel, native_elements=())` — returns `True` for raw HTML tag selectors (`h1`, `body`, `img`, `p`, `a`, `ul`, `ol`, `li`, etc.) and any selector listed in `excluded.nativeElementSelectors`.

Imported by `design-system-sync/scripts/validate_figma_extraction.py` and `figma-to-html-architect/scripts/process_html.py`.

---

## `scripts/`

### `repo_root.py`

Path-resolution helpers. Every script that needs the repo root imports from here.

- `find_repo_root(start=None)` — walks up from the given path until it finds a folder containing both `.claude/` and `agentic/`. Raises `RuntimeError` if not found.
- `resolve_repo_path(root, value)` — joins a value against `root` unless it is already absolute. Returns `None` when `value` is `None`.

### `utils.py`

Core helpers used by `resolve_client_first.py` and downstream consumers.

- `BASE_FONT_SIZE = 16` — px→rem divisor.
- `SPACING_SCALE` — Client-First spacing token name → px.
- `RgbaColor` dataclass (frozen, 0-255 RGB + 0-1 alpha).
- `to_rem(value)` — converts px/strings/lists to rem strings (3-decimal, stripped trailing zeros).
- `slugify(value)` — Client-First-safe slug, preserves `_`, lowercases, strips diacritics.
- `format_class(prefix, element=None, *, is_utility=False)` — builds `prefix_element` or just `prefix` per CF naming.
- `parse_color(value)` / `hex_to_rgba(value)` — accept hex (`#RGB`, `#RGBA`, `#RRGGBB`, `#RRGGBBAA`) or Figma RGBA dict. Returns `RgbaColor` or `None`.
- `color_distance(a, b)` — Euclidean RGBA distance (alpha scaled to 0-255).
- `log_entry(agent, entry_type, message, context=None)` — standardized workspace log dict with UTC timestamp.
- `load_client_first_class_map(path=None)` — loads `agentic/knowledge/client-first-class-map.json`.
- `suggest_client_first_classes(figma_properties, class_map=None)` — conservative helper that returns class-mapping candidates from a Figma property sample; the architect still decides final application.

### `resolve_client_first.py`

CLI: `python resolve_client_first.py --input <tagged-blueprint> --output <semantic-tree> ...`

Converts a tagged Figma blueprint (`workspace/semantic/tagged-blueprint.json`) into a semantic tree (`workspace/semantic/figma.semantic-tree.json`) by:

1. Reading tag/class rules, the Client-First contract, and the CSS variable index.
2. Resolving CSS variable chains recursively (`var(--x)` → raw value, with cycle detection).
3. Walking the blueprint, attaching pre-resolved `tag` + `role` from the auto-tagger, and mapping inline padding/spacing/typography to Finsweet utility classes (`padding-global`, `padding-section-*`, `container-large`, `heading-style-h*`, `button`).
4. Snapping raw hex colors to the closest allowed CSS variable (Euclidean threshold 15).
5. Verifying every emitted class against `allowed_classes ∪ allowed_combo_classes ∪ structural_convention_classes ∪ reserved_webflow_classes ∪ w-*`.
6. Writing the semantic tree plus `workspace/reports/missing-mapping-report.json`.

Strict by default; non-strict mode logs missing classes but still emits them.

### `index_css_library.py`

CLI: `python index_css_library.py --normalize <path> --webflow <path> --client-first <path> --out <dir>`

Front-end for the `css_indexer` library. Parses three CSS sources (normalize, webflow native, client-first) and writes the canonical contract + six indices into the output directory:

- `client-first-library-contract.json` (allowed_classes, allowed_combo_classes, allowed_variables, reserved_webflow_classes, styleguide_only_classes, structural_convention_classes, etc.)
- `css-variable-index.json`, `css-class-index.json`, `css-selector-index.json`, `css-property-value-index.json`, `css-breakpoint-index.json`, `webflow-native-class-index.json`

The contract hash (`source.client_first_css_hash`) and the strict-mode flag are populated for downstream validators.

### `run_quality_gate.py`

CLI: `python run_quality_gate.py [--target <path>] [--profile html-first]`

Top-level gate runner. With `--profile html-first` (the only profile currently), it sequentially executes:

1. `validate_agentic_structure.py`
2. `validate_workspace_artifacts.py`
3. `validate_css_contract.py`
4. `validate_css_index.py`
5. `validate_artifact_contracts.py`

Each sub-gate runs as a subprocess; any non-zero exit fails the overall gate. Without `--profile`, runs the legacy lightweight check (required-phrase and forbidden-phrase scan of `CLAUDE.md`, `README.md`, and key specs/policies).

Exit code: `0` pass / `1` fail.

### `validate_agentic_structure.py`

Standalone gate. Verifies the agentic skeleton is intact:

- Required folders: `agentic/knowledge/generated`, `agentic/knowledge/client-first`, `agentic/rules`, `agentic/knowledge`, `agentic/schemas/_shared`.
- Required specs (`*.md`).
- Required rules (`*.yaml`) — parses each with `yaml.safe_load` to confirm valid YAML.
- Required schemas (`*.json`) — parses each with `json.load` to confirm valid JSON.
- Required deps in `pyproject.toml`: `tinycss2`, `pydantic`, `typer`, `beautifulsoup4`.
- Documents the new workspace folders (`workspace/figma/`, `workspace/semantic/`, `workspace/html/`, `workspace/reports/`) in `workspace-artifact-schemas.md`.

Exits `0` pass, `1` fail.

### `validate_workspace_artifacts.py`

Standalone gate. If `workspace/meta.json` exists, validates workspace runtime artifacts:

- Core files present: `meta.json`, `page_structure.json`, `state.json`, `error-logs.json`.
- Every JSON under `workspace/` parses cleanly.
- `meta.json` has `projectName`, `figmaUrl`, `initializedAt`, `runtime`.
- `state.json` entries have `agent`, `phase`, `type`, `message`; entries that touch Webflow or are in `phase_2_webflow_build` additionally need ReAct fields `reason`, `action`, `observation`, `next_decision`.
- `error-logs.json` is a list.

If `workspace/` has no `meta.json`, gate is a no-op (pre-execution state).

### `validate_css_contract.py`

Standalone gate. Checks `agentic/knowledge/generated/client-first-library-contract.json`:

- `source.client_first_css_hash` non-empty.
- `allowed_classes` and `allowed_variables` non-empty.
- Required known classes present: `button`, `padding-global`, `container-large`, `heading-style-h1`, `text-size-medium`, `form_input`, `nav_component`, `grid-2-col`.
- Required known variables present: `--_layout---spacing--medium`, `--_layout---spacing--global-padding`, `--_theme---text-color--primary`.
- `styleguide_only_classes` non-empty and every entry matches the `fs-styleguide[_]…` pattern.
- `reserved_webflow_classes` non-empty and contains at least one `w-` prefixed class.

### `validate_css_index.py`

Standalone gate. Confirms these JSON files exist and parse under `agentic/knowledge/generated/`:

- `css-variable-index.json`
- `css-class-index.json`
- `css-selector-index.json`
- `css-property-value-index.json`
- `css-breakpoint-index.json`
- `webflow-native-class-index.json`

### `validate_artifact_contracts.py`

Standalone gate. Auto-discovers workspaces (`workspace/*`, excluding `_`-prefixed dirs) and runs `validate_artifacts.py --workspace <name>` for each. Aggregates results and fails on block-tier violations. See also: `validate_artifacts.py` below.

Exit codes: `0` pass / `1` block-tier violation in any workspace / `2` internal error.

### `validate_artifacts.py`

CLI: `python validate_artifacts.py --workspace <name> [--tier block|warn|log]`
CLI: `python validate_artifacts.py --path <file>`
CLI: `python validate_artifacts.py --list-tiers`

Per-artifact JSON Schema validator (JSON Schema 2020-12 via `jsonschema` + `referencing`). Maps each known workspace artifact path to a schema `$id` and a severity tier:

- `block` — must pass. Build halts. Exit `2`.
- `warn` — should pass. Build continues. Logged to `qa-report`.
- `log` — tracked, not gated.

Schema registry resolves `$id`s (e.g. `https://figwebflow.local/schemas/_shared/variable-entry.schema.json`) to local files in `agentic/schemas/...` and `.claude/skills/design-system-sync/schema/...`. JSONL artifacts (`write-audit-log.jsonl`) are split into per-line records before validation.

This is the only validator authorized to enforce the block tier; it is wired in by `validate_artifact_contracts.py` and by the orchestrator skill before any Webflow write.

---

## `scripts/css_indexer/`

Internal library used only by `scripts/index_css_library.py`. Not a CLI; not on the import path for other skills.

### `parser.py`

`CSSParser` — `tinycss2`-based CSS file reader. For each file extracts:

- `classes` — main class per compounded selector (e.g. `button` from `.button.is-secondary`).
- `combo_classes` — modifier classes chained to the same compound (`is-secondary`).
- `variables` — `--*` custom properties, each with `value` and `media` scope.
- `selectors` — raw selector strings.
- `breakpoints` — `@media` prelude strings (recursively walked).
- `declarations` — flat list of `{selector, property, value, media}` tuples.

Also exposes `get_md5_hash(path)` for the contract's source hash.

### `classifier.py`

`CSSClassifier.classify_class(name)` — single static method. Buckets a class name into one Client-First category by prefix/keyword heuristics:

- `styleguide-only` (`fs-styleguide[_]…`)
- `native` (`w-`)
- `spacing` (`padding-`, `margin-`, `spacer-`)
- `gap` (`gap-`)
- `grid` (`grid-`)
- `flex` (`flex-`)
- `typography` (`heading-style-`, `text-size-`, `text-weight-`, `text-style-`)
- `color` (`text-color-`, `background-color-`, `border-color-`)
- `components` (any name containing `button`/`form`/`nav`/`card`/`section`/`header`/`footer`/`menu`/`input`/`dropdown`)
- `custom` (fallback)

### `contract_builder.py`

`ContractBuilder` — orchestrates the indexer. Workflow:

1. Parse `normalize.css`, `webflow.css`, and the client-first CSS via `CSSParser`.
2. Compute `client-first-css` MD5 hash.
3. Build the contract (allowed/combo classes, allowed variables/selectors/breakpoints, reserved Webflow classes, styleguide-only classes from `CSSClassifier`).
4. Build six indices by merging declarations across the three sources, keyed by variable / class / selector / property / breakpoint.
5. Write all seven JSON files into the target directory.

This module is the single source of truth for the contract shape consumed by `validate_css_contract.py`, `resolve_client_first.py`, and every downstream skill.

---

## Call graph

```
run_quality_gate.py --profile html-first
  ├── validate_agentic_structure.py
  ├── validate_workspace_artifacts.py
  ├── validate_css_contract.py
  ├── validate_css_index.py
  └── validate_artifact_contracts.py
        └── validate_artifacts.py --workspace <name>  (per workspace)

index_css_library.py
  └── css_indexer/{parser, classifier, contract_builder}

resolve_client_first.py
  ├── repo_root.py
  └── utils.py

selector_guards.py — used by design-system-sync + figma-to-html-architect
```
