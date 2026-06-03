# MCP Risk and Auth Map

| Connector | Purpose | risk_class | Auth | Allowed Agents | Policy |
|---|---|---|---|---|---|
| Webflow MCP | Inspect and mutate Webflow site/page. | R3 | Webflow OAuth/session | operator, architect read/QA | Writes require approved blueprint and PM approval. |
| Figma connector | Extract design data. | R2 | Figma token/OAuth | operator | Read scope must be limited to target file/nodes. |
| Filesystem MCP | Read/write local workspace. | R0/R1 | none | all agents by role | Writes follow no-overwrite policy. |
| Local command runner | Run local Python scripts and gates. | R0/R4 | none | PM, steward, gatekeeper | Destructive scripts require explicit approval. |

`agentic/policies/mcp-config.example.json` is an example only. Configure the live Claude Code Webflow MCP command after auth is approved, and keep credentials outside committed files.
