---
_raw_url: https://finsweet.com/client-first/docs/usability/rtl
_distilled_at: 2026-06-04
_token_estimate: 500
---

# Finsweet Client-First — RTL Support

Right-to-left languages (Arabic, Hebrew, Persian, Urdu). The class system stays, but directional properties flip.

## `dir="rtl"` on `<html>`

```html
<html lang="ar" dir="rtl">
```

That single attribute triggers CSS to flip for any property that uses logical keywords.

## Logical properties (auto-flip)

Use these instead of `left`/`right`:

```css
/* instead of: */
.card { margin-left: 1rem; padding-right: 0.5rem; }

/* use: */
.card { margin-inline-start: 1rem; padding-inline-end: 0.5rem; }
```

Mapping:
- `margin-left`  → `margin-inline-start`
- `margin-right` → `margin-inline-end`
- `padding-left` → `padding-inline-start`
- `padding-right`→ `padding-inline-end`
- `border-left`  → `border-inline-start`
- `left`         → `inset-inline-start`
- `right`        → `inset-inline-end`
- `text-align: left` → `text-align: start`
- `text-align: right`→ `text-align: end`

In RTL context, `inline-start` = right, `inline-end` = left. Browser handles the flip.

## `text-align` for paragraphs

```css
.body { text-align: start; }  /* left in LTR, right in RTL */
```

## Things that DON'T auto-flip

Some properties are physical and need explicit RTL handling:

- `background-position: left center` — keep as `left` if the image is supposed to be on the reading-start side; the physical `left` is now the trailing side in RTL. Usually you want this to flip. Use logical: `background-position: start center`.
- Icons that point (arrows, chevrons) — flip them with `transform: scaleX(-1)` in RTL.
- Decorative borders that mark "leading edge" — use `border-inline-start`.
- Animation directions (sliding in from "right") — use `translate(inline-end)` not `translateX(100%)`.

## Class names do NOT change

The class system stays. `.card.is-featured` is the same in both directions. Only the *implementation* of those classes flips via logical properties.

## Font + typography

- Latin fonts don't render Arabic/Hebrew well. Use a proper Arabic font family:
  ```css
  :root[lang="ar"] { --font-family--body: "IBM Plex Sans Arabic", system-ui; }
  ```
- Letter-spacing often needs `0` or slightly negative for Arabic; English default 0 stays.
- Line-height: Arabic often reads better at 1.7–1.8 (vs 1.5 for English).

## Testing

- Chrome DevTools → Rendering → Directionality → "rtl". Reload, eyeball.
- Native speakers for content QA — automated translation misses cultural issues.
- Don't ship RTL without a native reviewer.

## Anti-patterns

- Hardcoding `left: 0` for a sidebar that should be on the "start" side.
- Forgetting to flip chevron icons (they now point the wrong way).
- Assuming the layout grid collapses the same way. RTL grids are fine; verify the column order matches reading direction.
