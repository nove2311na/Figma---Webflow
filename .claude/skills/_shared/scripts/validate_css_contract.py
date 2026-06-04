import os
import sys
import json

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    contract_path = os.path.join(root_dir, "knowledge-base", "generated", "client-first-library-contract.json")
    print(f"Validating CSS Contract at: {contract_path}")
    
    errors = []
    
    if not os.path.exists(contract_path):
        print("ERROR: client-first-library-contract.json is missing.")
        sys.exit(1)
        
    try:
        with open(contract_path, "r", encoding="utf-8") as f:
            contract = json.load(f)
    except Exception as e:
        print(f"ERROR: Failed to parse contract JSON: {e}")
        sys.exit(1)
        
    # Check CSS hash missing
    source_info = contract.get("source", {})
    if not source_info.get("client_first_css_hash"):
        errors.append("source.client_first_css_hash is missing or empty.")
        
    # Check allowed_classes empty
    allowed_classes = contract.get("allowed_classes", [])
    if not allowed_classes:
        errors.append("allowed_classes array is missing or empty.")
        
    # Check allowed_variables empty
    allowed_variables = contract.get("allowed_variables", [])
    if not allowed_variables:
        errors.append("allowed_variables array is missing or empty.")
        
    # Check known classes missing: button, padding-global, container-large, heading-style-h1, text-size-medium, form_input, nav_component, grid-2-col
    known_classes = ["button", "padding-global", "container-large", "heading-style-h1", "text-size-medium", "form_input", "nav_component", "grid-2-col"]
    for kc in known_classes:
        if kc not in allowed_classes:
            errors.append(f"Expected class '{kc}' is missing from allowed_classes.")
            
    # Check known variables missing: --_layout---spacing--medium, --_layout---spacing--global-padding, --_theme---text-color--primary
    known_variables = ["--_layout---spacing--medium", "--_layout---spacing--global-padding", "--_theme---text-color--primary"]
    for kv in known_variables:
        if kv not in allowed_variables:
            errors.append(f"Expected variable '{kv}' is missing from allowed_variables.")
            
    # Check fs-styleguide_* not marked styleguide-only
    styleguide_classes = contract.get("styleguide_only_classes", [])
    if not styleguide_classes:
        errors.append("styleguide_only_classes array is missing or empty.")
    else:
        for sc in styleguide_classes:
            if not (sc.startswith("fs-styleguide_") or sc.startswith("fs-styleguide")):
                errors.append(f"Class '{sc}' in styleguide_only_classes does not match styleguide name pattern.")
                
    # Check .w-* not marked native/reserved
    reserved_classes = contract.get("reserved_webflow_classes", [])
    if not reserved_classes:
        errors.append("reserved_webflow_classes is empty or missing.")
    else:
        # Some .w- classes should be present
        w_classes = [c for c in reserved_classes if c.startswith("w-")]
        if not w_classes:
            errors.append("No 'w-' prefixed classes found in reserved_webflow_classes.")

    if errors:
        print("\n--- CSS CONTRACT VALIDATION FAILED ---")
        for err in errors:
            print(f"ERROR: {err}")
        sys.exit(1)
    else:
        print("\n--- CSS CONTRACT VALIDATION PASSED ---")
        sys.exit(0)

if __name__ == "__main__":
    main()
