import os
import sys
import json

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
    generated_dir = os.path.join(root_dir, "knowledge-base", "generated")
    print(f"Validating CSS Index files in: {generated_dir}")
    
    indices = [
        "css-variable-index.json",
        "css-class-index.json",
        "css-selector-index.json",
        "css-property-value-index.json",
        "css-breakpoint-index.json",
        "webflow-native-class-index.json"
    ]
    
    errors = []
    
    for idx in indices:
        path = os.path.join(generated_dir, idx)
        if not os.path.exists(path):
            errors.append(f"Missing index file: {idx}")
            continue
            
        try:
            with open(path, "r", encoding="utf-8") as f:
                json.load(f)
        except Exception as e:
            errors.append(f"Failed to parse index file '{idx}' as valid JSON: {e}")
            
    if errors:
        print("\n--- CSS INDEX FILES VALIDATION FAILED ---")
        for err in errors:
            print(f"ERROR: {err}")
        sys.exit(1)
    else:
        print("\n--- CSS INDEX FILES VALIDATION PASSED ---")
        sys.exit(0)

if __name__ == "__main__":
    main()
