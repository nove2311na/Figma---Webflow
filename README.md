# MAS HTML-First Figma to Webflow Compiler

This folder is a Claude Code-native, Python-first agentic compiler framework for converting Figma design files into Webflow pages with strict Finsweet Client-First V2 conformance.

Unlike previous build architectures, this framework compiles Figma extract bundles into local HTML pages first. It validates class existence, accessibility alts, and Client-First structural wrappers locally, before generating serialized Webflow branch build plans.

## Runtime

- **Primary Agent CLI**: Claude Code.
- **Automation Language**: Python 3.10+.
- **External Connectors**: Webflow MCP and Figma MCP are only engaged under branch-first, approved operations.

## Core Compiler Pipeline

```text
Figma MCP + CSS Contract
→ Client-First Library Contract
→ Figma Extraction Bundle
→ Design-System Sync
→ Component Registry + Signature Matcher
→ Figma Normalized Tree
→ Semantic IR
→ Tag & Class Resolvers
→ Logical HTML Blueprint
→ Local HTML + QA
→ Asset Alt Policy Manifest
→ Sliced Section Chunks
→ Golden Fixtures Benchmarking
→ Webflow Native Build Plan
→ User Approval
→ Webflow Branch Deploys & Audit Logs
```

## Setup & Execution

Use Python 3.10 or newer.

```cmd
# 1. Parse CSS library and build contract
python scripts\index_css_library.py --normalize source-css\normalize.css --webflow source-css\webflow.css --client-first source-css\client-first-v2-2.webflow.css --out knowledge-base\generated

# 2. Normalize raw Figma bundle
python scripts\normalize_figma_nodes.py --input workspace\figma\figma.node-bundle.json

# 3. Resolve Semantic IR tree
python scripts\resolve_semantic_ir.py

# 4. Render local HTML
python scripts\render_html_from_blueprint.py

# 5. Slice page into section chunks
python scripts\slice_html_into_chunks.py

# 6. Compile Webflow build plan
python scripts\compile_native_ops_from_html.py

# 7. Unify gates validation
python scripts\gates\run_quality_gate.py --profile html-first
```

## Non-Negotiable Operating Rules

1. **Contract Binding**: Allowed CSS variables and classes defined by the CSS contract (`client-first-library-contract.json`) are the binding source of truth. Proposing or creating new classes in strict mode blocks compilation.
2. **Local HTML First**: No Webflow writes may occur directly from Figma designs. Elements must compile and pass local HTML gates first.
3. **No whtml_builder**: Webflow structures must be built using native element operations. Injecting raw HTML blocks is prohibited.
4. **Branch-First Mutations**: All Webflow mutations must target temporary site branches. Direct production builds are forbidden.
5. **Serialized Writes**: Concurrency policy serializes Webflow write processes to prevent database lockups.
6. **Audit Trails**: Every Webflow mutation must log payload and status to `write-audit-log.jsonl`.
7. **No Auto-Publish**: Auto-publish is strictly forbidden from the build pipeline. Publishing is manually triggered or gated separately.
8. **REM Units**: Spacing, sizing, and typography must use REM units.
