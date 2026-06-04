# HTML-first Pipeline Specification

## Pipeline Order

1. **Phase 2: CSS Contract Extraction** (`.claude/skills/_shared/.claude/skills/_shared/scripts/index_css_library.py`)
2. **Phase 3: Figma MCP Extraction** (Save `figma.node-bundle.json`)
3. **Phase 4: Design-System Sync** (Strict variable/style matching)
4. **Phase 5: Component Registry & Signature Matching**
5. **Phase 6: Figma Tree Normalization** (`.claude/skills/_shared/scripts/resolve_client_first.py`)
6. **Phase 7: Semantic IR, Tag & Class Resolution**
7. **Phase 8: HTML Blueprint Rendering & QA** (`.claude/skills/_shared/.claude/skills/_shared/scripts/index_css_library.py`)
8. **Phase 9: Asset & Alt Manifest Creation**
9. **Phase 10: Section Chunk Slicing** (`.claude/skills/_shared/scripts/resolve_client_first.py`)
10. **Phase 11: Webflow Native Build Plan Compiler** (`.claude/skills/_shared/scripts/validate_artifacts.py`)
11. **Phase 12: Webflow Branch Native Ops Execution & Audit**

## Forbidden Actions

- Never write directly to Webflow from raw Figma.
- Never write to Webflow without approved local HTML and approved native build plan.
- Never use inline styles or hardcoded hex colors in the final HTML.
- Never use classes not present in the generated Client-First Library Contract.
- `whtml_builder` remains strictly forbidden.
