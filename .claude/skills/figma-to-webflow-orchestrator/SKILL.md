---
name: figma-to-webflow-orchestrator
description: Use this skill when starting a full Figma→Webflow migration — it coordinates design-system sync and HTML architect in parallel, requires explicit user approval before any live Webflow write, and consolidates the branch outputs into a single evidence-backed completion report.
---

# Figma to Webflow Parallel Orchestrator

## 🎯 Goal
Execute the entire Figma-to-Webflow translation pipeline with maximum efficiency. It parallelizes the slow Webflow API sync process and the local section/page HTML extraction/parsing process by spawning a specialized subagent.

## 🚀 Usage
Invoke this command in chat:
`/project:figma-to-webflow-orchestrator <workspace-name> <node-id>`

*Example:* `/project:figma-to-webflow-orchestrator my-project 1003-521`

### Deterministic Orchestration Script (CLI alternative)
You can run all deterministic steps (Phase 1, Phase 2 Branch B) directly using the following CLI script:
```bash
python .claude/skills/figma-to-webflow-orchestrator/scripts/orchestrate.py --workspace <workspace-name> --node-id <node-id>
```
*Note: Steps requiring Figma MCP or Webflow MCP (Tasks 1 & 4 of design-system-sync, plus Figma raw HTML extraction in Branch B) are left to the LLM agent.*

### Workspace Bootstrap Input Schema
When bootstrapping a workspace with `init_workspace.py`, validate `--site-data` / `--site-data-file` against:

- `.claude/skills/figma-to-webflow-orchestrator/schema/webflow-site-data.schema.json`

The accepted input is one Webflow site object or an array of site objects from Webflow MCP `data_sites_tool` / `get_site`. Each item must include `id` or `siteId`; `shortName`, `displayName`, and `figmaFileKey` are optional.

---

## 📋 Orchestration Workflow

When this skill is triggered, parse `$ARGUMENTS` to extract:
1. `<workspace-name>` (e.g., `my-project`)
2. `<node-id>` (e.g., `1003-521`)

Follow the steps below to orchestrate the pipeline:

### Phase 1: Initialize Contracts (Sequential)
To prevent race conditions, the design system contracts must be created first:
1.  **Extract Figma Variables**: Trigger **Task 1** of `design-system-sync` to output `workspace/<workspace-name>/design-system/figma-design-system.json`.
2.  **Safety Gate Validation**: Run the extraction validation:
    ```bash
    python .claude/skills/design-system-sync/scripts/validate_figma_extraction.py --workspace <workspace-name>
    ```
    *If it fails, halt the pipeline and request the user/designer to fix the missing variables in Figma.*
3.  **Generate Translation Contract**: Run the variable mapping script to output `workspace/<workspace-name>/design-system/webflow-design-system.json`:
    ```bash
    python .claude/skills/design-system-sync/scripts/map_variables.py --workspace <workspace-name>
    ```

**Webflow contract policy**: The canonical Webflow contract template at `.claude/skills/design-system-sync/template/webflow-design-system-contract.json` is the allowed contract for validation and mapping. No CSS source file is required in this pipeline.

---

### Phase 2: Parallel Processing (Fork)
Once the `webflow-design-system.json` is generated, spawn a subagent and run the two branches concurrently:

#### Branch A: Main Agent (Sync to Webflow API)
*Proceed with Task 5 and Task 6 of `design-system-sync` in the background:*
*   Read `workspace/<workspace-name>/design-system/webflow-design-system.json`.
*   **🛑 APPROVAL GATE**: Before any `variable_tool` or `style_tool` call, render a preview, write `webflow-sync-preview.json`, append to `write-audit-log.jsonl`, and STOP for user `approve`/`revise`/`cancel`. See `design-system-sync` Task 4 for the full gate protocol.
*   **Branch-first Deployments**: Write to `ws/<workspace-name>/<run-id>` only. Never to the production branch.
*   Iterate and call Webflow MCP tools (`variable_tool` and `style_tool`) to sync the variables and styles to the Webflow branch.
*   *Note: Since Webflow API calls are sequential and slow, continue to Phase 3 only after Webflow is fully synced.*

#### Branch B: Subagent (Figma to HTML Architect)
*Spawn a subagent to parse the section/page HTML. Instruct the subagent with the following prompt:*
> **Task Description for Subagent:**
> You are the Figma to HTML Architect. Your task is to process the Figma section/page node `<node-id>` for workspace `<workspace-name>` by following the `figma-to-html-architect` skill.
> 
> **Instructions:**
> 1. Extract raw HTML from Figma MCP: `get_design_context` with nodeId `<node-id>`. Save it to `workspace/<workspace-name>/html-nodes/<node-id>/raw-figma.html`.
> 2. Run the layer naming validator:
>    `python .claude/skills/figma-to-html-architect/scripts/validate_figma_html.py --workspace <workspace-name> --node-id <node-id>`
>    *If validation fails, delete the raw-figma.html, write a failure report, and exit.*
> 3. Run the semantic & class parser:
>    `python .claude/skills/figma-to-html-architect/scripts/process_html.py --workspace <workspace-name> --node-id <node-id>`
> 4. Verify that `workspace/<workspace-name>/html-nodes/<node-id>/final-webflow.html` is generated successfully. Return a status report.

---

## 📚 Knowledge Lookup

This skill coordinates the other two. The knowledge base is the contract between them. Before forking, consult the index for the topic tags each branch needs:

- **Branch A (sync)**: `figma`, `webflow`, `variables`, `modes`, `alias-chains`, `stable-id`, `multi-machine`, `sync-drift`
- **Branch B (architect)**: `utility`, `combo`, `custom`, `semantic-html`, `a11y`, `responsive`, `layout`, `forms`, `grid`, `rem`, `widget-conflict`
- **Cross-cutting**: `components` (concepts/11), `naming-convention` (concepts/00)

**How to use**: read `agentic/knowledge/client-first/INDEX.yaml`, filter by `applicable_skill`, pull 1-3 files per branch. Never full-dump.

```bash
python -c "
import yaml
d = yaml.safe_load(open('agentic/knowledge/client-first/INDEX.yaml'))
for e in d['entries']:
    if 'figma-to-webflow-orchestrator' in e.get('applicable_skill',[]):
        print(f\"  - {e['file_path']}  [section: {e.get('section','?')}]\")
"
```

---

### Phase 3: Consolidation (Join)
Once both **Branch A** (Webflow sync complete) and **Branch B** (Subagent report returned) are finished:
1.  Verify the integrity of `workspace/<workspace-name>/html-nodes/<node-id>/final-webflow.html`.
2.  Print a summary of variables synced, classes created, and HTML files processed.
3.  Notify the user that the section/page HTML is fully ready and validated.

---

## 🛡️ Policies & Constraints
- Concurrency, retry-handling, and Webflow MCP limits are specified in:
  - [concurrency-policy.yaml](agentic/rules/concurrency-policy.yaml) (Serial write lock and concurrency configurations)
  - [retry-policy.yaml](agentic/rules/retry-policy.yaml) (API retry/backoff parameters)
  - [webflow-mcp.rules.yaml](agentic/rules/webflow-mcp.rules.yaml) (Webflow MCP API usage limits)
- Webflow JSON Schemas are indexed in [schema_index.json](agentic/schemas/webflow/schema_index.json).
