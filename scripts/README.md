# scripts/

Python scripts grouped by purpose.

## Pipeline scripts (`/` root — run in order)

These are the compiler pipeline steps. Run them in sequence:

```cmd
# Step 1: Parse CSS to build contract
python scripts\index_css_library.py

# Step 2: Normalize Figma nodes
python scripts\normalize_figma_nodes.py

# Step 3: Resolve semantic roles and classes
python scripts\resolve_semantic_ir.py

# Step 4: Render HTML from blueprint
python scripts\render_html_from_blueprint.py

# Step 5: Slice page into chunks
python scripts\slice_html_into_chunks.py

# Step 6: Compile native Webflow ops plan
python scripts\compile_native_ops_from_html.py
```

Other pipeline scripts:
- `match_components.py` — Component signature matching
- `sync_library_to_webflow.py` — Print MCP sync instructions for LLM
- `update_library_from_figma.py` — Update per-project library from Figma data

## Workspace lifecycle scripts (`/` root)

```cmd
python scripts\init_workspace.py          # Initialize workspace for a new project
python scripts\archive_workspace.py       # Snapshot current workspace
python scripts\restore_workspace.py       # Restore workspace from snapshot
python scripts\restore_workspace.py 0     # Restore from specific version
```

## Validation gates (`gates/`)

See `scripts/gates/README.md` for full list. Run the unified profile:

```cmd
python scripts\gates\run_quality_gate.py --profile html-first
```

## Hooks (`hooks/`)

Git and tool hooks for pre-commit validation.
