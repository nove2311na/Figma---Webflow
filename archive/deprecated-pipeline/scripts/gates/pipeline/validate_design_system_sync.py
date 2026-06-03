import os
import sys
import json

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    report_path = os.path.join(root_dir, "workspace", "reports", "design-system-sync-report.json")
    print(f"Validating Design System Sync Report at: {report_path}")
    
    errors = []
    
    if not os.path.exists(report_path):
        errors.append(f"Sync report is missing: design-system-sync-report.json. Run sync command first.")
    else:
        try:
            with open(report_path, "r", encoding="utf-8") as f:
                report = json.load(f)
                
            # Perform strict validation
            for prop in ["timestamp", "matched_tokens", "missing_tokens", "unmapped_styles", "hardcoded_values", "blockers", "status"]:
                if prop not in report:
                    errors.append(f"Property '{prop}' is missing from design-system-sync-report.json")
                    
            status = report.get("status", "")
            if status != "pass":
                errors.append(f"Sync status is '{status}' (must be 'pass')")
                
            blockers = report.get("blockers", [])
            if blockers:
                errors.append(f"Sync report contains blockers: {blockers}")
                
            missing_tokens = report.get("missing_tokens", [])
            if missing_tokens:
                errors.append(f"Sync report contains missing tokens: {missing_tokens}")
                
        except Exception as e:
            errors.append(f"Failed to parse design-system-sync-report.json as valid JSON: {e}")
            
    if errors:
        print("\n--- DESIGN SYSTEM SYNC VALIDATION FAILED ---")
        for err in errors:
            print(f"ERROR: {err}")
        sys.exit(1)
    else:
        print("\n--- DESIGN SYSTEM SYNC VALIDATION PASSED ---")
        sys.exit(0)

if __name__ == "__main__":
    main()
