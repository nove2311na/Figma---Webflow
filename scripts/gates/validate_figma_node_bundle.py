import os
import sys
import json

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    figma_dir = os.path.join(root_dir, "workspace", "figma")
    print(f"Validating Figma Node Bundle in: {figma_dir}")
    
    errors = []
    
    node_bundle = os.path.join(figma_dir, "figma.node-bundle.json")
    metadata_file = os.path.join(figma_dir, "metadata.json")
    variable_defs = os.path.join(figma_dir, "variable-defs.json")
    run_log = os.path.join(figma_dir, "extract-run.log")
    
    files_to_check = {
        "figma.node-bundle.json": node_bundle,
        "metadata.json": metadata_file,
        "variable-defs.json": variable_defs,
        "extract-run.log": run_log
    }
    
    for fname, path in files_to_check.items():
        if not os.path.exists(path):
            errors.append(f"Missing file in figma workspace: {fname}")
            continue
            
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            if fname == "figma.node-bundle.json":
                for prop in ["node_id", "name", "tree", "styles", "metadata"]:
                    if prop not in data:
                        errors.append(f"Property '{prop}' is missing from figma.node-bundle.json")
            elif fname == "extract-run.log":
                for prop in ["timestamp", "status", "duration_seconds", "errors", "steps"]:
                    if prop not in data:
                        errors.append(f"Property '{prop}' is missing from extract-run.log")
        except Exception as e:
            errors.append(f"Failed to parse '{fname}' as valid JSON: {e}")
            
    if errors:
        print("\n--- FIGMA NODE BUNDLE VALIDATION FAILED ---")
        for err in errors:
            print(f"ERROR: {err}")
        sys.exit(1)
    else:
        print("\n--- FIGMA NODE BUNDLE VALIDATION PASSED ---")
        sys.exit(0)

if __name__ == "__main__":
    main()
