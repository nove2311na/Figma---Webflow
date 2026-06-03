# Reflection Loop

The MAS workflow uses reflection as a bounded review loop before any risky Webflow action is treated as complete.

## Loop Contract

| Step | Owner | Action | Output |
|---|---|---|---|
| Draft | `figma-webflow-operator` or `client-first-architect` | Produce blueprint, build log, or QA report. | Candidate artifact in `workspace/`. |
| Critique | `qa-gatekeeper` or `client-first-architect` | Score against the reflection rubric and current evidence. | `reflection_review` entry in `workspace/state.json`. |
| Revise | Original producer | Apply only the cited fixes. | New artifact version or appended fix entry. |
| Decide | `pm` | Accept, request another loop, or escalate. | Phase status and handoff update. |

## Required Reflection Entry

```json
{
  "type": "reflection_review",
  "agent": "qa-gatekeeper",
  "phase": "phase_1_blueprint",
  "artifact": "workspace/blueprints/home.json",
  "score": 4.6,
  "verdict": "revise",
  "findings": [
    {
      "criterion": "Client-First structure",
      "severity": "major",
      "evidence": "Hero wrapper and content wrapper are merged.",
      "required_fix": "Split section, container, and component layers."
    }
  ],
  "next_decision": "route_to_architect"
}
```

## Stop Conditions

- Pass when the artifact reaches the phase threshold in `agentic/evals/reflection-rubric.md`.
- Stop and escalate after two failed reflection loops on the same issue.
- Stop immediately if the critique lacks evidence paths, screenshots, state references, or Webflow/Figma observations.
- Never convert a reflection pass into Webflow approval. The phase approval gate still applies.

