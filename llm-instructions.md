# LLM Coding Instructions - MAS HTML-First Figma-to-Webflow Compiler

This file contains coding styles, architectural guidelines, and constraints for AI Agents collaborating on the MAS HTML-First Figma-to-Webflow compiler.

## Core Mandates & Coding Style

1. **Client-First CSS Framework**:
   - Strictly follow Finsweet Client-First V2 principles.
   - The generated contract `knowledge-base/generated/client-first-library-contract.json` is the binding source of truth. Refer to this file for class naming and token variables.
   - Proposing or creating new classes in strict mode blocks compilation.
2. **Spacing & Units**:
   - Always use **REM** units for sizing, typography, margins, padding, and layout spacing. Do not use raw pixel units (`px`) unless explicitly mapping a border-width or similar small value.
3. **Automation Language**:
   - Python is the primary language for workspace automation scripts, quality gates, and data parsers.

## Invariants & Safety Gates

1. **Safety over Speed**:
   - Never silently overwrite existing files. Check if files exist and compare contents.
   - Do not perform external Webflow build actions unless the project blueprint is explicitly approved by the user.
   - External Webflow writes must target site branches and must be serialized to prevent database lockups.
   - Log all executed Webflow mutations to `write-audit-log.jsonl`.
2. **Workspace-Based State**:
   - `workspace/` is the single source of truth for the active run state. Communication and handoffs between agents must be recorded in workspace JSON files.
3. **Validation Gates**:
   - All changes must pass validation gates prior to moving phases. The unified gate runner is:
     - `python scripts/gates/run_quality_gate.py --profile html-first`
