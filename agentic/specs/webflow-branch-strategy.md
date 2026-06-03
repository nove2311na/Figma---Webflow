# Webflow Branch Strategy Specification

## Branching & Authorization Rules

- All mutations to Webflow must operate on a temporary site branch, rather than directly on the main/production site setup.
- Webflow native writes require:
  - Branch-first operations
  - A preflight verification step
  - A serialized execution sequence (single threaded writes to prevent database lockups)
  - Detailed audit logs mapping actions, observations, and results
  - Auto-publish is strictly forbidden from the build pipeline. Publishing is manually triggered or gated separately.
