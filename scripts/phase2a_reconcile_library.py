#!/usr/bin/env python3
"""B.1: Reconcile per-project library with what PM actually created on Webflow.

Input: workspace/blueprints/saas-futuristic-app_blueprint.json (new_classes list = 51 entries
that PM attempted to create, 1 of which already existed on the site).

Output:
- knowledge-base/libraries/<site_id>/client-first-library.json — mark 51 classes as
  status=created_on_webflow with created_at timestamp; set figma_token on color/typography
  classes from the blueprint cf_category mapping.
- knowledge-base/libraries/<site_id>/figma-token-map.json — create if missing, with the
  7 color token mappings derived from workspace/rawdata/saas-futuristic-app_raw.json#tokens.color.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SITE_ID = "6920a7d45c61690dd10ac690"
BLUEPRINT = REPO / "workspace" / "blueprints" / "saas-futuristic-app_blueprint.json"
RAWDATA = REPO / "workspace" / "rawdata" / "saas-futuristic-app_raw.json"
LIB_PATH = REPO / "knowledge-base" / "libraries" / SITE_ID / "client-first-library.json"
TOKEN_PATH = REPO / "knowledge-base" / "libraries" / SITE_ID / "figma-token-map.json"

# Map class name -> figma_token. Color tokens are explicit; layout/structure classes get
# the blueprint's source path as a tag.
COLOR_TOKEN_MAP = {
    "background-color-background-base": "background-base",
    "background-color-primary": "primary",
    "background-color-inverse": "inverse",
    "text-color-primary": "primary",
    "text-color-muted": "muted",
    "text-color-caption": "caption",
    "text-color-inverse": "inverse",
    "text-color-footer-muted": "footer-muted",
    "border-color-primary": "primary",
    "border-color-border-subtle": "border-subtle",
}

TYPOGRAPHY_TOKEN_HINT = {
    "text-size-": "font-size",
    "text-weight-": "font-weight",
    "heading-style-": "font-size",
}


def main() -> int:
    blueprint = json.loads(BLUEPRINT.read_text(encoding="utf-8"))
    raw = json.loads(RAWDATA.read_text(encoding="utf-8"))
    lib = json.loads(LIB_PATH.read_text(encoding="utf-8"))
    now = datetime.now(timezone.utc).isoformat()

    blueprint_class_names = {nc["name"] for nc in blueprint["new_classes"]}

    updated = 0
    for name, entry in lib["classes"].items():
        if name in blueprint_class_names:
            entry["status"] = "created_on_webflow"
            entry["created_at"] = now
            if name in COLOR_TOKEN_MAP:
                entry["figma_token"] = COLOR_TOKEN_MAP[name]
            else:
                entry["figma_token"] = "declared-in-blueprint"
            updated += 1
        else:
            entry.setdefault("figma_token", "cf-v2.2-utility")

    lib["version"] = "0.3.0"
    lib["updated_at"] = now
    lib["reconciled_count"] = updated
    LIB_PATH.write_text(json.dumps(lib, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"updated {updated} class entries in client-first-library.json")

    # Create figma-token-map.json (was missing per explore)
    figma_colors = raw["tokens"]["color"]
    token_map = {
        "figma_file_id": "",
        "updated_at": now,
        "naming_convention": {
            "pattern": "{cf_category}-{semantic_name}",
            "categories": ["text-color", "background-color", "border-color"],
        },
        "mappings": {
            "background-base": {
                "figma_value": figma_colors["background_base"],
                "css_property": "background-color",
                "class": "background-color-background-base",
                "source": "figma:138:8546"
            },
            "primary": {
                "figma_value": figma_colors["text_primary"],
                "css_property": "color",
                "class": "text-color-primary",
                "source": "figma:138:8546"
            },
            "muted": {
                "figma_value": figma_colors["text_muted"],
                "css_property": "color",
                "class": "text-color-muted",
                "source": "figma:138:8546"
            },
            "caption": {
                "figma_value": figma_colors["text_caption"],
                "css_property": "color",
                "class": "text-color-caption",
                "source": "figma:138:8546"
            },
            "inverse": {
                "figma_value": figma_colors["text_inverse_on_light"],
                "css_property": "color",
                "class": "text-color-inverse",
                "source": "figma:138:8546"
            },
            "footer-muted": {
                "figma_value": figma_colors["text_footer_muted"],
                "css_property": "color",
                "class": "text-color-footer-muted",
                "source": "figma:138:8546"
            },
            "border-subtle": {
                "figma_value": figma_colors["border_subtle"],
                "css_property": "border-color",
                "class": "border-color-border-subtle",
                "source": "figma:138:8546"
            },
        },
    }
    TOKEN_PATH.write_text(json.dumps(token_map, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"wrote figma-token-map.json with {len(token_map['mappings'])} mappings")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
