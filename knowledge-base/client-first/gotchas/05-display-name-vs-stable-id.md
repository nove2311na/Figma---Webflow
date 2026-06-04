---
_raw_url: null
_distilled_at: 2026-06-04
_token_estimate: 700
---

# Gotcha 05 — Display Name vs Stable ID

**Display name**: the human-readable string. Designers change these. "Brand Blue" → "Primary Brand" → "Blue-500".

**Stable ID**: a Figma-generated string that never changes for the life of the variable. Format: `VariableID:<32-hex-chars>:<N>`.

## Trap

The V3 pipeline (V3.0) uses display name as the primary key. If a designer renames a Figma variable, the pipeline creates a **new** Webflow variable. The old one is orphaned. After 10 renames, you have 10 Webflow variables for what should be 1.

**Critical for cross-machine / cross-person work**: if I have Figma file A and you have Figma file A on your machine, the display names match (it's the same file), but if either of us makes a local rename, we diverge silently. Stable IDs never diverge.

## Detection

In `figma-contract.json`, every variable entry must have `figmaId`:

```json
{
  "name": "brand/blue",
  "figmaId": "VariableID:abc123def456abc123def456abc12345:1",  ← good
  "value": "#2d62ff"
}
```

If a variable has `name` but no `figmaId`, the pipeline is in display-name-keyed mode. This is fragile.

## Code-level rule (from CLAUDE.md + Q2)

The repo will be worked on by **many people on many machines**. Stable IDs are mandatory. `figmaId` is `required` in `variable-entry.schema.json`. Producer scripts that omit it get rejected by the validation gate.

## Fix

1. In the Figma extraction, always read `id` (the stable id) AND `name`.
2. Store `figmaId` alongside `name` in the contract.
3. In the Webflow write, use `figmaId` as the dedup key. If a Webflow variable already has the same `figmaId` in its metadata, update it; otherwise create.
4. Store `figmaId` in the Webflow variable's description or in a sidecar `variable_id_map.json` (Webflow's API doesn't expose custom metadata on variables yet).
5. Migration: re-extract all current Figma variables, backfill `figmaId` into existing contracts. One-time cost.

## Pattern for stable ID resolution

```python
def resolve_figma_var(webflow_var_metadata: dict, figma_vars: list) -> dict:
    """Find the Figma var that matches this Webflow var by stable id, fallback to name."""
    figma_id = webflow_var_metadata.get("figmaId")
    if figma_id:
        for fv in figma_vars:
            if fv["id"] == figma_id:
                return fv
    # Fallback: name match (risky but better than nothing)
    for fv in figma_vars:
        if fv["name"] == webflow_var_metadata.get("name"):
            return fv
    return None
```
