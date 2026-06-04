---
_raw_url: null
_distilled_at: 2026-06-04
_token_estimate: 800
---

# Gotcha 01 — Variable Modes: Figma ↔ Webflow

**Figma side**: every color variable has 1+ modes (`Mode 1:1` = default/light, `Mode 2:1` = dark, etc.). Stored as `valuesByMode: { "Mode 1:1": "#000", "Mode 2:1": "#fff" }`.

**Webflow side**: variables also have modes. Both support it. The mismatch is in **shape**, not capability.

## Trap

Figma MCP `get_variable_defs` returns modes with raw keys like `Mode 1:1`. The V3 pipeline flattens this to `{ default: ..., dark: ... }` via a hardcoded mapping. If a Figma file uses non-default mode names (`high-contrast`, `print`, `compact`), the flattening silently loses them.

## Detection

```python
# In figma-contract.json, look for:
"modes": { "Mode 1:1": "...", "Mode 2:1": "..." }   ← bad: raw Figma mode ids leaked
"modes": { "default": "...", "dark": "..." }       ← good: normalized
```

## Fix

The pipeline must:
1. Read the Figma file's mode list first (via `get_local_variables` or `get_variable_defs`).
2. Build a mode-id → human-name map (default, dark, rtl, high-contrast, etc.).
3. Apply that map when constructing `modes: {}` in the contract.
4. Reject contracts where `modes` keys contain `Mode N:M` patterns.

## Code-level rule (Figma→Webflow)

If Webflow has a mode called `dark`, Figma MUST have a mode called `dark` (or whatever Webflow calls it). The V3 contract schema requires `modes` to be a complete superset of Webflow's mode set.

## User implication

**Whatever vars + modes Webflow supports, Figma must mirror.** Don't add a Figma mode Webflow doesn't have (it gets dropped on sync). Don't add a Webflow mode Figma doesn't have (it shows as undefined in dark/light toggle).
