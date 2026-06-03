# Webflow MCP Capabilities

Verified: 2026-06-03. Source: `https://github.com/webflow/mcp-server` (`src/tools/deElement.ts`, `rules.ts`).

---

## element_builder

**Verified:** accepts `parent_element_id` to target a specific parent node.

```typescript
// Per action in the actions[] array:
{
  build_label?: string;                    // optional label for result identification
  parent_element_id: {                     // REQUIRED — where to insert
    component: string;                     // component ID of target parent
    element:   string;                     // element ID of target parent
  };
  creation_position: "append" | "prepend" | "before" | "after";  // REQUIRED
  element_schema: DEElementSchema & {      // REQUIRED — element to create
    children?: element_schema[];           // recursive, optional
  };
  return_element_info?: boolean;           // return full element info if true
}
```

**Implication for Phase 2B:** parent operator captures `{component, element}` from each section
container created in Phase 2A, stores as `target_parent_element_id` in blueprint + state.json,
passes as `parent_element_id` directly to `element_builder` calls inside each section-builder subagent.

---

## element_tool

Manipulates existing elements. Key operations:
- `get_all_elements`, `get_selected_element`, `select_element`
- `add_or_update_attribute`, `remove_attribute`, `update_id_attribute`
- `set_text`, `set_style`, `set_link`, `set_heading_level`, `set_image_asset`
- `remove_element`
- `query_elements` — query by ID, type, text, style, tag, attributes, component name

All tools require `siteId`.

---

## style_tool

Creates/updates/queries CSS styles at the style-definition level. Actions:
- `create_style` — create style with name and CSS properties
- `get_styles` — retrieve with filtering/breakpoint options
- `update_style` — modify existing
- `remove_style` — delete
- `query_styles` (BETA) — query by name path, ID, or CSS properties

Operates on style definitions only — does not apply styles to specific elements.

---

## whtml_builder

**FORBIDDEN in this workspace.** Inserts HTML/CSS markup. Parameters: `parent_element_id`,
`creation_position`, `html`, `css`, `get_children_info`. Off-limits per operating rules.

---

## Concurrent Write Capability

**Status: unconfirmed.** No explicit concurrent-write limitations, session restrictions, or
multi-agent conflict-resolution mechanisms are documented in `rules.ts` or source code.

**Design consequence:** Phase 2B (parallel-section-build) is designed to degrade gracefully:
- If MCP allows concurrent writes from multiple subagent sessions → true parallel builds.
- If MCP serializes writes at the Designer layer → sections build sequentially.
- Correctness is identical either way; parallelism is a performance property only.

**To confirm:** call `webflow_guide_tool` in a live session or test two simultaneous
`element_builder` calls targeting the same site from different subagent contexts.

---

## Naming Convention Used in Codebase

| Our field name | Webflow MCP param | Type |
|---|---|---|
| `parent_element_id` | `parent_element_id` | `{component: string, element: string}` |
| `target_parent_element_id` (blueprint) | — | stored reference, same shape |
| `site_id` | `siteId` | string |

All schemas updated to use `parent_element_id` with `{component, element}` structure.
Previous name `parent_node_id` was incorrect and has been replaced everywhere.
