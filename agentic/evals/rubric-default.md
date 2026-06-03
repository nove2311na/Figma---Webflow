# Default Rubric

| Criterion | Weight | Target |
|---|---:|---|
| Standalone baseline | 12% | Required structure and gates exist without parent-folder dependencies. |
| Agent-system completeness | 14% | Spec includes agents, skills, tools, MCP, workflows, memory, gates, scaffold files. |
| MAS workflow fidelity | 12% | SOP phases, PM orchestration, approval gate, and handoff are preserved. |
| Client-First quality | 12% | Class naming, six-layer structure, REM units, component rules, and class-map usage are explicit. |
| Webflow safety | 14% | External writes require approval, target confirmation, MCP-352, and QA. |
| Evidence discipline | 12% | Workspace JSON evidence and gate output back every report. |
| Reflection and ReAct | 12% | Risky artifacts get reflection review and Webflow actions include reason, action, observation, next decision. |
| Skill and schema discipline | 8% | Skills follow anatomy rules and generated artifacts have JSON schema contracts. |

Hard failures:

- no approval gate before Webflow build,
- no secret policy,
- no QA evidence requirement,
- missing reflection or ReAct evidence for risky Webflow steps,
- missing skill anatomy or schema contracts,
- silent overwrite or unsafe restore,
- use of `whtml_builder`.
