---
_raw_url: null
_distilled_at: 2026-06-04
_token_estimate: 600
---

# Gotcha 06 — Multi-Machine Sync Drift

**The setup**: 5 designers, 3 developers, 1 Webflow project, 1 Figma file. Each person has a local clone of the repo. Each person can run the V3 pipeline.

## Trap

Without enforcement, here's what happens:

1. Designer A renames a Figma variable locally (Figma has no concept of "local rename" — it's global, so this is a real rename visible to all).
2. Designer B's pipeline still has the old name cached. Their contract has both the new variable AND the old one.
3. Developer's pipeline merges both contracts. The Webflow project now has 2 variables where 1 should be.
4. No one notices until the next QA round, when someone asks "why is there a duplicate brand-blue?".

## Detection

The `figma-design-system-contract.schema.json` requires:
- `figmaId` on every variable (catches display-name-based duplicates).
- `modes` keys to be a normalized set (`default`, `dark`, etc., not `Mode 1:1`).
- No two variables in the same contract with the same `figmaId` (catches truly duplicate entries).

A pre-merge check: count distinct `figmaId`s. If less than count of entries, there's a duplicate somewhere.

## Code-level rule

**Stable IDs are the source of truth for sync, not names.** Every entry in every contract carries its `figmaId`. Cross-machine sync uses `figmaId` as the join key.

## Fix

1. **Producer discipline**: every script that produces a contract reads from Figma's API, not from cached files. Stale caches cause drift.
2. **CI check**: before any contract lands in `main`, run `validate_figma_extraction.py` to confirm all `figmaId`s are present, unique, and match the live Figma file.
3. **Webflow side**: each Webflow variable has a sidecar `variable_id_map.json` mapping `webflowVarId → figmaId`. Updates match by `figmaId`, not name.
4. **Drift detector**: a script that reads the current Figma state, the current Webflow state, and the last synced contract, and reports any `figmaId` that's in Figma but not in Webflow (or vice versa). Run on PR.

## What NOT to do

- Don't rely on Figma file timestamps. Multiple machines can write to a Figma file concurrently.
- Don't store contracts in Figma comments or descriptions — they go stale.
- Don't rename variables in production Webflow projects without updating the Figma file. The next sync will create a duplicate.
