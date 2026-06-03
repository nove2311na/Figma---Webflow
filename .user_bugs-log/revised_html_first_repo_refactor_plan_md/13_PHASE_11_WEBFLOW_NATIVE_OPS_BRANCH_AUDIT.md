# Phase 11: Webflow Native Ops, Branch, Audit & Retry

> Audience: intern mới vào dự án, chưa biết repo, chưa biết Figma → HTML → Webflow pipeline.  
> Mode hiện tại: **strict mode** — missing token/class/style/component = dừng và báo lỗi.  
> Rule lõi: **Client-First CSS contract là ràng buộc bắt buộc**; final HTML chỉ được dùng class/var đã có trong contract hoặc Webflow native index/structural conventions.


## Goal

compile approved chunks into safe native build plan.

## Context

This phase is part of the revised compiler pipeline. Do not skip earlier gates. If a blocker appears, stop and report; do not patch downstream output to hide upstream issues.

## Files to create/update

- Create native ops spec and branch strategy spec.
- Create schemas: native build plan, section task, write audit log.
- Create prompts: build-webflow-section-native and qa-webflow-against-html.
- Create `scripts/compile_native_ops_from_html.py` and native plan gate.
- Compile step must not call Webflow; it only writes plan/task files.

## Detailed tasks

1. Create native ops spec and branch strategy spec.
2. Create schemas: native build plan, section task, write audit log.
3. Create prompts: build-webflow-section-native and qa-webflow-against-html.
4. Create `scripts/compile_native_ops_from_html.py` and native plan gate.
5. Compile step must not call Webflow; it only writes plan/task files.
6. Allowed native exceptions: nav/form/tabs/dropdown/slider/richtext structures and asset IDs.
7. Create concurrency policy: read/analyze parallel, Webflow writes serialized by default.
8. Create retry policy: transient MCP errors retryable; missing class/unknown component/destructive diff not retryable without human.
9. Webflow writes require approved local HTML, asset manifest, section manifest, native plan, target branch, payload summary, rollback/QA plan.

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
