---
_raw_url: https://finsweet.com/client-first/docs/concepts/combo-classes
_distilled_at: 2026-06-04
_token_estimate: 600
---

# Finsweet Client-First — Combo Classes

Base class + state/variant class. Period-separated. Used for: state, size, theme, intent.

## Anatomy

```text
.button                      ← base component
.button.is-primary           ← state: visual variant
.button.is-large             ← state: size variant
.button.is-primary.is-large  ← two states stack
```

The base class works on its own (default appearance). The combo adds/modifies.

## Naming rules

- Combo class uses the `is-` prefix.
- Combos describe **state or variant**, not content.
- Always possible to remove a combo without breaking the base.

## Common combo groups

### Color / intent

```text
.is-primary
.is-secondary
.is-tertiary
.is-alternate
```

### Size

```text
.is-small
.is-medium
.is-large
.is-xlarge
```

### State

```text
.is-active
.is-disabled
.is-current
.is-selected
```

### Layout

```text
.is-full-width
.is-centered
.is-stacked
.is-horizontal
```

## Examples

### Button

```css
.button { padding: 0.75rem 1.5rem; background: var(--_theme---background--primary); }
.button.is-primary  { background: var(--brand--blue); color: var(--neutral--white); }
.button.is-secondary{ background: transparent; border: 1px solid var(--_theme---border-color--primary); }
.button.is-large    { padding: 1rem 2rem; font-size: 1.125rem; }
.button.is-disabled { opacity: 0.5; pointer-events: none; }
```

### Card

```css
.card_component { /* base */ }
.card_component.is-featured { border: 2px solid var(--brand--blue); }
.card_component.is-dark     { background: var(--_theme---background--primary); color: var(--_theme---text-color--alternate); }
.card_component.is-horizontal { display: flex; flex-direction: row; }
```

## Anti-patterns

- `is-pricing` (content, not state). Use `.pricing_card` instead.
- `is-blue` (color literal). Use `.is-primary` which maps to `--brand--blue` indirectly.
- Combos that contradict each other: `is-large.is-small`. Pick one.
- Adding the same combo to every instance of a component → just bake it into the base, or split into a new base.

## Stacking order in Webflow Designer

Webflow sorts class list alphabetically. Combo order on the element doesn't matter for cascade (Webflow uses last-applied-wins via Styles panel), but matters for **readability**:

```text
card_component is-featured          ← good: base first
is-featured card_component          ← bad: hard to scan
```
