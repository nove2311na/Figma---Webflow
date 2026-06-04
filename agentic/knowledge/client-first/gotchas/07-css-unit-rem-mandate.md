---
_raw_url: null
_distilled_at: 2026-06-04
_token_estimate: 500
---

# Gotcha 07 — CSS Unit: REM Mandate

**CLAUDE.md rule**: "Always use REM units for spacing, sizes, and typography."

## Trap

Figma returns dimensions in **pixels**. Direct copy-paste to CSS = `font-size: 24px`. Wrong.

Webflow Designer accepts REM input, but the V3 pipeline's auto-generation logic (e.g. `process_html.py` in the architect skill) tends to default to whatever the source uses. Figma = px → output = px. Wrong.

## Detection

In any generated CSS or HTML, grep for non-REM units:

```bash
grep -E '(font-size|margin|padding|width|height|gap|border-radius):\s*[0-9]+(px|em|rem|%|vh|vw)\b' output.css
```

Allow: `rem`, `%` (for widths/heights of containers, not typography), `1px` (for borders, special case).

Disallow in this project: `px` (except 1px borders), `em`, `vh`, `vw`, `pt`.

## Code-level rule

`process_html.py` line ~50 (the unit formatter) **must** convert px → rem via `/16`. Any input in `em`/`vh`/`vw`/`pt` is rejected with a clear error referencing CLAUDE.md.

```python
def format_value(value: float, unit: str) -> str:
    if unit in ("PIXELS", "PX"):
        rem = value / 16
        return f"{rem}rem"
    if unit in ("PERCENT", "REM"):
        return f"{value}{unit.lower()}"
    raise ValueError(f"Unit {unit} not allowed. CLAUDE.md mandates REM for spacing/typography.")
```

## Fix

1. `process_html.py` already does this (Phase 5 of the skill overhaul added the rule).
2. Producer scripts in the V3 pipeline that emit CSS must call `format_value()` from the shared module.
3. Validation gate: `validate_figma_extraction.py` should grep generated CSS for `px` in disallowed contexts. Fail the build.
4. Test: add a unit test that feeds `12` + `PIXELS` and asserts `0.75rem` output.

## Edge case: 1px borders

`1px` is a special case. rem would round to `0.0625rem`, which is fine in modern browsers but feels fragile. CF V2.2's `--_sizes---border-width--thin: 1px` keeps it as px. Document this exception in the producer script.

## Edge case: % for container widths

Container widths like `width: 80%` are fine — they're not spacing or typography. The unit mandate covers spacing/typography, not all CSS. Don't reject %.
