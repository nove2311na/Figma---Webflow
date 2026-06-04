---
_raw_url: https://finsweet.com/client-first/docs/usability/grids
_distilled_at: 2026-06-04
_token_estimate: 600
---

# Finsweet Client-First — Grids

CSS Grid is the default layout tool. 12-column for complex, repeat(n, 1fr) for simple, auto-fit for responsive.

## Common patterns

### Fixed columns

```css
.grid-2  { display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--size--small); }
.grid-3  { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--size--small); }
.grid-4  { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--size--small); }
.grid-6  { display: grid; grid-template-columns: repeat(6, 1fr); gap: var(--size--small); }
```

Use for: card grids, feature lists, image galleries where items are equal width.

### Auto-fit (responsive collapse)

```css
.grid-auto  { display: grid; grid-template-columns: repeat(auto-fit, minmax(20rem, 1fr)); gap: var(--size--small); }
.grid-auto-large { display: grid; grid-template-columns: repeat(auto-fit, minmax(30rem, 1fr)); gap: var(--size--small); }
```

`minmax(20rem, 1fr)` = "each column is at least 20rem wide, grow to fill". As viewport shrinks, fewer columns fit. On mobile, it collapses to 1 column naturally.

### 12-column (complex layouts)

```css
.grid-12 { display: grid; grid-template-columns: repeat(12, 1fr); gap: var(--size--small); }
.col-span-4 { grid-column: span 4; }   /* 1/3 width */
.col-span-6 { grid-column: span 6; }   /* 1/2 width */
.col-span-8 { grid-column: span 8; }   /* 2/3 width */
.col-span-12{ grid-column: span 12; }  /* full width */
```

Use for: page-level layouts with mixed-width content (sidebar + main, hero with offset image).

## Asymmetric grids

```css
.feature-layout {
  display: grid;
  grid-template-columns: 2fr 1fr;
  gap: var(--size--large);
}
@media (max-width: 767px) {
  .feature-layout { grid-template-columns: 1fr; }
}
```

`2fr 1fr` = "first column takes 2/3 of remaining space, second takes 1/3". Use for: blog post body + sidebar, two-pane hero.

## Grid placement

```css
.hero_image { grid-column: 1 / 3; }     /* span from col 1 to col 3 */
.hero_text  { grid-column: 3 / -1; }    /* span from col 3 to end */
```

Use for: precise positioning when default flow doesn't work.

## Gap vs margin

Grid `gap` is preferred over per-item margins. Less CSS, cleaner collapse, gap doesn't double up at container edges.

## Subgrid (when needed)

```css
.card_grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--size--small); }
.card_component { display: grid; grid-template-rows: subgrid; grid-row: span 3; }
```

Subgrid lets the child inherit the parent's row tracks. Useful for: card grids where the title baseline + body baseline should align across cards.

Browser support: Chrome 117+, Firefox 71+, Safari 16+. Acceptable for most projects in 2026.

## Anti-patterns

- Mixing flex and grid for the same job. Pick one.
- Fixed-pixel column widths: `grid-template-columns: 200px 200px 200px`. Use the scale.
- Grid for 1D layouts (single row of items). Use flex.
- Custom `grid-template-areas` for a 1-off layout. Not worth the complexity.
