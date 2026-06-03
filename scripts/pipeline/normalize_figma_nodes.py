#!/usr/bin/env python3
"""Normalize Figma messy tree nodes before Semantic IR."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from tools.utils import parse_color, color_distance, slugify

def load_json(path: Path) -> Any:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))

def resolve_variable(var_name: str, var_index: dict[str, Any], visited: set[str] | None = None) -> str | None:
    """Recursively resolve a CSS variable to a raw value."""
    if visited is None:
        visited = set()
    if var_name in visited:
        return None  # Circular reference
    visited.add(var_name)

    entries = var_index.get(var_name, [])
    if not entries:
        return None
    
    # Get base value (media: null)
    base_val = None
    for entry in entries:
        if entry.get("media") is None:
            base_val = entry.get("value")
            break
    if not base_val:
        base_val = entries[0].get("value")

    if not base_val:
        return None

    # If it is var(--something), resolve recursively
    match = re.match(r"^var\(([^)]+)\)$", str(base_val).strip())
    if match:
        return resolve_variable(match.group(1), var_index, visited)
    return str(base_val)

class FigmaNormalizer:
    def __init__(self, rules: dict[str, Any], contract: dict[str, Any], var_index: dict[str, Any]):
        self.rules = rules.get("normalization_rules", {})
        self.allowed_classes = set(contract.get("allowed_classes", []))
        self.allowed_combo_classes = set(contract.get("allowed_combo_classes", []))
        self.allowed_variables = set(contract.get("allowed_variables", []))
        self.var_index = var_index
        
        # Build color variable cache
        self.color_vars = {}
        for var_name in self.allowed_variables:
            val = resolve_variable(var_name, self.var_index)
            if val:
                parsed = parse_color(val)
                if parsed:
                    self.color_vars[var_name] = val

        self.stats = {
            "generic_names_resolved": 0,
            "raw_colors_snapped": 0,
            "raw_spacing_snapped": 0,
            "layout_recovered": 0,
            "repeated_subtrees_found": 0,
            "blockers_count": 0,
            "warnings_count": 0
        }
        self.blockers = []
        self.warnings = []

    def normalize_node(self, node: dict[str, Any]) -> dict[str, Any]:
        node_id = node.get("id", "unknown")
        original_name = node.get("name", "")
        node_type = node.get("type", "FRAME")
        notes = []

        # 1. Generic names recovery
        name = original_name
        is_generic = False
        generic_patterns = self.rules.get("generic_names", [])
        for gp in generic_patterns:
            pattern = gp.get("pattern", "")
            if pattern and re.match(pattern, original_name):
                is_generic = True
                break

        if is_generic:
            # Infer name based on children or type
            children = node.get("children", [])
            child_types = [c.get("type") for c in children]
            
            if len(children) == 1 and children[0].get("type") == "TEXT":
                txt_content = children[0].get("name", "text")
                name = f"wrapper-{slugify(txt_content)}"
            elif "INSTANCE" in child_types:
                name = "component-wrapper"
            elif "IMAGE" in child_types or "RECTANGLE" in child_types:
                name = "media-wrapper"
            else:
                name = f"container-{slugify(node_type)}"
            
            notes.append(f"Normalized generic name '{original_name}' to '{name}'")
            self.stats["generic_names_resolved"] += 1

        # 2. Styles and raw colors normalization
        styles = node.get("styles", {})
        normalized_styles = {}
        classes = node.get("classes", [])

        # Ensure classes exist in contract
        valid_classes = []
        for cls in classes:
            if cls in self.allowed_classes or cls in self.allowed_combo_classes:
                valid_classes.append(cls)
            else:
                self.warnings.append({
                    "node_id": node_id,
                    "reason": f"Class '{cls}' not found in contract."
                })
                self.stats["warnings_count"] += 1

        for style_key, style_val in styles.items():
            if style_key in ("background-color", "color", "border-color"):
                # Check if it is a CSS variable
                if isinstance(style_val, str) and style_val.startswith("var("):
                    var_match = re.match(r"^var\(([^)]+)\)$", style_val)
                    if var_match:
                        var_name = var_match.group(1)
                        if var_name not in self.allowed_variables:
                            self.blockers.append({
                                "node_id": node_id,
                                "reason": f"Unrecognized CSS variable '{var_name}' in style '{style_key}'"
                            })
                            self.stats["blockers_count"] += 1
                    normalized_styles[style_key] = style_val
                else:
                    # It's a raw color value
                    parsed_raw = parse_color(style_val)
                    if parsed_raw:
                        # Find closest variable
                        closest_var = None
                        min_dist = float("inf")
                        for var_name, var_raw in self.color_vars.items():
                            dist = color_distance(style_val, var_raw)
                            if dist < min_dist:
                                min_dist = dist
                                closest_var = var_name

                        threshold = self.rules.get("untokenized_values", {}).get("threshold_snap_px", 15)
                        if closest_var and min_dist <= threshold:
                            normalized_styles[style_key] = f"var({closest_var})"
                            notes.append(f"Snapped raw color {style_val} to var({closest_var}) (dist: {min_dist:.2f})")
                            self.stats["raw_colors_snapped"] += 1
                        else:
                            normalized_styles[style_key] = style_val
                            msg = f"Raw color '{style_val}' in '{style_key}' has no close token match (closest: {closest_var} dist: {min_dist:.2f})."
                            if self.rules.get("untokenized_values", {}).get("mode") == "error_on_high_severity":
                                self.blockers.append({"node_id": node_id, "reason": msg})
                                self.stats["blockers_count"] += 1
                            else:
                                self.warnings.append({"node_id": node_id, "reason": msg})
                                self.stats["warnings_count"] += 1
                    else:
                        normalized_styles[style_key] = style_val
            elif style_key in ("padding", "margin", "gap"):
                # Simple spacing snapping (placeholder for robust layout logic)
                normalized_styles[style_key] = style_val
            else:
                normalized_styles[style_key] = style_val

        # 3. Layout Recovery
        layout = node.get("layout", {})
        if not layout and node_type in ("FRAME", "GROUP") and node.get("children"):
            # Check if auto-layout is enabled in rules
            if self.rules.get("auto_layout_recovery", {}).get("enabled", True):
                # Infer layout based on child coordinate offsets if available, otherwise default to vertical flex
                layout = {
                    "type": "flex",
                    "direction": "vertical",
                    "spacing": "0rem",
                    "padding": "0rem",
                    "wrap": True
                }
                notes.append("Recovered missing layout to default vertical flex")
                self.stats["layout_recovered"] += 1

        # 4. Check for ambiguous media
        ambiguous_media = False
        media_kind = "none"
        if node_type in ("VECTOR", "REGULAR_POLYGON", "STAR", "ELLIPSE"):
            ambiguous_media = True
            media_kind = "vector"
            notes.append("Marked vector layer as ambiguous media candidate")

        # Normalize children recursively
        normalized_children = []
        for child in node.get("children", []):
            normalized_children.append(self.normalize_node(child))

        # Build normalized node
        norm_node = {
            "id": node_id,
            "name": name,
            "original_name": original_name,
            "type": node_type,
            "classes": classes,
            "styles": normalized_styles,
            "layout": layout,
            "candidate_component": node.get("candidate_component", False),
            "component_name": node.get("component_name", ""),
            "ambiguous_media": ambiguous_media,
            "media_kind": media_kind,
            "normalization_notes": notes,
            "children": normalized_children
        }

        return norm_node

def main():
    parser = argparse.ArgumentParser(description="Normalize Figma Tree Nodes")
    parser.add_argument("--input", default="workspace/figma/figma.node-bundle.json")
    parser.add_argument("--output", default="workspace/figma/figma.normalized-tree.json")
    parser.add_argument("--report", default="workspace/reports/figma-normalization-report.json")
    parser.add_argument("--rules", default="agentic/rules/figma-normalization.rules.yaml")
    parser.add_argument("--contract", default="knowledge-base/generated/client-first-library-contract.json")
    parser.add_argument("--var-index", default="knowledge-base/generated/css-variable-index.json")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    report_path = Path(args.report)
    rules_path = Path(args.rules)
    contract_path = Path(args.contract)
    var_index_path = Path(args.var-index) if hasattr(args, "var-index") else Path(args.var_index)

    # Load data
    bundle = load_json(input_path)
    rules = load_json(rules_path) if rules_path.suffix == ".json" else {}
    if not rules and rules_path.exists():
        import yaml
        try:
            rules = yaml.safe_load(rules_path.read_text(encoding="utf-8"))
        except Exception:
            rules = {}

    contract = load_json(contract_path)
    var_index = load_json(var_index_path)

    if not bundle:
        print(f"Error: Input bundle {input_path} empty or missing.")
        sys.exit(1)

    normalizer = FigmaNormalizer(rules, contract, var_index)
    
    # Process tree
    raw_tree = bundle.get("tree", {})
    normalized_tree = normalizer.normalize_node(raw_tree)

    # Prepare outputs
    output_payload = {
        "node_id": bundle.get("node_id", "unknown"),
        "name": bundle.get("name", "unknown"),
        "normalized_tree": normalized_tree,
        "metadata": {
            "normalized_at": datetime.now(timezone.utc).isoformat(),
            "figma_file_version": bundle.get("metadata", {}).get("figma_file_version", "1.0"),
            "extractor_user": bundle.get("metadata", {}).get("extractor_user", "agent")
        }
    }

    success = len(normalizer.blockers) == 0
    report_payload = {
        "normalized_at": datetime.now(timezone.utc).isoformat(),
        "source_node_bundle": str(input_path),
        "stats": normalizer.stats,
        "blockers": normalizer.blockers,
        "warnings": normalizer.warnings,
        "success": success
    }

    # Ensure parent dirs exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    output_path.write_text(json.dumps(output_payload, indent=2, ensure_ascii=False), encoding="utf-8")
    report_path.write_text(json.dumps(report_payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Normalization complete. Success: {success}.")
    print(f"Blockers: {len(normalizer.blockers)}, Warnings: {len(normalizer.warnings)}")
    if not success:
        sys.exit(2)
    sys.exit(0)

if __name__ == "__main__":
    main()
