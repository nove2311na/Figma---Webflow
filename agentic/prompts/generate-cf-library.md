# Prompt: Generate Client-First Library from Figma Variables

## Purpose

This prompt template guides the LLM to auto-generate or update
`knowledge-base/libraries/{site_id}/client-first-library.json` and
`knowledge-base/libraries/{site_id}/figma-token-map.json`
from raw Figma variable data extracted via Figma MCP `get_variable_defs`.

Run `python scripts/update_library_from_figma.py --site-id <id>` first
to get the step-by-step instruction block before using this template.

---

## Input

- Figma variables output from: `get_variable_defs(figma_file_id="<id>")`
- Current library (if exists): `knowledge-base/libraries/{site_id}/client-first-library.json`
- Current token map (if exists): `knowledge-base/libraries/{site_id}/figma-token-map.json`

---

## Naming Rules

### CF Category from Figma variable type / path

| Figma variable path contains | CF category |
|---|---|
| `color` / `colours` / `brand` / `palette` | → generates THREE classes: `text-color-*`, `background-color-*`, `border-color-*` |
| `spacing` / `gap` / `padding` / `margin` | `spacing` |
| `font-size` / `text-size` / `size/text` | `font-size` |
| `font-weight` / `weight` | `font-weight` |
| `radius` / `border-radius` | `border-radius` |
| `opacity` / `alpha` | `opacity` |

### Semantic name derivation

1. Take the **last path segment** of the Figma variable path.
2. Lowercase and slugify (replace spaces with `-`, strip special chars).
3. Examples:
   - `colors/brand/Primary` → `primary`
   - `spacing/Large` → `large`
   - `font-size/Body Default` → `body-default`

### Full class name = `{cf_category}-{semantic_name}`

Examples:
- `colors/brand/Primary` → `text-color-primary`, `background-color-primary`, `border-color-primary`
- `spacing/Large` → `spacing-large`
- `font-size/Body Default` → `font-size-body-default`

### Unit conversion

- Spacing/font-size in px → divide by 16 → rem string
  - `48px` → `"3rem"`
  - `14px` → `"0.875rem"`
- Colors: keep as hex, e.g. `"#FF5733"`
- Font-weight: keep as number string, e.g. `"700"`
- Border-radius in px → rem (same ÷16 rule)
- Opacity: keep as decimal string, e.g. `"0.5"`

---

## Output Format

### figma-token-map.json

```json
{
  "figma_file_id": "<id>",
  "updated_at": "<ISO8601>",
  "naming_convention": {
    "pattern": "{cf_category}-{semantic_name}",
    "categories": ["text-color","background-color","border-color","spacing","font-size","font-weight","border-radius","opacity"]
  },
  "mappings": {
    "colors/brand/Primary": {
      "figma_value": "#FF5733",
      "cf_text_class": "text-color-primary",
      "cf_bg_class": "background-color-primary",
      "cf_border_class": "border-color-primary"
    },
    "spacing/Large": {
      "figma_value": "48px",
      "cf_class": "spacing-large",
      "rem_value": "3rem"
    }
  }
}
```

### client-first-library.json

```json
{
  "project_id": "<site_id>",
  "webflow_site_id": "<site_id>",
  "figma_file_id": "<figma_file_id>",
  "version": "1.0.0",
  "updated_at": "<ISO8601>",
  "classes": {
    "text-color-primary": {
      "figma_token": "colors/brand/Primary",
      "cf_category": "text-color",
      "webflow_property": "color",
      "value": "#FF5733",
      "description": "Primary brand text color"
    },
    "background-color-primary": {
      "figma_token": "colors/brand/Primary",
      "cf_category": "background-color",
      "webflow_property": "background-color",
      "value": "#FF5733",
      "description": "Primary brand background color"
    },
    "border-color-primary": {
      "figma_token": "colors/brand/Primary",
      "cf_category": "border-color",
      "webflow_property": "border-color",
      "value": "#FF5733",
      "description": "Primary brand border color"
    },
    "spacing-large": {
      "figma_token": "spacing/Large",
      "cf_category": "spacing",
      "webflow_property": "padding",
      "value": "3rem",
      "description": "Large spacing token"
    }
  }
}
```

---

## Update Rules (when library already exists)

1. **If class exists** → UPDATE `value` only. Preserve `description`, `figma_token`, `cf_category`, `webflow_property`.
2. **If class is new** → ADD with full schema (all required fields).
3. **If Figma token removed** → DO NOT delete class automatically. Flag it in changelog with `source: "figma_removed"` and ask PM.
4. **Always** write a changelog entry for every changed or added class.

---

## Changelog Entry Format

```json
{
  "timestamp": "<ISO8601>",
  "class": "text-color-primary",
  "old_value": null,
  "new_value": "#FF5733",
  "source": "figma_sync",
  "reason": "Initial generation from Figma variables"
}
```

`source` values: `figma_sync` | `manual_edit` | `figma_removed`

---

## Validation After Writing

Run mandatory gate before any Webflow sync:

```cmd
python scripts/gates/validate_project_library.py --site-id <site_id>
```

Gate must return exit 0 before proceeding to sync.
