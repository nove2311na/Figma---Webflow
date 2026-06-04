---
_raw_url: https://finsweet.com/client-first/docs/usability/accessibility
_distilled_at: 2026-06-04
_token_estimate: 700
---

# Finsweet Client-First — Accessibility

WCAG 2.1 AA is the floor. Class system doesn't replace semantic HTML, but supports it.

## Semantic HTML first

Class names don't fix bad markup. Use the right tag:

```text
<button>     not <div class="button">
<nav>        not <div class="nav">
<main>       not <div class="main">
<header>     not <div class="header">
<footer>     not <div class="footer">
<article>    for self-contained content
<section>    for thematic groupings WITH a heading
<aside>      for tangentially related content
```

Headings: only one `<h1>` per page. Don't skip levels (`<h1>` → `<h3>` is wrong).

## Focus state

The V2.2 library defines a system focus:

```css
:focus-visible {
  outline: var(--focus--width) solid var(--_theme---system--focus-state);
  outline-offset: var(--focus--offset);
}
```

Tokens:

```css
--focus--width:  .125rem;  /* 2px */
--focus--offset: .125rem;  /* 2px */
```

Never `outline: none` without providing a replacement. The `is-focused` combo class is for non-keyboard focus (autofilled inputs).

## Color contrast

Body text vs background: 4.5:1 minimum. Large text (18px+ or 14px+ bold): 3:1 minimum.

CF V2.2's neutral + brand pairs pass AA. If you customize colors, run them through a contrast checker before shipping.

## Alt text

Every `<img>` needs `alt`. Decorative images get `alt=""` (empty, not missing).

```html
<img src="hero.jpg" alt="Team collaborating around a laptop">
<img src="decorative-divider.svg" alt="">
```

The V2.2 utility `.is-icon` exists for inline SVG icons paired with a sibling label — keep the alt empty and let the label carry meaning.

## Keyboard navigation

- All interactive elements reachable by Tab.
- Tab order = visual order. Don't use `tabindex` to fix order.
- Skip-to-content link at top of page: `<a href="#main" class="skip-link">Skip to content</a>`.

```css
.skip-link {
  position: absolute;
  top: -40px;
  left: 0;
}
.skip-link:focus { top: 0; }
```

## ARIA — use sparingly

ARIA attributes exist to fill gaps in semantic HTML. Most of the time, the right tag is enough.

- `aria-label` only when visible text is misleading or missing (icon-only buttons).
- `aria-expanded` on disclosure widgets (mobile menu toggle).
- `aria-hidden="true"` on purely decorative SVGs.
- `role="navigation"` is redundant on `<nav>`. Skip it.

## Form labels

Every input has a label. Either:

```html
<label for="email">Email</label>
<input id="email" type="email">
```

or visually hidden but still in DOM:

```html
<label for="email" class="is-screenreader-only">Email</label>
<input id="email" type="email">
```

## Anti-patterns

- `<div onclick="...">` instead of `<button>`.
- Removing focus outlines globally.
- `aria-label` repeating the visible text.
- Placeholder text as a label replacement.
