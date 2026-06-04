import os
import re

def get_files_to_process(root_dir):
    files_to_process = []
    # Dirs to skip completely
    skip_dirs = {'.git', 'node_modules', '__pycache__', '.pytest_cache', '.user_bugs-log', '.user_versions'}
    
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Remove skipped dirs in-place to prevent os.walk from visiting them
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        
        for file in filenames:
            if file.endswith(('.md', '.json', '.yaml', '.py', '.ts', '.js')):
                files_to_process.append(os.path.join(dirpath, file))
                
    return files_to_process

def parse_report(report_path):
    with open(report_path, 'r', encoding='utf-8') as f:
        content = f.read()

    high_conf_replacements = {}
    high_conf_match = re.search(r'## High-confidence replace plan\n.*?\n\|---\|---\|---\:\|---\:\|---\|\n(.*?)\n\n', content, re.DOTALL)
    if high_conf_match:
        lines = high_conf_match.group(1).strip().split('\n')
        for line in lines:
            parts = [p.strip().strip('`') for p in line.split('|')[1:-1]]
            if len(parts) >= 2:
                old_path = parts[0]
                new_path = parts[1].split(' | ')[0]  # Take the first candidate if multiple
                high_conf_replacements[old_path] = new_path

    replace_candidates = {}
    invalid_match = re.search(r'## Invalid path occurrences requiring review/delete/runtime handling\n.*?\n\|---\|---\|---\|---\:\|---\|---\|\n(.*)', content, re.DOTALL)
    if invalid_match:
        lines = invalid_match.group(1).strip().split('\n')
        for line in lines:
            if not line.startswith('|'): continue
            parts = [p.strip().strip('`') for p in line.split('|')[1:-1]]
            if len(parts) >= 3:
                path = parts[0]
                action = parts[1]
                candidate = parts[2]
                if action == 'replace-candidate' and candidate:
                    new_path = candidate.split(' | ')[0]
                    replace_candidates[path] = new_path

    return high_conf_replacements, replace_candidates

def apply_replacements(files, replacements):
    modified_files = 0
    total_replacements = 0
    for file_path in files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content = content
            file_modified = False
            for old_p, new_p in replacements.items():
                if not old_p or not new_p: continue
                # We do a basic string replacement.
                if old_p in new_content:
                    new_content = new_content.replace(old_p, new_p)
                    file_modified = True
                    total_replacements += new_content.count(new_p) - content.count(new_p)
            
            if file_modified:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                modified_files += 1
                print(f"Modified: {file_path}")
                
        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            
    return modified_files, total_replacements

if __name__ == '__main__':
    workspace = r'g:\My Drive\10_Learning\_Research\auto-research\.docs\source\MAS-Figma-Webflow-khang'
    report_file = r'C:\Users\ADMIN\Downloads\path_audit_report (1).md'
    
    print("Parsing report...")
    high_conf, replace_cand = parse_report(report_file)
    print(f"High-confidence pairs: {len(high_conf)}")
    print(f"Replace-candidate pairs: {len(replace_cand)}")
    
    # Merge both dicts
    all_replacements = {**high_conf, **replace_cand}
    
    print("Finding files to process...")
    files = get_files_to_process(workspace)
    print(f"Found {len(files)} files to check.")
    
    print("Applying replacements...")
    mod_files, mod_count = apply_replacements(files, all_replacements)
    print(f"Done. Modified {mod_files} files.")
