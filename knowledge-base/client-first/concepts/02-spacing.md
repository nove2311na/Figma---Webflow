---
_raw_url: https://finsweet.com/client-first/docs/concepts/spacing
_distilled_at: 2026-06-04
_token_estimate: 700
---

# Finsweet Client-First — Spacing System

12-step scale driven by REM. All spacing (margin, padding, gap) flows from one variable set.

## The scale

| Token | REM | Px (16px root) | Use |
|---|---|---|---|
| `--size--tiny` | 0.125 | 2 | hairline gap |
| `--size--xxsmall` | 0.25 | 4 | icon-to-text |
| `--size--xsmall` | 0.5 | 8 | tight gap |
| `--size--small` | 1 | 16 | default gap |
| `--size--medium` | 2 | 32 | section element gap |
| `--size--large` | 3 | 48 | section inner padding |
| `--size--xlarge` | 4 | 64 | section padding |
| `--size--xxlarge` | 5 | 80 | big section padding |
| `--size--huge` | 6 | 96 | hero section |
| `--size--xhuge` | 8 | 128 | giant section |
| `--size--xxhuge` | 12 | 192 | marketing hero |
| `--size--customhuge` | custom | — | per-project override |

## Section padding (most-used pattern)

Three preset section paddings. Pick one based on visual weight, then never override inline.

```css
.section-spacing { padding-top: var(--size--xlarge); padding-bottom: var(--size--xlarge); }
.section-spacing-medium { padding-top: var(--size--medium); padding-bottom: var(--size--medium); }
.section-spacing-large { padding-top: var(--size--xxhuge); padding-bottom: var(--size--xxhuge); }
```

Apply as a utility class. Done. Don't write `padding: 64px` on individual sections.

## Element gaps (within a section)

`--size--small` (16) is the default gap between sibling elements in a flex/grid. Most projects never override it.

## REM mandate (CLAUDE.md)

- ALL spacing values in generated HTML/CSS must be REM. PX only inside `:root` for the root-font-size declaration.
- Conversion: `px / 16 = rem`. Examples: 16px → 1rem, 32px → 2rem, 48px → 3rem.
- Reject any input in `em`, `vh`, `vw`, `%` for spacing — convert to rem or escalate to user.

## Utility classes from the V2.2 library

```text
.margin-0
.margin-top, .margin-bottom, .margin-left, .margin-right
.padding-0
.padding-top, .padding-bottom, .padding-left, .padding-right
.gap-0
```

Don't use these as a substitute for system tokens. If a value isn't on the scale, decide whether the design is wrong (use the scale) or whether the project needs a new custom token (extend the scale, don't go off-piste).
