# Phase State Machine

The PM controls phase movement. Workers can propose state changes, but only the PM records phase decisions.

## States

| State | Entry Condition | Exit Condition |
|---|---|---|
| `phase_0_setup_audit` | New request or resumed workspace. | Workspace, handoff, MCP readiness, and target evidence are known. |
| `phase_1_blueprint` | Figma source or source substitute is accepted. | Blueprint exists and user approval is recorded. |
| `phase_2_webflow_build` | User approval exists for a specific blueprint version. | Webflow action log exists and QA is ready. (Single-operator path or umbrella for 2A/2B.) |
| `phase_2a_class_setup` | User approval exists; build-contract gate passes. | All `new_classes` created and registered; all section containers created with node IDs. |
| `phase_2b_parallel_section_build` | Phase 2A complete (classes + containers exist). | All section action logs present and ready for QA. |
| `phase_3_qa_loop` | Build or fix action is complete. | QA verdict is `[APPROVED]` or unresolved blockers are documented. |
| `handoff_closeout` | Phase completes or session ends. | `agentic/memory/session-handoff.md` is updated. |

## Allowed Transitions

```text
phase_0_setup_audit -> phase_1_blueprint
phase_1_blueprint -> phase_2_webflow_build
phase_1_blueprint -> phase_2a_class_setup
phase_2a_class_setup -> phase_2b_parallel_section_build
phase_2b_parallel_section_build -> phase_3_qa_loop
phase_2_webflow_build -> phase_3_qa_loop
phase_3_qa_loop -> phase_2_webflow_build
phase_3_qa_loop -> phase_2b_parallel_section_build
phase_3_qa_loop -> handoff_closeout
any_phase -> handoff_closeout
```

The parallel-section path (`phase_2a_class_setup -> phase_2b_parallel_section_build`) and the
single-operator path (`phase_2_webflow_build`) are alternatives. Both require the same approval gate.

## Approval Rule

`phase_1_blueprint -> phase_2_webflow_build` and `phase_1_blueprint -> phase_2a_class_setup` are both blocked unless `workspace/state.json` contains an approval entry with:

- `type`: `approval`
- `phase`: `phase_1_blueprint`
- `artifact`: the approved blueprint path
- `message`: contains `Approved`
- `approver`: `user`

## ReAct Rule

Every Webflow mutation in `phase_2_webflow_build` must record:

- `reason`
- `action`
- `observation`
- `next_decision`

This keeps tool use auditable and prevents build steps from becoming unexplained mutations.

