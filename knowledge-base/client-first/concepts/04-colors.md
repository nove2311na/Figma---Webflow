---
_raw_url: https://finsweet.com/client-first/docs/concepts/colors
_distilled_at: 2026-06-04
_token_estimate: 800
---

# Finsweet Client-First — Colors

Two layers: **primitives** (neutral/brand) and **aliases** (theme/role). Aliases point to primitives. Switching theme = remap aliases, not primitives.

## Primitive scale (neutrals + brand)

```css
--neutral--black:           #000;
--neutral--white:           #fff;
--neutral--neutral-lightest: #eee;
--neutral--neutral-lighter:  #ccc;
--neutral--neutral-light:    #aaa;
--neutral--neutral:          #666;
--neutral--neutral-dark:     #444;
--neutral--neutral-darker:   #222;
--neutral--neutral-darkest:  #111;
--neutral--transparent:      transparent;

--brand--blue:        #2d62ff;
--brand--blue-light:  #d9e5ff;
--brand--blue-dark:   #080331;
--brand--pink:        #dd23bb;
--brand--pink-light:  #ffaefe;
--brand--pink-dark:   #3c043b;
--brand--green:       #cef5ca;
--brand--green-darker:#114e0b;
--brand--yellow:      #fcf8d8;
--brand--yellow-darker:#5e5515;
--brand--red:         #f8e4e4;
--brand--red-darker:  #3b0b0b;
```

## Theme / role aliases (always use these in components)

```css
--_theme---text-color--primary:    var(--neutral--black);
--_theme---text-color--secondary:  var(--neutral--neutral-darker);
--_theme---text-color--alternate:  var(--neutral--white);

--_theme---background--primary:    var(--neutral--black);
--_theme---background--secondary:  var(--brand--blue);
--_theme---background--tertiary:   var(--brand--pink);
--_theme---background--alternate:  var(--neutral--white);

--_theme---border-color--primary:  var(--neutral--neutral-lightest);
--_theme---border-color--secondary:var(--brand--blue);

--_theme---link-color--primary:    var(--brand--blue);
--_theme---link-color--secondary:  var(--neutral--black);
--_theme---link-color--alternate:  var(--neutral--white);
```

Components reference aliases. Switch theme = remap aliases. Components unchanged.

## System status colors

```css
--_theme---system--success-background: var(--brand--green);
--_theme---system--success-text:       var(--brand--green-darker);
--_theme---system--warning-background: var(--brand--yellow);
--_theme---system--warning-text:       var(--brand--yellow-darker);
--_theme---system--error-background:   var(--brand--red);
--_theme---system--error-text:         var(--brand--red-darker);
--_theme---system--focus-state:        var(--brand--blue);
--_theme---system--selection-text:     var(--neutral--white);
--_theme---system--selection-background: var(--brand--blue);
```

## Color utility classes

```text
.text-color-primary
.text-color-secondary
.text-color-alternate
.background-color-primary
.background-color-secondary
.background-color-tertiary
.background-color-alternate
.border-color-primary
```

## Rules

- NEVER hardcode `#2d62ff` in component CSS. Use `var(--brand--blue)` or `var(--_theme---background--secondary)`.
- Never reference primitives directly from components. Always go through aliases.
- Adding a brand color? Add to `--brand--*` AND add the matching `--_theme---*` alias that uses it.
- Dark mode: keep primitives. Create a second alias set (e.g. `--_theme---text-color--primary: var(--neutral--white)`) and swap.
