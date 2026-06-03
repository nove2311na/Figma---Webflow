# Prompt: Write HTML Contract from Figma Blueprint

## Purpose

Guide LLM to produce the `html_contract` per section and the `new_classes` list in
`workspace/blueprints/*.json`. The HTML contract is the **naming authority** — all Client-First
class names are decided HERE, once, serially. Subagents in Phase 2B never invent new names.

Run AFTER:
1. Figma data is in `workspace/rawdata/` and `workspace/contents/`.
2. Per-project CF library loaded: `knowledge-base/libraries/{site_id}/client-first-library.json`.
3. Global CF class map read: `knowledge-base/client-first-class-map.json`.

---

## The Core Question You Must Answer for Every Element

> "Does a Client-First class already exist that does exactly this job?"

If YES → **use it, never recreate it.**
If NO → **name a new custom class using `component_element` underscore convention** and add it to `new_classes`.

Getting this wrong is the #1 mistake. Over-creating classes creates bloat. Under-creating (forcing utilities to do component work) creates fragile, unmaintainable builds.

---

## Layer 1: Always Use These — Never Create Replacements

These six structural classes are **mandatory** on every page. They are predefined CF globals. Never invent alternatives.

| HTML tag | CF class | CSS job | Never replace with |
|---|---|---|---|
| `<div>` | `page-wrapper` | outermost page container | anything else |
| `<main>` | `main-wrapper` | wraps all content (not nav/footer) | `<div class="main">` |
| `<section>` | `section_[section-id]` | section band with anchor ID | `<div class="hero">` |
| `<div>` | `padding-global` | left/right horizontal gutters only | custom padding divs |
| `<div>` | `container-large` / `container-medium` / `container-small` | max-width centering | hardcoded width classes |
| `<div>` | `padding-section-small` / `padding-section-medium` / `padding-section-large` | top/bottom vertical rhythm | custom top/bottom padding |

**Rule:** `padding-global` wraps `container-*`. `container-*` wraps content. Nesting order is fixed.

```html
<!-- CORRECT structural skeleton -->
<div class="page-wrapper">
  <main class="main-wrapper">
    <section class="section_hero">
      <div class="padding-global">
        <div class="container-large">
          <div class="padding-section-large">
            <!-- content here -->
          </div>
        </div>
      </div>
    </section>
  </main>
</div>
```

**Section styling note:** Do not put visual styles (background color, text color) directly on `section_[name]`. For section-level visual variants, use a combo add-on class on the same section element:

```html
<!-- CORRECT: structural class + style variant combo -->
<section class="section_pricing section-style-dark">

<!-- WRONG: visual styles on structural class -->
<section class="section_pricing">  <!-- with background-color set on section_pricing itself -->
```

`section-style-dark`, `section-style-brand` — these global style combos let you toggle section appearance without overriding the structural class.

---

## Layer 2: Existing Utility Classes — Check Before Creating

These cover **single-purpose, globally reusable CSS properties**. If a Figma property maps cleanly to one of these, use it. No underscore = utility class = no custom equivalent needed.

### Typography utilities (text deviating from default HTML tag style)

| Property needed | Use this class |
|---|---|
| Visual h1 on a non-h1 element | `heading-style-h1` |
| Visual h2 | `heading-style-h2` |
| Visual h3 | `heading-style-h3` |
| Visual h4 | `heading-style-h4` |
| Visual h5 | `heading-style-h5` |
| Visual h6 | `heading-style-h6` |
| Large body text | `text-size-large` |
| Medium body text | `text-size-medium` |
| Regular / body text (default) | `text-size-regular` |
| Small text | `text-size-small` |
| Tiny / caption text | `text-size-tiny` |
| All caps | `text-style-allcaps` |
| Italic | `text-style-italic` |
| Muted / subdued | `text-style-muted` |
| Strikethrough | `text-style-strikethrough` |
| No-wrap | `text-style-nowrap` |
| 1-line truncation | `text-style-1line` |
| 2-line truncation | `text-style-2lines` |
| 3-line truncation | `text-style-3lines` |
| Balanced line breaks | `text-style-balance` |
| Orphan-free wrapping | `text-style-pretty` |
| Bold | `text-weight-bold` |
| Semibold | `text-weight-semibold` |
| Medium weight | `text-weight-medium` |
| Extra bold | `text-weight-xbold` |
| Normal weight | `text-weight-normal` |
| Light weight | `text-weight-light` |
| Left align | `text-align-left` |
| Center align | `text-align-center` |
| Right align | `text-align-right` |
| Link-styled text | `text-style-link` |
| Pull quote / blockquote | `text-style-quote` |

**Note:** `text-size-huge` does NOT exist in CF V2.2. The size scale is: tiny / small / regular / medium / large.

### Color utilities (from per-project library)

Colors in the per-project library (`client-first-library.json`) already have three classes each:

| Figma color token | Apply this class for | Class name |
|---|---|---|
| any color token | text color | `text-color-[token-name]` |
| any color token | background | `background-color-[token-name]` |
| any color token | border | `border-color-[token-name]` |

**Example:** Figma token `colors/brand/Primary` → classes `text-color-primary`, `background-color-primary`, `border-color-primary`. All three are already in the library.

### Display / visibility utilities

| Need | Use this class |
|---|---|
| Hide on all screens | `hide` |
| Hide on tablet | `hide-tablet` |
| Hide on mobile landscape | `hide-mobile-landscape` |
| Hide on mobile portrait | `hide-mobile-portrait` |
| Inline flex behavior | `display-inlineflex` |

### Inherit utilities (override stacked color/size/weight)

| Need | Use this class |
|---|---|
| Text color inherits from parent | `inherit-text-color` |
| Font weight inherits | `inherit-text-weight` |
| Font size inherits | `inherit-text-size` |
| Text decoration inherits | `inherit-text-decoration` |
| Border radius inherits | `inherit-border-radius` |

### Button base (always a starting base)

| Need | Use this class |
|---|---|
| Primary button | `button` |
| Secondary button variant | `button is-secondary` |
| Text link button variant | `button is-text` |

**CF V2.2 only ships `is-secondary` and `is-text` as button combos.** Do not use `is-brand` or `is-outline` — these are not CF V2.2 defaults. Any additional variant must be declared in `new_classes` with Case 5.

### Max-width utilities (constrain readable line length)

| Need | Use this class |
|---|---|
| Constrain content width inside container | `max-width-[xxlarge\|xlarge\|large\|medium\|small\|xsmall\|xxsmall]` |
| Full width at tablet | `max-width-full-tablet` |
| Full width at mobile landscape | `max-width-full-mobile-landscape` |
| Full width at mobile portrait | `max-width-full-mobile-portrait` |

### Icon sizing

| Need | Use this class |
|---|---|
| Icon with height only (variable width) | `icon-height-[small\|medium\|large]` |
| Square icon (equal w+h) | `icon-1x1-[small\|medium\|large]` |

### Advanced layout / decoration utilities

| Need | Use this class |
|---|---|
| Hide overflow (image crop, mask) | `overflow-hidden` |
| Scrollable container | `overflow-scroll` / `overflow-auto` |
| Square 1:1 aspect ratio | `aspect-ratio-square` |
| Portrait 2:3 aspect ratio | `aspect-ratio-portrait` |
| Landscape 3:2 aspect ratio | `aspect-ratio-landscape` |
| Widescreen 16:9 aspect ratio | `aspect-ratio-widescreen` |
| Full-cover absolute layer | `layer` |

**Note: all `aspect-ratio-*` classes include `object-fit:cover` — no separate object-fit class needed for images. Real ratios: portrait=2/3, landscape=3/2 (not 3/4 or 4/3).**
| Inline flex (badge/tag chip) | `display-inlineflex` |
| z-index 1 | `z-index-1` |
| z-index 2 | `z-index-2` |
| Disable pointer events | `pointer-events-none` |
| Restore pointer events | `pointer-events-auto` |
| Reset all margin and padding | `spacing-clean` |

### Spacer (dedicated vertical gap element)

| Need | Use this class |
|---|---|
| Vertical space between siblings | `spacer-[tiny\|small\|medium\|large\|huge]` |

Use a plain `<div class="spacer-medium">` as a dedicated spacer div. Do NOT apply margin directly on content elements for sibling spacing — use a spacer div or spacing wrapper instead.

### Spacing utilities (for small adjustments only)

Use margin/padding direction utilities as **modifier wrappers** for standardized spacer amounts.
Form: `margin-[direction]` + `margin-[size]` (applied together on a wrapper div).

⚠️ Do NOT use these for complex component-level spacing — create a custom class instead (see below).

**Spacing wrapper pattern (preferred for component spacing):**

Wrap the child element in a `<div>` and apply spacing utilities to the wrapper — not to the content element itself.

Use this pattern when:
- Element is inside a Webflow Symbol/component (instance-specific spacing)
- Element is a CSS Grid child where gap utility does not apply
- You need different spacing on one instance without affecting all others

```html
<!-- CORRECT: wrapper owns spacing -->
<div class="margin-bottom margin-medium">
  <p class="text-size-regular">Paragraph text</p>
</div>

<!-- WRONG: margin applied to content element directly -->
<p class="text-size-regular margin-bottom margin-medium">Paragraph text</p>
```

---

## Layer 3: When to Create a NEW Custom Class

Create a new custom class when **none of the above covers the need**. Custom classes use `_` (underscore) to separate component from element.

### Naming convention

```
[component-name]_[element-name]
```

- `component-name`: the section or component this belongs to. Slugify, lowercase, no underscores.
- `element-name`: the element's role within the component. Slugify, lowercase, dashes allowed.

**Component wrapper = `[name]_component`; children = `[name]_[el]`; nested = `[a]_[b]_[el]`. The `_component` suffix signals this is the outermost wrapper of a reusable component.**

Examples:
| Element | New class name |
|---|---|
| Nav outermost wrapper | `nav_component` |
| Nav brand/logo child | `nav_brand` |
| Nav menu link (nested) | `nav_menu_link` |
| Hero section background layer | `hero_background-layer` |
| Nav bar link item | `navbar_link` |
| Pricing card wrapper | `pricing-card_component` |
| Pricing card CTA area | `pricing-card_cta-wrapper` |
| Team member photo | `team_headshot` |
| Footer copyright text | `footer_copyright` |

**Prefix strategy — global vs page-specific:**
- Element shared across multiple pages → generic prefix only: `card_wrapper`, `faq_item`, `nav_link`
- Element only on one specific page → add page slug prefix: `home_hero-text`, `about_team-grid`
- Never apply a page-prefixed class (`home_*`, `about_*`) to elements on other pages.

### The 5 mandatory cases for NEW custom class

#### CASE 1 — Layout (flex/grid/positioning)
**CF never provides layout utility classes.** Any flex container, grid, positioning, or size constraint = custom class.

```
ALWAYS create new:
  hero_content-grid       ← flex/grid layout
  hero_text-block         ← width/sizing within layout
  navbar_inner-wrapper    ← flex between logo and links
  feature_icon-wrapper    ← sized icon container
```

#### CASE 2 — Unique visual treatment not covered by tokens
Decorative backgrounds, gradients, shadows, borders, clip-paths, custom radii NOT in the token library.

```
ALWAYS create new:
  hero_gradient-bg        ← unique gradient
  card_shadow-layer       ← box-shadow not in library
  section_divider-line    ← decorative border
```

#### CASE 3 — Recurring component elements (managed as a group)
When the same styled element appears 4+ times inside a component (e.g., every `li` in a feature list), create ONE custom class so all instances update together.

```
ALWAYS create new:
  feature-list_item       ← used on every <li> in the feature list
  nav_menu-link           ← every link in the nav
  footer_column-heading   ← every column header in footer
```

#### CASE 4 — Component-specific responsive overrides
When the element needs different spacing/layout/sizing at tablet or mobile that conflicts with the global utility value at that breakpoint.

```
ALWAYS create new:
  hero_text-block         ← needs width:100% at mobile but 50% at desktop
```

#### CASE 5 — Combo class variant
When a component has 2+ visual variants of the same base element, use a base custom class + `is-[variant]` combo.

```
Base:    button
Combo:   button is-secondary  ← CF V2.2 shipped secondary variant
Combo:   button is-text       ← CF V2.2 shipped text/link variant
Combo:   button is-ghost      ← custom variant (not CF default — declare in new_classes)
```

**CF V2.2 only ships `is-secondary` and `is-text` as button combos. `is-brand` and `is-outline` are NOT in CF V2.2 — any such variant must be declared as a new combo class.**

`is-` prefix classes are always combos — never standalone.

---

## Layer 4: Decision Flowchart

```
For EACH element in the Figma design:

1. Is it a STRUCTURAL wrapper (page, main, section, padding, container)?
   YES → Use mandatory Layer 1 class. STOP.

2. Does it need a TYPOGRAPHY style change from HTML default?
   YES → Pick from Layer 2 typography utilities. STOP.
       → Need multiple utilities? Stack max 3. Beyond 3 = custom class.

3. Does it need a COLOR from the project token library?
   YES → Use `text-color-*` / `background-color-*` / `border-color-*` from library. STOP.

4. Is it a BUTTON?
   YES → Start with `button`. Add `is-[variant]` combo only if variant exists. STOP.

5. Is it SHOW/HIDE responsive behavior only?
   YES → Use `hide-*` utility. STOP.

6. Does it need LAYOUT (flex, grid, columns, positioning, sizing)?
   YES → Create NEW custom class `[component]_[element]`. Add to new_classes.

7. Does it have UNIQUE VISUAL treatment (gradient, shadow, special border, custom radius)?
   YES → Create NEW custom class. Add to new_classes.

8. Is it a RECURRING element within a component (same style, 4+ instances)?
   YES → Create ONE custom class shared by all instances. Add to new_classes.

9. Does it need BREAKPOINT OVERRIDES that conflict with the global utility?
   YES → Create NEW custom class with breakpoint styles. Add to new_classes.

10. Does it have COMPONENT-SPECIFIC SPACING (not standard section padding)?
    YES → Create NEW custom class. Add to new_classes.
```

---

## Layer 5: Hard Rules (Never Break)

### Maximum stacking
Never stack more than **4 classes on one element** — 4 is the absolute CF maximum.
1–2 classes: ideal. 3 classes: acceptable but justify it. 4: only when no merge option exists.
5+: always merge into a single custom class, no exceptions.

```html
<!-- BAD: 6 classes = maintenance nightmare -->
<div class="flex-row justify-between align-center gap-2rem padding-top-4rem text-color-primary">

<!-- GOOD: custom class handles layout, utility handles color -->
<div class="hero_content-row text-color-primary">
```

### Layout utilities first, custom class as fallback
CF V2.2 ships real layout utilities. Apply in this order:
1. Flex row → `flex-horizontal` + `gap-[token]`
2. Flex column → `flex-vertical` + `gap-[token]`
3. N-column grid → `grid-[N]-col` (+ `-tab`/`-mobile` for column reflow)
4. Responsive auto grid → `grid-autofit-[size]` / `grid-autofill-[size]`
5. **Only create a custom layout class** when utilities cannot express the layout
   (unique child sizing, >6 columns, asymmetric tracks, specific offset positioning).

```html
<!-- CORRECT: layout utilities for simple flex/grid -->
<div class="flex-horizontal gap-medium">

<!-- CORRECT: custom class when utilities can't cover it -->
<div class="pricing_card-inner">   ← create this in new_classes when truly needed
```

### No duplicate semantics
Never have two classes doing the same CSS property on the same element.

```html
<!-- WRONG: both set text color -->
<p class="text-color-primary hero_description">   ← hero_description also has color

<!-- CORRECT: one source of truth per property -->
<p class="text-color-primary hero_description">   ← hero_description has no color
```

### REM exceptions — do not blindly convert all px values

- **Borders:** Keep as literal `1px` — do NOT convert to rem. Retina displays handle px borders correctly; rem borders can blur. (CF border-width-thin = 1px, normal = 0.125rem, bold = 0.25rem)
- **Typography minimum:** 14px = `0.875rem` is acceptable for small labels/captions. Never go below 12px (0.75rem).
- **Tiny gaps:** 2px = `0.125rem` is OK for hairline visual gaps. Avoid irrational decimals like `8.4375rem`.
- **Spacing: use utility class (`margin-medium`, `gap-large`) that references a Layout variable — the variable auto-provides tablet/mobile values. Never compute px/16 for spacing. Token-snap to the nearest scale value instead.**

### Color ONLY from library or token
Never hardcode a hex value in a custom class when that color exists as a Figma token in the per-project library. Reference the library class instead.

```html
<!-- WRONG: redundant when text-color-primary exists -->
<p class="hero_description">   ← hero_description has color:#FF5733 hardcoded

<!-- CORRECT -->
<p class="text-color-primary hero_description">   ← utility handles color, custom handles layout
```

### Semantic HTML tags match content role

| Content type | Use tag |
|---|---|
| Navigation | `<nav>` |
| Page sections | `<section>` (must have a heading inside) |
| Blog post / product card / self-contained content | `<article>` |
| Sidebar / supplementary content | `<aside>` |
| Heading hierarchy | `<h1>` once per page, `<h2>`–`<h6>` nested without skipping |
| Inline text variation | `<span>` |
| Generic block | `<div>` |
| Generic inline | `<span>` |
| Self-contained content (blog post, product card) | `<article>` |
| Supplementary / sidebar content | `<aside>` |
| Image + caption pair | `<figure>` (with `<figcaption>`) |
| Sub-header within a section or article | `<header>` |
| Contact / authorship info | `<address>` |
| Navigation group (navbar, breadcrumbs, footer links) | `<nav>` |

---

## HTML Contract Output Format

For each section, output this structure:

```html
<!-- section_id: hero -->
<section class="section_hero">
  <div class="padding-global">
    <div class="container-large">
      <div class="padding-section-large">

        <!-- Content row: CASE 1 — layout = new class -->
        <div class="hero_content-row">

          <!-- Text block: CASE 1 — sizing = new class -->
          <div class="hero_text-block">
            <!-- heading: Layer 2 utility only, no new class needed -->
            <h1 class="heading-style-h1 text-color-primary">Headline here</h1>

            <!-- body: Layer 2 utility only -->
            <p class="text-size-medium text-style-muted">Description here</p>

            <!-- button: base + combo variant -->
            <a class="button is-brand">CTA</a>
          </div>

          <!-- Image: CASE 2 — unique visual = new class -->
          <div class="hero_image-wrapper">
            <img class="hero_hero-image" src="" alt="">
          </div>

        </div>
      </div>
    </div>
  </div>
</section>
```

---

## new_classes Entry Format

For every class you invent (all CASE 1–5 above), add ONE entry to the blueprint `new_classes` array:

```json
{
  "name": "hero_content-row",
  "cf_category": "spacing",
  "webflow_property": "display",
  "value": "flex",
  "reason": "Flex row layout for hero text + image side-by-side. No CF utility covers flex layout — custom class required (Case 1)."
}
```

`cf_category` pick:
- Layout/flex/grid/positioning → `spacing`
- Unique background/shadow/border → use closest: `background-color`, `border-color`, `border-radius`
- Component-specific text → `font-size` or `font-weight`

`reason` MUST reference the case number (Case 1–5) from this guide. This is auditable evidence.

---

## Pre-output Checklist

Before finalizing HTML contracts and new_classes, verify:

- [ ] Every section has `section_[id]` → `padding-global` → `container-*` → `padding-section-*` skeleton.
- [ ] No layout (flex/grid) via utility classes — all layout is custom class.
- [ ] No element has more than 4 classes stacked.
- [ ] Every color references a library class (`text-color-*`, `background-color-*`) — no hardcoded hex in custom classes.
- [ ] Every `new_classes` entry has a `reason` citing Case 1–5.
- [ ] No class in `cf_classes[]` (per section) is missing from the library OR `new_classes` list.
- [ ] `is-*` combo classes are always paired with a base class on the same element.
- [ ] `section_[id]` class name matches `section_id` in the blueprint JSON.
- [ ] Heading hierarchy: one `<h1>` per page, levels not skipped.
- [ ] No duplicate CSS property coverage from two classes on the same element.

---

## Source References

- `knowledge-base/client-first-class-map.json` — global CF utility class catalog
- `knowledge-base/libraries/{site_id}/client-first-library.json` — project token classes
- `agentic/specs/figma-to-client-first-mapping.md` — mapping pipeline
- `finsweet.com/client-first/docs/classes-strategy-1` — Class types reference
- `finsweet.com/client-first/docs/classes-strategy-2` — Combo classes and deep stacking rules
- `finsweet.com/client-first/docs/utility-class-systems` — Full utility catalog
