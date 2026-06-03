import os
import sys
import json

try:
    import yaml
except ImportError:
    yaml = None

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    print(f"Validating Agentic Structure from Root: {root_dir}")
    
    errors = []
    
    # 1. Folders validation
    folders = [
        "source-css",
        "knowledge-base/generated",
        "agentic/rules",
        "agentic/knowledge",
        "workspace/figma",
        "workspace/semantic",
        "workspace/reports",
    ]
    for folder in folders:
        full_path = os.path.join(root_dir, folder)
        if not os.path.isdir(full_path):
            errors.append(f"Required folder missing: {folder}")
            
    # 2. Specs validation
    specs = [
        "agentic/specs/pipeline/html-first-pipeline.md",
        "agentic/specs/pipeline/webflow-mcp-sync.md",
        "agentic/specs/pipeline/figma-extraction-contract.md",
        "agentic/specs/pipeline/html-tag-resolution.md",
        "agentic/specs/pipeline/asset-and-image-policy.md",
        "agentic/specs/pipeline/webflow-branch-strategy.md",
        "agentic/specs/contracts/client-first-library-contract.md",
        "agentic/specs/contracts/visual-qa-evidence-contract.md",
        "agentic/specs/system/agent-system-spec.md",
        "agentic/specs/system/workspace-artifact-schemas.md"
    ]
    for spec in specs:
        full_path = os.path.join(root_dir, spec)
        if not os.path.exists(full_path):
            errors.append(f"Required specification file missing: {spec}")
            
    # 3. Rules validation
    rules = [
        ".claude/skills/[new]-semantic-html-resolver/rules/tag.rules.yaml",
        "agentic/rules/webflow-mcp.rules.yaml",
        "agentic/rules/class-selection.rules.yaml",
        "agentic/rules/html-qa.rules.yaml",
        "agentic/rules/asset-alt.rules.yaml",
        "agentic/rules/concurrency-policy.yaml",
        "agentic/rules/retry-policy.yaml"
    ]
    for rule in rules:
        full_path = os.path.join(root_dir, rule)
        if not os.path.exists(full_path):
            errors.append(f"Required rule file missing: {rule}")
        else:
            if yaml is not None:
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        yaml.safe_load(f)
                except Exception as e:
                    errors.append(f"Invalid YAML in rule file {rule}: {e}")
            else:
                try:
                    with open(full_path, "r", encoding="utf-8") as f:
                        content = f.read()
                        if ":" not in content:
                            errors.append(f"Rule file {rule} does not seem to contain valid colon mappings.")
                except Exception as e:
                    errors.append(f"Cannot read rule file {rule}: {e}")
                    
    # 4. Schemas validation (Valid JSON)
    schemas = [
        # Figma pipeline schemas
        # Semantic schemas
        "agentic/schemas/semantic/semantic-tree.schema.json",
        # HTML pipeline schemas
        "agentic/schemas/html/alt-policy.schema.json",
        # Webflow schemas
        "agentic/schemas/webflow/mcp-sync-report.schema.json",
        "agentic/schemas/webflow/webflow-write-audit-log.schema.json",
        # Library schemas
        "agentic/schemas/library/client-first-library-contract.schema.json",
        "agentic/schemas/library/client-first-library.schema.json",
        # Component schemas
        # Design-system schemas
    ]
    for schema in schemas:
        full_path = os.path.join(root_dir, schema)
        if not os.path.exists(full_path):
            errors.append(f"Required schema file missing: {schema}")
        else:
            try:
                with open(full_path, "r", encoding="utf-8") as f:
                    json.load(f)
            except Exception as e:
                errors.append(f"Invalid JSON in schema file {schema}: {e}")
                
    # 5. pyproject.toml dependencies check
    pyproject_path = os.path.join(root_dir, "pyproject.toml")
    required_deps = ["tinycss2", "pydantic", "typer", "beautifulsoup4"]
    if not os.path.exists(pyproject_path):
        errors.append("pyproject.toml is missing.")
    else:
        try:
            with open(pyproject_path, "r", encoding="utf-8") as f:
                content = f.read()
                for dep in required_deps:
                    if dep not in content:
                        errors.append(f"Dependency '{dep}' not documented in pyproject.toml")
        except Exception as e:
            errors.append(f"Cannot read pyproject.toml: {e}")
            
    # 6. workspacespec check
    workspace_spec_path = os.path.join(root_dir, "agentic/specs/system/workspace-artifact-schemas.md")
    if not os.path.exists(workspace_spec_path):
        errors.append("agentic/specs/system/workspace-artifact-schemas.md is missing.")
    else:
        try:
            with open(workspace_spec_path, "r", encoding="utf-8") as f:
                content = f.read()
                expected_folders = [
                    "workspace/figma/",
                    "workspace/semantic/",
                    "workspace/html/",
                    "workspace/reports/"
                ]
                for fld in expected_folders:
                    if fld not in content:
                        errors.append(f"New workspace folder '{fld}' not documented in workspace-artifact-schemas.md")
        except Exception as e:
            errors.append(f"Cannot read workspace-artifact-schemas.md: {e}")
            
    if errors:
        print("\n--- AGENTIC STRUCTURE VALIDATION FAILED ---")
        for err in errors:
            print(f"ERROR: {err}")
        sys.exit(1)
    else:
        print("\n--- AGENTIC STRUCTURE VALIDATION PASSED ---")
        sys.exit(0)

if __name__ == "__main__":
    main()
