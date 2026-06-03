# Prompt: Read and Analyze Figma Raw Data

## Purpose

Produce a structured **design analysis document** BEFORE writing the HTML contract.
This analysis is the mandatory input to `write-html-contract.md`. Do not skip this step.

Run AFTER:
1. Figma raw data is in `workspace/rawdata/`.
2. `agentic/specs/figma-to-client-first-mapping.md` is read.
3. Per-project CF library loaded: `knowledge-base/libraries/{site_id}/client-first-library.json`.

Output file: `workspace/blueprints/[page-slug]_design-analysis.json`

---

## Why This Step Exists

Jumping from raw Figma JSON directly to HTML contract is error-prone on complex pages.
This pre-analysis step forces systematic extraction of all decisions before naming begins:
- Section inventory locks the vertical order and structural sizing choices.
- Layout map decides every custom class name before the contract is written.
- Typography catalog maps every text style to CF utilities once, consistently.
- Color catalog verifies every color token is in the library before HTML is written.

---

## Output: Design Analysis JSON Structure

Write `workspace/blueprints/[page-slug]_design-analysis.json` with this shape:

```json
{
  "page_slug": "home",
  "figma_file_id": "...",
  "generated_at": "ISO date",
  "section_inventory": [...],
  "layout_pattern_map": [...],
  "typography_catalog": [...],
  "color_token_catalog": [...],
  "component_map": [...],
  "responsive_notes": []
}
```

---

## Section 1: section_inventory

For each top-level section frame (in vertical order on page):

```json
{
  "section_id": "hero",
  "figma_node_id": "123:456",
  "figma_name": "Hero Section",
  "order": 1,
  "container_size": "large",
  "padding_section_size": "large",
  "background_token": "background-color-dark",
  "has_dark_bg": true,
  "notes": ""
}
```

Rules:
- `section_id`: slugify Figma frame name (lowercase, spaces→hyphens, drop special chars)
- `container_size`: apply Section C thresholds from `agentic/specs/figma-to-client-first-mapping.md`
- `padding_section_size`: apply Section D thresholds
- `background_token`: CF library class name, or `null` if no background token

---

## Section 2: layout_pattern_map

For each flex/grid layout frame inside sections:

```json
{
  "section_id": "hero",
  "layouts": [
    {
      "figma_node_id": "123:789",
      "figma_name": "Content Row",
      "direction": "horizontal",
      "columns": null,
      "gap_px": 48,
      "gap_token": "gap-medium",
      "cf_decision": "utility",
      "suggested_utility_classes": ["flex-horizontal", "gap-medium"],
      "suggested_custom_class": null,
      "case": null
    }
  ]
}
```

Rules:
- `direction`: `"horizontal"` (flex row) | `"vertical"` (flex col) | `"grid"` | `"absolute"` (no auto-layout)
- `columns`: number if grid, `null` if flex
- `gap_token`: snap to nearest Layout token name (tiny/xxsmall/xsmall/small/medium/large/xlarge/xxlarge/huge/xhuge/xxhuge or semantic gaps small/regular/medium/large)
- `cf_decision`: `"utility"` when flex-horizontal/flex-vertical/gap-*/grid-N-col covers it; `"custom"` only when utilities can't express it
- `suggested_utility_classes`: if `cf_decision=utility`, list the classes; if custom, leave empty array
- `suggested_custom_class`: if `cf_decision=custom`, suggest the class name using Section G naming; if utility, leave `null`
- `case`: only set to `"Case 1"` if `cf_decision=custom`; `null` if utility

---

## Section 3: typography_catalog

One entry per distinct text style used on the page (not per-node):

```json
{
  "style_id": "figma-style-id",
  "figma_style_name": "Heading/H1",
  "font_size_px": 64,
  "font_size_rem": "4rem",
  "font_weight": 700,
  "cf_heading_class": "heading-style-h1",
  "cf_size_class": null,
  "cf_weight_class": null,
  "cf_style_classes": [],
  "suggested_tag": "h1",
  "notes": "Sole H1 on page — no heading-style class needed, tag alone"
}
```

Rules:
- Apply Section E algorithm from `agentic/specs/figma-to-client-first-mapping.md`
- `cf_heading_class`: set if semantic/visual mismatch; `null` if tag alone is correct
- `cf_size_class`: set for body text sizes; `null` for headings
- `cf_weight_class`: set if weight utility needed; `null` if weight already in heading-style or is default
- `cf_style_classes`: array of any `text-style-*` utilities (allcaps, italic, etc.)
- `font_size_rem`: `font_size_px / 16`, keep as string with rem unit; exception: 14px = "0.875rem"

---

## Section 4: color_token_catalog

One entry per Figma color variable used on the page:

```json
{
  "figma_variable": "colors/brand/Primary",
  "library_token": "primary",
  "text_class": "text-color-primary",
  "bg_class": "background-color-primary",
  "border_class": "border-color-primary",
  "usage_contexts": ["hero heading", "CTA button fill"]
}
```

Rules:
- Apply Section F from `agentic/specs/figma-to-client-first-mapping.md`
- Look up `figma_token` in `knowledge-base/libraries/{site_id}/client-first-library.json`
- If ANY variable is NOT in the library → write a `blocker` entry and STOP. Do not proceed to HTML contract until PM resolves.
- If a Figma color is a hardcoded hex with no variable mapping → flag as blocker; operator must add to library first before writing HTML contract.
- Never hardcode hex values anywhere in the analysis or contract.
- **Dark Mode note:** Dark Mode is a variable collection mode (Theme collection, `mode-61994c14-2f10-542b-e084-a014a8caf47a`). Classes remain identical — the Theme variable resolves differently in Dark Mode. Document `dark_mode_value` per token for reference but do not create separate classes for dark mode. The same `text-color-primary` class works in both modes.

---

## Section 5: component_map

One entry per Figma component type used (not per-instance):

```json
{
  "figma_component": "Button/Primary",
  "cf_pattern": "button",
  "variant_class": null,
  "instances_count": 3
},
{
  "figma_component": "Button/Secondary",
  "cf_pattern": "button",
  "variant_class": "is-secondary",
  "instances_count": 1
}
```

---

## Section 6: responsive_notes

Flag elements that need breakpoint treatment:

```json
{
  "element_class": "hero_content-row",
  "desktop": "flex row, 2 columns",
  "tablet": "flex column, 1 column",
  "mobile": "flex column, full width",
  "hide_at": null,
  "requires_breakpoint_custom_class": true,
  "case": "Case 4",
  "notes": "2-col → 1-col at tablet; width 100% on mobile"
}
```

Rules:
- `requires_breakpoint_custom_class`: **Default `false` for spacing/type** — variable modes handle responsive shifts automatically. Set `true` only for structural reflow (column count, hide/show, complex positional changes that utilities can't express).
- `hide_at`: `"tablet"` | `"mobile-landscape"` | `"mobile-portrait"` | `null` → maps to `hide-*` utility
- If element is hidden at a breakpoint, use `hide-*` utility (NOT a custom class)
- For column reflow (e.g., 3-col desktop → 1-col mobile), use `grid-N-col-tab` / `grid-N-col-mobile` utilities — NOT a custom class; set `requires_breakpoint_custom_class: false`

---

## Validation Checklist Before Proceeding to HTML Contract

Run through this checklist after producing the analysis JSON. Do NOT proceed to `write-html-contract.md` until all pass:

- [ ] Every `section_id` is unique (no duplicate slugs)
- [ ] Section order in `section_inventory` matches Figma vertical order (top to bottom)
- [ ] Every color variable used on the page has a matching `library_token` in `color_token_catalog` — if any are missing, STOP and request library update from PM
- [ ] Every layout frame has a `suggested_class` in `layout_pattern_map` (no layout without a class name)
- [ ] `typography_catalog` covers every distinct text style visible on the page
- [ ] `component_map` covers every Figma component type used
- [ ] No hex values appear anywhere in the analysis JSON

---

## Source References

- `agentic/specs/figma-to-client-first-mapping.md` — Sections A–G (node types, layout, sizing, typography, colors, naming)
- `knowledge-base/libraries/{site_id}/client-first-library.json` — project token classes
- `knowledge-base/client-first-class-map.json` — global CF utility catalog
- `workspace/design-system.json` — project-specific REM scale
