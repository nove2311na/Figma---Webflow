import os
import sys
import json

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    match_report_path = os.path.join(root_dir, "workspace", "reports", "component-match-report.json")
    sync_report_path = os.path.join(root_dir, "workspace", "reports", "component-sync-report.json")
    
    print(f"Validating Component Matching Gate at:\n - {match_report_path}\n - {sync_report_path}")
    
    errors = []
    
    # 1. Validate Component Match Report
    if not os.path.exists(match_report_path):
        errors.append(f"Component Match report is missing: {match_report_path}. Run matching script first.")
    else:
        try:
            with open(match_report_path, "r", encoding="utf-8") as f:
                report = json.load(f)
                
            # Perform strict validation of required fields
            for prop in ["timestamp", "matched_instances", "unmatched_instances", "status", "blockers"]:
                if prop not in report:
                    errors.append(f"Property '{prop}' is missing from component-match-report.json")
                    
            status = report.get("status", "")
            if status != "pass":
                errors.append(f"Match status is '{status}' (must be 'pass')")
                
            blockers = report.get("blockers", [])
            if blockers:
                errors.append(f"Match report contains blockers: {blockers}")
                
        except Exception as e:
            errors.append(f"Failed to parse component-match-report.json as valid JSON: {e}")

    # 2. Validate Component Sync Report
    if not os.path.exists(sync_report_path):
        errors.append(f"Component Sync report is missing: {sync_report_path}. Run matching script first.")
    else:
        try:
            with open(sync_report_path, "r", encoding="utf-8") as f:
                report = json.load(f)
                
            # Perform strict validation of required fields
            for prop in ["timestamp", "registry_version", "total_components", "synced_components", "out_of_sync_components", "status", "errors"]:
                if prop not in report:
                    errors.append(f"Property '{prop}' is missing from component-sync-report.json")
                    
            status = report.get("status", "")
            if status != "pass":
                errors.append(f"Sync status is '{status}' (must be 'pass')")
                
            sync_errors = report.get("errors", [])
            if sync_errors:
                errors.append(f"Sync report contains errors: {sync_errors}")
                
        except Exception as e:
            errors.append(f"Failed to parse component-sync-report.json as valid JSON: {e}")
            
    if errors:
        print("\n--- COMPONENT MATCHING VALIDATION FAILED ---")
        for err in errors:
            print(f"ERROR: {err}")
        sys.exit(1)
    else:
        print("\n--- COMPONENT MATCHING VALIDATION PASSED ---")
        sys.exit(0)

if __name__ == "__main__":
    main()
