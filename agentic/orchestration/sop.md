# Standard Operating Procedure

This SOP governs the Claude Code-native, Python-first MAS Figma-to-Webflow workflow.

## Phase 0: Setup and Audit

Goal: synchronize state and protect the Webflow site and local workspace.

1. PM reads:
   - `CLAUDE.md`
   - `agentic/memory/team-memory.md`
   - `agentic/policies/runtime-instructions.md`
   - `agentic/memory/session-handoff.md`
   - `agentic/specs/agent-system-spec.md`
2. Workspace steward validates or initializes workspace:

```cmd
python scripts\init_workspace.py --project "Project Name" --figma "Figma URL"
```

3. If changing projects, steward must archive first:

```cmd
python scripts\archive_workspace.py
```

4. Before restoring, steward must confirm `workspace/` is empty:

```cmd
python scripts\restore_workspace.py 0
```

5. Operator verifies target Figma and Webflow scope when connectors are configured.
6. PM records blockers and current phase in `agentic/memory/session-handoff.md`.

Stop conditions:

- missing Figma URL,
- missing Webflow site/page target,
- non-empty workspace before restore,
- archive validation failure,
- missing approval for external access.

## Phase 1: Blueprint Establishment

Goal: produce Client-First blueprints and isolate data.

1. Operator extracts raw Figma data into:
   - `workspace/rawdata/[section_id]_raw.json`
   - `workspace/contents/[section_id]_content.json`
2. Architect reads:
   - `knowledge-base/client-first-theory.md`
   - `knowledge-base/client-first-class-map.json`
   - `agentic/specs/figma-to-client-first-mapping.md`
   - raw data,
   - content data,
   - `workspace/design-system.json`
3. Produce design analysis: run `agentic/prompts/read-figma-data.md` prompt to output `workspace/blueprints/[page-slug]_design-analysis.json` from Figma raw data. Validate all color tokens and layout patterns before proceeding.
4. Architect writes:
   - `workspace/blueprints/[section_id]_blueprint.json`
   - updates to `workspace/page_structure.json`
5. PM presents blueprint to the user.
6. PM stops until the user says `Approved` or `Agree`.

Hard rules:

- `page-wrapper` and `main-wrapper` must be accounted for.
- Global components cannot be vague stand-ins.
- Every class mapping must cite the Client-First class map.
- `page_structure.json` stores routing/index data, not raw Figma data.
- All spacing and sizes use rem.

## Phase 2: Webflow Execution

Goal: execute only the approved blueprint with Webflow native operations.

Preconditions (all of Phase 2):

- user approval exists,
- Webflow site/page target confirmed,
- approved blueprint path exists,
- operator has a scoped task.

MCP-352 (applies to every Webflow turn, parent and subagent):

- max 3 nesting levels per turn,
- max 5 Webflow actions per turn,
- verify state after every 2 successful actions.

Forbidden:

- no `whtml_builder` (the blueprint `html_contract` is an instruction, recreated with native ops),
- no unapproved Webflow writes,
- no real asset uploads by default,
- no silent creation of pages/components.

The build runs as two sub-phases. A single-section page may collapse 2A and 2B into one operator pass.

### Phase 2A: Class and Container Setup (serial, parent)

Run by the parent operator. This is the only place classes are created, which removes the
parallel naming race.

1. Run the build-contract gate before any write:

```cmd
python scripts\gates\validate_build_contract.py --site-id <webflow_site_id>
```

2. For each entry in the blueprint `new_classes`, create the class on Webflow with the native
   `style_tool`, then register it into `knowledge-base/libraries/{site_id}/client-first-library.json`
   and append a `changelog.json` entry (`source: "figma_adapt"`).
3. Create the N section container elements under `main-wrapper` in correct vertical order.
4. Record each container's returned `{component, element}` object as the section's
   `target_parent_element_id`, logged to `workspace/state.json` under phase `phase_2a_class_setup`.
   This object is passed directly as `parent_element_id` to `element_builder` in Phase 2B.

Exit: all `new_classes` exist on Webflow and are registered; all section containers created with `parent_element_id` objects.

### Phase 2B: Parallel Section Build

Run by one `section-builder` subagent per section (apply-only).

1. PM builds a `subagent-task` payload per section (see `agentic/schemas/subagent-task.schema.json`).
2. PM spawns one `section-builder` per section. Spawn in parallel when the Webflow MCP supports
   concurrent writes to one site; otherwise the same payloads run sequentially. Correctness is identical.
3. Each subagent recreates its `html_contract` under its `parent_element_id` with native operations,
   applies existing classes only, and never creates classes, pages, or components.
4. Each subagent logs to `workspace/sections/[section_id]_action_log.json`.

Exit: all section action logs present and ready for QA.

Output:

- action entries in `workspace/state.json` and `workspace/sections/[section_id]_action_log.json`,
- blockers in `workspace/error-logs.json`.

## Phase 3: QA Loop

Goal: verify 1:1 Webflow output against Figma and Client-First blueprint.

1. Architect inspects actual Webflow state or snapshots.
2. Architect compares:
   - hierarchy,
   - classes,
   - spacing,
   - typography,
   - responsive layout,
   - component behavior.
3. Architect writes `[APPROVED]` or `[FIX]`.
4. PM routes fixes to operator and repeats QA when needed.
5. Gatekeeper runs local gates:

```cmd
python scripts\gates\validate_agentic_structure.py --target .
python scripts\gates\run_quality_gate.py --target .
python scripts\gates\scan_secrets.py --target .
python scripts\gates\validate_agent_system_spec.py --target .
python scripts\gates\validate_skills.py --target .
python scripts\gates\validate_workspace_artifacts.py --target .
python scripts\gates\validate_phase_state.py --target .
python scripts\gates\validate_relative_paths.py --target .
python scripts\gates\validate_client_first_library.py --target .
```

Completion requires:

- QA evidence,
- passing local gates,
- updated `agentic/memory/session-handoff.md`,
- evidence-backed final report.
