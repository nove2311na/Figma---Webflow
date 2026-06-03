#!/usr/bin/env python3
"""Extract Figma design context and styling data, compile a raw HTML with inline styles and a layout blueprint JSON."""
from __future__ import annotations

import argparse
import html
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

def load_json(path: Path) -> Any:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def extract_node_styles(node: dict[str, Any]) -> dict[str, str]:
    """Extract and normalize inline styles from Figma node properties."""
    raw_styles = node.get("styles", {})
    inline_styles = {}
    
    for key, val in raw_styles.items():
        # Keep background color, color, border, text styles, margins, padding, gaps, widths, heights
        if key in (
            "background-color", "color", "border-color", "border-width", "border-style",
            "padding", "padding-left", "padding-right", "padding-top", "padding-bottom",
            "margin", "margin-left", "margin-right", "margin-top", "margin-bottom",
            "font-size", "font-family", "font-weight", "line-height", "text-align",
            "gap", "width", "height", "display", "flex-direction", "justify-content",
            "align-items", "flex-wrap"
        ):
            inline_styles[key] = str(val)
            
    # Add display properties if flex-direction or layoutMode suggests flex
    layout_mode = node.get("layoutMode")
    if layout_mode in ("HORIZONTAL", "VERTICAL"):
        inline_styles["display"] = "flex"
        inline_styles["flex-direction"] = "row" if layout_mode == "HORIZONTAL" else "column"
        
        # Figma spacing mode to css justification
        primary_align = node.get("primaryAxisAlignItems")
        counter_align = node.get("counterAxisAlignItems")
        if primary_align == "CENTER":
            inline_styles["justify-content"] = "center"
        elif primary_align == "MAX":
            inline_styles["justify-content"] = "flex-end"
        elif primary_align == "SPACE_BETWEEN":
            inline_styles["justify-content"] = "space-between"
            
        if counter_align == "CENTER":
            inline_styles["align-items"] = "center"
        elif counter_align == "MAX":
            inline_styles["align-items"] = "flex-end"
            
        item_spacing = node.get("itemSpacing")
        if item_spacing is not None:
            inline_styles["gap"] = f"{item_spacing}px"
            
    # Normalize explicit paddings if layout properties are present
    paddings = []
    for side in ("top", "right", "bottom", "left"):
        pad_val = node.get(f"padding{side.capitalize()}")
        if pad_val is not None:
            inline_styles[f"padding-{side}"] = f"{pad_val}px"
            
    return inline_styles

def build_raw_blueprint(node: dict[str, Any]) -> dict[str, Any]:
    """Recursively traverse Figma nodes to build raw layout blueprint node."""
    node_id = node.get("id", "unknown")
    node_name = node.get("name", "Unnamed Node")
    node_type = node.get("type", "FRAME")
    
    styles = extract_node_styles(node)
    
    # Infer basic semantic tag based on Figma name patterns
    tag = "div"
    name_lower = node_name.lower()
    if "[section]" in name_lower or "section" in name_lower:
        tag = "section"
    elif "[h1]" in name_lower or "h1" in name_lower:
        tag = "h1"
    elif "[h2]" in name_lower or "h2" in name_lower:
        tag = "h2"
    elif "[h3]" in name_lower or "h3" in name_lower:
        tag = "h3"
    elif "[p]" in name_lower or "paragraph" in name_lower:
        tag = "p"
    elif "[a]" in name_lower or "button" in name_lower or "cta" in name_lower:
        tag = "a"
    elif node_type == "TEXT":
        tag = "p"

    text_content = node.get("characters", "") if node_type == "TEXT" else ""
    
    children = []
    for child in node.get("children", []):
        children.append(build_raw_blueprint(child))
        
    bp_node = {
        "id": node_id,
        "name": node_name,
        "type": node_type,
        "tag": tag,
        "styles": styles,
        "children": children
    }
    if text_content:
        bp_node["text"] = text_content
        
    return bp_node

def render_inline_html(node: dict[str, Any], indent_level: int = 0) -> str:
    """Recursively render raw blueprint nodes into raw HTML with inline styles."""
    indent = "  " * indent_level
    tag = node.get("tag", "div")
    styles = node.get("styles", {})
    text_content = node.get("text", "")
    children = node.get("children", [])
    
    # Assemble inline style attribute
    style_parts = [f"{k}: {v}" for k, v in styles.items()]
    style_str = f' style="{"; ".join(style_parts)}"' if style_parts else ""
    attrs_str = f' data-figma-id="{node.get("id")}"{style_str}'
    
    if not children and text_content:
        return f"{indent}<{tag}{attrs_str}>{html.escape(text_content)}</{tag}>"
        
    html_lines = [f"{indent}<{tag}{attrs_str}>"]
    if text_content:
        html_lines.append(f"{indent}  {html.escape(text_content)}")
        
    for child in children:
        html_lines.append(render_inline_html(child, indent_level + 1))
        
    html_lines.append(f"{indent}</{tag}>")
    return "\n".join(html_lines)

def main():
    parser = argparse.ArgumentParser(description="Extract Figma raw context and generate inline HTML")
    parser.add_argument("--input", default="workspace/figma/figma.raw-context.json")
    parser.add_argument("--output", default="workspace/html/raw-inline.html")
    parser.add_argument("--blueprint-out", default="workspace/figma/raw-layout-blueprint.json")
    args = parser.parse_args()
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    bp_path = Path(args.blueprint_out)
    
    # Fallback cascade to avoid breaking if raw-context does not exist yet
    if not input_path.exists():
        fallback_path = Path("workspace/figma/figma.node-bundle.json")
        if fallback_path.exists():
            input_path = fallback_path
        else:
            fallback_path = Path("tests/fixtures/figma/hero-clean.json")
            if fallback_path.exists():
                input_path = fallback_path
                
    print(f"Loading raw design data from: {input_path}")
    raw_payload = load_json(input_path)
    
    if not raw_payload:
        print(f"Error: Input data {input_path} empty or missing.")
        sys.exit(1)
        
    # Standardize tree root lookup
    raw_tree = raw_payload.get("tree") or raw_payload.get("normalized_tree")
    if not raw_tree and "id" in raw_payload:
        raw_tree = raw_payload
        
    if not raw_tree:
        print("Error: Could not locate Figma node tree root inside JSON payload.")
        sys.exit(1)
        
    # Generate blueprint
    blueprint_root = build_raw_blueprint(raw_tree)
    
    blueprint_payload = {
        "version": "1.0.0",
        "name": raw_payload.get("name", "Figma Compiled Raw Page"),
        "node_id": raw_payload.get("node_id", "unknown"),
        "blueprint_root": blueprint_root,
        "metadata": {
            "extracted_at": datetime.now(timezone.utc).isoformat(),
            "source_figma_file": str(input_path)
        }
    }
    
    # Render inline HTML
    body_html = render_inline_html(blueprint_root, indent_level=1)
    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>{blueprint_payload["name"]}</title>
</head>
<body>
{body_html}
</body>
</html>
"""
    
    # Ensure parents exist
    output_path.parent.mkdir(parents=True, exist_ok=True)
    bp_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write files
    bp_path.write_text(json.dumps(blueprint_payload, indent=2, ensure_ascii=False), encoding="utf-8")
    output_path.write_text(full_html, encoding="utf-8")
    
    print(f"Successfully generated raw layout blueprint: {bp_path}")
    print(f"Successfully generated raw inline-styled HTML: {output_path}")
    sys.exit(0)

if __name__ == "__main__":
    main()
