---
_raw_url: https://finsweet.com/client-first/docs/figma
_distilled_at: 2026-06-04
_token_estimate: 800
---

# Finsweet Client-First — Figma Integration

Figma side: Variables for colors/spacing/typography, Styles for text, Components for reusables. All must map 1:1 to Webflow via the V3 pipeline.

## Variables (design tokens)

Figma Variables are the source of truth for: colors, spacing, typography sizes, radii, border widths, font weights.

Naming convention in Figma:
- Match the Webflow variable name exactly, character for character.
- Use `/` to denote namespace: `colors/brand/blue`, `spacing/small`, `typography/h1-size`.
- Or use `--` prefix style: `colors--brand--blue`. Either works; pick one per project.

The Figma file MUST have these variable collections:

| Collection | Examples |
|---|---|
| `colors` | `colors/brand/blue`, `colors/neutral/black`, `colors/theme/background-primary` |
| `spacing` | `spacing/tiny`, `spacing/medium`, `spacing/xlarge` |
| `sizing` | `sizing/container-large`, `sizing/border-radius-medium` |
| `typography` | `typography/h1-size`, `typography/h1-line-height`, `typography/h1-weight` |
| `fonts` | `fonts/body`, `fonts/heading` |

## Modes (themes)

Figma Variables support modes for theme switching:

- Mode 1: `default` (or `light`)
- Mode 2: `dark`
- Optional: `high-contrast`, `rtl`, etc.

Each color variable defines a value per mode. The sync pipeline must mirror all modes to Webflow.

## Text styles

Figma Text Styles = Webflow Heading classes. Naming:

| Figma style | Webflow class |
|---|---|
| `heading/xlarge` | `heading-xlarge` |
| `heading/large` | `heading-large` |
| `heading/medium` | `heading-medium` |
| `heading/small` | `heading-small` |
| `text/large` | `text-size-large` |
| `text/regular` | `text-size-regular` |
| `text/small` | `text-size-small` |

## Components

Figma Components = Webflow Components. Reusable card, button, form field, etc.

A component variant in Figma = a combo class in Webflow:

| Figma variant property | Webflow combo |
|---|---|
| `state: primary` | `.button.is-primary` |
| `state: secondary` | `.button.is-secondary` |
| `size: large` | `.button.is-large` |

## Sync pipeline (V3)

```
Figma file (Variables + Styles + Components)
  ↓ get_variable_defs, get_design_context (MCP)
figma-contract.json (LLM-produced)
  ↓ validate_figma_extraction.py
  ↓ map_variables.py
webflow-contract.json (LLM-produced)
  ↓ validate + user approval
Webflow Designer (variable_tool, style_tool)
```

The LLM is in-loop for both contracts — schemas + gate scripts constrain the shape.

## Common sync issues

- **Name mismatch**: Figma variable renamed but Webflow variable not. Sync produces orphans.
- **Mode missing**: Figma file added a mode (e.g. dark), Webflow doesn't have it. The mode is dropped silently.
- **Type drift**: Figma variable is `FLOAT` but Webflow expects `COLOR`. Sync fails.
- **Style composition**: Figma style includes a color that's not in the color collection. Style is partially syncible.

## Stable IDs (cross-machine stability)

Every Figma variable has a stable id like `VariableID:abc123def:42`. The V3 pipeline preserves these as `figmaId` in contracts. Display names can drift; IDs can't.

When syncing across machines/people, match by id first, name second.

## Anti-patterns

- Using Figma styles for one-off designs (should be a component).
- Naming variables with display text ("Brand Blue 1") instead of role ("brand/blue").
- Adding Figma Variables for properties Webflow doesn't support — they get silently dropped.
