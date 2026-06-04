---
_raw_url: https://finsweet.com/client-first/docs/components
_distilled_at: 2026-06-04
_token_estimate: 600
---

# Finsweet Client-First — Components

Reusable UI blocks. Webflow Symbol/Component + Figma Component. Built from utility + combo + custom classes.

## Component anatomy

```text
<component>          ← root wrapper (e.g. .card_component)
  <child>            ← structural child (e.g. .card_image)
  <child>
    <grandchild>     ← nested (e.g. .card_meta_author)
```

The CF naming convention:

```text
.card_component          ← root
.card_image              ← child of root
.card_body               ← child of root
.card_title              ← child of root
.card_meta               ← child of root
.card_meta_author        ← grandchild
.card_meta_date          ← grandchild
.card_cta                ← call-to-action child
```

Children of children always include parent name. Names must be unique across the project to avoid style collisions.

## When to make a component

- Used in 3+ places.
- Has variants (state, size, theme).
- Has internal structure that should stay consistent.
- Will be updated across many pages at once.

When NOT to make a component:
- Used once. Just write the HTML.
- Internal structure varies wildly per instance. Use a section + utilities.

## Component property → combo class

Webflow Component Property = Figma Variant Property = CF Combo Class.

| Property | Webflow class | Use case |
|---|---|---|
| `intent: primary` | `.is-primary` | button color |
| `intent: secondary` | `.is-secondary` | button color |
| `size: small` | `.is-small` | button size |
| `size: large` | `.is-large` | button size |
| `theme: dark` | `.is-inverted` | card theme |
| `theme: light` | (no class) | default |

The base class always works without the combo. The combo is a strict addition.

## Slots (CF doesn't have a formal slot concept)

CF doesn't have a "slot" primitive like Webflow Slots. Instead:

- Use a child class as the slot name: `.card_body` is the "body slot".
- The component consumer fills the child class with whatever content fits.
- Multiple slots = multiple children: `.card_image`, `.card_title`, `.card_cta`.

This works because the class names are predictable, so consumers can target them with custom CSS if needed.

## Nested components

A Button inside a Card uses the same Button class:

```html
<article class="card_component">
  <h3 class="card_title">Title</h3>
  <a class="button is-primary" href="...">Read more</a>
</article>
```

The Button is a separate Webflow Component, instanced inside the Card. No special nesting class.

## Variants vs separate components

If a thing has 1-2 visual variants → use a component with combo classes.
If a thing has fundamentally different internals → make it 2 components.

Example: Card (1 component, combos for is-featured, is-horizontal, is-dark).
Example: PricingCard vs BlogCard (2 components, different internals).

## State (hover, focus, active)

CF doesn't ship hover/focus as utility classes. State styling goes in the base class:

```css
.button { background: var(--_theme---background--primary); transition: background 150ms; }
.button:hover { background: var(--_theme---background--secondary); }
.button:focus-visible { outline: var(--focus--width) solid var(--_theme---system--focus-state); }
```

Combos describe persistent state (primary, large, dark). Pseudo-classes (`:hover`, `:focus`) describe transient state. Different concerns, different layers.

## Anti-patterns

- Components with 10+ variant properties. Split into 2 components.
- Deeply nested children: `.card_body_meta_author_avatar`. Cap at 2 levels.
- Component + same class on a child. Either the child is part of the component (no extra class) or it's a separate concern.
- Forgetting to test the component without its combos. Base should always work standalone.
