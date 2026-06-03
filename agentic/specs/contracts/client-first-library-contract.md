# Client-First Library Contract Specification

## Strict Mode Requirement

- The generated Client-First Library Contract (`client-first-library-contract.json`) is the absolute binding source of truth.
- LLMs or compilers cannot invent or propose classes that are not verified by this contract.
- Any curated files (e.g. `client-first-class-map.json`) or examples are purely conceptual; if a class or token is not in the generated contract, it must be blocked.
- Structural convention classes like `page-wrapper` and `main-wrapper` are allowed if documented in the contract.
