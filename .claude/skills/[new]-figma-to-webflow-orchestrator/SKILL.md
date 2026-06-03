---
name: figma-to-webflow-orchestrator
description: Parallel orchestrator for Figma-to-Webflow migration. Syncs Design Systems and translates HTML concurrently using subagents.
---

# Figma to Webflow Parallel Orchestrator

## 🎯 Goal
Execute the entire Figma-to-Webflow translation pipeline with maximum efficiency. It parallelizes the slow Webflow API sync process and the local HTML extraction/parsing process by spawning a specialized subagent.

## 🚀 Usage
Invoke this command in chat:
`/project:figma-to-webflow-orchestrator <workspace-name> <node-id>`

*Example:* `/project:figma-to-webflow-orchestrator my-project 1003-521`

---

## 📋 Orchestration Workflow

When this skill is triggered, parse `$ARGUMENTS` to extract:
1. `<workspace-name>` (e.g., `my-project`)
2. `<node-id>` (e.g., `1003-521`)

Follow the steps below to orchestrate the pipeline:

### Phase 1: Initialize Contracts (Sequential)
To prevent race conditions, the design system contracts must be created first:
1.  **Extract Figma Variables**: Trigger **Task 1** of `[new]-design-system-sync` to output `workspace/<workspace-name>/design-system/figma-contract.json`.
2.  **Safety Gate Validation**: Run the extraction validation:
    ```bash
    python .claude/skills/[new]-design-system-sync/scripts/validate_figma_extraction.py --workspace <workspace-name>
    ```
    *If it fails, halt the pipeline and request the user/designer to fix the missing variables in Figma.*
3.  **Generate Translation Contract**: Run the variable mapping script to output `workspace/<workspace-name>/design-system/webflow-contract.json`:
    ```bash
    python .claude/skills/[new]-design-system-sync/scripts/map_variables.py --workspace <workspace-name>
    ```

---

### Phase 2: Parallel Processing (Fork)
Once the `webflow-contract.json` is generated, spawn a subagent and run the two branches concurrently:

#### Branch A: Main Agent (Sync to Webflow API)
*Proceed with Task 4 of `[new]-design-system-sync` in the background:*
*   Read `workspace/<workspace-name>/design-system/webflow-contract.json`.
*   Iterate and call Webflow MCP tools (`variable_tool` and `style_tool`) to sync the variables and styles to the live Webflow project.
*   *Note: Since Webflow API calls are sequential and slow, continue to Phase 3 only after Webflow is fully synced.*

#### Branch B: Subagent (Figma to HTML Architect)
*Spawn a subagent to parse the component HTML. Instruct the subagent with the following prompt:*
> **Task Description for Subagent:**
> You are the Figma to HTML Architect. Your task is to process the Figma node `<node-id>` for workspace `<workspace-name>` by following the `[new]-figma-to-html-architect` skill.
> 
> **Instructions:**
> 1. Extract raw HTML from Figma MCP: `get_design_context` with nodeId `<node-id>`. Save it to `workspace/<workspace-name>/components/<node-id>/raw-figma.html`.
> 2. Run the layer naming validator:
>    `python .claude/skills/[new]-figma-to-html-architect/scripts/validate_figma_html.py --workspace <workspace-name> --node-id <node-id>`
>    *If validation fails, delete the raw-figma.html, write a failure report, and exit.*
> 3. Run the semantic & class parser:
>    `python .claude/skills/[new]-figma-to-html-architect/scripts/process_html.py --workspace <workspace-name> --node-id <node-id>`
> 4. Verify that `workspace/<workspace-name>/components/<node-id>/final-webflow.html` is generated successfully. Return a status report.

---

### Phase 3: Consolidation (Join)
Once both **Branch A** (Webflow sync complete) and **Branch B** (Subagent report returned) are finished:
1.  Verify the integrity of `workspace/<workspace-name>/components/<node-id>/final-webflow.html`.
2.  Print a summary of variables synced, classes created, and HTML files processed.
3.  Notify the user that the component is fully ready and validated.
