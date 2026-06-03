# Figma Normalization Policy Specification

## Messy Figma Tree Normalization

- This step processes the raw Figma tree structure before semantic parsing.
- Issues to recover/normalize:
  - Generic layer names (e.g. `Frame 1234`, `Rectangle 5` -> resolve intent)
  - Missing styles (e.g. elements with raw hex fill -> map to color tokens if possible, otherwise error)
  - Raw color/spacing values -> snap to nearest contract utility/variable
  - Missing Auto Layout -> flag and compute structural layouts (flex/grid)
  - Repeated uncomponentized subtree -> mark as candidate components
  - Ambiguous media (e.g. vector shapes without image or icon tags -> classify)
- Unresolved issues of high severity will result in a blocker, halting the pipeline.
