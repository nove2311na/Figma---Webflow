# agentic/prompts/

Agent prompts are grouped by pipeline stage.

| Folder | Purpose |
|---|---|
| `extraction/` | Prompts for reading Figma data, extracting context, and syncing design system variables |
| `normalization/` | Prompts for normalizing Figma nodes and converting to Semantic IR |
| `resolution/` | Prompts for resolving HTML tags, selecting Client-First classes, and generating the CSS library |
| `webflow/` | Prompts for building Webflow sections from native ops and QA-ing the built DOM against HTML blueprint |

## Pipeline Flow

```
extraction/ → normalization/ → resolution/ → (HTML rendered locally) → webflow/
```
