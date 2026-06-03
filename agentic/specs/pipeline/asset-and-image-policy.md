# Asset and Image Policy Specification

## Asset Manifest & Alt Policy

- Every image, vector illustration, or media element extracted from Figma must have an entry in `asset-manifest.json`.
- The manifest maps Figma node IDs to assets and stores:
  - Asset filename / URL
  - Asset role: `informative` | `decorative` | `functional` | `complex`
  - Required alt text (must not be empty for informative/functional assets; decorative assets must have empty alt text `alt=""` and `role="presentation"`)
- The alt policy catches missing alt tags or generic placeholder alts.
