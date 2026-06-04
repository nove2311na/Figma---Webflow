---
_raw_url: https://finsweet.com/client-first/docs/concepts/sizing
_distilled_at: 2026-06-04
_token_estimate: 600
---

# Finsweet Client-First — Sizing

Width/height tokens for containers, max-width, icon sizes, borders. All REM.

## Container widths

```css
--_sizes---container--small:  48rem;   /* 768px  */
--_sizes---container--medium: 64rem;   /* 1024px */
--_sizes---container--large:  80rem;   /* 1280px */
```

`container-large` is the default page wrapper. `container-medium` for narrow content (blog post body, forms). `container-small` for compact UI panels.

## Max-width scale

```css
--_sizes---max-width--xxsmall: 12rem;
--_sizes---max-width--xsmall:  16rem;
--_sizes---max-width--small:   20rem;
--_sizes---max-width--medium:  32rem;
--_sizes---max-width--large:   48rem;
--_sizes---max-width--xlarge:  64rem;
--_sizes---max-width--xxlarge: 80rem;
```

## Container utility classes (from V2.2)

```text
.container-small
.container-medium
.container-large
```

Pattern:

```html
<section class="section">
  <div class="container-large">
    <!-- page content -->
  </div>
</section>
```

`section` gives the vertical padding. `container-large` caps the width + centers.

## Border radius

```css
--_sizes---border-radius--small:  .25rem;
--_sizes---border-radius--medium: .5rem;
--_sizes---border-radius--large:  1rem;
```

Utility classes:

```text
.is-rounded-small
.is-rounded-medium
.is-rounded-large
```

## Border width

```css
--_sizes---border-width--thin:   1px;   /* base border */
--_sizes---border-width--normal: .125rem; /* 2px */
--_sizes---border-width--bold:   .25rem;  /* 4px */
```

The 1px value is a special case (sub-pixel) — it does NOT become rem. Keep as `1px` because rem rounding at 0.0625 rem is fragile.

## Grid columns

```css
--_layout---grid-columns--default-count: 8;
--_layout---grid-columns--xsmall: 15rem;
--_layout---grid-columns--small:  20rem;
--_layout---grid-columns--medium: 25rem;
--_layout---grid-columns--large:  30rem;
--_layout---grid-columns--xlarge: 35rem;
--_layout---grid-columns--xxlarge:40rem;
```

`--default-count` is the implicit column count for `grid-template-columns`. The other tokens define the min-width per column for `repeat(auto-fit, minmax(20rem, 1fr))`-style responsive grids.

## Anti-patterns

- Hardcoding `width: 1200px` on a wrapper. Use `container-large` or `--_sizes---container--large`.
- Mixing `max-width` and `width` on the same element. Pick one.
- Border-radius as `9999px` for "pill" shapes — use `--_sizes---border-radius--large` or define a new pill token.
