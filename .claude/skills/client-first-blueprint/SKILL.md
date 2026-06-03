---
name: client-first-blueprint
description: Produce Client-First V2 Webflow blueprints from Figma raw data using strict structure, naming, REM units, and component rules.
---

# Client-First Blueprint

## Use When

- Figma raw data is ready in `workspace/rawdata/`.
- A Webflow build needs an approved blueprint before execution.
- Client-First class naming or structure decisions are needed.

## Workflow

1. Read `knowledge-base/client-first-theory.md`.
2. Read `knowledge-base/client-first-class-map.json`.
3. Read `knowledge-base/libraries/{site_id}/client-first-library.json` (per-project token classes).
4. Read `agentic/specs/figma-to-client-first-mapping.md`.
5. **Read `agentic/prompts/write-html-contract.md`** — mandatory decision guide for utility vs custom class.
6. Read Figma raw data and content files from `workspace/rawdata/` and `workspace/contents/`.
7. **Run `agentic/prompts/read-figma-data.md` prompt** — produce `workspace/blueprints/[page-slug]_design-analysis.json`. Use the analysis as structured input before writing any HTML contract. Do not skip.
8. Identify global components, sections, grids, flex layouts, variables, text styles, and assets.
9. For each section, write `html_contract` using the 5-layer decision flowchart in `write-html-contract.md`.
10. List every new custom class in the page-level `new_classes` array; each entry must cite Case number in `reason`.
11. Generate blueprint JSON under `workspace/blueprints/` with `html_contract`, `cf_classes`, `new_classes`.
12. Update `workspace/page_structure.json` with routing and section map only.
13. Confirm REM conversion and Client-First naming.
14. Run `python scripts/gates/validate_build_contract.py --site-id <id>` before returning to PM.
15. Return blueprint summary to PM for user approval.

## Hard Rules

- Use six-layer Client-First structure (see `write-html-contract.md` Layer 1).
- Use `section_[name]`, `padding-global`, `container-[size]`, and `padding-section-[size]`.
- Use underscore ONLY for custom child classes (`component_element`). Utilities have NO underscore.
- Use REM units only — no px in final values.
- **Never create a utility class** when `knowledge-base/client-first-class-map.json` or the per-project library contains a matching rule.
- **Never create a custom class** for typography size/weight/color/align — use existing utilities.
- **Always create a custom class** for layout (flex/grid/positioning/sizing) — CF has no layout utilities.
- Max 3–4 classes per element. If you need 5+, merge into a single custom class.
- Every `new_classes` entry must cite Case 1–5 from `write-html-contract.md` in `reason`.
- Every Figma property to class mapping needs `source` pointing to class map or library file.
- Do not approve generic global components.

## Validation

Gatekeeper checks blueprint evidence, class map usage, required Client-First phrases, and `python scripts\gates\validate_client_first_library.py --target .`.
