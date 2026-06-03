# Scaffold File Plan

Default write mode: `create_only`.

| Path | Kind | Owner | Source Template | Write Mode | Validation |
|---|---|---|---|---|---|
| `CLAUDE.md` | file | seed system | V2 Claude entrypoint | create_only | quality gate |
| `agentic/memory/team-memory.md` | file | seed system | V2 team memory | create_only | structure gate |
| `agentic/memory/session-handoff.md` | file | PM | MAS handoff template | create_only | quality gate |
| `.gitignore` | file | seed system | local runtime ignore template | create_only | secret gate |
| `agentic/policies/mcp-config.example.json` | file | seed system | MCP risk-mapped example | create_only | JSON parse |
| `.claude/settings.json.example` | file | seed system | Claude settings example | create_only | JSON parse |
| `.claude/agents/*.md` | file | seed system | V2 agent contract | create_only | structure gate |
| `.claude/skills/*/SKILL.md` | file | seed system | V2 skill contract | create_only | quality gate |
| `agentic/specs/agent-system-spec.md` | file | system-architect | generated spec | create_only | system spec gate |
| `agentic/specs/workspace-artifact-schemas.md` | file | system-architect | V3 artifact contract | create_only | workspace artifact gate |
| `agentic/specs/visual-qa-evidence-contract.md` | file | QA gatekeeper | V3 QA contract | create_only | quality gate |
| `agentic/schemas/*.schema.json` | file | system-architect | V3 JSON schema pack | create_only | JSON parse |
| `agentic/policies/*.md` | file | gatekeeper | policy templates | create_only | quality gate |
| `agentic/orchestration/*.md` | file | workflow-designer | workflow contracts | create_only | quality gate |
| `scripts/gates/*.py` | file | gatekeeper | deterministic gates | create_only | py_compile |
| `.user_versions/*.md` | file | PM | version log | create_only | relative path gate |

Existing files preserved:

- `README.md`
- `agentic/policies/runtime-instructions.md`
- `agentic/orchestration/sop.md`
- `knowledge-base/client-first-theory.md`

Files removed during Claude Code-only cleanup:

- non-Claude runtime instructions,
- standalone PM pointer replaced by `.claude/agents/pm.md`,
- workspace scripts from the previous automation runtime,
- previous utility module replaced by `tools/utils.py`.
