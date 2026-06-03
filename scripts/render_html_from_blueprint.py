#!/usr/bin/env python3
"""Render logical HTML Blueprint and output physical HTML with Client-First guidelines."""
from __future__ import annotations

import argparse
import html
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Ensure project root is in path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

def load_json(path: Path) -> Any:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))

def build_blueprint_node(sem_node: dict[str, Any]) -> dict[str, Any]:
    """Convert a semantic node into a blueprint node."""
    tag = sem_node.get("tag", "div")
    classes = sem_node.get("classes", [])
    
    # Construct attributes
    attrs = {
        "data-figma-node": sem_node.get("id", "")
    }

    # Data markers for sections & components
    role = sem_node.get("role", "")
    node_name = sem_node.get("name", "")
    if role == "section" or "section" in node_name.lower():
        attrs["data-section"] = sem_node.get("name", "Section")
    elif role == "component" or "component" in role:
        attrs["data-component"] = sem_node.get("name", "Component")

    node_type = sem_node.get("type", "FRAME")
    text_content = ""
    if node_type == "TEXT":
        # Text nodes hold raw content in figma name
        text_content = sem_node.get("name", "")

    children = []
    for child in sem_node.get("children", []):
        children.append(build_blueprint_node(child))

    node_bp = {
        "tag": tag,
        "classes": classes,
        "attributes": attrs,
        "children": children
    }
    if text_content:
        node_bp["text"] = text_content

    return node_bp

def render_blueprint_to_html(bp_node: dict[str, Any], indent_level: int = 0) -> str:
    """Recursively render a blueprint node into indented HTML."""
    indent = "  " * indent_level
    tag = bp_node.get("tag", "div")
    classes = bp_node.get("classes", [])
    attrs = bp_node.get("attributes", {})
    text_val = bp_node.get("text", "")
    children = bp_node.get("children", [])

    # Assemble attribute string
    attr_list = []
    if classes:
        attr_list.append(f'class="{" ".join(classes)}"')
    for k, v in attrs.items():
        attr_list.append(f'{k}="{html.escape(v)}"')
    
    attr_str = " " + " ".join(attr_list) if attr_list else ""

    # Self-closing tags
    if tag in ("img", "input", "br", "hr", "meta", "link") and not children and not text_val:
        return f"{indent}<{tag}{attr_str} />"

    # Single-line rendering for text only
    if not children and text_val:
        escaped_text = html.escape(text_val)
        return f"{indent}<{tag}{attr_str}>{escaped_text}</{tag}>"

    # Multi-line rendering for tags with children
    html_lines = [f"{indent}<{tag}{attr_str}>"]
    
    # If there is both text and children (uncommon in clean layouts but handled)
    if text_val:
        html_lines.append(f"{indent}  {html.escape(text_val)}")

    for child in children:
        html_lines.append(render_blueprint_to_html(child, indent_level + 1))

    html_lines.append(f"{indent}</{tag}>")
    return "\n".join(html_lines)

def main():
    parser = argparse.ArgumentParser(description="Render HTML from Semantic IR Blueprint")
    parser.add_argument("--input", default="workspace/semantic/figma.semantic-tree.json")
    parser.add_argument("--blueprint-out", default="workspace/html/page.blueprint.json")
    parser.add_argument("--html-out", default="workspace/html/page.html")
    args = parser.parse_args()

    input_path = Path(args.input)
    bp_path = Path(args.blueprint_out)
    html_path = Path(args.html_out)

    semantic_payload = load_json(input_path)
    if not semantic_payload:
        print(f"Error: Semantic tree payload {input_path} empty or missing.")
        sys.exit(1)

    semantic_root = semantic_payload.get("semantic_tree", {})
    
    # Build blueprint tree
    body_content_bp = build_blueprint_node(semantic_root)
    
    # Apply Client-First structural wrapping: page-wrapper -> main-wrapper -> contents
    # If the root semantic node is already page-wrapper, keep it, otherwise wrap it
    root_classes = body_content_bp.get("classes", [])
    
    if "page-wrapper" not in root_classes:
        # Wrap everything in page-wrapper and main-wrapper
        main_wrapper_bp = {
            "tag": "main",
            "classes": ["main-wrapper"],
            "attributes": {"role": "main"},
            "children": [body_content_bp]
        }
        body_bp = {
            "tag": "div",
            "classes": ["page-wrapper"],
            "attributes": {},
            "children": [main_wrapper_bp]
        }
    else:
        body_bp = body_content_bp

    blueprint_payload = {
        "version": "1.0.0",
        "page_title": semantic_payload.get("name", "Compiled Webflow Page"),
        "head_elements": [
            {"tag": "meta", "attributes": {"charset": "utf-8"}},
            {"tag": "meta", "attributes": {"name": "viewport", "content": "width=device-width, initial-scale=1"}},
            {"tag": "link", "attributes": {"rel": "stylesheet", "href": "../../source-css/normalize.css"}},
            {"tag": "link", "attributes": {"rel": "stylesheet", "href": "../../source-css/webflow.css"}},
            {"tag": "link", "attributes": {"rel": "stylesheet", "href": "../../source-css/client-first-v2-2.webflow.css"}}
        ],
        "body": body_bp,
        "metadata": {
            "compiled_at": datetime.now(timezone.utc).isoformat(),
            "source_semantic_tree": str(input_path)
        }
    }

    # Generate physical HTML content
    body_html = render_blueprint_to_html(body_bp, indent_level=1)
    
    head_lines = []
    for elem in blueprint_payload["head_elements"]:
        tag = elem["tag"]
        attrs = elem["attributes"]
        attr_str = " ".join(f'{k}="{html.escape(v)}"' for k, v in attrs.items())
        head_lines.append(f'  <{tag} {attr_str} />')

    head_html = "\n".join(head_lines)

    full_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
{head_html}
  <title>{blueprint_payload["page_title"]}</title>
</head>
<body>
{body_html}
</body>
</html>
"""

    # Write files
    bp_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.parent.mkdir(parents=True, exist_ok=True)

    bp_path.write_text(json.dumps(blueprint_payload, indent=2, ensure_ascii=False), encoding="utf-8")
    html_path.write_text(full_html, encoding="utf-8")

    print(f"HTML Rendering complete. Blueprint written to {bp_path}. HTML written to {html_path}.")
    sys.exit(0)

if __name__ == "__main__":
    main()
