---
_raw_url: https://finsweet.com/client-first/docs/webflow
_distilled_at: 2026-06-04
_token_estimate: 800
---

# Finsweet Client-First — Webflow Integration

Webflow Variables + Style Classes + Components. The CF class library is pasted into the project, then extended per-project.

## Webflow Variables

Webflow Variables = Figma Variables, 1:1.

Types supported in Webflow:
- `Color` (hex)
- `Length` (px/rem)
- `Percentage`
- `Font Family`
- `Font Weight`
- `Number`
- `Font Size` (special length, scoped to typography)
- `Time`

Modes: Webflow Variables support light/dark/etc. modes natively. Create them in Designer → Variables panel.

The V3 sync maps each Figma variable to a Webflow variable, preserving:
- `name` (display name)
- `figmaId` (stable id, stored as a custom field in the Webflow variable description or in the audit log)
- `modes` (all mode values)
- `type` (one of the above)

## Style Classes (the V2.2 library)

The CF V2.2 stylesheet (`client-first-v2-2.webflow.css`) is pasted into the project's Webflow custom code. It defines:

- ~200 utility classes
- ~50 combo classes
- 0 custom classes (project-specific)

The V3 pipeline does NOT inject this stylesheet — it's a one-time paste by the developer. The pipeline assumes it's there.

## Component Classes

Webflow Components = reusable, parameterizable UI blocks. Built from utility + combo + custom classes.

Example: a Button component has:
- Base class: `button`
- Combos: `is-primary`, `is-secondary`, `is-large`, `is-small`
- Composition: `<a class="button is-primary is-large">Click me</a>`

In Designer, the Button component is a Symbol with variants. The variant property maps to a combo class.

## Multi-mode styling

When a Webflow Variable has multiple modes, applying it to a property (color, padding, etc.) means the property changes per mode. Designer handles the mode-switching automatically.

A button with `background-color: var(--_theme---background--primary)`:
- Light mode: white background
- Dark mode: black background

No additional CSS needed.

## CMS Collections + Variables

CMS collection fields can reference variables via:
- Plain text fields
- Option fields (set to a variable's display name)
- Reference fields (to a single-item collection of variables)

The V3 pipeline does NOT support CMS-driven content yet (out of scope for V3.1).

## Sync targets (the V3 writes)

When the V3 pipeline writes to Webflow, it calls:

1. `variable_tool.create` / `update` — for new / changed variables.
2. `style_tool.create` / `update` — for new / changed classes.
3. `element_builder.create` / `update` / `delete` — for component instances.

Every write is:
- Preceded by user approval (🛑 APPROVAL GATE).
- On a branch, not main.
- Logged to `write-audit-log.jsonl`.

## Naming drift prevention

The `figmaId` stored in the Webflow variable description (or in a sidecar) lets the next sync detect "this Webflow variable was created from Figma variable X" and avoid creating duplicates when the name drifts.

## Anti-patterns

- Renaming a Webflow variable without updating Figma (the id is preserved but the name is now misleading).
- Adding a new variable in Webflow manually (skips the pipeline, won't sync to Figma).
- Using raw hex in component styles instead of variables (breaks theme switching).
