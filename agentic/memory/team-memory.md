# Team Memory

Keep this file concise. Archive older notes into `agentic/memory/archive/` when it grows beyond 200 lines.

## What This Folder Is

This is a standalone Claude-native agentic folder for MAS V3: Figma to Webflow automation using a PM-led multi-agent workflow, Finsweet Client-First V2 rules, workspace JSON chunking, MCP-352 micro-chunking, and evidence-backed QA.

The existing files remain source-of-truth inputs:

- `agentic/policies/runtime-instructions.md`: original MAS V3 mandates adapted for Claude Code.
- `agentic/orchestration/sop.md`: four-phase workflow.
- `README.md`: user-facing system overview.
- `knowledge-base/client-first-theory.md`: Client-First theory.
- `knowledge-base/client-first-class-map.json`: structured Client-First class and Figma property mapping library.
- `scripts/*.py`: active Python workspace lifecycle tools and gates.

## Hard Invariants

1. Standalone baseline is mandatory: this folder must pass `agentic/evals/standalone-architecture-baseline.md`.
2. Agent-system output is mandatory: `agentic/specs/agent-system-spec.md` records seed input, agent system spec, matrix, workflows, gates, and validation report.
3. `@pm` is the only user-facing orchestrator.
4. `@architect` owns blueprint logic and QA; it can reject builds.
5. `@operator` owns Figma extraction and Webflow execution.
6. `workspace/` is the operational state layer. Agents communicate through workspace artifacts, not hidden chat memory.
7. Figma properties must map through `knowledge-base/client-first-class-map.json` before class decisions enter a blueprint.
8. Blueprint approval is a hard stop before Webflow build.
9. No silent overwrite. Existing project files and workspace state are preserved unless a documented gate approves a transition.
10. Webflow external writes are high risk and require explicit workflow phase, target site/page, payload summary, and validation evidence.
11. Secrets belong outside committed files.

## Agent Team

| Agent | Role | Default Access |
|---|---|---|
| `pm` | User-facing orchestrator and phase controller. | read, write plans, run safe gates |
| `client-first-architect` | Blueprint, Client-First class system, layout logic, QA rejection. | read, write blueprints, inspect Webflow |
| `figma-webflow-operator` | Figma extraction and Webflow native build execution. | read/write workspace, external Figma/Webflow when approved |
| `workspace-steward` | Archive, restore, state hygiene, handoff integrity. | read/write workspace lifecycle files |
| `qa-gatekeeper` | Deterministic validation, standalone baseline, final QA report. | read, run gates |

## Current Status

This scaffold is self-contained. Run:

```cmd
python scripts\gates\validate_agentic_structure.py --target .
python scripts\gates\run_quality_gate.py --target .
python scripts\gates\scan_secrets.py --target .
python scripts\gates\validate_agent_system_spec.py --target .
python scripts\gates\validate_skills.py --target .
python scripts\gates\validate_workspace_artifacts.py --target .
python scripts\gates\validate_phase_state.py --target .
python scripts\gates\validate_relative_paths.py --target .
python scripts\gates\validate_client_first_library.py --target .
```

## Memory Promotion

Promote a memory only when it has:

- source file or command evidence,
- date,
- owner,
- validation status,
- reason it should persist.
