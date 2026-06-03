# Workflow Map

## Phase 0: Setup and Audit

Trigger: new project, resumed session, or page transition.

Steps:

1. PM reads `agentic/memory/session-handoff.md`, `agentic/orchestration/sop.md`, and `agentic/policies/runtime-instructions.md`.
2. Workspace steward checks `workspace/` and archive status.
3. Operator scans target Webflow page when configured.
4. PM records phase status and blockers.

Output:

- workspace audit,
- updated handoff,
- target IDs or documented missing auth.

Stop conditions:

- unarchived workspace data,
- missing target Figma/Webflow details,
- missing approval for external reads.

## Phase 1: Blueprint Establishment

Trigger: Figma target confirmed.

Steps:

1. Operator extracts raw Figma data.
2. Operator writes content JSON.
3. Architect creates Client-First blueprint.
4. PM presents blueprint to user.

Output:

- `workspace/rawdata/*.json`,
- `workspace/contents/*.json`,
- `workspace/blueprints/*.json`,
- user approval request.

Stop condition:

- wait for user `Approved` or `Agree`.

## Phase 2: Webflow Execution

Trigger: user approves blueprint.

Steps:

1. Operator confirms Webflow site/page.
2. Operator takes pre-build state/snapshot.
3. Operator builds with MCP-352.
4. Operator logs state.

Output:

- Webflow changes,
- `workspace/state.json`.

Stop conditions:

- verification boundary,
- tool failure,
- QA required.

## Phase 3: QA Loop

Trigger: build or fix complete.

Steps:

1. Architect inspects actual Webflow state/snapshot.
2. Architect compares against blueprint and Figma.
3. Architect returns `[APPROVED]` or `[FIX]`.
4. PM routes fixes or reports completion.

Output:

- QA verdict,
- `workspace/error-logs.json`,
- updated `agentic/memory/session-handoff.md`.
