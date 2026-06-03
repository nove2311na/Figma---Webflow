# HTML to Webflow Native Ops Specification

## Build Plan Compiler Rules

- Final local HTML is parsed and converted into a serialized Webflow Native Build Plan (`native-build-plan.json`).
- The build plan consists of serialized element operations:
  - `create_class` / `update_class`
  - `create_element` / `update_element` (specifying type, class list, and target parent)
  - `update_variable`
- Every section/component in the blueprint must carry `data-section`, `data-component`, and `data-figma-node` properties to trace Webflow elements back to Figma nodes.
- No Webflow writes may occur directly from HTML without this compiled, approved plan.
