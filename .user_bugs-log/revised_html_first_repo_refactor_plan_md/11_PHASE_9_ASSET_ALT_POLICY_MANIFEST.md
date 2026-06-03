# Phase 9: Asset & Alt Policy Manifest

> Audience: intern mới vào dự án, chưa biết repo, chưa biết Figma → HTML → Webflow pipeline.  
> Mode hiện tại: **strict mode** — missing token/class/style/component = dừng và báo lỗi.  
> Rule lõi: **Client-First CSS contract là ràng buộc bắt buộc**; final HTML chỉ được dùng class/var đã có trong contract hoặc Webflow native index/structural conventions.


## Goal

make media deterministic and accessible.

## Context

This phase is part of the revised compiler pipeline. Do not skip earlier gates. If a blocker appears, stop and report; do not patch downstream output to hide upstream issues.

## Files to create/update

- Create asset/image policy spec and asset-alt rules.
- Create asset manifest schema and alt-policy schema.
- Create `scripts/gates/validate_asset_policy.py`.
- Add `media` field to Semantic IR: kind, role, alt_policy, alt_text, asset_ref.
- Roles: informative, decorative, functional, complex, unknown.

## Detailed tasks

1. Create asset/image policy spec and asset-alt rules.
2. Create asset manifest schema and alt-policy schema.
3. Create `scripts/gates/validate_asset_policy.py`.
4. Add `media` field to Semantic IR: kind, role, alt_policy, alt_text, asset_ref.
5. Roles: informative, decorative, functional, complex, unknown.
6. Informative image requires alt; decorative image uses aria-hidden/empty alt; functional icons require accessible name; complex images need description/manual review.
7. Output `workspace/html/asset-manifest.json` and `workspace/reports/asset-policy-report.json`.
8. Gate fails on missing content assets, unknown media role, missing alt, missing functional accessible name.

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
