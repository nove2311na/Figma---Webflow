import re
import json
import sys

def parse_report(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the "High-confidence replace plan" section
    high_conf_match = re.search(r'## High-confidence replace plan\n.*?\n\|---\|---\|---\:\|---\:\|---\|\n(.*?)\n\n', content, re.DOTALL)
    
    high_conf_replacements = []
    if high_conf_match:
        lines = high_conf_match.group(1).strip().split('\n')
        for line in lines:
            parts = [p.strip().strip('`') for p in line.split('|')[1:-1]]
            if len(parts) >= 2:
                old_path = parts[0]
                new_path = parts[1]
                high_conf_replacements.append((old_path, new_path))

    # Find "Invalid path occurrences requiring review/delete/runtime handling"
    invalid_match = re.search(r'## Invalid path occurrences requiring review/delete/runtime handling\n.*?\n\|---\|---\|---\|---\:\|---\|---\|\n(.*)', content, re.DOTALL)
    
    review_items = []
    if invalid_match:
        # Since it's the last section (probably), split by newline
        lines = invalid_match.group(1).strip().split('\n')
        for line in lines:
            if not line.startswith('|'): continue
            parts = [p.strip().strip('`') for p in line.split('|')[1:-1]]
            if len(parts) >= 3:
                path = parts[0]
                action = parts[1]
                candidate = parts[2]
                review_items.append((path, action, candidate))

    return high_conf_replacements, review_items

if __name__ == '__main__':
    file_path = r'C:\Users\ADMIN\Downloads\path_audit_report (1).md'
    high_conf, review = parse_report(file_path)
    print(f"Found {len(high_conf)} high-confidence replacements.")
    print(f"Found {len(review)} items to review/delete.")
