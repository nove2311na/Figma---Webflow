# Design System Sync References

Load these on-demand, in this order:

1. **`../template/figma-design-system-contract.json`** — Read first when preparing a Figma file. The Figma file must expose the same variable and style keys so `build_figma_design_system.py` can overlay MCP values without inventing data.
2. **`figma-webflow-mapping.md`** — Read second. The translation contract that maps Figma names to Webflow names. Consumed by `map_variables.py` and `validate_figma_extraction.py`; treat the Figma-to-Webflow name transforms here as authoritative for the project.

Do not duplicate content from these files into the SKILL.md body — load them on demand. If you add project-specific extensions, append a new file (e.g. `mapping-extensions.md`) and link it from here.
