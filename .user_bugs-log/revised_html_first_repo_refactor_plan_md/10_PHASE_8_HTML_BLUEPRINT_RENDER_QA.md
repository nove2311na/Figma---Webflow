# Phase 8: HTML Blueprint, Render & QA

> Audience: intern mới vào dự án, chưa biết repo, chưa biết Figma → HTML → Webflow pipeline.  
> Mode hiện tại: **strict mode** — missing token/class/style/component = dừng và báo lỗi.  
> Rule lõi: **Client-First CSS contract là ràng buộc bắt buộc**; final HTML chỉ được dùng class/var đã có trong contract hoặc Webflow native index/structural conventions.


## Goal

render local HTML and validate it before chunks/Webflow.

## Context

This phase is part of the revised compiler pipeline. Do not skip earlier gates. If a blocker appears, stop and report; do not patch downstream output to hide upstream issues.

## Files to create/update

- Create HTML blueprint schema, validation report schema, render prompt.
- Create `scripts/render_html_from_blueprint.py`.
- Create gates: html blueprint, semantic html, class usage, accessibility, responsive, Client-First structure.
- Renderer must produce full HTML document with normalize.css, webflow.css, client-first CSS links.
- Renderer must preserve class order and data markers, escape text, and never output inline style.

## Detailed tasks

1. Create HTML blueprint schema, validation report schema, render prompt.
2. Create `scripts/render_html_from_blueprint.py`.
3. Create gates: html blueprint, semantic html, class usage, accessibility, responsive, Client-First structure.
4. Renderer must produce full HTML document with normalize.css, webflow.css, client-first CSS links.
5. Renderer must preserve class order and data markers, escape text, and never output inline style.
6. Class gate must fail on any class not in contract; examples like button_component/card_component fail unless contract proves them.
7. Accessibility gate checks alt, label, input type/name/id, button type, accessible names.
8. Client-First gate checks page-wrapper/main-wrapper/section markers/padding/container patterns.

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
