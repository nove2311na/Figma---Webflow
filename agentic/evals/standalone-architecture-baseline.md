# Standalone Architecture Baseline

This local baseline records the minimum structure this repo must keep when it is used independently.

## Baseline Checks

- [x] `CLAUDE.md` exists and names commands, safety rules, and workflow.
- [x] `agentic/memory/team-memory.md` exists and records team memory/invariants.
- [x] `.claude/agents/` contains bounded roles.
- [x] `.claude/skills/` contains procedural skills.
- [x] `agentic/README.md` exists.
- [x] `agentic/knowledge/` exists.
- [x] `agentic/memory/` exists.
- [x] `agentic/policies/` exists.
- [x] `agentic/orchestration/` exists.
- [x] `scripts/gates/` exists.
- [x] Structure, quality, and secret scan gates exist.
- [x] No silent overwrite policy exists.

## Agentic Completeness Checks

- [x] `agentic/specs/agent-system-spec.md` exists.
- [x] Agent/skill/tool/MCP matrix is in the system spec.
- [x] Workflow contracts include retry limits and stop conditions.
- [x] MCP risk and auth map exists.
- [x] Memory promotion rule exists.
- [x] Scaffold file plan includes owner, write mode, source template, and validation.
- [x] Reflection and ReAct contracts exist.
- [x] Structured Client-First class library exists.
- [x] Workspace artifact schemas exist.
- [x] Version history exists.

## Score Targets

- Structure validator: pass standard profile.
- Quality rubric target: 4.7.
- All local gates: pass.
