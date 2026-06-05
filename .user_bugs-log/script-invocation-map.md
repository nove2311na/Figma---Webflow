# Script Invocation Map

**Date:** 2026-06-04
**Purpose:** Identify scripts in `.claude/skills/` that are never invoked during normal Figma → HTML → Webflow flow, so they can be deleted in a future pass.

## Method

For each script under `.claude/skills/`, the following callsites were searched:
- Markdown code blocks + descriptions in `SKILL.md` and `references/README.md`
- `subprocess.run(...)` invocations from other scripts
- `import` statements (Python `from X import Y`)

---

## A. Skills (3)

| Skill | Location |
|---|---|
| `design-system-sync` | `.claude/skills/design-system-sync/` |
| `figma-to-html-architect` | `.claude/skills/figma-to-html-architect/` |
| `figma-to-webflow-orchestrator` | `.claude/skills/figma-to-webflow-orchestrator/` |

---

## B. Skill-Owned Scripts (called by parent skill)

| Script | Caller | Use case |
|---|---|---|
| `design-system-sync/scripts/extract_client_first_baseline.py` | `SKILL.md` Task 0 + `orchestrate.py` | Parse Finsweet CSS → baseline contract |
| `design-system-sync/scripts/validate_figma_extraction.py` | `SKILL.md` Task 2 + `orchestrate.py` + `selector_guards.py` import | Validate figma-design-system.json |
| `design-system-sync/scripts/map_variables.py` | `SKILL.md` Task 3 + `orchestrate.py` | Map Figma variables → Webflow contract |
| `figma-to-html-architect/scripts/validate_figma_html.py` | `SKILL.md` Task 2 + `orchestrate.py` | Validate layer names |
| `figma-to-html-architect/scripts/process_html.py` | `SKILL.md` Task 3 + `orchestrate.py` + `selector_guards.py` import | Process HTML → final-webflow.html |
| `figma-to-webflow-orchestrator/scripts/orchestrate.py` | (entrypoint) | Orchestrate the 2 branches |

**Tests wired in:**

- `design-system-sync/tests/test_sync.py` — imports from `validate_figma_extraction.py` + `map_variables.py`
- `figma-to-html-architect/tests/test_architect.py` — imports from `validate_figma_html.py` + `process_html.py`

---

## C. Cross-Skill Shared Scripts (`.claude/skills/_shared/scripts/`)

| Script | Caller | Use case |
|---|---|---|
| `validate_figma_extraction.py` | Manual CLI / Task 2 | Validate `figma-design-system.json` |
| `resolve_client_first.py` | `.claude/agents/client-first-architect.md` (agent invokes) | Resolve inline styles → CF classes |
| `validate_artifacts.py` | `CLAUDE.md` rule + `validate_artifact_contracts.py` subprocess | Schema validation block/warn/log |
| `run_quality_gate.py` | Manual CLI | Run html-first profile |
| `validate_agentic_structure.py` | `run_quality_gate.py` (sub-gate) | Structural gate |
| `validate_workspace_artifacts.py` | `run_quality_gate.py` (sub-gate) | Workspace JSON gate |
| `validate_css_contract.py` | `run_quality_gate.py` (sub-gate) | CSS contract gate |
| `validate_css_index.py` | `run_quality_gate.py` (sub-gate) | CSS index gate |
| `validate_artifact_contracts.py` | `run_quality_gate.py` (sub-gate) | Q2 schema wire-up |
| `utils.py` | `resolve_client_first.py` (import) | `parse_color`, `slugify`, etc. |
| `design-system-sync/scripts/contract_paths.py` | `map_variables.py` + `validate_figma_extraction.py` (import) | Canonical design-system path utilities |
| `selector_guards.py` (at `_shared/`, not `_shared/scripts/`) | `process_html.py` + `validate_figma_extraction.py` (import) | Denylist guards |
| `build_e2e_fixture.py` | (see D) | E2E fixture builder |

---

## D. Orphans — never invoked in normal flow

| Script | Status |
|---|---|
| `_shared/scripts/build_e2e_fixture.py` | **ORPHAN** — no caller in scripts/agents/SKILL.md. Was a one-time Phase 8 evidence builder. Useful only if rebuilding the E2E fixture. |
| `_shared/test_approval_gates.py` | **ORPHAN** — no caller. Was a one-time test for approval gate wording. |
| `_shared/__init__.py` | **EMPTY** — 0 bytes, no purpose. |
| `figma-to-webflow-orchestrator/scripts/orchestrate.py` | **ORPHAN** — no Python file invokes it via `subprocess.run`. The orchestrator skill exposes `SKILL.md` for Claude Code to read directly, not for script invocation. Wire or delete. |

---

## E. Tests

| Test | Wired to |
|---|---|
| `design-system-sync/tests/test_sync.py` | `validate_figma_extraction.py`, `map_variables.py` |
| `figma-to-html-architect/tests/test_architect.py` | `validate_figma_html.py`, `process_html.py` |

No `figma-to-webflow-orchestrator/tests/` — orchestrator has no test file.

---

## F. Decisions (recorded for future cleanup)

| Script | Recommendation | Reason |
|---|---|---|
| `_shared/scripts/resolve_client_first.py` | **KEEP** | Invoked by `client-first-architect` agent. Core to the Figma → HTML transformation. |
| `_shared/scripts/build_e2e_fixture.py` | **DELETE** | One-time evidence builder. Re-running it requires re-running Phase 8. Output already in `workspace/_fixtures/`. |
| `_shared/test_approval_gates.py` | **DELETE** | No callers. One-time approval gate wording test. |
| `_shared/__init__.py` | **DELETE** | Empty. |
| `figma-to-webflow-orchestrator/scripts/orchestrate.py` | **KEEP** (uncertain) | Not invoked by any current code path, but skill README references it. Decision: keep for now — wiring it would make orchestrator truly script-driven, not LLM-driven. If user later wants script-driven orchestration, this is the entrypoint. If user wants LLM-only flow, delete. |

---

## G. Verification Commands

```bash
# Re-check no caller for orphans
for f in build_e2e_fixture.py test_approval_gates.py orchestrate.py; do
  count=$(grep -rln "$f" .claude/skills/ 2>/dev/null | grep -v "$f" | wc -l | tr -d ' ')
  echo "$f: $count callers"
done
```
