# Tool Risk Levels

| Class | Meaning | Default Policy |
|---|---|---|
| R0 | Local read-only inspection. | allow |
| R1 | Local write inside this folder. | ask unless create-only scaffold or approved workflow file. |
| R2 | External read from Figma/Webflow or web. | ask and log source. |
| R3 | External write to Webflow or messaging tools. | explicit approval per phase and target. |
| R4 | Destructive, archive/delete/restore, secrets, production data. | deny unless explicitly approved and validated. |

Every tool and MCP server must include `risk_class`, approval policy, auth requirements, allowed agents, and validation.

