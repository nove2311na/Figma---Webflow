# System Map

## Layers

| Layer | Paths | Purpose |
|---|---|---|
| Claude-facing | `CLAUDE.md`, `.claude/` | Runtime entrypoint, agents, and skills. |
| Agentic knowledge | `agentic/knowledge`, `agentic/memory`, `agentic/policies`, `agentic/orchestration` | Durable knowledge, memory, policies, workflows, reflection, and phase rules. |
| Artifact contracts | `agentic/specs`, `agentic/schemas` | System spec, scaffold plan, workspace schemas, ReAct trace, and visual QA contracts. |
| Validation | `scripts/gates/` | Deterministic structure, quality, skill, workspace, phase, relative-path, secret, and spec gates. |
| Product/source | `agentic/orchestration/sop.md`, `agentic/policies/runtime-instructions.md`, `scripts/*.py`, `tools/`, `knowledge-base/` | MAS V3 workflow and implementation helpers. |
| Runtime state | `workspace/`, `archives/` | Generated project state and backups. |

## Data Flow

```text
User request
  -> PM
  -> Workspace steward checks state
  -> Operator extracts Figma data
  -> Architect creates blueprint
  -> User approves
  -> Operator builds Webflow via MCP-352
  -> Gatekeeper reflection review
  -> Architect QA
  -> Gatekeeper validates
  -> PM reports and updates handoff
```
