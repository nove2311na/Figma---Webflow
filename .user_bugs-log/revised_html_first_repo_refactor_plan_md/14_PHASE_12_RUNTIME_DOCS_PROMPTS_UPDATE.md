# Phase 12: Runtime Docs & Prompts Update

> Audience: intern mới vào dự án, chưa biết repo, chưa biết Figma → HTML → Webflow pipeline.  
> Mode hiện tại: **strict mode** — missing token/class/style/component = dừng và báo lỗi.  
> Rule lõi: **Client-First CSS contract là ràng buộc bắt buộc**; final HTML chỉ được dùng class/var đã có trong contract hoặc Webflow native index/structural conventions.


## Goal

make human/agent docs follow revised workflow.

## Context

This phase is part of the revised compiler pipeline. Do not skip earlier gates. If a blocker appears, stop and report; do not patch downstream output to hide upstream issues.

## Files to create/update

- Update README.md to HTML-first compiler positioning.
- Update CLAUDE.md with non-negotiable rules and command order.
- Update llm-instructions.md, agentic/README.md, workflow-map, SOP, retry/stop conditions.
- Update approval-gates and MCP risk map: Webflow write = external mutation, branch-first, audit log, approval required.
- Archive old write-html-contract prompt and replace with split prompts.

## Detailed tasks

1. Update README.md to HTML-first compiler positioning.
2. Update CLAUDE.md with non-negotiable rules and command order.
3. Update llm-instructions.md, agentic/README.md, workflow-map, SOP, retry/stop conditions.
4. Update approval-gates and MCP risk map: Webflow write = external mutation, branch-first, audit log, approval required.
5. Archive old write-html-contract prompt and replace with split prompts.
6. Docs must mention: Client-First Library Contract is binding; research examples are conceptual until class exists in contract.
7. Add MVP command sequence and stop conditions.

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
