import os
import sys

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    print(f"Validating Archive Cleanup from Root: {root_dir}")
    
    # 1. Check archive README and migration log
    readme_path = os.path.join(root_dir, "archive", "README.md")
    migration_log_path = os.path.join(root_dir, "archive", "MIGRATION_LOG.md")
    
    errors = []
    
    if not os.path.exists(readme_path):
        errors.append("archive/README.md is missing.")
    if not os.path.exists(migration_log_path):
        errors.append("archive/MIGRATION_LOG.md is missing.")
        
    # 2. Verify old paths DO NOT exist
    old_paths = [
        "agentic/memory/final-report-saas-futuristic-app.md",
        "scripts/phase2a_reconcile_library.py",
        "scripts/phase2b_synthesize_logs.py",
        "scripts/phase3_fix_library.py",
        "scripts/phase3_fix_tokenmap.py",
        "scripts/run_all_gates.py",
        "knowledge-base/libraries/6920a7d45c61690dd10ac690",
        "knowledge-base/libraries/6a1fa213c04827556dcac7b5",
        "agentic/prompts/write-html-contract.md",
    ]
    
    for op in old_paths:
        full_op = os.path.join(root_dir, op)
        if os.path.exists(full_op):
            errors.append(f"Old path still exists: {op}")
            
    # 3. Verify moved paths exist under archive
    archive_paths = [
        "archive/runs/saas-futuristic-app/final-report.md",
        "archive/runs/saas-futuristic-app/scripts/phase2a_reconcile_library.py",
        "archive/runs/saas-futuristic-app/scripts/phase2b_synthesize_logs.py",
        "archive/runs/saas-futuristic-app/scripts/phase3_fix_library.py",
        "archive/runs/saas-futuristic-app/scripts/phase3_fix_tokenmap.py",
        "archive/runs/saas-futuristic-app/scripts/run_all_gates.py",
        "archive/site-libraries/6920a7d45c61690dd10ac690",
        "archive/site-libraries/6a1fa213c04827556dcac7b5",
        "archive/deprecated-workflows/write-html-contract.webflow-first.md",
    ]
    
    for ap in archive_paths:
        full_ap = os.path.join(root_dir, ap)
        if not os.path.exists(full_ap):
            errors.append(f"Moved archive path is missing: {ap}")
            
    # 4. Search for references to old scripts/folders in active codebase
    # excluding .git, archive, .gitnexus, .user_bugs-log, .user_versions, workspace, docs, and generated files
    forbidden_terms = [
        "phase2a_reconcile_library",
        "phase2b_synthesize_logs",
        "phase3_fix_library",
        "phase3_fix_tokenmap",
        "run_all_gates",
        "write-html-contract"
    ]
    
    exclude_dirs = {
        ".git", 
        "archive", 
        ".gitnexus", 
        ".user_bugs-log", 
        ".user_versions", 
        "workspace", 
        "docs",
        "__pycache__"
    }
    exclude_files = {
        "repomix-output.xml", 
        "validate_archive_cleanup.py",
        "registry.json"
    }
    
    for root, dirs, files in os.walk(root_dir):
        # prune excluded dirs
        dirs[:] = [d for d in dirs if d not in exclude_dirs]
        for file in files:
            if file in exclude_files or file.endswith(".xml") or file.endswith(".jsonl"):
                continue
            file_path = os.path.join(root, file)
            rel_file_path = os.path.relpath(file_path, root_dir)
            
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    for term in forbidden_terms:
                        if term in content:
                            lines = content.splitlines()
                            for i, line in enumerate(lines):
                                if term in line:
                                    # If not an archive reference
                                    if "archive/" not in line:
                                        errors.append(f"Active file '{rel_file_path}' (line {i+1}) contains reference to forbidden term '{term}': {line.strip()}")
            except Exception as e:
                pass
                
    if errors:
        print("\n--- ARCHIVE CLEANUP VALIDATION FAILED ---")
        for err in errors:
            print(f"ERROR: {err}")
        sys.exit(1)
    else:
        print("\n--- ARCHIVE CLEANUP VALIDATION PASSED ---")
        sys.exit(0)

if __name__ == "__main__":
    main()
