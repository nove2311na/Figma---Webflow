# Repo Creation Runbook

Use this guide to create another standalone Claude Code agentic repo with the same quality bar as this MAS Figma-to-Webflow folder.

## Goal

Create a self-contained repo that can turn one domain idea into:

- Claude Code entrypoint,
- bounded agents,
- procedural skills,
- domain knowledge library,
- workflow and phase contracts,
- tool and MCP risk policy,
- runtime memory,
- deterministic gates,
- schemas,
- version logs.

## Step 1: Define The Idea Contract

Write the repo idea in `agentic/specs/agent-system-spec.md` with:

- `idea`
- `jobs_to_be_done`
- `domain`
- `target_runtime`
- `stack`
- `risk_level`
- `reference_repos`
- `embedded_standards`
- `required_tools`
- `constraints`
- `success_criteria`

Keep this contract local. Do not depend on parent folders or machine-specific paths.

## Step 2: Create The Minimal Root

Keep root clean:

```text
CLAUDE.md
README.md
LICENSE
pyproject.toml
.gitignore
.claude/
.user_versions/
agentic/
knowledge-base/
scripts/
tools/
```

Move operational docs into `agentic/`:

- agent rules -> `agentic/memory/team-memory.md`
- session handoff -> `agentic/memory/session-handoff.md`
- runtime instructions -> `agentic/policies/runtime-instructions.md`
- SOP -> `agentic/orchestration/sop.md`
- MCP example -> `agentic/policies/mcp-config.example.json`

## Step 3: Build The Agent Team

Create `.claude/agents/*.md`. Each agent must define:

- role,
- trigger,
- allowed tools,
- forbidden actions,
- input contract,
- output contract,
- stop conditions,
- escalation path.

For this repo, the pattern is:

- PM owns user-facing orchestration.
- Architect owns blueprint, domain logic, and QA rejection.
- Operator owns external execution.
- Steward owns workspace lifecycle.
- Gatekeeper owns deterministic validation.

Reuse the pattern, but rename roles for the next domain.

## Step 4: Build Skills With Progressive Disclosure

Create `.claude/skills/<skill-name>/` with:

```text
SKILL.md
references/
scripts/
assets/
```

`SKILL.md` must include frontmatter:

```yaml
---
name: skill-name
description: Clear trigger-oriented description with when to use the skill.
---
```

Required body sections:

- `## Use When`
- `## Workflow`
- `## Validation`

Keep detailed domain references in `references/`, deterministic checks in `scripts/`, and reusable templates in `assets/`.

## Step 5: Add Domain Knowledge As A Library

Do not leave domain knowledge as only prose. Use both:

- `knowledge-base/<domain>-theory.md`
- `knowledge-base/<domain>-map.json`

For this repo:

- theory: `knowledge-base/client-first-theory.md`
- structured map: `knowledge-base/client-first-class-map.json`

For another repo, create the equivalent structured map so agents can turn input properties into implementation decisions.

Example mapping shape:

```json
{
  "input_property": "fontSize",
  "input_value": "64px",
  "target_decision": "heading-style-h1",
  "implementation_property": "font-size",
  "reason": "Hero title is visually H1 scale.",
  "source": "knowledge-base/domain-map.json"
}
```

## Step 6: Define Workflow, Reflection, And Phase Rules

Create:

- `agentic/orchestration/workflow-map.md`
- `agentic/orchestration/sop.md`
- `agentic/orchestration/handoff-contracts.md`
- `agentic/orchestration/retry-and-stop-conditions.md`
- `agentic/orchestration/reflection-loop.md`
- `agentic/orchestration/phase-state-machine.md`

Every risky phase transition must have:

- owner,
- entry condition,
- exit condition,
- approval rule,
- evidence rule,
- retry limit,
- stop condition.

## Step 7: Define Artifact Contracts And Schemas

Create:

- `agentic/specs/workspace-artifact-schemas.md`
- `agentic/schemas/*.schema.json`

Minimum generated artifact set:

- metadata,
- state log,
- domain blueprint or plan,
- error log,
- QA or validation report,
- phase state.

For tool actions, require ReAct fields:

- reason,
- action,
- observation,
- next decision.

## Step 8: Define Policies

Create:

- `agentic/policies/approval-gates.md`
- `agentic/policies/tool-risk-levels.md`
- `agentic/policies/mcp-risk-auth-map.md`
- `agentic/policies/no-overwrite-policy.md`
- `agentic/policies/runtime-instructions.md`

Every external write must include:

- target,
- payload summary,
- approval evidence,
- rollback or recovery plan,
- validation command or artifact.

## Step 9: Add Gates

Create Python gates in `scripts/gates/`:

- `validate_agentic_structure.py`
- `run_quality_gate.py`
- `validate_agent_system_spec.py`
- `validate_skills.py`
- `validate_workspace_artifacts.py`
- `validate_phase_state.py`
- `validate_relative_paths.py`
- domain library gate, such as `validate_client_first_library.py`
- `scan_secrets.py`

Keep gates standard-library only unless the repo truly needs dependencies.

## Step 10: Add Version Logs

Create `.user_versions/`:

- `README.md`
- `VERSION_HISTORY.md`
- one markdown file per version,
- this creation runbook.

Log:

- preserved strengths,
- cleanup decisions,
- new features,
- gates added,
- evidence commands,
- remaining constraints.

## Step 11: Verify Independence

Run:

```cmd
python scripts\gates\validate_agentic_structure.py --target .
python scripts\gates\run_quality_gate.py --target .
python scripts\gates\validate_agent_system_spec.py --target .
python scripts\gates\validate_skills.py --target .
python scripts\gates\validate_workspace_artifacts.py --target .
python scripts\gates\validate_phase_state.py --target .
python scripts\gates\validate_relative_paths.py --target .
python scripts\gates\scan_secrets.py --target .
```

Then run the domain library gate.

For this repo:

```cmd
python scripts\gates\validate_client_first_library.py --target .
```

## Acceptance Checklist

- Root has no unnecessary visible docs.
- No local absolute filesystem paths are embedded in repo files.
- Claude Code is the only intended runtime.
- Python is the automation language.
- Agents have bounded contracts.
- Skills have `SKILL.md`, `references/`, `scripts/`, and `assets/`.
- Domain knowledge has both prose and structured JSON.
- Workflow has approval, reflection, ReAct, and QA evidence.
- Gates pass without external services.
- Version history explains what changed and why.

