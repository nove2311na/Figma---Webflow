#!/usr/bin/env python3
"""Resolve Semantic roles, HTML tags, and Client-First class choices strictly."""
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
from tools.utils import load_client_first_class_map

def load_json(path: Path) -> Any:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))

class SemanticResolver:
    def __init__(self, tag_rules: dict[str, Any], class_rules: dict[str, Any], contract: dict[str, Any]):
        self.tag_rules = tag_rules.get("tag_resolution", {})
        self.class_rules = class_rules.get("selection_policy", {})
        self.contract = contract
        
        self.allowed_classes = set(contract.get("allowed_classes", []))
        self.allowed_combo_classes = set(contract.get("allowed_combo_classes", []))
        self.structural_classes = set(contract.get("structural_convention_classes", ["page-wrapper", "main-wrapper"]))
        self.reserved_classes = set(contract.get("reserved_webflow_classes", []))

        self.missing_classes = []
        self.missing_tokens = []
        self.unresolved_elements = []
        self.warnings = []
        
        self.stats = {
            "resolved_nodes": 0,
            "classes_verified": 0,
            "confidence_sum": 0.0
        }

    def infer_role_and_tag(self, node: dict[str, Any], parent_tag: str | None = None) -> tuple[str, str, float]:
        """Infer the semantic role, HTML tag, and confidence score."""
        node_name = node.get("name", "").lower()
        node_type = node.get("type", "FRAME").upper()
        classes = node.get("classes", [])

        # Priority 1: Component registry default tags
        component_name = node.get("component_name", "")
        if component_name:
            role = "component"
            tag = "div"
            if component_name.lower() == "button":
                role = "button"
                tag = "a"
            elif component_name.lower() == "navigation bar" or "nav" in component_name.lower():
                role = "navigation"
                tag = "nav"
            elif "footer" in component_name.lower():
                role = "footer"
                tag = "footer"
            return role, tag, 0.95

        # Priority 2: Explicit prefixes in name, e.g. [h1], [section], [button]
        prefix_match = re.match(r"^\[([a-z0-9]+)\]", node.get("name", ""))
        if prefix_match:
            tag = prefix_match.group(1)
            role = f"custom-{tag}"
            return role, tag, 0.98

        # Priority 3: Normalized role mapping based on class lists
        role = "structure"
        tag = "div"
        confidence = 0.70

        if "button" in classes or "button-group" in classes:
            role = "button"
            tag = "a"
            confidence = 0.90
        elif "nav_component" in classes:
            role = "navigation"
            tag = "nav"
            confidence = 0.90
        elif "form_input" in classes or "form_component" in classes:
            role = "control"
            tag = "input"
            if "is-text-area" in classes:
                tag = "textarea"
            confidence = 0.90
        elif "text-rich-text" in classes:
            role = "rich_text"
            tag = "div"
            confidence = 0.90
        elif "padding-section-large" in classes or "padding-section-medium" in classes or "padding-section-small" in classes:
            role = "section"
            tag = "section"
            confidence = 0.85
        elif node_type == "TEXT":
            # Typography check
            is_heading = False
            for cls in classes:
                if cls.startswith("heading-style-"):
                    h_level = cls.replace("heading-style-", "")
                    role = f"heading-{h_level}"
                    tag = h_level
                    is_heading = True
                    confidence = 0.95
                    break
            if not is_heading:
                # Default text tag
                role = "paragraph"
                tag = "p"
                confidence = 0.80
        elif node.get("ambiguous_media") or node.get("media_kind") == "vector":
            role = "media"
            tag = "img"
            confidence = 0.85

        # Priority 4: Standard role-to-tag configurations from tag.rules.yaml
        rule_mappings = self.tag_rules.get("mappings", [])
        for mapping in rule_mappings:
            if mapping.get("role") == role:
                tag = mapping.get("tag", tag)
                break

        # Priority 5: Context check (lists, forms, sections)
        if parent_tag == "ul" or parent_tag == "ol":
            tag = "li"
            role = "list-item"
            confidence = 0.95

        # Rule overrides for generic tags
        if node_type == "FRAME" and "section" in node_name:
            role = "section"
            tag = "section"
            confidence = 0.85

        return role, tag, confidence

    def resolve_classes(self, node_id: str, raw_classes: list[str]) -> list[str]:
        resolved = []
        for cls in raw_classes:
            # Check validation rules
            is_valid = (
                cls in self.allowed_classes or
                cls in self.allowed_combo_classes or
                cls in self.structural_classes or
                cls in self.reserved_classes or
                cls.startswith("w-")  # Webflow native
            )
            if is_valid:
                resolved.append(cls)
                self.stats["classes_verified"] += 1
            else:
                self.missing_classes.append({
                    "node_id": node_id,
                    "class_name": cls,
                    "reason": f"Class '{cls}' is not defined in Client-First contract."
                })
                # If strict mode blocks, we do not append to resolved classes
                if self.class_rules.get("strict_mode", True):
                    # In strict mode, unknown classes are excluded or block execution
                    pass
                else:
                    resolved.append(cls)
        return resolved

    def resolve_node(self, node: dict[str, Any], parent_tag: str | None = None) -> dict[str, Any]:
        node_id = node.get("id", "unknown")
        
        # tag and role resolution
        role, tag, confidence = self.infer_role_and_tag(node, parent_tag)
        self.stats["resolved_nodes"] += 1
        self.stats["confidence_sum"] += confidence

        # Class verification
        resolved_classes = self.resolve_classes(node_id, node.get("classes", []))

        # Media resolution (Phase 9 placeholder, populated deterministically)
        media = {}
        if tag == "img" or node.get("ambiguous_media"):
            media_role = "decorative" if "decorative" in node.get("name", "").lower() else "informative"
            media = {
                "kind": node.get("media_kind", "image"),
                "role": media_role,
                "alt_policy": "required" if media_role == "informative" else "decorative",
                "alt_text": "Decorative image" if media_role == "decorative" else node.get("name", "Asset image"),
                "asset_ref": f"assets/{node_id}.png"
            }

        # Resolve children
        resolved_children = []
        for child in node.get("children", []):
            resolved_children.append(self.resolve_node(child, parent_tag=tag))

        return {
            "id": node_id,
            "name": node.get("name", ""),
            "type": node.get("type", "FRAME"),
            "role": role,
            "tag": tag,
            "classes": resolved_classes,
            "styles": node.get("styles", {}),
            "media": media,
            "children": resolved_children
        }

def main():
    parser = argparse.ArgumentParser(description="Resolve Semantic IR tag and class choices")
    parser.add_argument("--input", default="workspace/figma/figma.normalized-tree.json")
    parser.add_argument("--output", default="workspace/semantic/figma.semantic-tree.json")
    parser.add_argument("--tag-rules", default="agentic/rules/tag.rules.yaml")
    parser.add_argument("--class-rules", default="agentic/rules/class-selection.rules.yaml")
    parser.add_argument("--contract", default="knowledge-base/generated/client-first-library-contract.json")
    parser.add_argument("--reports-dir", default="workspace/reports")
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)
    tag_rules_path = Path(args.tag_rules)
    class_rules_path = Path(args.class_rules)
    contract_path = Path(args.contract)
    reports_dir = Path(args.reports-dir) if hasattr(args, "reports-dir") else Path(args.reports_dir)

    # Load resources
    norm_tree_payload = load_json(input_path)
    
    # Rules parsing helper
    import yaml
    tag_rules = {}
    if tag_rules_path.exists():
        try:
            tag_rules = yaml.safe_load(tag_rules_path.read_text(encoding="utf-8"))
        except Exception:
            tag_rules = {}
    class_rules = {}
    if class_rules_path.exists():
        try:
            class_rules = yaml.safe_load(class_rules_path.read_text(encoding="utf-8"))
        except Exception:
            class_rules = {}

    contract = load_json(contract_path)

    if not norm_tree_payload:
        print(f"Error: Input normalized tree {input_path} empty or missing.")
        sys.exit(1)

    resolver = SemanticResolver(tag_rules, class_rules, contract)
    
    # Process
    normalized_tree = norm_tree_payload.get("normalized_tree", {})
    semantic_tree = resolver.resolve_node(normalized_tree)

    # Calculate global metrics
    node_count = resolver.stats["resolved_nodes"]
    avg_confidence = resolver.stats["confidence_sum"] / node_count if node_count > 0 else 0.0

    # Strict compliance validation
    success = True
    if avg_confidence < 0.60:
        success = False
        resolver.unresolved_elements.append({
            "node_id": semantic_tree.get("id"),
            "node_name": semantic_tree.get("name"),
            "reason": f"Global resolver confidence average {avg_confidence:.2f} is below strict threshold 0.60"
        })

    # Blocker check
    if len(resolver.missing_classes) > 0 and class_rules.get("selection_policy", {}).get("missing_class_behavior", "block") == "block":
        success = False

    # Output files
    output_payload = {
        "node_id": norm_tree_payload.get("node_id", "unknown"),
        "name": norm_tree_payload.get("name", "unknown"),
        "semantic_tree": semantic_tree,
        "metadata": {
            "resolved_at": datetime.now(timezone.utc).isoformat(),
            "resolver_version": "1.0.0",
            "confidence_score": round(avg_confidence, 3)
        }
    }

    missing_report = {
        "resolved_at": datetime.now(timezone.utc).isoformat(),
        "missing_classes": resolver.missing_classes,
        "missing_tokens": resolver.missing_tokens,
        "unresolved_elements": resolver.unresolved_elements,
        "confidence_score": round(avg_confidence, 3),
        "success": success
    }

    tag_report = {
        "resolved_at": datetime.now(timezone.utc).isoformat(),
        "nodes_resolved": node_count,
        "average_confidence": round(avg_confidence, 3),
        "success": success
    }

    class_usage_report = {
        "resolved_at": datetime.now(timezone.utc).isoformat(),
        "classes_verified": resolver.stats["classes_verified"],
        "missing_classes_count": len(resolver.missing_classes),
        "success": success
    }

    # Collect assets for manifest
    def collect_assets(node: dict[str, Any], assets_list: list[dict[str, Any]]) -> None:
        media_item = node.get("media")
        if media_item and media_item.get("kind") != "none":
            assets_list.append({
                "figma_node_id": node.get("id"),
                "filename": f"{node.get('id')}.png",
                "role": media_item.get("role", "informative"),
                "alt_text": media_item.get("alt_text", ""),
                "aria_hidden": media_item.get("role") == "decorative",
                "local_path": media_item.get("asset_ref", "")
            })
        for child in node.get("children", []):
            collect_assets(child, assets_list)

    assets = []
    collect_assets(semantic_tree, assets)
    
    asset_manifest = {
        "version": "1.0.0",
        "assets": assets,
        "metadata": {
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "total_assets": len(assets)
        }
    }
    asset_manifest_path = output_path.parent.parent / "html" / "asset-manifest.json"
    asset_manifest_path.parent.mkdir(parents=True, exist_ok=True)
    asset_manifest_path.write_text(json.dumps(asset_manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    # Ensure parent dirs exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    output_path.write_text(json.dumps(output_payload, indent=2, ensure_ascii=False), encoding="utf-8")
    (reports_dir / "missing-mapping-report.json").write_text(json.dumps(missing_report, indent=2, ensure_ascii=False), encoding="utf-8")
    (reports_dir / "tag-report.json").write_text(json.dumps(tag_report, indent=2, ensure_ascii=False), encoding="utf-8")
    (reports_dir / "class-usage-report.json").write_text(json.dumps(class_usage_report, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Semantic resolution complete. Success: {success}. Confidence: {avg_confidence:.2f}")
    if not success:
        sys.exit(2)
    sys.exit(0)

if __name__ == "__main__":
    main()
