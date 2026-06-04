---
_raw_url: null
_distilled_at: 2026-06-04
_token_estimate: 700
---

# Gotcha 08 — Webflow Native Widget Conflict

**Webflow's native widgets** rely on specific HTML structures AND class names. If your Figma layer name matches a widget's expected class or data attribute, Webflow assumes you're trying to use the widget — even if you're not.

## Trap

A Figma layer named `w-nav` (or `Nav`, or `nav-bar`, or `navigation`) gets processed into HTML with `class="w-nav"`. Webflow Designer recognizes `w-nav` and applies its Navbar widget styling + scripts. Your custom CSS is overridden by the widget's internal styles.

The same happens for:
- `w-slider` (Slider widget)
- `w-tabs` (Tabs widget)
- `w-dropdown` (Dropdown widget)
- `w-form` (Form widget)
- `w-lightbox` (Lightbox widget)
- `w-condition-visible` (conditional visibility class)

## Detection

`validate_figma_html.py` (in the architect skill) runs in `strict` mode for production builds. It checks every class name against the widget-conflict list:

```python
WIDGET_CONFLICTS = {
    "w-nav", "w-slider", "w-tabs", "w-dropdown",
    "w-form", "w-lightbox", "w-condition-visible",
    "w-icon", "w-image", # Note: w-image is just a class, not a widget, but often conflicts
}
```

In `warn` mode (development), conflicts are logged but don't fail. In `strict` mode (production), they fail.

## Code-level rule

Layer names containing `w-` prefix are flagged. Either:
- Rename the layer to something else (`my-nav`, `nav_component`).
- Or, if the widget is actually intended, ensure the HTML structure matches Webflow's expected structure (otherwise it'll break visually).

## Fix

1. **Naming discipline in Figma**: never use `w-*` as a layer name. Use `navbar_component`, `hero_slider`, etc.
2. **Validation gate**: `validate_figma_html.py --mode strict` rejects contracts with `w-*` class names unless explicitly marked as widget-intent.
3. **LLM prompt constraint**: the Figma→HTML prompt must list `w-*` prefixes as forbidden unless widget-intent is confirmed.
4. **Layer rename in Figma**: bulk rename layers that match the conflict list. One-time cleanup.

## How Webflow recognizes a widget

Webflow doesn't just check class names. It looks at:
- The `class` attribute (must contain `w-<widget>`).
- The `data-w-id` attribute (animation ID).
- The HTML structure (e.g. Navbar has a specific `w-container`, `w-nav-menu` structure).

If any of these match, the widget activates. The class name is the first gate.

## HTML produced by Figma's `get_design_context`

Figma's MCP often returns class names that match Webflow widgets by coincidence. Always run `validate_figma_html.py` after extraction, even on small builds.
