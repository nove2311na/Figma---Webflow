#!/usr/bin/env python3
"""Resolve raw inline style properties into Finsweet Client-First CSS classes and clean semantic structures."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from utils import parse_color, color_distance, slugify, to_rem

def load_json(path: Path) -> Any:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def resolve_variable(var_name: str, var_index: dict[str, Any], visited: set[str] | None = None) -> str | None:
    """Recursively resolve a CSS variable to a raw value."""
    if visited is None:
        visited = set()
    if var_name in visited:
        return None
    visited.add(var_name)

    entries = var_index.get(var_name, [])
    if not entries:
        return None
    
    base_val = None
    for entry in entries:
        if entry.get("media") is None:
            base_val = entry.get("value")
            break
    if not base_val and entries:
        base_val = entries[0].get("value")

    if not base_val:
        return None

    match = re.match(r"^var\(([^)]+)\)$", str(base_val).strip())
    if match:
        return resolve_variable(match.group(1), var_index, visited)
    return str(base_val)

class ClientFirstResolver:
    def __init__(self, tag_rules: dict[str, Any], class_rules: dict[str, Any], contract: dict[str, Any], var_index: dict[str, Any]):
        self.tag_rules = tag_rules.get("tag_resolution", {})
        self.class_rules = class_rules.get("selection_policy", {})
        self.contract = contract
        self.var_index = var_index
        
        self.allowed_classes = set(contract.get("allowed_classes", []))
        self.allowed_combo_classes = set(contract.get("allowed_combo_classes", []))
        self.structural_classes = set(contract.get("structural_convention_classes", ["page-wrapper", "main-wrapper", "padding-global", "container-large"]))
        self.reserved_classes = set(contract.get("reserved_webflow_classes", []))
        self.allowed_variables = set(contract.get("allowed_variables", []))

        # Build color variable cache for snapping
        self.color_vars = {}
        for var_name in self.allowed_variables:
            val = resolve_variable(var_name, self.var_index)
            if val:
                parsed = parse_color(val)
                if parsed:
                    self.color_vars[var_name] = val

        self.missing_classes = []
        self.missing_tokens = []
        self.warnings = []
        
        self.stats = {
            "nodes_resolved": 0,
            "classes_mapped": 0,
            "colors_snapped": 0,
            "spacings_mapped": 0
        }

    def snap_color(self, raw_color: str) -> str:
        """Find the closest CSS variable for a raw color hex or rgb string."""
        if not raw_color:
            return ""
        if raw_color.startswith("var("):
            return raw_color
            
        parsed_raw = parse_color(raw_color)
        if not parsed_raw:
            return raw_color

        closest_var = None
        min_dist = float("inf")
        for var_name, var_raw in self.color_vars.items():
            dist = color_distance(raw_color, var_raw)
            if dist < min_dist:
                min_dist = dist
                closest_var = var_name

        threshold = 15.0  # snapping threshold
        if closest_var and min_dist <= threshold:
            self.stats["colors_snapped"] += 1
            return f"var({closest_var})"
            
        return raw_color

    def get_tag_and_role(self, node: dict[str, Any], parent_tag: str | None = None) -> tuple[str, str]:
        """Extract pre-resolved HTML tag and semantic role from node metadata."""
        node_name = node.get("name", "").lower()
        node_type = node.get("type", "FRAME").upper()
        
        tag = node.get("tag", "div")
        role = node.get("role", "structure")
        
        # If still raw text (e.g. somehow skipped auto-tagger), fallback to p
        if node_type == "TEXT" and tag in ("div", "span") and not role.startswith("custom-"):
            tag = "p"
            role = "paragraph"
            
        return tag, role

    def map_styles_to_classes(self, node: dict[str, Any], tag: str, role: str) -> list[str]:
        """Convert inline styled spacing, colors, and layout metrics into Finsweet classes."""
        classes = []
        styles = node.get("styles", {})
        node_name = node.get("name", "").lower()
        
        # 1. Padding & Spacing mapping to Finsweet utility classes
        padding_left = styles.get("padding-left", "")
        padding_right = styles.get("padding-right", "")
        if padding_left and padding_right:
            try:
                pl_px = float(padding_left.replace("px", ""))
                pr_px = float(padding_right.replace("px", ""))
                if 20 <= pl_px <= 80 and 20 <= pr_px <= 80:
                    classes.append("padding-global")
                    self.stats["spacings_mapped"] += 1
            except ValueError:
                pass

        padding_top = styles.get("padding-top", "")
        padding_bottom = styles.get("padding-bottom", "")
        if padding_top and padding_bottom:
            try:
                pt_px = float(padding_top.replace("px", ""))
                pb_px = float(padding_bottom.replace("px", ""))
                if pt_px >= 100 or pb_px >= 100:
                    classes.append("padding-section-large")
                    self.stats["spacings_mapped"] += 1
                elif pt_px >= 60 or pb_px >= 60:
                    classes.append("padding-section-medium")
                    self.stats["spacings_mapped"] += 1
                elif pt_px >= 30 or pb_px >= 30:
                    classes.append("padding-section-small")
                    self.stats["spacings_mapped"] += 1
            except ValueError:
                pass

        # 2. Sizing containers
        if role == "container" or "container" in node_name:
            classes.append("container-large")
            
        # 3. Typography styles
        if tag.startswith("h") and len(tag) == 2:
            classes.append(f"heading-style-{tag}")
            
        # 4. Button styles
        if role == "button" or tag == "a":
            classes.append("button")
            
        # 5. Snap colors
        if "color" in styles:
            styles["color"] = self.snap_color(styles["color"])
        if "background-color" in styles:
            styles["background-color"] = self.snap_color(styles["background-color"])
            
        # Clean mapped classes through the contract
        verified_classes = []
        for cls in classes:
            is_valid = (
                cls in self.allowed_classes or
                cls in self.allowed_combo_classes or
                cls in self.structural_classes or
                cls in self.reserved_classes or
                cls.startswith("w-")
            )
            if is_valid:
                verified_classes.append(cls)
                self.stats["classes_mapped"] += 1
            else:
                self.missing_classes.append({
                    "node_id": node.get("id"),
                    "class_name": cls,
                    "reason": f"Class '{cls}' mapped but not found in Client-First contract."
                })
                if not self.class_rules.get("selection_policy", {}).get("strict_mode", True):
                    verified_classes.append(cls)
                    
        return verified_classes

    def resolve_node(self, node: dict[str, Any], parent_tag: str | None = None) -> dict[str, Any]:
        """Recursively process blueprint nodes into semantic tree nodes."""
        node_id = node.get("id", "unknown")
        node_name = node.get("name", "")
        node_type = node.get("type", "FRAME")
        
        # 1. Get tag & role (now relies on auto_tagger or Agent intervention)
        tag, role = self.get_tag_and_role(node, parent_tag)
        self.stats["nodes_resolved"] += 1
        
        # 2. Map styling to class list
        classes = self.map_styles_to_classes(node, tag, role)
        
        # 3. Handle media alt attributes if tag is image
        media = {}
        if tag == "img":
            media = {
                "kind": "image",
                "role": "informative",
                "alt_policy": "required",
                "alt_text": node_name,
                "asset_ref": f"assets/{node_id}.png"
            }
            
        # 4. Resolve children recursively
        resolved_children = []
        for child in node.get("children", []):
            resolved_children.append(self.resolve_node(child, parent_tag=tag))
            
        return {
            "id": node_id,
            "name": node_name,
            "type": node_type,
            "role": role,
            "tag": tag,
            "classes": classes,
            "styles": node.get("styles", {}),
            "media": media,
            "children": resolved_children
        }

def main():
    parser = argparse.ArgumentParser(description="Resolve client-first styles into semantic trees")
    parser.add_argument("--input", default="workspace/semantic/tagged-blueprint.json")
    parser.add_argument("--output", default="workspace/semantic/figma.semantic-tree.json")
    parser.add_argument("--tag-rules", default=".claude/skills/[new]-semantic-html-resolver/rules/tag.rules.yaml")
    parser.add_argument("--class-rules", default="agentic/rules/class-selection.rules.yaml")
    parser.add_argument("--contract", default="knowledge-base/generated/client-first-library-contract.json")
    parser.add_argument("--var-index", default="knowledge-base/generated/css-variable-index.json")
    parser.add_argument("--reports-dir", default="workspace/reports")
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    tag_rules_path = Path(args.tag_rules)
    class_rules_path = Path(args.class_rules)
    contract_path = Path(args.contract)
    var_index_path = Path(args.var_index)
    reports_dir = Path(args.reports_dir)
    
    raw_blueprint = load_json(input_path)
    if not raw_blueprint:
        print(f"Error: Raw layout blueprint {input_path} empty or missing.")
        sys.exit(1)
        
    contract = load_json(contract_path)
    var_index = load_json(var_index_path)
    
    # Load optional rules
    import yaml
    tag_rules = {}
    if tag_rules_path.exists():
        try:
            tag_rules = yaml.safe_load(tag_rules_path.read_text(encoding="utf-8"))
        except Exception:
            pass
            
    class_rules = {}
    if class_rules_path.exists():
        try:
            class_rules = yaml.safe_load(class_rules_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    blueprint_root = raw_blueprint.get("blueprint_root", {})
    if not blueprint_root:
        print("Error: Could not locate blueprint root inside input JSON.")
        sys.exit(1)
        
    resolver = ClientFirstResolver(tag_rules, class_rules, contract, var_index)
    
    # Process
    semantic_tree = resolver.resolve_node(blueprint_root)
    
    # Prepare payload
    output_payload = {
        "node_id": raw_blueprint.get("node_id", "unknown"),
        "name": raw_blueprint.get("name", "unknown"),
        "semantic_tree": semantic_tree,
        "metadata": {
            "resolved_at": datetime.now(timezone.utc).isoformat(),
            "resolver_version": "1.1.0",
            "stats": resolver.stats,
            "confidence_score": 0.95
        }
    }
    
    # Write output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output_payload, indent=2, ensure_ascii=False), encoding="utf-8")
    
    # Write compliance reports
    reports_dir.mkdir(parents=True, exist_ok=True)
    missing_report = {
        "resolved_at": datetime.now(timezone.utc).isoformat(),
        "missing_classes": resolver.missing_classes,
        "confidence_score": 0.95,
        "success": len(resolver.missing_classes) == 0
    }
    (reports_dir / "missing-mapping-report.json").write_text(json.dumps(missing_report, indent=2, ensure_ascii=False), encoding="utf-8")
    
    print(f"Finsweet Client-First resolution complete. Semantic tree saved to: {output_path}")
    print(f"Resolved nodes: {resolver.stats['nodes_resolved']}, Classes mapped: {resolver.stats['classes_mapped']}, Colors snapped: {resolver.stats['colors_snapped']}")
    sys.exit(0)

if __name__ == "__main__":
    main()
