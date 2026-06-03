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
