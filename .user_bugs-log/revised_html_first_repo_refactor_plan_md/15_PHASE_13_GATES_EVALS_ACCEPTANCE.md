# Phase 13: Gates, Evals & Acceptance

> Audience: intern mới vào dự án, chưa biết repo, chưa biết Figma → HTML → Webflow pipeline.  
> Mode hiện tại: **strict mode** — missing token/class/style/component = dừng và báo lỗi.  
> Rule lõi: **Client-First CSS contract là ràng buộc bắt buộc**; final HTML chỉ được dùng class/var đã có trong contract hoặc Webflow native index/structural conventions.


## Goal

update gate profile, eval scoring, final acceptance criteria.

## Context

This phase is part of the revised compiler pipeline. Do not skip earlier gates. If a blocker appears, stop and report; do not patch downstream output to hide upstream issues.

## Files to create/update

- Create all new gates listed in the matrix.
- Update `validate_agentic_structure.py`, `validate_workspace_artifacts.py`, and `run_quality_gate.py`.
- Add `--profile html-first` sequence.
- Update eval rubrics with scoring: CSS contract, extraction/normalization, design sync, component signature, semantic HTML, class strictness, asset/a11y, Webflow safety.
- Final acceptance: no active archived refs, contract generated, strict class gate works, HTML gates pass, chunks generated, native plan generated, no Webflow writes during refactor.

## Detailed tasks

1. Create all new gates listed in the matrix.
2. Update `validate_agentic_structure.py`, `validate_workspace_artifacts.py`, and `run_quality_gate.py`.
3. Add `--profile html-first` sequence.
4. Update eval rubrics with scoring: CSS contract, extraction/normalization, design sync, component signature, semantic HTML, class strictness, asset/a11y, Webflow safety.
5. Final acceptance: no active archived refs, contract generated, strict class gate works, HTML gates pass, chunks generated, native plan generated, no Webflow writes during refactor.
6. Quality profile must fail if unknown classes are used.

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
