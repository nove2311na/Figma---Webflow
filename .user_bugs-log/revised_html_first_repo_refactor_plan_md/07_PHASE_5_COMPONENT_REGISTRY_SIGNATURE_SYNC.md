# Phase 5: Component Registry & Signature Sync

> Audience: intern mới vào dự án, chưa biết repo, chưa biết Figma → HTML → Webflow pipeline.  
> Mode hiện tại: **strict mode** — missing token/class/style/component = dừng và báo lỗi.  
> Rule lõi: **Client-First CSS contract là ràng buộc bắt buộc**; final HTML chỉ được dùng class/var đã có trong contract hoặc Webflow native index/structural conventions.


## Goal

map Figma components to known component contracts and signatures.

## Context

This phase is part of the revised compiler pipeline. Do not skip earlier gates. If a blocker appears, stop and report; do not patch downstream output to hide upstream issues.

## Files to create/update

- Create `knowledge-base/component-registry.json`.
- Create `knowledge-base/component-signatures.json`.
- Create `agentic/specs/component-registry-contract.md` and `component-signature-matching.md`.
- Create component schemas and reports.
- Create `scripts/match_components.py` and validation gates.

## Detailed tasks

1. Create `knowledge-base/component-registry.json`.
2. Create `knowledge-base/component-signatures.json`.
3. Create `agentic/specs/component-registry-contract.md` and `component-signature-matching.md`.
4. Create component schemas and reports.
5. Create `scripts/match_components.py` and validation gates.
6. Registry must cover Button, Button Group, Card, Nav, Footer, Form fields, Rich Text, Image/Figure, Section types.
7. Signature matcher uses exact instance/name/child roles/layout topology/token cluster/repeated pattern.
8. Confidence: >=0.95 exact, >=0.85 usable, 0.60-0.84 candidate warning, <0.60 no match.
9. Unknown component instance blocks pipeline in strict mode.

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
