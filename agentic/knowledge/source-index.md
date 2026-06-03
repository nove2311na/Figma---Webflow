# Source Index

| Source | Type | Role in System |
|---|---|---|
| `README.md` | Local doc | User-facing MAS V3 overview and workflow. |
| `agentic/policies/runtime-instructions.md` | Local mandate | Highest MAS V3 operational rules. |
| `agentic/orchestration/sop.md` | Local SOP | Four-phase workflow and gates. |
| `knowledge-base/client-first-theory.md` | Local knowledge | Finsweet Client-First rules. |
| `agentic/evals/standalone-architecture-baseline.md` | Local baseline | Standalone repo quality and structure target. |
| `knowledge-base/client-first-class-map.json` | Local class library | Structured Client-First class and Figma property mapping catalog. |
| `webflow/webflow-skills` | External skill index | Webflow CLI/code component skill patterns. |
| `OneWave-AI/claude-skills` | External skill index | Agent team, sub-agent orchestration, workflow, and design-system patterns. |

## Reference-Learning Evidence

Reference-learning was performed before scaffold adaptation. The results were distilled into this folder rather than installed or vendored.

Distilled takeaways:

- Webflow work should be split into narrow skills and command surfaces.
- Agent teams need explicit roles, handoffs, and tool boundaries.
- Design-system work should be treated as a first-class artifact.
- Workflow automation needs clear before/after state, gates, and evidence.
- Agentic quality improves when reflection, ReAct traces, phase state, and visual QA evidence are explicit contracts.
