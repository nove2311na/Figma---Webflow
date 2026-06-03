# Client-First Library

The Client-First library is split into two layers:

- `knowledge-base/client-first-theory.md`: human-readable rules and rationale.
- `knowledge-base/client-first-class-map.json`: structured class, property, and Figma signal catalog for agents and scripts.

## How Agents Use It

1. Read Figma raw data from `workspace/rawdata/`.
2. Match Figma signals against `knowledge-base/client-first-class-map.json`.
3. Choose the Client-First class strategy:
   - required global class,
   - utility selection,
   - utility pair,
   - variable-backed utility,
   - custom section,
   - custom component,
   - combo class.
4. Write the decision into `workspace/blueprints/*.json`.
5. Copy the same selected classes into Webflow build actions after user approval.

## Class Mapping Rule

Every mapped class in a blueprint must include:

- `figma_property`
- `figma_value`
- `client_first_class` or `client_first_class_pattern`
- `webflow_property`
- `reason`
- `source`

Example:

```json
{
  "figma_property": "vertical section padding",
  "figma_value": "80px top and bottom",
  "client_first_class": "padding-section-medium",
  "webflow_property": "padding-top and padding-bottom",
  "reason": "Section-level vertical rhythm maps to the Client-First section padding utility.",
  "source": "knowledge-base/client-first-class-map.json"
}
```

## Multi-Project Library Workflow

Each Webflow project can have a dedicated Client-First library variant stored in
`knowledge-base/libraries/{webflow_site_id}/`. This decouples project-specific
token values (colors, spacing, typography) from the global CF methodology rules.

### Library files per project

| File | Purpose |
|---|---|
| `client-first-library.json` | CF class → CSS property map (source of truth for Webflow sync) |
| `figma-token-map.json` | Raw Figma variable → CF class name mapping |
| `changelog.json` | Audit trail of every class value change |

### How agents use per-project libraries

1. Read `workspace/meta.json` → get `webflowSiteId`.
2. Load correct library via `tools/library_resolver.py:load_library(root, site_id)`.
3. Match Figma signals against `figma-token-map.json` first; fall back to global
   `knowledge-base/client-first-class-map.json` for structural/layout decisions.
4. Write class decisions into `workspace/blueprints/*.json` with `source` pointing
   to the per-project library path.
5. After approval: sync library to Webflow via `scripts/sync_library_to_webflow.py`.

### Updating a library from Figma

```cmd
python scripts/update_library_from_figma.py --site-id <webflow_site_id> --figma-file-id <id>
```

Follow the printed instructions: call Figma MCP → apply `agentic/prompts/generate-cf-library.md`
rules → validate → sync.

### Registry

`knowledge-base/libraries/registry.json` indexes all projects. The quality gate
(`scripts/gates/run_quality_gate.py`) auto-runs `validate_project_library.py` when
`workspace/meta.json` contains a `webflowSiteId`.

---

## Webflow Project Sync

The Webflow project should contain matching variables and global classes before build execution:

- page and main wrappers,
- section, padding, and container classes,
- text-size, heading-style, text-weight, and text-align utilities,
- text-color, background-color, and border-color utilities backed by variables,
- component custom classes generated from the approved blueprint.

If a mapped utility class does not exist in Webflow, the operator must record the missing class in `workspace/error-logs.json` and ask PM before creating or substituting it.

### New Classes in a Parallel Build

Not every Figma value maps to an existing Finsweet/CF class, so a build sometimes needs new custom
classes. These are decided up front by the architect (listed as `new_classes` in the blueprint) and
created once by the **parent operator in Phase 2A**, then registered into the per-project
`client-first-library.json` + `changelog.json` (`source: "figma_adapt"`). Because one author names and
creates them serially before any subagent runs, two sections can never invent conflicting names.

`section-builder` subagents in Phase 2B stay strictly apply-only: a class missing from the canvas is a
blocker recorded in `workspace/error-logs.json`, never a self-creation.

