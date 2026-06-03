#!/usr/bin/env python3
import os
import sys
import json
import re
import argparse
from datetime import datetime, timezone

# Add root folder to sys.path
root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(root_dir)

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def calculate_match(node, signature):
    # Weights
    w_name = 0.20
    w_type = 0.10
    w_topology = 0.50
    w_tokens = 0.20

    # 1. Name Score
    name = node.get("name", "")
    name_pattern = signature.get("name_pattern", "")
    s_name = 0.0
    if name_pattern:
        try:
            if re.search(name_pattern, name, re.IGNORECASE):
                s_name = 1.0
            elif re.search(signature.get("component_id", ""), name, re.IGNORECASE):
                s_name = 0.5
        except Exception:
            if signature.get("component_id", "").lower() in name.lower():
                s_name = 0.5

    # 2. Node Type Score
    node_type = node.get("type", "")
    sig_node_type = signature.get("node_type", "")
    s_type = 1.0 if node_type == sig_node_type else 0.0

    # 3. Layout Topology Score
    topology = signature.get("layout_topology", {})
    children = node.get("children", [])
    s_topology = 1.0
    
    if topology:
        min_children = topology.get("min_children", 0)
        max_children = topology.get("max_children", 999)
        role_rules = topology.get("children", [])
        
        satisfied_roles = 0
        total_roles = len(role_rules)
        
        # Track child assignments to avoid double-counting
        used_child_ids = set()
        
        for rule in role_rules:
            role_name_pattern = rule.get("name_pattern", ".*")
            role_node_types = rule.get("node_types", [])
            min_count = rule.get("min_count", 0)
            max_count = rule.get("max_count", 999)
            
            matched_count = 0
            for child in children:
                if matched_count >= max_count:
                    break
                child_id = child.get("id")
                if child_id in used_child_ids:
                    continue
                child_type = child.get("type", "")
                child_name = child.get("name", "")
                
                type_matches = not role_node_types or child_type in role_node_types
                name_matches = False
                try:
                    name_matches = bool(re.search(role_name_pattern, child_name, re.IGNORECASE))
                except Exception:
                    name_matches = True
                    
                if type_matches and name_matches:
                    matched_count += 1
                    used_child_ids.add(child_id)
            
            if min_count <= matched_count <= max_count:
                satisfied_roles += 1
        
        if total_roles > 0:
            s_topology = satisfied_roles / total_roles
        else:
            s_topology = 1.0
            
        # Penalize if child count is out of bounds
        child_count = len(children)
        if child_count < min_children or child_count > max_children:
            s_topology *= 0.5

    # 4. Token Cluster Score
    token_cluster = signature.get("token_cluster", {})
    s_tokens = 1.0
    if token_cluster:
        classes = token_cluster.get("classes", [])
        css_props = token_cluster.get("css_properties", [])
        
        matched_tokens = 0
        total_tokens = len(classes) + len(css_props)
        
        if total_tokens > 0:
            # Check classes
            node_classes = node.get("classes", [])
            # Also check if name contains class as fallback (slugified)
            slugified_name = name.lower().replace(" ", "-").replace("_", "-")
            for cls in classes:
                if cls in node_classes or cls in slugified_name or cls in name.lower():
                    matched_tokens += 1
            
            # Check css properties from node styles if present
            node_styles = node.get("styles", {})
            for prop in css_props:
                # Mock styles might have keys or properties
                if prop in node_styles or prop in node.get("css_properties", []):
                    matched_tokens += 1
            
            s_tokens = matched_tokens / total_tokens

    # Total Score
    total_score = (w_name * s_name) + (w_type * s_type) + (w_topology * s_topology) + (w_tokens * s_tokens)
    return total_score

def walk_and_match(node, signatures, matched_list, unmatched_list, blockers, is_strict=True):
    node_type = node.get("type", "")
    node_name = node.get("name", "")
    node_id = node.get("id", "")

    # We evaluate frames, instances, or anything named with potential component triggers
    is_candidate = (node_type == "INSTANCE") or (node_type == "FRAME" and any(
        kw in node_name.lower() for kw in ["button", "card", "navbar", "nav", "footer", "form", "input", "group", "section"]
    ))

    if is_candidate:
        highest_score = 0.0
        best_sig = None
        
        for sig in signatures:
            score = calculate_match(node, sig)
            if score > highest_score:
                highest_score = score
                best_sig = sig
                
        if best_sig and highest_score >= 0.85:
            matched_list.append({
                "figma_node_id": node_id,
                "figma_node_name": node_name,
                "component_id": best_sig["component_id"],
                "signature_id": best_sig["id"],
                "confidence": round(highest_score, 4),
                "matching_notes": f"Matched {best_sig['id']} with confidence {highest_score:.2f}"
            })
        else:
            # Unmatched or candidate warning
            highest_component = best_sig["component_id"] if best_sig else None
            reason = f"No signature matched with usable confidence. Best match: {best_sig['id'] if best_sig else 'None'} ({highest_score:.2f})"
            
            unmatched_list.append({
                "figma_node_id": node_id,
                "figma_node_name": node_name,
                "highest_candidate_component": highest_component,
                "highest_confidence": round(highest_score, 4),
                "reason": reason
            })
            
            if is_strict:
                blockers.append(f"Strict Mode Blocker: Node '{node_name}' ({node_id}) has no usable component match ({highest_score:.2f} < 0.85)")

    # Recurse children
    for child in node.get("children", []):
        walk_and_match(child, signatures, matched_list, unmatched_list, blockers, is_strict)

def main():
    parser = argparse.ArgumentParser(description="Component Matching CLI")
    parser.add_argument("--figma-bundle", required=True, help="Path to Figma node bundle JSON")
    parser.add_argument("--registry", default="knowledge-base/component-registry.json", help="Path to component registry JSON")
    parser.add_argument("--signatures", default="knowledge-base/component-signatures.json", help="Path to signatures JSON")
    parser.add_argument("--out-match-report", default="workspace/reports/component-match-report.json", help="Output path for match report")
    parser.add_argument("--out-sync-report", default="workspace/reports/component-sync-report.json", help="Output path for sync report")
    parser.add_argument("--strict", action="store_true", default=True, help="Enable strict mode matching enforcement")

    args = parser.parse_args()

    # Resolve paths relative to root if they are relative
    figma_path = args.figma_bundle if os.path.isabs(args.figma_bundle) else os.path.join(root_dir, args.figma_bundle)
    registry_path = args.registry if os.path.isabs(args.registry) else os.path.join(root_dir, args.registry)
    sigs_path = args.signatures if os.path.isabs(args.signatures) else os.path.join(root_dir, args.signatures)
    out_match_path = args.out_match_report if os.path.isabs(args.out_match_report) else os.path.join(root_dir, args.out_match_report)
    out_sync_path = args.out_sync_report if os.path.isabs(args.out_sync_report) else os.path.join(root_dir, args.out_sync_report)

    if not os.path.exists(figma_path):
        print(f"Error: Figma bundle not found at {figma_path}")
        sys.exit(1)
    if not os.path.exists(registry_path):
        print(f"Error: Registry not found at {registry_path}")
        sys.exit(1)
    if not os.path.exists(sigs_path):
        print(f"Error: Signatures not found at {sigs_path}")
        sys.exit(1)

    print(f"Loading Figma Bundle: {figma_path}")
    bundle = load_json(figma_path)
    registry = load_json(registry_path)
    signatures = load_json(sigs_path).get("signatures", [])

    matched_instances = []
    unmatched_instances = []
    blockers = []

    # Run recursive matching from figma tree root
    tree = bundle.get("tree", {})
    if tree:
        walk_and_match(tree, signatures, matched_instances, unmatched_instances, blockers, args.strict)

    status = "pass" if not blockers else "fail"

    # 1. Save Component Match Report
    match_report = {
      "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
      "matched_instances": matched_instances,
      "unmatched_instances": unmatched_instances,
      "status": status,
      "blockers": blockers
    }
    save_json(out_match_path, match_report)
    print(f"Saved Component Match Report to {out_match_path} (Status: {status})")

    # 2. Save Component Sync Report
    synced_components = list(set(m["component_id"] for m in matched_instances))
    
    # Identify out of sync components
    # A component is out of sync if there are active unmatched instances that matched it as highest candidate
    out_of_sync = []
    for unm in unmatched_instances:
        cand = unm.get("highest_candidate_component")
        if cand and cand not in [o["component_id"] for o in out_of_sync]:
            out_of_sync.append({
                "component_id": cand,
                "reason": unm["reason"]
            })
            
    sync_report = {
      "timestamp": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
      "registry_version": "1.0.0",
      "total_components": len(registry.get("components", [])),
      "synced_components": synced_components,
      "out_of_sync_components": out_of_sync,
      "status": status,
      "errors": blockers
    }
    save_json(out_sync_path, sync_report)
    print(f"Saved Component Sync Report to {out_sync_path} (Status: {status})")

    if blockers:
        print(f"\nMatching failed with {len(blockers)} blocker(s):")
        for blk in blockers:
            print(f" - {blk}")
        sys.exit(1)
    else:
        print("\nComponent matching completed successfully. All components synced.")
        sys.exit(0)

if __name__ == "__main__":
    main()
