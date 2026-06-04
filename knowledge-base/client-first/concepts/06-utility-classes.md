---
_raw_url: https://finsweet.com/client-first/docs/concepts/utility-classes
_distilled_at: 2026-06-04
_token_estimate: 700
---

# Finsweet Client-First — Utility Classes

Pre-shipped one-job classes from the V2.2 stylesheet. Read-only. Don't redefine.

## Hide / show

```text
.hide                        ← display: none at all breakpoints
.show                        ← display: block (often the default; rarely needed)
.hide-on-mobile              ← only ≤479px
.hide-on-mobile-portrait     ← only ≤479px
.hide-on-mobile-landscape    ← only ≤767px
.hide-on-tablet              ← only ≤991px
.hide-on-tablet-down         ← only ≤991px (same as above)
```

Breakpoints (Webflow defaults):
- mobile-portrait:  ≤ 479px
- mobile-landscape: ≤ 767px
- tablet:           ≤ 991px
- desktop:          ≥ 992px (default)

## Spacing utilities (zeros + directional)

```text
.margin-0
.margin-top
.margin-bottom
.margin-left
.margin-right
.padding-0
.padding-top
.padding-bottom
.padding-left
.padding-right
.gap-0
```

These reset to 0 or align to the spacing scale. Use for component-level overrides, not page-level rhythm.

## Layout helpers

```text
.is-full-width              ← breaks out of container, spans 100vw
.is-relative                ← position: relative
.is-absolute                ← position: absolute (rarely needed; usually parent does)
```

## Display helpers

```text
.is-block
.is-inline-block
.is-flex
.is-inline-flex
.is-grid
.is-hidden                  ← display: none (alias of .hide; deprecated in V2.2)
```

## Z-index scale

The V2.2 library does not ship z-index utilities. Define your own:

```css
:root {
  --z--base: 1;
  --z--dropdown: 10;
  --z--sticky: 100;
  --z--overlay: 1000;
  --z--modal: 10000;
}
```

## Color utilities (alias-driven)

```text
.text-color-primary
.text-color-secondary
.text-color-alternate
.background-color-primary
.background-color-secondary
.background-color-tertiary
.background-color-alternate
.border-color-primary
```

Reference the alias variables from `04-colors.md`. Never hardcode hex in a utility.

## Text utilities

```text
.text-size-tiny
.text-size-small
.text-size-regular
.text-size-medium
.text-size-large
.text-weight-light          ← 300
.text-weight-normal         ← 400
.text-weight-medium         ← 500
.text-weight-semibold       ← 600
.text-weight-bold           ← 700
.text-align-left
.text-align-center
.text-align-right
```

## When NOT to write a utility class

- Single-use styling → custom class.
- Component state → combo class.
- Project-specific layout pattern → custom class.

Utility classes are for cross-component patterns that appear in 3+ places.
