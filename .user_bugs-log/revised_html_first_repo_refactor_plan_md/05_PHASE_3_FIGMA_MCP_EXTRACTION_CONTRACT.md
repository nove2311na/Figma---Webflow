# Phase 3: Figma MCP Extraction Contract

> Audience: intern mới vào dự án, chưa biết repo, chưa biết Figma → HTML → Webflow pipeline.  
> Mode hiện tại: **strict mode** — missing token/class/style/component = dừng và báo lỗi.  
> Rule lõi: **Client-First CSS contract là ràng buộc bắt buộc**; final HTML chỉ được dùng class/var đã có trong contract hoặc Webflow native index/structural conventions.


## Goal

extract Figma once into stable bundle.

## Context

This phase is part of the revised compiler pipeline. Do not skip earlier gates. If a blocker appears, stop and report; do not patch downstream output to hide upstream issues.

## Files to create/update

- Create `agentic/specs/figma-extraction-contract.md`.
- Create `agentic/prompts/extract-figma-context.md`.
- Create `agentic/schemas/figma-node-bundle.schema.json`.
- Create `agentic/schemas/figma-extract-run-log.schema.json`.
- Create `scripts/gates/validate_figma_node_bundle.py`.

## Detailed tasks

1. Create `agentic/specs/figma-extraction-contract.md`.
2. Create `agentic/prompts/extract-figma-context.md`.
3. Create `agentic/schemas/figma-node-bundle.schema.json`.
4. Create `agentic/schemas/figma-extract-run-log.schema.json`.
5. Create `scripts/gates/validate_figma_node_bundle.py`.
6. Outputs must go to `workspace/figma/`: metadata, design-context, variable-defs, screenshot, node-bundle, extract-run-log.
7. Prompt must instruct: do not generate HTML, do not choose final classes, do not call Webflow.
8. Large frame policy: use metadata, slice by top-level section, re-run context per section, merge bundle.
9. Gate fails if node bundle/screenshot/variable defs/run log missing or required tool failed without fallback.

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
[x] Files created/updated.
[x] References stabilized.
[x] Gate added/updated.
[x] Strict behavior documented.
[x] Phase output path documented.
```
