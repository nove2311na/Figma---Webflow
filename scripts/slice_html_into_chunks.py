#!/usr/bin/env python3
"""Slice the compiled HTML page into self-contained section chunks."""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Try to use BeautifulSoup, fallback to simple custom regex if missing
try:
    from bs4 import BeautifulSoup
    USE_BS4 = True
except ImportError:
    USE_BS4 = False

def load_json(path: Path) -> Any:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))

def slice_with_bs4(html_content: str, chunks_dir: Path) -> list[dict[str, Any]]:
    soup = BeautifulSoup(html_content, "html.parser")
    chunks = []

    # 1. Global styles chunk
    head = soup.find("head")
    styles_html = ""
    if head:
        links = head.find_all("link")
        styles_html = "\n".join(str(link) for link in links)

    global_styles_filename = "section-global-styles.html"
    (chunks_dir / global_styles_filename).write_text(styles_html, encoding="utf-8")
    chunks.append({
        "id": "global-styles",
        "name": "Global Styles",
        "filename": global_styles_filename,
        "figma_node_id": "global",
        "type": "global-styles"
    })

    # 2. Main structure checks
    # Find navigation elements (either <nav> or element with nav classes)
    nav_el = soup.find("nav") or soup.find(class_=re.compile("nav"))
    if nav_el:
        nav_filename = "section-nav.html"
        (chunks_dir / nav_filename).write_text(str(nav_el), encoding="utf-8")
        chunks.append({
            "id": "nav",
            "name": "Navigation Bar",
            "filename": nav_filename,
            "figma_node_id": nav_el.get("data-figma-node", "nav"),
            "type": "nav"
        })

    # Find sections
    # They can be inside <main> or directly in body
    main_el = soup.find("main") or soup.find(class_="main-wrapper")
    sections_container = main_el if main_el else soup.find("body")
    
    sections = []
    if sections_container:
        # Find direct children that are sections or sections by tag/class
        sections = sections_container.find_all(["section", "div"], recursive=False)
        # If no direct children found, search for sections inside container
        if not sections:
            sections = sections_container.find_all("section")

    section_idx = 1
    for sec in sections:
        # Avoid double-slicing nav/footer
        if sec.name in ("nav", "footer") or "nav" in "".join(sec.get("class", [])) or "footer" in "".join(sec.get("class", [])):
            continue
            
        figma_id = sec.get("data-figma-node", f"section-{section_idx}")
        sec_name = sec.get("data-section") or sec.get("id") or f"section-{section_idx}"
        slug = re.sub(r"[^a-z0-9\-]", "", sec_name.lower().replace(" ", "-").replace("_", "-"))
        filename = f"section-{slug}.html"

        (chunks_dir / filename).write_text(str(sec), encoding="utf-8")
        chunks.append({
            "id": f"section-{slug}",
            "name": sec_name,
            "filename": filename,
            "figma_node_id": figma_id,
            "type": "section"
        })
        section_idx += 1

    # 3. Footer chunk
    footer_el = soup.find("footer") or soup.find(class_=re.compile("footer"))
    if footer_el:
        footer_filename = "section-footer.html"
        (chunks_dir / footer_filename).write_text(str(footer_el), encoding="utf-8")
        chunks.append({
            "id": "footer",
            "name": "Footer",
            "filename": footer_filename,
            "figma_node_id": footer_el.get("data-figma-node", "footer"),
            "type": "footer"
        })

    return chunks

def slice_with_regex(html_content: str, chunks_dir: Path) -> list[dict[str, Any]]:
    # Fallback regex-based slicing if beautifulsoup is absent
    chunks = []
    
    # Extract link stylesheets
    links = re.findall(r'<link[^>]*href="[^"]*"[^>]*>', html_content)
    styles_html = "\n".join(links)
    global_styles_filename = "section-global-styles.html"
    (chunks_dir / global_styles_filename).write_text(styles_html, encoding="utf-8")
    chunks.append({
        "id": "global-styles",
        "name": "Global Styles",
        "filename": global_styles_filename,
        "figma_node_id": "global",
        "type": "global-styles"
    })

    # Regex search for sections with data-section/data-figma-node
    sections = re.findall(r'(<(section|div)[^>]*data-section="([^"]*)"[^>]*>.*?</\2>)', html_content, re.DOTALL)
    for idx, (full_tag, tag_name, sec_name) in enumerate(sections, 1):
        figma_match = re.search(r'data-figma-node="([^"]*)"', full_tag)
        figma_id = figma_match.group(1) if figma_match else f"section-{idx}"
        
        slug = re.sub(r"[^a-z0-9\-]", "", sec_name.lower().replace(" ", "-").replace("_", "-"))
        filename = f"section-{slug}.html"
        (chunks_dir / filename).write_text(full_tag, encoding="utf-8")
        
        sec_type = "section"
        if "nav" in slug or "navbar" in slug:
            sec_type = "nav"
        elif "footer" in slug:
            sec_type = "footer"

        chunks.append({
            "id": f"section-{slug}",
            "name": sec_name,
            "filename": filename,
            "figma_node_id": figma_id,
            "type": sec_type
        })

    return chunks

def main():
    parser = argparse.ArgumentParser(description="Slice HTML file into section chunks")
    parser.add_argument("--input", default="workspace/html/page.html")
    parser.add_argument("--chunks-dir", default="workspace/html/chunks")
    args = parser.parse_args()

    input_path = Path(args.input)
    chunks_dir = Path(args.chunks_dir)

    if not input_path.exists():
        print(f"Error: Input HTML file {input_path} is missing.")
        sys.exit(1)

    html_content = input_path.read_text(encoding="utf-8")
    chunks_dir.mkdir(parents=True, exist_ok=True)

    if USE_BS4:
        print("Using BeautifulSoup for robust HTML parsing.")
        chunks = slice_with_bs4(html_content, chunks_dir)
    else:
        print("Warning: bs4 not found. Using fallback regex parser.")
        chunks = slice_with_regex(html_content, chunks_dir)

    # Write manifest
    manifest_payload = {
        "version": "1.0.0",
        "chunks": chunks,
        "metadata": {
            "sliced_at": datetime.now(timezone.utc).isoformat(),
            "total_chunks": len(chunks)
        }
    }

    manifest_path = chunks_dir / "section-manifest.json"
    manifest_path.write_text(json.dumps(manifest_payload, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Slicing complete. Sliced {len(chunks)} chunks under {chunks_dir}.")
    sys.exit(0)

if __name__ == "__main__":
    main()
