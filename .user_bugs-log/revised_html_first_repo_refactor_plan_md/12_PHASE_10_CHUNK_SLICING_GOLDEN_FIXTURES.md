# Phase 10: Chunk Slicing, Golden Fixtures & Benchmarks

> Audience: intern mới vào dự án, chưa biết repo, chưa biết Figma → HTML → Webflow pipeline.  
> Mode hiện tại: **strict mode** — missing token/class/style/component = dừng và báo lỗi.  
> Rule lõi: **Client-First CSS contract là ràng buộc bắt buộc**; final HTML chỉ được dùng class/var đã có trong contract hoặc Webflow native index/structural conventions.


## Goal

slice page into chunks and validate resolver quality.

## Context

This phase is part of the revised compiler pipeline. Do not skip earlier gates. If a blocker appears, stop and report; do not patch downstream output to hide upstream issues.

## Files to create/update

- Create `scripts/slice_html_into_chunks.py` and `validate_html_chunks.py`.
- Create section manifest schema.
- Output chunks under `workspace/html/chunks/`.
- Slicing rules: global-styles chunk, nav chunk, each direct section under main, footer chunk; never split inside component root.
- Create fixtures: hero clean/messy, form clean/missing label, card-grid, nav native, richtext.

## Detailed tasks

1. Create `scripts/slice_html_into_chunks.py` and `validate_html_chunks.py`.
2. Create section manifest schema.
3. Output chunks under `workspace/html/chunks/`.
4. Slicing rules: global-styles chunk, nav chunk, each direct section under main, footer chunk; never split inside component root.
5. Create fixtures: hero clean/messy, form clean/missing label, card-grid, nav native, richtext.
6. Create broken fixtures: missing-class, bad-heading-order, missing-alt, inline-style, hardcoded-hex.
7. Create gates: golden fixtures and resolver benchmark.
8. Benchmarks: tag resolver accuracy >=95%, invented_classes=0 in strict mode, broken fixtures fail with actionable errors.

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
