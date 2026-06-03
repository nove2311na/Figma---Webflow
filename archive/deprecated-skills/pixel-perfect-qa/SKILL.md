---
name: pixel-perfect-qa
description: Validate Webflow output against Figma and Client-First blueprint evidence before final approval.
---

# Pixel Perfect QA

## Use When

- Operator reports a Webflow build is complete.
- A fix loop needs verification.
- PM needs a final go/no-go report.

## Workflow

1. Read approved blueprint and current `workspace/state.json`.
2. Inspect actual Webflow state or snapshots.
3. Compare hierarchy, classes, layout, spacing, typography, and components.
4. Record `[APPROVED]` or `[FIX]` with evidence.
5. Write issues to `workspace/error-logs.json`.
6. Ask PM to route fixes to operator when needed.

## Hard Rules

- Do not guess.
- Do not approve without Webflow evidence.
- Reject 1px visual drift, wrong hierarchy, wrong class naming, or px units.

## Validation

Final report must include evidence paths and gate results.

