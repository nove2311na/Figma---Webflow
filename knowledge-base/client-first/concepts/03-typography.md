---
_raw_url: https://finsweet.com/client-first/docs/concepts/typography
_distilled_at: 2026-06-04
_token_estimate: 900
---

# Finsweet Client-First — Typography

Tokenized type scale: 1 family for body, 1 for headings, named size + line-height + letter-spacing tokens. All values in REM.

## Token set

| Token | Default | Purpose |
|---|---|---|
| `--font-family--body` | system-ui stack | `<p>`, `<li>`, `<a>` |
| `--font-family--heading` | inherits body OR custom | `<h1>`–`<h6>` |
| `--_typography---body--body-font-size` | 1rem | default body text |
| `--_typography---body--body-line-height` | 1.5 | body line-height |
| `--_typography---body--body-letter-spacing` | 0 | body letter-spacing |
| `--_typography---h1--h1-font-size` | 4rem | h1 |
| `--_typography---h1--h1-line-height` | 1.1 | h1 line-height |
| `--_typography---h1--h1-font-weight` | 700 | h1 weight |
| `--_typography---h1--h1-letter-spacing` | 0 | h1 letter-spacing |
| ... | ... | one row per h2/h3/h4/h5/h6 |

Pattern: every heading has 4 tokens (size, line-height, weight, letter-spacing). Never hardcode.

## Heading class system (CF V2.2 ships these)

```text
.heading-xlarge   ← h1
.heading-large    ← h2
.heading-medium   ← h3
.heading-small    ← h4
.heading-tiny     ← h5, h6
```

- `heading-xlarge` → 4rem / 1.1 / 700
- `heading-large`  → 3rem / 1.2 / 700
- `heading-medium` → 2rem / 1.3 / 700
- `heading-small`  → 1.5rem / 1.4 / 700

`<h1>` through `<h6>` are styled by element selector. Apply `.heading-xlarge` etc. to align visual weight with semantic level.

## Text utility classes

```text
.text-size-tiny       ← 0.75rem
.text-size-small      ← 0.875rem
.text-size-regular    ← 1rem
.text-size-medium     ← 1.25rem
.text-size-large      ← 1.5rem

.text-color-primary   ← var(--neutral--black)
.text-color-secondary ← var(--neutral--neutral-dark)
.text-color-alternate ← var(--neutral--white)
.text-weight-bold     ← 700
.text-weight-medium   ← 500
```

## Text alignment

```text
.text-align-left
.text-align-center
.text-align-right
```

## Anti-patterns

- Hardcoding `font-size: 24px` on a heading — break the scale, lose responsiveness.
- Skipping heading levels for visual size (`<h4>` styled to look like h1). Bad for SEO + a11y.
- Mixing 3 different font families. System says 2 max (body + heading).
- Using `<br>` for paragraph spacing. Use `padding` or `margin` from the scale.
