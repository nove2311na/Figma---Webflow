import os
import sys
import json

try:
    import yaml
except ImportError:
    yaml = None

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    print(f"Validating Agentic Structure from Root: {root_dir}")
    
    errors = []
    
    # 1. Folders validation
    folders = [
        "source-css",
        "knowledge-base/generated",
        "agentic/rules",
        "workspace/figma",
        "workspace/semantic",
        "workspace/html/chunks",
        "workspace/webflow-native/section-tasks",
        "workspace/webflow-native/section-results",
        "workspace/reports",
        "tests/fixtures/figma",
        "tests/fixtures/expected",
        "tests/fixtures/broken",
        "tests/goldens"
    ]
    for folder in folders:
        full_path = os.path.join(root_dir, folder)
        if not os.path.isdir(full_path):
            errors.append(f"Required folder missing: {folder}")
            
    # 2. Specs validation
    specs = [
        "agentic/specs/html-first-pipeline.md",
        "agentic/specs/client-first-library-contract.md",
        "agentic/specs/figma-extraction-contract.md",
        "agentic/specs/figma-design-system-contract.md",
        "agentic/specs/figma-normalization-policy.md",
        "agentic/specs/html-tag-resolution.md",
        "agentic/specs/component-registry-contract.md",
        "agentic/specs/component-signature-matching.md",
        "agentic/specs/html-to-webflow-native-ops.md",
        "agentic/specs/asset-and-image-policy.md",
        "agentic/specs/tailwind-trace-to-client-first-evidence.md",
        "agentic/specs/webflow-branch-strategy.md"
    ]
    for spec in specs:
        full_path = os.path.join(root_dir, spec)
        if not os.path.exists(full_path):
            errors.append(f"Required specification file missing: {spec}")
            
    # 3. Rules validation
    rules = [
        "agentic/rules/tag.rules.yaml",
        "agentic/rules/class-selection.rules.yaml",
        "agentic/rules/component-match.rules.yaml",
        "agentic/rules/html-qa.rules.yaml",
        "agentic/rules/figma-normalization.rules.yaml",
        "agentic/rules/asset-alt.rules.yaml",
        "agentic/rules/webflow-native-ops.rules.yaml",
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
        "agentic/schemas/client-first-library-contract.schema.json",
        "agentic/schemas/figma-node-bundle.schema.json",
        "agentic/schemas/figma-extract-run-log.schema.json",
        "agentic/schemas/design-system-sync-report.schema.json",
        "agentic/schemas/component-registry.schema.json",
        "agentic/schemas/component-signature.schema.json",
        "agentic/schemas/component-match-report.schema.json",
        "agentic/schemas/component-sync-report.schema.json",
        "agentic/schemas/figma-normalized-tree.schema.json",
        "agentic/schemas/figma-normalization-report.schema.json",
        "agentic/schemas/figma-semantic-tree.schema.json",
        "agentic/schemas/missing-mapping-report.schema.json",
        "agentic/schemas/html-blueprint.schema.json",
        "agentic/schemas/html-validation-report.schema.json",
        "agentic/schemas/asset-manifest.schema.json",
        "agentic/schemas/alt-policy.schema.json",
        "agentic/schemas/section-manifest.schema.json",
        "agentic/schemas/webflow-native-build-plan.schema.json",
        "agentic/schemas/webflow-section-task.schema.json",
        "agentic/schemas/webflow-write-audit-log.schema.json"
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
    workspace_spec_path = os.path.join(root_dir, "agentic/specs/workspace-artifact-schemas.md")
    if not os.path.exists(workspace_spec_path):
        errors.append("agentic/specs/workspace-artifact-schemas.md is missing.")
    else:
        try:
            with open(workspace_spec_path, "r", encoding="utf-8") as f:
                content = f.read()
                expected_folders = [
                    "workspace/figma/",
                    "workspace/semantic/",
                    "workspace/html/",
                    "workspace/html/chunks/",
                    "workspace/webflow-native/",
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
