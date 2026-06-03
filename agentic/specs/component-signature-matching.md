# Component Signature Matching Specification

## Matching Levels

- Matching level definitions:
  - **Exact Match**: The component's structure, styles, and names perfectly align with a registry signature. Map directly.
  - **Usable Match**: Small discrepancies exist (e.g. slight text styling differences or spacing overrides) but structurally identical. Map with overrides.
  - **Candidate Match**: Visual/structural similarities exist but requires review to decide if it's a new variant or should be normalized.
  - **No Match**: A new component or a primitive layout. Recreate using default Client-First elements.
