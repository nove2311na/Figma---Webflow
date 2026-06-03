# Figma to Client-First Mapping

This contract turns Figma properties into Client-First class decisions. It prevents the architect and operator from inventing one-off classes when a reusable Client-First class or variable should be used.

## Mapping Pipeline

| Step | Input | Decision | Output |
|---|---|---|---|
| Identify role | Frame name, hierarchy, component context | Page wrapper, section, component, child, or utility wrapper. | `element_role` |
| Read properties | Auto-layout, fills, strokes, typography, variant, size | Select matching rule from `knowledge-base/client-first-class-map.json`. | `class_mapping[]` |
| Normalize units | Pixel-like values | Convert to REM and token size. | `rem_value` |
| Pick strategy | Global, utility, custom, combo, variable-backed utility | Decide class application mode. | `class_strategy` |
| Write blueprint | Mapped classes and reasons | Build-ready class contract. | `workspace/blueprints/*.json` |

## Blueprint Class Mapping Shape

```json
{
  "element_id": "figma-node-hero-title",
  "element_role": "heading",
  "class_mapping": [
    {
      "figma_property": "fontSize",
      "figma_value": "64px",
      "client_first_class": "heading-style-h1",
      "webflow_property": "font-size",
      "class_strategy": "utility_selection",
      "reason": "Hero title is visually H1 scale.",
      "source": "knowledge-base/client-first-class-map.json"
    }
  ]
}
```

## Selection Rules

- Use `page-wrapper` and `main-wrapper` once per page.
- Use `section_[name]` for every major page band.
- Use `padding-global` for site gutters, not for local component padding.
- Use `container-[size]` for centered max-width content.
- Use `padding-section-[size]` for top and bottom section rhythm.
- Use typography utilities for reusable type styling.
- Use color utilities only when the color is mapped to a Webflow variable.
- Use `[component]_[element]` for layout decisions that are unique to a section or component.
- Use `is-[state]` only as a combo class on top of a base class.

## Rejection Rules

Reject a blueprint when:

- it uses a custom class where an existing Client-First utility should be used,
- it maps a Figma property without a reason,
- it uses pixel units in the final Webflow property,
- it skips source attribution to the class map,
- it applies a Webflow class that has not been confirmed or created through the approved build path.

---

## Section A — Figma Node Type → HTML Tag

| Figma Node Type | Condition | HTML Tag | CF Class Pattern |
|---|---|---|---|
| FRAME | outermost page composition | `<div>` | `page-wrapper` |
| FRAME | named "main" / "content" / wraps all sections | `<main>` | `main-wrapper` |
| FRAME | large vertical band (hero, features, pricing, etc.) | `<section>` | `section_[slug]` |
| FRAME | named "nav" / "navbar" / "navigation" | `<nav>` | custom `nav_component` |
| FRAME | named "footer" | `<footer>` | custom `footer_component` |
| FRAME | named "header" within a section | `<header>` | custom `[section]_header` |
| COMPONENT INSTANCE | button component | `<a>` or `<button>` | `button` + combo |
| COMPONENT INSTANCE | card/tile component | `<article>` if self-contained | custom `[comp]_card` |
| FRAME with `clipsContent: true` + image fill | image mask | `<div>` | custom `[comp]_image-wrapper` + `overflow-hidden` |
| TEXT | sole H1 on page | `<h1>` | no heading-style class needed |
| TEXT | heading with semantic mismatch | `<h2>` (semantic) | + `heading-style-h3` (visual) |
| TEXT | body paragraph | `<p>` | `text-size-*` utilities |
| TEXT | inline variation | `<span>` | `text-style-*` utilities |
| TEXT | list item | `<li>` | custom `[comp]_list-item` |
| VECTOR / SVG < 64px | icon | `<img>` or `<svg>` | `icon-1x1-[size]` |
| GROUP | layout grouping | `<div>` | custom `[section]_[role]` — ALWAYS custom (Case 1) |

Slugify rule: lowercase, spaces→hyphens, drop special chars. "Hero Section" → `hero`.

---

## Section B — Auto-Layout → Layout Decision

CF V2.2 ships real layout utilities. Use them first; custom class only as fallback.

| Figma Auto-Layout | Preferred CF utility | Custom class when |
|---|---|---|
| `direction: HORIZONTAL` + itemSpacing | `flex-horizontal` + `gap-[token]` | Need unique alignment, responsive reflow, or sizing not expressible by flex alone |
| `direction: VERTICAL` + itemSpacing | `flex-vertical` + `gap-[token]` | Same — unique constraints only |
| Multi-column grid (equal columns, N=1–6) | `grid-N-col` (+ `-tab`/`-mobile` for responsive) | > 6 columns, asymmetric columns, complex track sizes |
| Auto-fill/auto-fit responsive grid | `grid-autofit-[size]` or `grid-autofill-[size]` | Custom min-width needed |
| `layoutWrap: WRAP` | `flex-horizontal` + `flex-wrap-down` | — |
| No auto-layout, absolute children | position:relative on parent (custom class) + `layer` on full-cover child | Always custom for positioning |

**Gap token selection:** Look up Figma itemSpacing in the Layout/Spacing or Layout/Gaps token scale.
Pick the nearest token name (tiny/xxsmall/.../xxhuge or small/regular/medium/large for semantic gaps).
Apply `gap-[token]` utility. Do NOT compute px/16 for literal rem — the variable handles responsive shift.

**When to create a custom class instead of using layout utilities:**
- Element needs unique width/height constraints on layout children
- 7+ column grids or complex CSS grid track definitions
- Absolute positioning with specific top/left/right/bottom offsets (not full-cover)

## Section B2 — Responsive Strategy in CF V2.2

Spacing, typography, and grid gap responsive shifts are handled by **variable collection modes**,
not per-breakpoint utility classes. The Layout collection has Tablet and Mobile Landscape modes
that automatically change spacing values. The Typography collection has Tablet and Mobile Landscape
modes that shift heading font sizes.

**Consequence for HTML contract writing:**
- Do NOT create a custom class just to override spacing at tablet/mobile — the utility class handles it.
- Do NOT add `hide-tablet` + a custom class for spacing — just apply the spacing utility.
- Only create breakpoint custom classes for TRUE structural reflow: column count (use `grid-N-col-tab`),
  hide/show (`hide-tablet`), or complex layout changes that utilities can't express.

---

**Spacing: token-snap, not px/16 math.**
Look at the Figma spacing/gap/padding value. Find the nearest Layout token in the scale
(none→0, tiny→0.125, xxsmall→0.25, xsmall→0.5, small→1, medium→2, large→3, xlarge→4, xxlarge→5,
huge→6, xhuge→8, xxhuge→12 rem on desktop). Apply that utility class. The variable automatically
provides tablet and mobile-landscape responsive values — no breakpoint custom class needed.
Exception: border sizes use explicit values (thin=1px, normal=0.125rem, bold=0.25rem).

## Section C — Container Size Selection (project heuristic — real CF V2.2 values: container-small 48rem, container-medium 64rem, container-large 80rem)

Pick `container-[size]` by comparing content frame max-width:

| Figma content frame max-width | CF class |
|---|---|
| >= 1200px | `container-large` |
| 900px–1199px | `container-medium` |
| < 900px | `container-small` |
| No explicit max-width frame found | default `container-large` |

---

## Section D — Padding-Section Size Selection (project heuristic — real CF V2.2 values: section-small 3rem, section-medium 5rem, section-large 8rem desktop)

Pick `padding-section-[size]` from section vertical padding (top + bottom combined):

| Section top+bottom padding combined | CF class |
|---|---|
| >= 120px | `padding-section-large` |
| 64px–119px | `padding-section-medium` |
| < 64px | `padding-section-small` |

---

## Section E — Typography Matching Algorithm

For each TEXT node in Figma:

1. Is this the ONLY h1-level heading on the page? → Use `<h1>` tag alone. No `heading-style-*` class needed (tag IS the style).
2. Does the Figma text style name contain "Heading" / "H1"–"H6"?
   - Determine visual level (H1=largest, H6=smallest by font-size).
   - Determine semantic level needed for SEO/accessibility.
   - If visual level matches semantic level → use semantic tag alone.
   - If mismatch (e.g., SEO needs `<h2>` but visual = H3 size) → `<h2 class="heading-style-h3">`.
3. Body text: compare fontSize to project scale in `workspace/design-system.json`; map to `text-size-[token]`.
4. Font weight mapping:
   - 100–300 → `text-weight-light`
   - 400 → no class (if default body weight); otherwise `text-weight-normal`
   - 500 → `text-weight-medium`
   - 600 → `text-weight-semibold`
   - 700 → `text-weight-bold`
   - 800+ → `text-weight-xbold`
5. Color: if fill references a Figma variable → use `text-color-[token]` from per-project library.
6. Decoration/case:
   - `textDecoration: STRIKETHROUGH` → `text-style-strikethrough`
   - `textCase: UPPER` → `text-style-allcaps`
   - `fontStyle: Italic` → `text-style-italic`
7. Multi-line clamp: 2-line truncation → `text-style-2lines`; 3-line → `text-style-3lines`.

---

## Section F — Figma Variable → Color Class

1. All Figma color variables are listed in raw data under `"variables"` or `"variableCollections"`.
2. For each variable used on a node, look up `figma_token` in `knowledge-base/libraries/{site_id}/client-first-library.json`.
3. Apply the correct class by context:
   - Fill on TEXT node → `text-color-[token]`
   - Fill on FRAME (not text) → `background-color-[token]`
   - Stroke on FRAME/RECTANGLE → `border-color-[token]`
4. Variable NOT in library → STOP. Request library update before writing HTML contract.
5. Never hardcode hex values. Every color must trace back to a library class.

---

## Section G — Custom Class Naming from Figma Layer Names

1. Section prefix = slugified Figma section frame name:
   - "Hero Section" → `hero`
   - "Feature Cards Grid" → `feature-cards`
2. Element name = slugified Figma child layer name:
   - "Content Row" → `content-row`
   - "Image Wrapper" → `image-wrapper`
   - "CTA Button" → `cta-btn`
3. Combined: `[section-prefix]_[element-name]`
   - `hero_content-row`, `feature-cards_image-wrapper`
4. Generic layer names ("Group 1", "Frame 23") → infer from content type:
   - Contains only text nodes → `[section]_text-block`
   - Contains image/vector → `[section]_image-wrapper`
   - Horizontal row of children → `[section]_content-row`
   - Grid/list of repeated items → `[section]_grid`
   - Background decoration → `[section]_bg-layer`
5. Page-specific elements (appear only on this page) → add page slug prefix: `home-hero_content-row`
6. Global/reusable elements (shared across pages) → no page prefix: `card_wrapper`, `faq_item`
7. Never apply a page-prefixed class to elements on other pages.

**`_component` wrapper convention (CF V2.2):**
- The outermost wrapper of a reusable component = `[name]_component` (e.g. `nav_component`, `form_component`)
- Direct children = `[name]_[element]` (e.g. `nav_brand`, `nav_menu`)
- Nested multi-level = `[name]_[parent]_[element]` (e.g. `nav_menu_link`)
- `fs-styleguide_*` classes = demo/styleguide only — NEVER use in builds

