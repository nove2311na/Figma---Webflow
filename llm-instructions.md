# LLM Coding Instructions - MAS V3 Figma-to-Webflow

This file contains coding styles, architectural guidelines, and constraints for AI Agents collaborating on the MAS V3 Figma-to-Webflow automation project.

## Core Mandates & Coding Style

1. **Client-First CSS Framework**:
   - Strictly follow Finsweet Client-First V2 principles.
   - Map Figma styles to Client-First class structures. Refer to `knowledge-base/client-first-class-map.json` for class naming.

2. **Spacing & Units**:
   - Always use **REM** units for sizing, typography, margins, padding, and layout spacing. Do not use raw pixel units (`px`) unless explicitly mapping a border-width or similar small value.

3. **Automation Language**:
   - Python is the primary language for workspace automation scripts, quality gates, and data parsers.

## Invariants & Safety Gates

1. **Safety over Speed**:
   - Never silently overwrite existing files. Check if files exist and compare contents.
   - Do not perform external Webflow build actions unless the project blueprint is explicitly approved by the user.
   - External Webflow writes must log a detailed reason, payload summary, and execution confirmation inside the workspace.

2. **Workspace-Based State**:
   - `workspace/` is the single source of truth for the active run state. Communication and handoffs between agents must be recorded in workspace JSON files (e.g., `workspace/state.json`, `workspace/blueprints/`).

3. **Validation Gates**:
   - All changes must pass validation gates prior to moving phases:
     - Structure: `python scripts/gates/validate_agentic_structure.py`
     - Quality: `python scripts/gates/run_quality_gate.py`
     - Spec validation: `python scripts/gates/validate_agent_system_spec.py`
