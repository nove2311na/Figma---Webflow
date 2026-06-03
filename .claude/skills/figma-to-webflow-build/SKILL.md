---
name: figma-to-webflow-build
description: Run the MAS V3 Figma-to-Webflow workflow from project intake through blueprint, approved Webflow build, QA loop, and session handoff.
---

# Figma to Webflow Build

## Use When

- The user wants to build a Webflow page from a Figma design.
- The workflow must use MAS V3 agents and Finsweet Client-First rules.
- Webflow execution requires approval, MCP-352, and QA evidence.

## Workflow

1. PM reads `agentic/memory/session-handoff.md`, `agentic/policies/runtime-instructions.md`, `agentic/orchestration/sop.md`, and `agentic/specs/agent-system-spec.md`.
2. Workspace steward validates or initializes `workspace/`.
3. Operator extracts Figma data into `workspace/rawdata/` and `workspace/contents/`.
4. Architect produces Client-First blueprints in `workspace/blueprints/`, each with an `html_contract`
   plus `cf_classes` per section and a page-level `new_classes` list (the naming authority).
5. PM presents blueprint and stops for user approval.
6. Build in Webflow using native element operations and MCP-352. For multi-section pages, use the
   `parallel-section-build` skill: Phase 2A (parent creates new classes + section containers) then
   Phase 2B (one apply-only `section-builder` subagent per section). Single-section pages may use a
   single operator pass.
7. Architect runs QA against actual Webflow state or snapshots, aggregating all section action logs.
8. Gatekeeper runs local gates and standalone baseline checks.
9. PM updates `agentic/memory/session-handoff.md` and reports evidence.

## Required Evidence

- `workspace/meta.json`
- `workspace/page_structure.json`
- `workspace/design-system.json`
- `workspace/blueprints/*.json`
- `workspace/state.json`
- `workspace/error-logs.json`
- `agentic/memory/session-handoff.md`

## Validation

Run:

```cmd
python scripts\gates\validate_agentic_structure.py --target .
python scripts\gates\run_quality_gate.py --target .
python scripts\gates\scan_secrets.py --target .
python scripts\gates\validate_agent_system_spec.py --target .
python scripts\gates\validate_client_first_library.py --target .
```

## Pack Layout

- `references/` stores source notes.
- `scripts/` stores helper checks.
- `assets/` stores reusable static diagrams or snapshots.
