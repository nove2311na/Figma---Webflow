# Reflection Rubric

Use this rubric when a blueprint, Webflow action log, QA report, or handoff needs a second pass before the PM closes a phase.

| Criterion | Weight | 1 | 3 | 5 |
|---|---:|---|---|---|
| Evidence grounding | 20% | Claims lack artifact paths or observations. | Some claims cite workspace files. | Every claim cites Figma, blueprint, Webflow state, snapshot, or gate evidence. |
| Client-First fidelity | 20% | Structure or classes violate core Client-First rules. | Main structure is right with minor naming issues. | Six-layer structure, classes, components, utilities, and REM units are explicit. |
| ReAct trace quality | 20% | Actions are logged without reason or observation. | Most actions include reason and observation. | Every risky action has reason, action, observation, and next decision. |
| Safety and approval | 20% | External write or phase transition bypasses approval. | Approval exists but evidence is thin. | Approval target, payload summary, and phase transition are clear. |
| Revision usefulness | 20% | Feedback is vague or not actionable. | Feedback identifies issues but misses owners or fixes. | Feedback names severity, owner, required fix, and stop condition. |

## Thresholds

- `4.6+`: pass and continue to the next phase gate.
- `4.0-4.59`: revise once, then re-score.
- `<4.0`: block phase movement and route to PM.

Hard failure: any Webflow write without user approval, any missing ReAct field in a mutation log, or any `[APPROVED]` QA verdict without evidence.

