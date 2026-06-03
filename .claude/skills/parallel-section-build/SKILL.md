---
name: parallel-section-build
description: Orchestrate Phase 2A and 2B of the MAS Webflow build - the parent creates new classes and section containers, then spawns one apply-only section-builder subagent per section.
---

# Parallel Section Build

## Use When

- The blueprint is approved and carries an `html_contract` plus `cf_classes` per section.
- Webflow target site/page IDs are confirmed.
- The page has multiple sections that can be built independently under a shared parent.

## Naming-Race Prevention

All class names are decided by the parent in the serial blueprint/HTML-contract stage. Because one
author names everything (existing Client-First classes and any new custom classes), two subagents can
never invent conflicting names. New classes are created once, by the parent, in Phase 2A, then registered
into `knowledge-base/libraries/{site_id}/client-first-library.json` and `changelog.json`. Subagents only
reference names that already exist on the canvas.

## Workflow

1. Load the approved blueprint; confirm each section has `section_id`, `html_contract`, `cf_classes`,
   and that the page-level `new_classes` list covers any class not yet in the per-project library.
2. Run the build-contract gate:
   `python scripts/gates/validate_build_contract.py --site-id <id>`. Stop on failure.
3. Phase 2A (serial, parent): for each entry in `new_classes`, create the class on Webflow via the
   native `style_tool`, then append it to the per-project library + changelog (`source: "figma_adapt"`).
4. Phase 2A (serial, parent): create the N section container elements under `main-wrapper` in correct
   vertical order; record each returned node ID as the section's `target_parent_element_id` and log to
   `workspace/state.json` (phase `phase_2a_class_setup`).
5. Phase 2B: build one `subagent-task` payload per section (matching `agentic/schemas/subagent-task.schema.json`),
   then spawn one `section-builder` subagent per section. Each is apply-only and scoped to its parent node.
6. Collect each subagent's `workspace/sections/[section_id]_action_log.json`; hand the aggregate to QA.

## Concurrency

Spawn subagents in parallel when the Webflow MCP supports concurrent writes from multiple sessions to one
site; otherwise the same payloads run sequentially. The design is identical either way - parallelism is a
performance property, not a correctness requirement. Verify capability once with `webflow_guide_tool`.

## Forbidden

- No `whtml_builder`. The HTML contract is recreated with native element operations.
- Subagents never create classes, pages, or components.
- No Webflow writes before the user-approval gate and target confirmation.
- No exceeding MCP-352 (max 3 nesting, max 5 actions per turn, verify every 2).

## Validation

- `validate_build_contract.py` must pass before any Webflow write.
- QA (`pixel-perfect-qa`) inspects actual Webflow state and aggregates all section action logs against
  the blueprint and Figma before final approval.
