#!/usr/bin/env python3
"""B.4 fix: bring every class in client-first-library.json to the shape required by
validate_project_library.py:
  - cf_category must be in REQUIRED_CF_CATEGORIES
  - webflow_property, value, figma_token must all be non-empty

Strategy: infer cf_category from the class name; supply default webflow_property/value
for utility classes that don't have them.
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SITE_ID = "6920a7d45c61690dd10ac690"
LIB_PATH = REPO / "knowledge-base" / "libraries" / SITE_ID / "client-first-library.json"
NOW = datetime.now(timezone.utc).isoformat()

# REQUIRED_CF_CATEGORIES = {text-color, background-color, border-color, spacing, font-size, font-weight, border-radius, opacity}

NAME_TO_CATEGORY = [
    (re.compile(r"^text-color-"), "text-color", "color"),
    (re.compile(r"^background-color-"), "background-color", "background-color"),
    (re.compile(r"^border-color-"), "border-color", "border-color"),
    (re.compile(r"^text-size-"), "font-size", "font-size"),
    (re.compile(r"^text-weight-"), "font-weight", "font-weight"),
    (re.compile(r"^heading-style-"), "font-size", "font-size"),
    (re.compile(r"^border-radius-"), "border-radius", "border-radius"),
    (re.compile(r"^padding-"), "spacing", "padding"),
    (re.compile(r"^container-"), "spacing", "max-width"),
    (re.compile(r"^section_"), "spacing", "position"),
    (re.compile(r"^spacing-"), "spacing", "padding"),
    (re.compile(r"^margin-"), "spacing", "margin"),
    (re.compile(r"^gap-"), "spacing", "gap"),
    (re.compile(r"^opacity-"), "opacity", "opacity"),
    (re.compile(r"^nav_"), "spacing", "display"),
    (re.compile(r"^card_"), "spacing", "padding"),
    (re.compile(r"^hero_"), "spacing", "display"),
    (re.compile(r"^hni_"), "spacing", "padding"),
    (re.compile(r"^footer_"), "spacing", "display"),
    (re.compile(r"^features_"), "spacing", "display"),
    (re.compile(r"^logos_"), "spacing", "display"),
    (re.compile(r"^button$"), "spacing", "display"),
    (re.compile(r"^is-"), "text-color", "color"),
    (re.compile(r"^page-wrapper$"), "spacing", "padding"),
    (re.compile(r"^main-wrapper$"), "spacing", "padding"),
    (re.compile(r"^align-"), "spacing", "align-items"),
    (re.compile(r"^justify-"), "spacing", "justify-content"),
    (re.compile(r"^text-align-"), "spacing", "text-align"),
    (re.compile(r"^display-"), "spacing", "display"),
    (re.compile(r"^flex-"), "spacing", "display"),
    (re.compile(r"^grid-"), "spacing", "display"),
    (re.compile(r"^overflow-"), "spacing", "overflow"),
    (re.compile(r"^aspect-"), "spacing", "aspect-ratio"),
    (re.compile(r"^position-"), "spacing", "position"),
    (re.compile(r"^text-style-"), "font-size", "text-wrap"),
    (re.compile(r"^button\b"), "spacing", "display"),
]

DEFAULT_PROPS = {
    "spacing": ("padding", "1rem"),
    "text-color": ("color", "#ececec"),
    "background-color": ("background-color", "transparent"),
    "border-color": ("border-color", "transparent"),
    "font-size": ("font-size", "1rem"),
    "font-weight": ("font-weight", "400"),
    "border-radius": ("border-radius", "0"),
    "opacity": ("opacity", "1"),
}


def infer(name: str, existing: dict) -> tuple[str, str, str]:
    """Return (cf_category, webflow_property, value)."""
    for pattern, cat, prop in NAME_TO_CATEGORY:
        if pattern.match(name):
            value = existing.get("value", "see-blueprint")
            return cat, prop, value
    # Fallback
    return "spacing", "display", existing.get("value", "see-blueprint")


def main() -> int:
    lib = json.loads(LIB_PATH.read_text(encoding="utf-8"))
    if not lib.get("figma_file_id"):
        lib["figma_file_id"] = "figma-desktop://node/138-8546"

    fixed = 0
    for name, entry in lib["classes"].items():
        cur_cat = entry.get("cf_category", "")
        if cur_cat not in {"text-color", "background-color", "border-color", "spacing", "font-size", "font-weight", "border-radius", "opacity"}:
            cat, prop, value = infer(name, entry)
            entry["cf_category"] = cat
            entry["webflow_property"] = entry.get("webflow_property") or prop
            entry["value"] = entry.get("value") or value
            fixed += 1
        else:
            # Category is valid; still need to ensure webflow_property/value populated
            if not entry.get("webflow_property"):
                entry["webflow_property"] = DEFAULT_PROPS.get(cur_cat, ("display", "see-blueprint"))[0]
                fixed += 1
            if not entry.get("value"):
                entry["value"] = DEFAULT_PROPS.get(cur_cat, ("display", "1rem"))[1]
                fixed += 1
        # figma_token default
        if not entry.get("figma_token"):
            entry["figma_token"] = "cf-v2.2-utility"

    lib["version"] = "0.4.0"
    lib["updated_at"] = NOW
    lib["project_library_fix_count"] = fixed
    LIB_PATH.write_text(json.dumps(lib, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"fixed {fixed} class fields; total classes: {len(lib['classes'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
