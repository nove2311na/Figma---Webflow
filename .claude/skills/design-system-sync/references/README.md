# Design System Sync References

Load these on-demand, in this order:

1. **`.user-figma-setup.md`** — Read first. The Finsweet V2.2 source-of-truth list of Figma Variables and Styles that must exist before `validate_figma_extraction.py` can pass. The `validate_figma_extraction.py` script parses this file at runtime; do not rename or restructure it without updating the script.
2. **`figma-webflow-mapping.md`** — Read second. The translation contract that maps Figma names to Webflow (Finsweet) names. Consumed by `map_variables.py` and `validate_figma_extraction.py`; treat the Figma→Webflow name transforms here as authoritative for the project.

Do not duplicate content from these files into the SKILL.md body — load them on demand. If you add project-specific extensions, append a new file (e.g. `mapping-extensions.md`) and link it from here.
