# Agent System Spec

## Summary

MAS-Figma-Webflow-khang is a standalone Claude-native, Python-first agentic folder for converting Figma designs into Webflow builds using MAS V3 orchestration, Finsweet Client-First V2 rules, structured class mapping, workspace JSON chunking, MCP-352 micro-chunking, reflection, and strict QA.

## Seed Input

```json
{
  "idea": "Create an AI agentic folder that coordinates PM, architect, and operator agents to convert Figma designs into Webflow pages with Client-First quality.",
  "jobs_to_be_done": [
    "Initialize and preserve project workspace state",
    "Extract Figma raw data and content into chunked workspace files",
    "Produce Client-First Webflow blueprints",
    "Run user approval before Webflow execution",
    "Build in Webflow with native element operations and MCP-352",
    "Run pixel-perfect QA and fix loops",
    "Record evidence, handoff state, and validation reports"
  ],
  "domain": "Figma to Webflow implementation",
  "target_runtime": "claude_code",
  "stack": ["python", "powershell", "webflow-mcp", "figma-source-data"],
  "risk_level": "high",
  "reference_repos": [
    "webflow/webflow-skills",
    "OneWave-AI/claude-skills"
  ],
  "embedded_standards": [
    "standalone_architecture_baseline",
    "agent_system_spec_contract",
    "client_first_class_library",
    "reflection_react_contract",
    "visual_qa_evidence_contract"
  ],
  "required_tools": ["git", "python", "figma", "webflow-mcp"],
  "constraints": [
    "no silent overwrite",
    "no Webflow external write without approval",
    "no whtml_builder",
    "MCP-352 required",
    "REM units only",
    "Client-First V2 structure required",
    "Client-First class mapping library required",
    "workspace JSON evidence required"
  ],
  "success_criteria": [
    "standalone architecture baseline passes",
    "Client-First library gate passes",
    "agent_system_spec contains agents, skills, tools, MCP servers, workflows, memory, gates, scaffold files, and validation report",
    "structure, quality, skill, workspace, phase, path, library, and secret gates pass",
    "PM can run the four SOP phases from one user request"
  ]
}
```

## Agents

| Agent | Role | Trigger | Allowed Tools | Forbidden Actions | Output |
|---|---|---|---|---|---|
| `pm` | User-facing orchestrator and phase controller. | Any user request or phase transition. | Read, write plans/handoff, run safe gates. | Bypass approval, direct Webflow writes, direct QA approval. | Phase report, task requests, handoff. |
| `client-first-architect` | Blueprint and QA owner. | Phase 1 blueprint or Phase 3 QA. | Read/write blueprints, inspect Webflow evidence. | Build in Webflow, approve without evidence. | Blueprint JSON, QA verdict. |
| `figma-webflow-operator` | Figma extraction and Webflow execution. | Phase 1 extraction, Phase 2 build, fix loops. | Read/write workspace, external Figma/Webflow when approved. | Use `whtml_builder`, exceed MCP-352, mutate unknown targets. | Raw/content JSON, state log. |
| `workspace-steward` | Workspace lifecycle and handoff integrity. | Archive, restore, init, page transition. | Workspace scripts and handoff updates. | Delete unarchived state, restore into non-empty workspace. | Lifecycle report. |
| `qa-gatekeeper` | Deterministic gates and standalone readiness. | After scaffold/build/QA report. | Read and run gates. | Edit producer artifacts, mark unchecked gates as pass. | Validation report. |
| `section-builder` | Apply-only build of one section subtree under a given parent node. | Phase 2B parallel section build, one per section. | Native Webflow ops confined to `parent_node_id`, write section action log. | Use `whtml_builder`, create classes/pages/components, write outside its subtree, exceed MCP-352. | Section action log. |

## Skills

| Skill | Purpose | Validation |
|---|---|---|
| `figma-to-webflow-build` | Run the full MAS V3 workflow. | Gate results and handoff update. |
| `client-first-blueprint` | Produce Client-First blueprints from Figma data. | Blueprint evidence and Client-First checks. |
| `mcp-352-webflow-build` | Build in Webflow using native micro-chunks. | State log and QA evidence. |
| `parallel-section-build` | Orchestrate Phase 2A class/container setup then Phase 2B per-section subagents. | Build-contract gate pass and aggregated section logs. |
| `pixel-perfect-qa` | Validate Webflow output against Figma/blueprint. | `[APPROVED]` or `[FIX]` with evidence. |
| `reflection-review` | Critique risky artifacts with a bounded reflection loop. | Pass, revise, or block with score and evidence. |

## Tools

| Tool | Purpose | risk_class | approval_policy | auth_requirements | allowed_agents |
|---|---|---|---|---|---|
| `Read/Grep/Glob` | Local inspection. | R0 | allow | none | all agents |
| `Write/Edit` | Create specs, workspace files, reports. | R1 | ask/create-only | none | pm, architect, operator, steward |
| `python scripts/init_workspace.py` | Initialize workspace. | R1 | ask | none | workspace-steward, pm |
| `python scripts/archive_workspace.py` | Archive and wipe workspace after zip validation. | R4 | explicit approval | none | workspace-steward |
| `python scripts/restore_workspace.py` | Restore archived workspace. | R4 | explicit approval | none | workspace-steward |
| `python scripts/gates/*.py` | Deterministic validation. | R0 | allow | none | qa-gatekeeper, pm |
| `knowledge-base/client-first-class-map.json` | Structured Figma property to Client-First class mapping. | R0 | allow read | none | architect, operator, gatekeeper |
| `Figma API/MCP` | Extract design data. | R2 | ask | Figma token or approved connector | figma-webflow-operator |
| `Webflow MCP` | Inspect and mutate Webflow site. | R3 | explicit approval for writes | Webflow auth | operator, architect for read/QA |

## MCP Servers

| Server | Purpose | risk_class | approval_policy | auth_requirements | allowed_agents | config_path |
|---|---|---|---|---|---|---|
| `webflow` | Webflow inspect/build operations through Claude Code MCP after auth setup. | R3 | ask; writes require explicit phase approval | Webflow OAuth/session | operator, architect read/QA | `agentic/policies/mcp-config.example.json` example |
| `filesystem` | Local project file access. | R0/R1 | allow read, ask write | none | all agents by role | `agentic/policies/mcp-config.example.json` |
| `figma` | Figma data extraction if configured. | R2 | ask | Figma token/OAuth | operator | documented skip until configured |

## Workflows

| Workflow | Trigger | Outputs | retry_limit | stop_conditions | validation_gate |
|---|---|---|---:|---|---|
| `phase_0_setup_audit` | New project or resumed session. | workspace audit, handoff update. | 2 | missing auth/target, unsafe workspace state. | structure + quality gate |
| `phase_1_blueprint` | Figma target confirmed. | raw/content data, blueprint JSON with class mapping. | 2 | blueprint ready for approval, missing Figma data. | blueprint review + client-first library |
| `phase_2_webflow_build` | User approves blueprint. | Webflow state changes, ReAct action log. | 3 | MCP-352 boundary, Webflow failure, QA needed. | state log + phase gate |
| `phase_3_qa_loop` | Build or fix complete. | `[APPROVED]` or `[FIX]`. | 5 | approved, unresolved blocker, repeated failure. | pixel-perfect QA + reflection |
| `handoff_closeout` | Phase complete or session ending. | updated `agentic/memory/session-handoff.md`. | 1 | handoff complete. | quality gate |

## Memory

| Path | kind | owner | promotion_rule |
|---|---|---|---|
| `agentic/knowledge/project-overview.md` | durable knowledge | pm | update when project architecture changes |
| `agentic/knowledge/system-map.md` | durable knowledge | pm | update when workflow/files change |
| `agentic/knowledge/client-first-library.md` | durable knowledge | architect | update when class mapping rules change |
| `knowledge-base/client-first-class-map.json` | structured library | architect | update only with source and gate validation |
| `agentic/memory/memory-candidates.md` | candidate memory | all agents | promote only with source, date, validation |
| `agentic/memory/session-handoff.md` | operational memory | pm | update every phase boundary |
| `workspace/state.json` | runtime log | operator | generated evidence, not durable memory |

## Gates

| Gate | command_or_rule | scope | pass_condition |
|---|---|---|---|
| structure | `python scripts/gates/validate_agentic_structure.py --target .` | repo scaffold | required standalone paths exist |
| quality | `python scripts/gates/run_quality_gate.py --target .` | docs/specs | mandatory phrases and policies present |
| secrets | `python scripts/gates/scan_secrets.py --target .` | committed files | no common secret patterns |
| system spec | `python scripts/gates/validate_agent_system_spec.py --target .` | system spec | required spec sections present |
| skill anatomy | `python scripts/gates/validate_skills.py --target .` | Claude skills | frontmatter, workflow, validation, and resource folders exist |
| workspace artifacts | `python scripts/gates/validate_workspace_artifacts.py --target .` | generated workspace | JSON and ReAct action entries are valid when workspace exists |
| phase state | `python scripts/gates/validate_phase_state.py --target .` | runtime phase log | phase 2 cannot start without user approval |
| relative paths | `python scripts/gates/validate_relative_paths.py --target .` | repo content | no local absolute filesystem paths |
| Client-First library | `python scripts/gates/validate_client_first_library.py --target .` | class catalog | structured class groups and mapping rules exist |
| approval | policy check | workflow | external write has target, payload summary, and approval |

## Scaffold Files

See `agentic/specs/scaffold-file-plan.md`.

## Standalone Architecture Baseline

This folder targets self-contained readiness:

- Structure parity: `CLAUDE.md`, `.claude/`, `agentic/memory/team-memory.md`, `agentic/`, `knowledge-base/`, and `scripts/gates/` exist.
- Quality target: 4.7.
- Exceedance: agent system spec, tool/MCP matrix, workflow contracts, memory promotion, MCP risk map, scaffold file plan, reflection loop, ReAct trace, JSON schemas, visual QA evidence, and Client-First class library exist.
- Runtime specialization: Claude Code-only and Python-first.

## Validation Report

```json
{
  "weighted_score": 4.7,
  "hard_gates": {
    "silent_overwrite_policy": "pass",
    "agent_contracts": "pass",
    "tool_mcp_contracts": "pass",
    "workflow_contracts": "pass",
    "source_index": "pass",
    "output_contract": "pass",
    "standalone_architecture_baseline": "pass",
    "client_first_library": "pass",
    "reflection_react_contract": "pass",
    "skill_anatomy": "pass",
    "relative_paths": "pass"
  },
  "standalone_architecture_baseline": {
    "structure_profile": "standard",
    "expected_structure_validator": "pass",
    "quality_target": 4.7,
    "parity_items": ["CLAUDE.md", "agentic/memory/team-memory.md", ".claude/agents", ".claude/skills", "agentic/policies", "agentic/orchestration", "knowledge-base", "scripts/gates"],
    "exceedance_items": ["agent_system_spec", "tool_mcp_matrix", "workflow_contracts", "mcp_risk_auth_map", "scaffold_file_plan", "reflection_loop", "react_trace", "client_first_library", "json_schemas", "visual_qa_contract"],
    "documented_skips": ["Live .mcp.json is skipped until Webflow/Figma auth is configured"]
  },
  "revision_notes": []
}
```
