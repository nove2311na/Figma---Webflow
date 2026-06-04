# Token Sync Architecture

This document explains the design token sync mechanism between **Figma → Repo → Webflow** and the deterministic conditions required by the pipeline.

## Core Principle

> **Class definition = immutable. Token value = the only payload that needs to sync.**

```
class text-weight-bold  →  var --font-weight--bold  →  value (project A: 700, project B: 900)
       (never changes)            (fixed key)              (changes per project)
```

`text-weight-bold` never changes its name or meaning. What changes is **the value of the variable** behind it. The LLM does not guess "what bold is" — it reads the value from the token catalog.

---

## 3-Way Ledger

```
┌─────────────────┐      read       ┌──────────────────┐      push       ┌─────────────────┐
│  Figma Project  │ ─────────────►  │   Repo Contract  │ ─────────────►  │ Webflow Project │
│  (design SoT)   │                 │ (git-versioned)  │                 │ (build target)  │
│                 │                 │                  │                 │                 │
│ Variables panel │                 │ agentic/         │                 │ Variables panel │
│ - Base tokens   │ ◄─── drift? ──► │ knowledge/       │ ◄─── drift? ──► │ - same tokens   │
│ - Theme aliases │                 │ generated/       │                 │ - applied live  │
│                 │                 │ webflow-         │                 │                 │
│                 │                 │ contract.json    │                 │                 │
│                 │                 │ figma-           │                 │                 │
│                 │                 │ contract.json    │                 │                 │
└─────────────────┘                 └──────────────────┘                 └─────────────────┘
```

**Figma** = where the designer defines token values.
**Repo** = git-versioned ledger, source of truth for the build agent.
**Webflow** = build target; receives values from the repo via `variable_tool`.

Each sync round appends to `write-audit-log.jsonl` — the audit trail.

---

## Token is the "Contract" between Designer and LLM

| | Figma | Repo | Webflow |
|---|---|---|---|
| **Key (fixed)** | `Font Weight/bold` | `figmaId` mapping | `--font-weight--bold` |
| **Value (synced)** | 700 | `client-first-library-contract.json` | variable value |

Designer changes `Font Weight/bold` from 700 → 900 in Figma
→ `design-system-sync` skill Task 2 (validate extraction) + Task 3 (map variables) re-generates `webflow-contract.json`
→ LLM calls Webflow `variable_tool` to push value to Webflow (approval-gated, branch-first)
→ **class `text-weight-bold` does not change one character.**

---

## Critical Condition: Designer MUST Use Figma Variables

This is a technical requirement, not a recommendation.

| Designer does | Pipeline outcome |
|---|---|
| Use Variable for color, spacing, typography | Token can sync → LLM deterministic |
| Hardcode raw value (e.g. `font-weight: 700` directly) | No token to sync → LLM must guess → breaks |

**Pre-flight gate** at ingest:
- Detect Figma nodes with raw values not backed-by-variable
- Flag: `untokenized_property` → block pipeline or require designer fix first
- No automatic workaround — only input discipline

---

## Position in Pipeline

```
Step 1  design-system-sync     ← TOKEN SYNC (this document)
          │ Figma vars → repo (figma-contract.json) → Webflow vars + drift gate + untokenized gate
          │
Step 2  figma-to-html-architect  ← Figma node → HTML with CF classes
          │ Uses agentic/knowledge/generated/* for class selection
          │
Step 3  figma-to-webflow-orchestrator  ← parallel sync + render
          │ Branch A: Webflow MCP write
          │ Branch B: HTML output
```

Step 1 is the foundation. If the token layer is correct, Steps 2-3 are deterministic.

---

## Skill-Owned Scripts (in current architecture)

| Script | Owner | Role |
|---|---|---|
| `design-system-sync/scripts/extract_client_first_baseline.py` | design-system-sync | Task 0: Parse Webflow CSS → baseline contract |
| `design-system-sync/scripts/validate_figma_extraction.py` | design-system-sync | Task 2: Validate figma-contract.json against baseline |
| `design-system-sync/scripts/map_variables.py` | design-system-sync | Task 3: Map Figma variables → Webflow contract |

**Shared (cross-skill):**

| Script | Role |
|---|---|
| `.claude/skills/_shared/.claude/skills/_shared/scripts/index_css_library.py` | One-time setup: parse `agentic/knowledge/source-css/` → `agentic/knowledge/generated/` |
| `.claude/skills/_shared/scripts/validate_artifacts.py` | Q2 schema validation block/warn/log |
| `.claude/skills/_shared/scripts/run_quality_gate.py` | Full quality gate |

---

## Quick Reference

### Designer (Figma side)
- **Always use Variables** for color, spacing, typography, border — even in prototype
- Name variables with established patterns
- Do not apply raw hex or raw numbers directly to elements that will appear in component builds
- Adding new token → add to Figma Variable collection first, then notify operator

### Operator / Developer
1. After designer updates Figma tokens → run `validate_figma_extraction.py` + `map_variables.py`
2. Review `webflow-contract.json` diff
3. Run `validate_artifacts.py --tier block` to ensure schema compliance
4. Push to Webflow via `variable_tool` (approval-gated)

### LLM / Agent (build side)
- Before writing HTML contract → read `agentic/knowledge/generated/client-first-library-contract.json` for allowed classes
- Every color must trace back to a token class — no hardcoded hex
- Every spacing picks a token — no `px/16` computation
- If Figma node has raw value without token → flag `untokenized` in design analysis, STOP

---

## Reference Files

| File | Content |
|---|---|
| `agentic/knowledge/client-first-class-map.json` | Global utility class catalog |
| `agentic/knowledge/generated/client-first-library-contract.json` | Generated contract (CF V2.2 + class allowlist + breakpoint policy) |
| `agentic/schemas/_shared/variable-entry.schema.json` | Q2 schema for variable entries (requires `figmaId` + `modes`) |
| `agentic/specs/contracts/figma-to-client-first-mapping.md` | Figma node → CF class rules (Sections A–G) |
| `.claude/skills/_shared/scripts/validate_artifacts.py` | Q2 schema validation gate |
