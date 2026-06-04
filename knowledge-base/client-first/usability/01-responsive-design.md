---
_raw_url: https://finsweet.com/client-first/docs/usability/responsive-design
_distilled_at: 2026-06-04
_token_estimate: 900
---

# Finsweet Client-First — Responsive Design

Mobile-first. Three breakpoints. Element-level overrides via media queries, not per-page CSS.

## Breakpoint system

| Name | Max-width | Trigger |
|---|---|---|
| mobile-portrait  | 479px  | phones (portrait) |
| mobile-landscape | 767px  | phones (landscape), small tablets |
| tablet           | 991px  | tablets, small laptops |
| desktop          | 992px+ | default styles target this |

Base styles target desktop. Mobile/tablet overrides come via media queries using `max-width`.

## Mobile-first vs desktop-first

CF V2.2 is **desktop-first** by default (the stylesheet assumes desktop, then steps down). For new projects, prefer mobile-first because it forces a content-first mindset:

```css
/* base = mobile */
.card { padding: var(--size--small); }

@media (min-width: 768px) {
  /* tablet+ */
  .card { padding: var(--size--medium); }
}

@media (min-width: 992px) {
  /* desktop+ */
  .card { padding: var(--size--large); }
}
```

If using V2.2's desktop-first classes, just stick with that convention.

## Hide-on-breakpoint utilities

```text
.hide-on-mobile              ← ≤ 479px
.hide-on-mobile-portrait     ← ≤ 479px
.hide-on-mobile-landscape    ← ≤ 767px
.hide-on-tablet              ← ≤ 991px
```

Use for: nav collapse (mobile menu replaces desktop nav), decorative sidebars that don't fit small screens, large hero images replaced with smaller versions on mobile.

## Grid collapse pattern

Most grids go: 4 cols → 2 cols → 1 col as viewport shrinks.

```css
.grid-4 {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: var(--size--small);
}
@media (max-width: 991px) { .grid-4 { grid-template-columns: repeat(2, 1fr); } }
@media (max-width: 479px) { .grid-4 { grid-template-columns: 1fr; } }
```

`grid-auto` does this automatically: `repeat(auto-fit, minmax(20rem, 1fr))`. Use it when each card can be a different width.

## Typography scaling

Headings don't shrink 1:1 with viewport — they have a min and max. Use `clamp()`:

```css
.heading-xlarge {
  font-size: clamp(2.5rem, 5vw, 4rem);
  line-height: 1.1;
}
```

`clamp(min, preferred, max)`. The `preferred` adapts to viewport; min and max prevent extreme values.

## Container padding on mobile

Containers keep their max-width but lose the side padding reduction:

```css
@media (max-width: 479px) {
  .container-large { padding-left: var(--size--small); padding-right: var(--size--small); }
}
```

This prevents content from touching the screen edge.

## Anti-patterns

- Hiding content on mobile that should still be there (use a different layout instead).
- Setting `font-size: 16px` on mobile `<html>` to "lock" the size. Bad a11y — users with vision issues can't zoom.
- Multiple breakpoints per project. Stick to 3 (mobile, tablet, desktop).
- Targeting devices (`@media (max-width: 768px)` for "iPad") — use viewport ranges, not device names.
