---
_raw_url: https://finsweet.com/client-first/docs/concepts/class-system
_distilled_at: 2026-06-04
_token_estimate: 800
---

# Finsweet Client-First — Class System

Three class types: **utility**, **combo**, **custom**. Each has a strict purpose and naming rule.

## 1. Utility classes

One job. No content-specific meaning. Used directly on any element.

```text
.hide              ← hides element at all breakpoints
.hide-tablet       ← hides only on tablet (≤991px)
.text-color-blue   ← sets color from system palette
.is-rounded        ← border-radius: 4px
.margin-bottom-0   ← removes default margin
```

- Lowercase, hyphen-separated.
- Often paired with breakpoint suffix: `-tablet`, `-mobile-landscape`, `-mobile-portrait`.
- Source: the V2.2 stylesheet (`client-first-v2-2.webflow.css`) ships a fixed utility library. Treat as read-only.

## 2. Combo classes

Add a state/variant to a base component without duplicating CSS.

```text
.button                       ← base
.button.is-primary             ← state: primary
.button.is-secondary           ← state: secondary
.button.is-large               ← state: large
.button.is-primary.is-large    ← both
```

Rules:
- Prefix `is-` for **state** (primary, secondary, large, small, active, disabled).
- Prefix `is-` for **variant** (featured, dark, light, center, full).
- NEVER use `is-` for **content** — `is-blog-post` is wrong; use a custom class like `.blog_post`.
- The base class must work without the combo (no broken default state).

## 3. Custom classes

Project-specific, content-aware. Always underscore-separated, often project-prefixed.

```text
.nav_component
.nav_menu
.nav_brand
.hero_section
.hero_heading
.hero_image
.card_component
.card_image
.card_title
```

Component / child naming:
- `<component>` for the root (e.g. `card_component`).
- `<component>_<child>` for parts (e.g. `card_image`, `card_title`).
- Children of children get nested: `card_meta_author`, `card_meta_date`.

## Class application order in Webflow

In Designer, the "selector" is the full class list. Order in Webflow = cascade order, **not visual order**. First class = lowest priority among ties.

```text
nav navbar_component w-nav          ← correct: combo + utility + native
nav w-nav navbar_component          ← wrong: native overrides your custom
```

Always put your custom + utility classes FIRST, native widget classes LAST.

## Common mistakes

- Using `is-` for content variants (`is-pricing-page`).
- Naming children without the parent (`title` instead of `card_title`) — names collide across components.
- Forgetting the period — `button is-primary` in CSS selector vs `button.is-primary` on the element.
- Treating custom classes as the only option. Many layout jobs are solved by utility classes alone.
