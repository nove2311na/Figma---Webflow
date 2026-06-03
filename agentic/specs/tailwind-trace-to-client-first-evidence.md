# Tailwind-trace to Client-First Evidence Specification

## Tailwind Classes as Intent Evidence Only

- If Figma MCP outputs contain Tailwind-like utility classes (e.g. `p-4`, `flex`, `text-center`), these classes must NOT be written to the final HTML blueprint or Webflow build.
- Instead, use them strictly as "intent evidence" to map them to the corresponding Finsweet Client-First V2 classes:
  - `p-4` -> `padding-medium` (or equivalent spacing variable token class)
  - `flex` -> `flex-horizontal` or custom component wrapper
  - `text-center` -> `text-align-center`
- This ensures full styling compliance with Finsweet Client-First structures.
