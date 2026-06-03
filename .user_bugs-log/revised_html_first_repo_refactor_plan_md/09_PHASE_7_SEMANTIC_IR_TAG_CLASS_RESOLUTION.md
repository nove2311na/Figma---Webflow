# Phase 7: Semantic IR, Tag & Class Resolution

> Audience: intern mới vào dự án, chưa biết repo, chưa biết Figma → HTML → Webflow pipeline.  
> Mode hiện tại: **strict mode** — missing token/class/style/component = dừng và báo lỗi.  
> Rule lõi: **Client-First CSS contract là ràng buộc bắt buộc**; final HTML chỉ được dùng class/var đã có trong contract hoặc Webflow native index/structural conventions.


## Goal

produce semantic role, HTML tag intent, and strict class decisions.

## Context

This phase is part of the revised compiler pipeline. Do not skip earlier gates. If a blocker appears, stop and report; do not patch downstream output to hide upstream issues.

## Files to create/update

- Create Semantic IR schema and missing mapping schema.
- Create prompts: normalize-figma-to-semantic-ir, resolve-html-tags, resolve-client-first-classes.
- Update `tag.rules.yaml` and `class-selection.rules.yaml`.
- Tag resolver priority: component registry, explicit prefix, normalized role, text purpose, control/media/list context, parent context, fallback.
- Class resolver priority: component base, component variant, Client-First utility, Webflow native, structural convention, blocker.

## Detailed tasks

1. Create Semantic IR schema and missing mapping schema.
2. Create prompts: normalize-figma-to-semantic-ir, resolve-html-tags, resolve-client-first-classes.
3. Update `tag.rules.yaml` and `class-selection.rules.yaml`.
4. Tag resolver priority: component registry, explicit prefix, normalized role, text purpose, control/media/list context, parent context, fallback.
5. Class resolver priority: component base, component variant, Client-First utility, Webflow native, structural convention, blocker.
6. Final classes must exist in Client-First Library Contract or native index or structural conventions.
7. Output semantic tree, tag report, class usage report, missing mapping report.
8. Gate fails on confidence <0.60, unresolved style refs, component refs, or unknown classes.

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
