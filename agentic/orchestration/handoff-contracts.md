# Handoff Contracts

## PM to Operator: Figma Extraction

Required input:

- Figma URL or node IDs,
- project name,
- output section ID,
- required workspace paths.

Required output:

- `workspace/rawdata/[section_id]_raw.json`,
- `workspace/contents/[section_id]_content.json`,
- extraction summary.

## PM to Architect: Blueprint

Required input:

- raw data path,
- content path,
- design-system path,
- target page context.

Required output:

- blueprint JSON path,
- page structure update,
- approval summary.

## PM to Operator: Webflow Build

Required input:

- approved blueprint path,
- Webflow site ID,
- Webflow page ID,
- MCP-352 constraints.

Required output:

- action log,
- verification points,
- blockers.

## PM to Section Builder: Webflow Section Build

Spawned once per section during Phase 2B, after Phase 2A creates all classes and containers.

Required input (matches `agentic/schemas/subagent-task.schema.json`):

- `section_id`,
- `parent_element_id` (`{component, element}` object of section container from Phase 2A; passed directly to `element_builder`),
- `html_contract` (section slice with Client-First tags + final class names),
- `cf_classes` (all must already exist on the canvas),
- Webflow site ID,
- Webflow page ID,
- MCP-352 constraints,
- `mode: apply_only`.

Required output:

- `workspace/sections/[section_id]_action_log.json` (ReAct entries with `subagent_id` + `parent_element_id`),
- verification points,
- blockers in `workspace/error-logs.json`.

Invariant: the subagent applies existing classes only. A missing class is a blocker, never a creation.

## PM to Architect: QA

Required input:

- approved blueprint,
- Webflow state/snapshot,
- build action log.

Required output:

- `[APPROVED]` or `[FIX]`,
- evidence,
- error log entries.

