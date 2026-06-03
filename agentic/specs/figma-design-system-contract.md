# Figma Design System Contract Specification

## Sync and Mode Requirements

- Figma variables (modes, variables, theme aliases) must match the allowed variables and classes in the CSS contract.
- Spacing, colors, and typography variables must be validated in strict mode.
- If there are variable mismatches or raw untokenized properties in the Figma node bundle, the validation must fail.
- All styles must map to a corresponding Client-First library utility or token.
