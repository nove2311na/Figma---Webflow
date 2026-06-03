# Design System Sync Scripts

This directory contains the core Python scripts that power the `[new]-design-system-sync` skill. These scripts act as the "Fast Path" and the "Safety Net" for the Agent, saving LLM tokens and ensuring strict data integrity when migrating variables and styles from Figma to Webflow.

## 1. `validate_figma_extraction.py` (The Safety Gate)

**Purpose:** 
Ensures that the designer has properly set up the design system in Figma before the Agent attempts to sync it to Webflow.

**How it works:**
- It reads the `.user-figma-setup.md` file (which contains the exhaustive list of required Figma Variables and Styles based on the Finsweet V2.2 Source of Truth).
- It compares that list against the data just extracted from Figma (usually saved to `workspace/figma-design-system-contract.md`).
- If any variables are missing, it halts the pipeline, throwing a clear error listing exactly what the designer forgot to add in Figma.
- If everything is present, it returns a `PASSED` status, allowing the pipeline to proceed to the translation phase.

**Usage:**
```bash
python validate_figma_extraction.py --contract <path/to/extracted/file> --guide <path/to/user/guide>
```

---

## 2. `map_variables.py` (The Fast Path Translator)

**Purpose:**
Translates the Figma-formatted design system contract into a Webflow-formatted (Finsweet V2.2) design system contract instantly, bypassing the need for the LLM to manually translate hundreds of lines.

**How it works:**
- It reads the `workspace/figma-design-system-contract.md`.
- It applies deterministic string manipulation rules (e.g., converting `Theme / Background / Primary` ➔ `--_theme---background--primary` by converting to lowercase, replacing slashes with triple-hyphens, etc.).
- It outputs the results directly into `workspace/webflow-design-system-contract.md`.
- **Note:** This is currently a mock implementation scaffolding. The actual mapping logic needs to be fully implemented to execute the string replacement automatically.

**Usage:**
```bash
python map_variables.py --input <path/to/figma/contract> --output <path/to/webflow/contract> --mapping <path/to/mapping/rules>
```
