---
_raw_url: https://finsweet.com/client-first/docs/overview
_distilled_at: 2026-06-04
_token_estimate: 400
---

# Finsweet Client-First — Overview

Utility + combo + custom class system for Webflow. Goals: consistency, scalability, readability, portability across projects.

## Philosophy

- **One class = one purpose.** No presentational class that does 5 unrelated things.
- **Utility classes for fast iteration** (`is-rounded`, `hide-tablet`).
- **Combo classes for state/variants** (`.button.is-primary`, `.card.is-featured`).
- **Custom classes for one-off components** (`.nav_menu`, `.hero_component`).
- **System scales, not magic numbers** — spacing, sizing, colors all derive from a token set.

## Naming convention (core rule)

Every custom class uses `snake_case` and starts with a project prefix. Finsweet's default example:

```text
.button               ← component
.button.is-primary    ← combo class adds state
.nav_menu             ← component child
.nav_brand             ← grandchild
```

Rules:
- Lowercase only.
- Underscore separates words within a name.
- Period `.` separates combo from base.
- Hyphen `-` separates words inside a single token.
- Numbers allowed (`section-2`, `step-1`) but never start a class.

## What it is NOT

- Not a CSS framework. No JS, no class generation step. You write the CSS in Webflow Designer.
- Not a build tool. The "system" is naming discipline + utility tokens you paste into the project's variables.
- Not a replacement for Webflow's native classes (`w-nav`, `w-button`) — those stay for built-in widgets.

## When to use Client-First

- Project has 5+ pages with repeating patterns.
- Handoff / multi-developer work — naming convention is a contract.
- Design system needs to travel across Webflow projects cleanly.

When NOT to use: 1-page landing, prototype, anything where the convention overhead exceeds the benefit.
