# Phase 4: Design-System Sync Strict Mode

> Audience: intern mới vào dự án, chưa biết repo, chưa biết Figma → HTML → Webflow pipeline.  
> Mode hiện tại: **strict mode** — missing token/class/style/component = dừng và báo lỗi.  
> Rule lõi: **Client-First CSS contract là ràng buộc bắt buộc**; final HTML chỉ được dùng class/var đã có trong contract hoặc Webflow native index/structural conventions.


## Goal

compare Figma variables/styles with CSS contract.

## Context

This phase is part of the revised compiler pipeline. Do not skip earlier gates. If a blocker appears, stop and report; do not patch downstream output to hide upstream issues.

## Files to create/update

- Create `knowledge-base/design-system-contract.json`.
- Create `agentic/prompts/sync-design-system-from-figma.md`.
- Create `agentic/schemas/design-system-sync-report.schema.json`.
- Create `scripts/gates/validate_design_system_sync.py`.
- Inputs: figma.node-bundle, figma.variable-defs, client-first-library-contract.

## Detailed tasks

1. Create `knowledge-base/design-system-contract.json`.
2. Create `agentic/prompts/sync-design-system-from-figma.md`.
3. Create `agentic/schemas/design-system-sync-report.schema.json`.
4. Create `scripts/gates/validate_design_system_sync.py`.
5. Inputs: figma.node-bundle, figma.variable-defs, client-first-library-contract.
6. Do not call Figma MCP in this phase; read saved extraction bundle.
7. Strict behavior: missing token/style/class = blocker; no auto class proposals.
8. Report must include matched/missing tokens, unmapped styles, hardcoded values, blockers.
9. Gate fails if missing_in_css, unmapped styles, hardcoded values, or blockers exist.

## Stabilization requirements

After creating/updating these files:

1. Search for old references that contradict this phase.
2. Update README/CLAUDE/SOP references if command names changed.
3. Add or update gate scripts so the phase can be checked automatically.
4. Ensure generated artifacts go under `workspace/` or `knowledge-base/generated/`, not committed as source unless they are golden fixtures.
5. Ensure strict mode behavior is documented and enforced.

## Pass/fail criteria

Pass if:

- Required files exist.
- Schemas parse as valid JSON where applicable.
- Gates exist or are documented as TODO with exact behavior.
- No Webflow write is performed.
- No unknown class is allowed into final HTML.

Fail if:

- A missing token/class/style is silently ignored.
- A prompt instructs direct Figma-to-Webflow build.
- A final HTML example uses a class not in CSS contract.
- A Webflow mutation can happen without approved local HTML and native build plan.

## Done checklist

```text
[ ] Files created/updated.
[ ] References stabilized.
[ ] Gate added/updated.
[ ] Strict behavior documented.
[ ] Phase output path documented.
```
