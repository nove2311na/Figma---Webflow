# Version History

| Version | Date | Focus | Main Improvements |
|---|---|---|---|
| v0.1.0 | 2026-06-02 | Baseline preservation | Kept MAS V3 phase flow, PM/architect/operator split, Client-First rules, approval gate, MCP-352, workspace evidence, and handoff discipline. |
| v0.2.0 | 2026-06-02 | Claude Code and Python cleanup | Made Claude Code the only runtime, moved non-root docs into `agentic/`, removed unrelated runtime artifacts, added Python project metadata and gates. |
| v0.3.0 | 2026-06-02 | Agentic quality upgrades | Added reflection loop, ReAct action traces, JSON schemas, visual QA evidence contract, phase state gate, skill anatomy gate, relative-path gate, and version logs. |
| v0.4.0 | 2026-06-03 | Multi-project CF library + parallel-section build | Per-project Client-First library system keyed by Webflow site ID (registry, resolver, sync pipeline, gate). Parallel-section build workflow with HTML contract, Phase 2A/2B split, apply-only section-builder subagent, and naming-race guard gate. |
| v0.5.0 | 2026-06-03 | Figma→HTML deep optimization | Expanded figma-to-client-first-mapping.md with 7 new sections (node types, auto-layout, container/padding sizing, typography algorithm, color mapping, custom class naming). Added 9 missing class groups to client-first-class-map.json (~40 new classes). Patched write-html-contract.md (8 edits: missing utilities, CF-spec stacking rule, REM exceptions, semantic HTML, spacing wrapper, folder prefix, section add-on). New read-figma-data.md pre-analysis prompt with 6-section design analysis output. |
| v0.6.0 | 2026-06-03 | CF V2.2 ground-truth sync | Connected to live Webflow Client-First V2.2 site via MCP. Read ~250 classes + 5 variable collections. Synced repo 100% to live site: per-project library generated, class-map corrected (layout utilities exist, aspect-ratio fixed, text-size-huge removed, text-weight-medium kept), prompts/spec updated (layout-utility-first rule, token-snap spacing, variable-mode responsive strategy, _component naming), bugs reconciled. |
| v0.7.0 | 2026-06-03 | HTML-First compiler refactor start | Initiated refactoring to strict HTML-first compiler structure: completed Phase 0 (cleanup archive), Phase 1 (pipeline folders, specs, rules, schemas, dependencies), Phase 2 (Client-First CSS contract builder CLI and validation gates), and Phase 3 (Figma extraction contract, schemas, and node bundle validation). |
| v0.8.0 | 2026-06-03 | Design system sync & Component registry | Strict mode validation of design tokens (Phase 4) and schema-validated component signature matching with layout topology and token cluster scoring (Phase 5). |

## Current Quality Bar

- Runtime scope: Claude Code only.
- Automation language: Python.
- Path discipline: local filesystem paths inside this folder must be relative.
- Architecture target: pass the local standalone baseline in `agentic/evals/standalone-architecture-baseline.md`.
- Client-First target: use `knowledge-base/client-first-class-map.json` for Figma property to class mapping.
