#!/usr/bin/env python3
"""Compile sliced HTML section chunks into a serialized Webflow Native Build Plan."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Try to use BeautifulSoup
try:
    from bs4 import BeautifulSoup
    USE_BS4 = True
except ImportError:
    USE_BS4 = False

def load_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def compile_node(element: Any, operations: list[dict[str, Any]], parent_node_id: str | None = None) -> str | None:
    """Recursively compile HTML elements into build plan operations."""
    if not hasattr(element, "name") or element.name is None:
        return None

    tag = element.name
    classes = element.get("class", [])
    figma_id = element.get("data-figma-node") or f"gen-{element.name}-{len(operations)}"
    
    # Map HTML tags to Webflow native element types
    el_type = "div"
    if tag in ("h1", "h2", "h3", "h4", "h5", "h6"):
        el_type = "heading"
    elif tag == "p":
        el_type = "paragraph"
    elif tag == "span":
        el_type = "text-block"
    elif tag == "a":
        el_type = "link"
    elif tag == "img":
        el_type = "image"
    elif tag == "input":
        el_type = "input"

    # Create element operation
    op = {
        "type": "create_element",
        "payload": {
            "type": el_type,
            "tag": tag,
            "classes": classes,
            "parent_id": parent_node_id,
            "text": element.get_text(strip=True) if tag in ("p", "span", "h1", "h2", "h3", "h4", "h5", "h6", "a") and not element.find() else ""
        },
        "node_id": figma_id
    }
    
    if tag == "img":
        op["payload"]["src"] = element.get("src", "")
        op["payload"]["alt"] = element.get("alt", "")

    operations.append(op)

    # Compile children
    for child in element.find_all(recursive=False):
        compile_node(child, operations, parent_node_id=figma_id)

    return figma_id

def compile_chunks(chunks_dir: Path, manifest: dict[str, Any]) -> list[dict[str, Any]]:
    operations = []
    
    # Pre-seed classes if any
    # (In a real run, classes are resolved from the Client-First contract)
    
    for chunk in manifest.get("chunks", []):
        filename = chunk.get("filename")
        chunk_type = chunk.get("type")
        if chunk_type == "global-styles" or not filename:
            continue

        chunk_path = chunks_dir / filename
        if not chunk_path.exists():
            continue

        content = chunk_path.read_text(encoding="utf-8")
        
        if USE_BS4:
            soup = BeautifulSoup(content, "html.parser")
            root_el = soup.find()
            if root_el:
                compile_node(root_el, operations)
        else:
            # Simple regex fallback if BS4 not installed
            # Extract classes and tags
            tags = re.findall(r'<([a-z1-6]+)([^>]*class="([^"]+)")?[^>]*>(.*?)</\1>', content, re.DOTALL)
            for idx, (tag, _, classes_str, text) in enumerate(tags):
                classes = classes_str.split() if classes_str else []
                operations.append({
                    "type": "create_element",
                    "payload": {
                        "type": tag,
                        "tag": tag,
                        "classes": classes,
                        "parent_id": None,
                        "text": text.strip() if "<" not in text else ""
                    },
                    "node_id": f"gen-regex-{idx}"
                })

    return operations

def main():
    parser = argparse.ArgumentParser(description="Compile HTML Chunks into Webflow Native Build Plan")
    parser.add_argument("--chunks-dir", default="workspace/html/chunks")
    parser.add_argument("--meta", default="workspace/meta.json")
    parser.add_argument("--output", default="workspace/webflow-native/native-build-plan.json")
    args = parser.parse_args()

    chunks_dir = Path(args.chunks_dir)
    meta_path = Path(args.meta)
    output_path = Path(args.output)

    manifest_path = chunks_dir / "section-manifest.json"
    if not manifest_path.exists():
        print(f"Error: manifest {manifest_path} is missing.")
        sys.exit(1)

    manifest = load_json(manifest_path)
    meta = load_json(meta_path)

    print(f"Compiling native operations from chunks in {chunks_dir}...")
    operations = compile_chunks(chunks_dir, manifest)

    build_plan = {
        "version": "1.0.0",
        "target_site_id": meta.get("webflowSiteId", "mock-site-id"),
        "target_page_id": meta.get("webflowPageId", "mock-page-id"),
        "target_branch": "refactor/html-first-compiler-revised",
        "operations": operations,
        "metadata": {
            "compiled_at": datetime.now(timezone.utc).isoformat(),
            "total_operations": len(operations)
        }
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(build_plan, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Compilation complete. Serialized {len(operations)} operations to {output_path}.")
    sys.exit(0)

if __name__ == "__main__":
    main()
