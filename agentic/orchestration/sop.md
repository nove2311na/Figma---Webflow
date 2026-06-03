# Standard Operating Procedure (SOP)

This SOP details the operational steps for Agents building Webflow sites from Figma via the modern 3-phase MCP pipeline.

## 1. Safety & Context Verification
- Check that the `workspace/figma/` and `workspace/semantic/` folders exist.
- Verify access to the **Figma MCP Server** and **Webflow MCP Server**.

## 2. Execution Flow

### Step A: Extract
Run the extraction routine to pull raw context from Figma:
```bash
python scripts/pipeline/extract_raw_styling.py --input workspace/figma/figma.raw-context.json
```
- **Goal:** Ensure `raw-layout-blueprint.json` and `raw-inline.html` are correctly generated.

### Step B: Translate
Run the Client-First translation routine:
```bash
python scripts/pipeline/resolve_client_first.py --input workspace/figma/raw-layout-blueprint.json
```
- **Goal:** Generate the `figma.semantic-tree.json` output which maps inline styles to standardized Finsweet classes and variables.

### Step C: Audit
Review the output of the translation logic.
- Ensure the missing-mapping-report (`workspace/reports/missing-mapping-report.json`) is free of critical failures.
- If unmapped styles or orphaned tokens exist, update `client-first-class-map.json` or consult the user.

### Step D: Synchronize (Webflow MCP)
Instruct the Webflow Sync Agent to read `figma.semantic-tree.json` and execute the push to Webflow using the MCP server.
- The agent must strictly follow the rules in `agentic/rules/webflow-mcp.rules.yaml`.
- The agent must use `agentic/knowledge/component-registry.json` to link recognized Symbols.

### Step E: Quality Gate
Run the standard validation suite:
```bash
python scripts/gates/run_quality_gate.py --profile html-first
```
- **Goal:** All structural, CSS contract, and index tests must PASS.

## 3. Deployment Approval
Once Phase 1 through 3 are complete and Quality Gates pass:
1. Provide the user with the Webflow Sync Report (`mcp-sync-report.json`).
2. Ask for explicit approval before triggering the Webflow Site Publish action.
