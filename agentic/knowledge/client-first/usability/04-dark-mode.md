---
_raw_url: https://finsweet.com/client-first/docs/usability/dark-mode
_distilled_at: 2026-06-04
_token_estimate: 800
---

# Finsweet Client-First — Dark Mode

Theme switching via CSS variables. Components reference aliases, not primitives, so dark mode = swap alias values.

## The setup

```css
/* default (light) */
:root {
  --_theme---text-color--primary:    var(--neutral--black);
  --_theme---background--primary:    var(--neutral--white);
  --_theme---background--alternate:  var(--neutral--black);
  --_theme---text-color--alternate:  var(--neutral--white);
}

/* dark mode override */
:root[data-theme="dark"] {
  --_theme---text-color--primary:    var(--neutral--white);
  --_theme---background--primary:    var(--neutral--black);
  --_theme---background--alternate:  var(--neutral--white);
  --_theme---text-color--alternate:  var(--neutral--black);
}
```

Components using `var(--_theme---text-color--primary)` etc. flip automatically.

## Toggling via JS

```js
document.documentElement.dataset.theme = 'dark';  // or 'light'
```

Persist to localStorage. Respect `prefers-color-scheme` for first visit:

```js
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
document.documentElement.dataset.theme = localStorage.getItem('theme')
  ?? (prefersDark ? 'dark' : 'light');
```

## Figma parity (critical for sync)

The Figma file MUST have matching mode variables:

| Mode id (Figma) | Maps to |
|---|---|
| `Mode 1:1` (or `default`) | light theme |
| `Mode 2:1` (or `dark`) | dark theme |

The `figma-design-system-contract` schema requires `modes: { default: ..., dark: ... }`. If the Figma file only has one mode, dark mode doesn't exist in the design system. Add it.

## Component-level dark classes (avoid when possible)

If a component can't rely on aliases (e.g. has a colored background that needs to invert), use a combo:

```css
.card { background: var(--_theme---background--primary); color: var(--_theme---text-color--primary); }
.card.is-inverted { background: var(--_theme---background--alternate); color: var(--_theme---text-color--alternate); }
```

`is-inverted` is a manual dark variant. Used sparingly.

## Images and assets

Photos often need separate dark versions. Two options:

1. Different files: `hero-light.jpg` + `hero-dark.jpg`. Use combo to swap.
2. CSS filter: `filter: brightness(0.85) invert(1) hue-rotate(180deg);` — quick but quality varies.

For brand-critical assets, option 1. For backgrounds, option 2.

## Testing checklist

- All text passes contrast (4.5:1) on both themes.
- Borders, shadows still visible.
- Focus ring color works on both backgrounds.
- Images don't have white halos or unreadable areas in dark.
- Form inputs (placeholder text, autofill) don't go unreadable.

## Anti-patterns

- Hardcoding `color: white` instead of `var(--_theme---text-color--alternate)`. Breaks when theme flips.
- Forgetting to set `color-scheme: light dark` on `<html>` — browser default form controls stay light, look out of place.
- Adding dark mode to a design system that has 0 alias usage. You'll rewrite every component.
