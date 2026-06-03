# Phase 6: Figma Normalization & Messy Recovery

> Audience: intern mới vào dự án, chưa biết repo, chưa biết Figma → HTML → Webflow pipeline.  
> Mode hiện tại: **strict mode** — missing token/class/style/component = dừng và báo lỗi.  
> Rule lõi: **Client-First CSS contract là ràng buộc bắt buộc**; final HTML chỉ được dùng class/var đã có trong contract hoặc Webflow native index/structural conventions.


## Goal

normalize bad Figma data before Semantic IR.

## Context

This phase is part of the revised compiler pipeline. Do not skip earlier gates. If a blocker appears, stop and report; do not patch downstream output to hide upstream issues.

## Files to create/update

- Create `agentic/specs/figma-normalization-policy.md`.
- Create `agentic/prompts/normalize-figma-nodes.md`.
- Create `agentic/rules/figma-normalization.rules.yaml`.
- Create normalized tree/report schemas.
- Create `scripts/normalize_figma_nodes.py` and gate.

## Detailed tasks

1. Create `agentic/specs/figma-normalization-policy.md`.
2. Create `agentic/prompts/normalize-figma-nodes.md`.
3. Create `agentic/rules/figma-normalization.rules.yaml`.
4. Create normalized tree/report schemas.
5. Create `scripts/normalize_figma_nodes.py` and gate.
6. Detect generic names, missing styles, raw colors, arbitrary spacing, missing Auto Layout, repeated subtree, ambiguous media.
7. Output `workspace/figma/figma.normalized-tree.json` and `workspace/reports/figma-normalization-report.json`.
8. Severity: unresolved raw values/ambiguous content images/unknown component instances block.
9. Gate fails if blockers exist or emitted semantic leaves remain unknown.

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
