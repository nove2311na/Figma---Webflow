# Figma to Webflow Orchestrator References

The orchestrator is a coordinator. It owns only the workspace bootstrap input schema; design-system and HTML contracts stay in their specialist skills.

Workspace bootstrap schema:

- `../schema/webflow-site-data.schema.json` validates `init_workspace.py --site-data` and `--site-data-file`.

When the orchestrator needs to understand a phase in detail, load the corresponding skill's SKILL.md or its references/ on demand:

- **Phase 1 (Sequential contract init)** — load `../design-system-sync/SKILL.md` (specifically Tasks 0–3) and `../design-system-sync/references/`.
- **Phase 2 Branch A (Webflow sync)** — load `../design-system-sync/SKILL.md` (Task 4, including the 🛑 APPROVAL GATE) before issuing any `variable_tool`/`style_tool` call.
- **Phase 2 Branch B (HTML architect)** — load `../figma-to-html-architect/SKILL.md` and dispatch the subagent with the Branch B prompt template from the orchestrator's SKILL.md.

Do not duplicate the specialist skills' content here. The orchestrator stays a thin dispatch layer so that changes to design-system or HTML rules don't require an orchestrator update.

If a project needs a cross-cutting artifact (e.g. an audit log schema that both branches must append to), put it in `audit-log.schema.json` next to this README and link it from both specialist skills.
