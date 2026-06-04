# MAS Claude Code Instructions

This is the highest directive document for the Claude Code-native MAS Figma-to-Webflow workflow.

## 1. Runtime Scope

- Use Claude Code only.
- Use Python as the automation language.
- Use `.claude/agents/` and `.claude/skills/` for runtime agent and skill behavior.
- Use `agentic/` for durable specs, knowledge, memory, policies, orchestration, and evals.

## 2. Core Principles

- PM-led orchestration: `pm` is the only user-facing coordinator.
- Context isolation: use Claude subagents for architect, operator, steward, and gatekeeper roles.
- Workspace-driven state: all operational evidence goes through `workspace/` JSON files.
- Evidence-based reporting: every progress report must cite real files, command output, Webflow state, or workspace JSON snippets.
- Deterministic gates: structure, quality, skill, workspace, phase, path, library, secret, and system-spec gates run before completion.
- No silent overwrite: use create-only or documented merge modes.

## 3. Agent Architecture

| Agent | Responsibility |
|---|---|
| `pm` | Coordinate SOP phases, user approvals, specialist handoffs, and reports. |
| `client-first-architect` | Produce Client-First blueprints and QA verdicts. |
| `figma-webflow-operator` | Extract Figma data and execute approved Webflow native builds. |
| `workspace-steward` | Protect archive, restore, workspace initialization, and handoff state. |
| `qa-gatekeeper` | Run deterministic gates and standalone readiness checks. |

## 4. Data and Knowledge

Runtime state:

- `workspace/meta.json`
- `workspace/page_structure.json`
- `workspace/rawdata/`
- `workspace/blueprints/`
- `workspace/contents/`
- `workspace/state.json`
- `workspace/design-system.json`
- `workspace/error-logs.json`

Durable knowledge:

- `knowledge-base/client-first-theory.md`
- `knowledge-base/client-first-class-map.json`
- `agentic/knowledge/`
- `agentic/specs/agent-system-spec.md`
- `agentic/orchestration/`
- `agentic/policies/`

## 5. Webflow and Figma Mandates

- Diagnostic-first: verify site ID, page ID, node ID, and current Webflow state before retrying.
- Snapshot/state-first: inspect before and after Webflow changes.
- Client-First first: reuse existing variables/classes before creating new ones.
- REM only: convert all px values to rem through Python utility logic or explicit calculation.
- Native build only: `whtml_builder` is prohibited.
- MCP-352 required: max 3 nesting levels, max 5 actions per turn, verify every 2 actions.
- Asset uploads are not default. Use temporary stand-ins unless the user approves asset handling.

## 6. Approval Gates

The PM must stop and ask for user approval:

- after blueprint completion,
- before any Webflow write,
- before archive/restore destructive workspace actions,
- before accessing secrets or production-sensitive data.

## 7. Success Definition

The system is working when:

- PM runs the SOP without skipping approval gates,
- operator records extraction/build evidence in workspace JSON,
- architect produces and QA-checks Client-First blueprints,
- gatekeeper passes local Python gates,
- final report is grounded in evidence.

## 8. Build Discipline (mandatory)

Every agent (`pm`, `client-first-architect`, `figma-webflow-operator`, `section-builder`, `qa-gatekeeper`, `workspace-steward`) MUST read and apply `agentic/policies/build-discipline.md` (D-1..D-8) on every MAS run. The 8 patterns are:

- D-1: Write→Bash (no multi-line `python -c` with embedded newlines)
- D-2: No subagents for MCP-dependent work (subagent runtimes in this Claude Code instance do not inherit MCP)
- D-3: EnterPlanMode for any phase with >5 Webflow writes
- D-4: Retry on bash error in same turn (never end a turn on a tool failure)
- D-5: Caveman terse for messages >3 lines
- D-6: Stop after first tool failure; never stack
- D-7: Surface stand-in asset swap path inline
- D-8: Blocker format includes retry count + next action + recoverability

A PreToolUse hook at `.claude/settings.local.json` enforces D-1 by warning on `python -c` with embedded newlines.

- **Mandatory Response Narration**: At the end of every agent response, the agent must append a detailed `### Execution Log` listing each step, tool used, specific command, and result achieved during the turn.
