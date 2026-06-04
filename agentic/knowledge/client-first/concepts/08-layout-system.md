---
_raw_url: https://finsweet.com/client-first/docs/concepts/layout-system
_distilled_at: 2026-06-04
_token_estimate: 800
---

# Finsweet Client-First — Layout System

The page is built from: `section` > `container` > `grid` > component. Each level has a fixed job.

## The 4 levels

```text
section          ← vertical rhythm, full-width background
  container      ← horizontal cap, max-width
    grid         ← 2D layout, gap from scale
      component  ← the actual UI (card, button, hero)
```

## 1. `section`

Full-width, vertical padding. Sets the page rhythm.

```css
.section              { padding-top: var(--size--xlarge); padding-bottom: var(--size--xlarge); }
.section.is-small     { padding-top: var(--size--medium); padding-bottom: var(--size--medium); }
.section.is-large     { padding-top: var(--size--xxhuge);  padding-bottom: var(--size--xxhuge); }
```

Almost every page section uses `.section` + a container. The combo `.is-small` / `.is-large` swaps padding without rewriting the section.

## 2. `container`

Caps the width and centers. Always inside a section.

```css
.container-small  { max-width: 48rem;  margin: 0 auto; padding-left: var(--size--small); padding-right: var(--size--small); }
.container-medium { max-width: 64rem;  margin: 0 auto; padding-left: var(--size--small); padding-right: var(--size--small); }
.container-large  { max-width: 80rem;  margin: 0 auto; padding-left: var(--size--small); padding-right: var(--size--small); }
```

The horizontal padding (`--size--small`) is intentional — gives breathing room on mobile where the viewport is narrower than `container-large`.

## 3. `grid`

CSS grid with responsive auto-fit columns. Default uses the system grid column tokens.

```css
.grid-3 { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--size--small); }
.grid-2 { display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--size--small); }
.grid-auto { display: grid; grid-template-columns: repeat(auto-fit, minmax(20rem, 1fr)); gap: var(--size--small); }
```

Common patterns:

```text
.grid-2
.grid-3
.grid-4
.grid-auto            ← responsive collapse to 1 col on small screens
```

Responsive collapse happens via media queries:

```css
@media (max-width: 991px) {
  .grid-3, .grid-4 { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 767px) {
  .grid-2, .grid-3, .grid-4 { grid-template-columns: 1fr; }
}
```

## 4. Component

The actual card, button, hero, etc. Always uses custom + combo + utility classes per `01-class-system.md`.

## Full page skeleton

```html
<section class="section is-large background-color-primary">
  <div class="container-large">
    <h2 class="heading-large text-color-alternate">Section title</h2>
    <p class="text-size-medium text-color-alternate">Body copy.</p>
    <div class="grid-3 margin-top-medium">
      <div class="card_component is-featured">...</div>
      <div class="card_component">...</div>
      <div class="card_component">...</div>
    </div>
  </div>
</section>
```

## Anti-patterns

- Using `flex` for a 2D layout. Use `grid`.
- Inline `style="display:grid; grid-template-columns: 1fr 1fr"` — that's what utility classes are for.
- Skipping `container-` and writing a custom `max-width`. Use the system.
- Nesting sections without a container inside.
