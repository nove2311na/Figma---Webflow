---
_raw_url: null
_distilled_at: 2026-06-04
_token_estimate: 700
---

# Gotcha 03 — Alias Chains

**CSS reality**: variables can reference other variables. The user's Webflow CSS shows:
```css
--_theme---text-color--primary: var(--neutral--black);
--_theme---background--primary: var(--neutral--white);
--_theme---background--secondary: var(--brand--blue);
```

This is a 2-level alias: theme → primitive. Can go deeper: `--_theme---background--success: var(--_theme---system--success-background)` → `var(--brand--green)`.

## Trap

The V3 pipeline's `map_variables.py` does a 1:1 name → Webflow variable mapping. Alias chains are **not preserved** unless the pipeline understands them.

Worse: the Webflow side has a hard limit on alias depth (max 5 levels). Figma has no such limit. A 6-level Figma alias chain creates a Webflow variable that references a deleted var → undefined.

## Detection

In `webflow-contract.json`, check for `aliasOf` field:

```json
{
  "figmaId": "VariableID:abc:1",
  "name": "_theme---text-color--primary",
  "type": "color",
  "value": "#000",
  "modes": { "default": "#000", "dark": "#fff" },
  "aliasOf": "VariableID:def:42"
}
```

If `aliasOf` is present, the Webflow variable is a reference. Missing `aliasOf` for a variable that should be a reference = bug.

## Code-level rule

The `variable-entry.schema.json` requires `aliasOf` for any variable of `type: "alias"`. The producer scripts must populate it for every aliased variable.

## Fix

1. In the Figma extraction, walk the alias tree (BFS or DFS) starting from each leaf.
2. Record `aliasOf` = parent variable's `figmaId`.
3. Mark `type: "alias"` for any variable that has no concrete value of its own.
4. Reject aliases with depth > 5 (Webflow's limit).
5. For the Webflow write, use the `variable_tool.create` with `isAlias: true` and `aliasTo: <parent_id>`.
